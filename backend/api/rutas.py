import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import settings

router = APIRouter()

from typing import List

@router.post("/evaluar_documento/")
async def evaluar_documento(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos")
        
    import uuid
    from celery import chord, group
    from services.tareas_ia import auditar_documento_pesado, generar_reporte_ejecutivo
    
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    
    firmas = []
    lista_info = []
    
    try:
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"El archivo {file.filename} debe ser PDF")
                
            safe_filename = f"temp_{uuid.uuid4().hex}.pdf"
            temp_pdf_path = os.path.join(settings.DOCS_DIR, safe_filename)
            
            with open(temp_pdf_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            firmas.append(auditar_documento_pesado.s(temp_pdf_path, file.filename))
            lista_info.append({"documento": file.filename})
            
        id_lote = f"LOTE_{uuid.uuid4().hex[:8]}"
        callback = generar_reporte_ejecutivo.s(id_lote)
        
        # Orquestación con Chord
        g = group(firmas)
        chord_result = chord(g)(callback)
        
        # chord_result es el AsyncResult de generar_reporte_ejecutivo.
        # chord_result.parent es el GroupResult que contiene las tareas de auditar_documento_pesado.
        task_ids = [res.id for res in chord_result.parent.results]
        
        for i, info in enumerate(lista_info):
            info["task_id"] = task_ids[i]
            info["status"] = "EN COLA"
            
        return {
            "mensaje": f"Lote {id_lote} encolado para auditoría.",
            "id_lote": id_lote,
            "tareas": lista_info,
            "callback_task_id": chord_result.id
        }
        
    except Exception as e:
        import traceback
        print("="*50)
        print(f"🚨 ERROR AL ENCOLAR LOTE: {str(e)}")
        traceback.print_exc()
        print("="*50)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    from services.tareas_ia import celery_app
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"status": "EN COLA"}
    elif task_result.state == 'SUCCESS':
        return {"status": "COMPLETADO", "resultado": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "ERROR", "error": str(task_result.info)}
    else:
        return {"status": task_result.state}
