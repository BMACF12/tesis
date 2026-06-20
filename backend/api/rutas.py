import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import settings

router = APIRouter()

@router.post("/evaluar_documento/")
async def evaluar_documento(file: UploadFile = File(...)):
    # 1. Validar que el archivo subido sea un PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pdf")

    # Asegurar que el directorio exista
    import uuid
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    safe_filename = f"temp_{uuid.uuid4().hex}.pdf"
    temp_pdf_path = os.path.join(settings.DOCS_DIR, safe_filename)

    try:
        # 2. Guardar el archivo PDF temporalmente
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # 3. Enviar a la cola de Redis de forma asíncrona mediante Celery
            from services.tareas_ia import auditar_documento_pesado
            tarea = auditar_documento_pesado.delay(temp_pdf_path, file.filename)
            
            return {
                "mensaje": "Documento recibido y encolado para auditoría en segundo plano.",
                "task_id": tarea.id,
                "documento": file.filename
            }
        except Exception as e:
            import traceback
            print("="*50)
            print(f"🚨 ERROR AL ENCOLAR TAREA: {str(e)}")
            traceback.print_exc()
            print("="*50)
            raise HTTPException(status_code=500, detail=f"Error al enviar la tarea a Celery: {str(e)}")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"🚨 ERROR GENERAL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
        
    # NOTA: Se ha eliminado el bloque 'finally' que borraba el archivo temporal.
    # Ahora la responsabilidad de borrar el PDF es del Worker de Celery una vez analizado.

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
