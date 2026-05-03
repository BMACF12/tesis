import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    PROJECT_NAME: str = "API Gateway - Sistema CACES RAG"
    
    # Configuración de CORS
    CORS_ORIGINS = ["*"]  # En producción cambiar por la URL del frontend (ej. ["http://localhost:3000"])
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Rutas base relativas a backend/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_DIR = os.path.join(BASE_DIR, "documentos_prueba")
    CHROMA_DIR = os.path.join(BASE_DIR, "chroma_data")

settings = Settings()
