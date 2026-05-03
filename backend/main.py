from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.rutas import router

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
