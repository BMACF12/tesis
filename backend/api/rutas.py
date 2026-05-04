import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.rag_service import RAGService
from core.config import settings

router = APIRouter()
rag_service = RAGService()

@router.post("/evaluar_documento/")
async def evaluar_documento(file: UploadFile = File(...)):
    # 1. Validar que el archivo subido sea un PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pdf")

    # Asegurar que el directorio exista
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    temp_pdf_path = os.path.join(settings.DOCS_DIR, f"temp_{file.filename}")

    try:
        # 2. Guardar el archivo PDF temporalmente
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # 3. Delegar TODA la lógica de negocio al servicio RAG
            resultado = rag_service.procesar_documento(temp_pdf_path)
            
            # 4. Fase Final: Orquestador de Archivos Físicos (Triage)
            from services.orchestrator_service import enrutar_documento
            enrutar_documento(resultado, temp_pdf_path, file.filename)
            
            return resultado
        except Exception as e:
            import traceback
            print("="*50)
            print(f"🚨 ERROR FATAL AL PROCESAR: {str(e)}")
            traceback.print_exc()
            print("="*50)
            raise HTTPException(status_code=500, detail=f"Error en procesamiento de IA u Orquestador: {str(e)}")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"🚨 ERROR GENERAL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
        
    finally:
        # 4. Limpieza: Eliminar siempre el archivo temporal
        if os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as cleanup_error:
                print(f"Advertencia: No se pudo eliminar el archivo temporal: {cleanup_error}")
