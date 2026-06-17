from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.rutas import router
from tareas_ia import auditar_documento_pesado

# Inicializar la aplicación con un nombre limpio
app = FastAPI(title=settings.PROJECT_NAME)

# Configuración de CORS usando las variables de core/config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Incluir las rutas (Endpoints)
app.include_router(router)

@app.get("/")
def read_root():
    return {"status": f"{settings.PROJECT_NAME} inicializado bajo arquitectura N-Capas."}

# =========================================================
# ENDPOINT DE PRUEBA PARA LA COLA DE TAREAS (CELERY + REDIS)
# =========================================================
@app.post("/api/auditar-prueba")
async def procesar_evidencia_prueba(ruta_pdf: str):
    
    # 1. Enviar el documento a la sala de espera de Redis
    # El comando .delay() es la clave de la arquitectura asíncrona
    auditar_documento_pesado.delay(ruta_pdf)
    
    # 2. Responder de inmediato al usuario sin trabar el servidor
    return {
        "estado": "Aceptado",
        "mensaje": f"El documento '{ruta_pdf}' entró a la cola. El análisis inteligente inició en segundo plano."
    }