# Auditor IA - Sistema de Evaluación Normativa CACES (N-Capas)

Este proyecto implementa un sistema automatizado de evaluación de evidencias documentales (Sílabos, Mallas Curriculares, etc.) basado en la normativa oficial del CACES (Ecuador) 2024. 

El sistema ha sido escalado a una **Arquitectura de N-Capas** robusta para manejar procesamiento concurrente y masivo de PDFs sin colapsar, integrando:
- **Frontend:** Interfaz de usuario interactiva y moderna construida con Next.js (React) y TailwindCSS.
- **Backend (API):** Servidor web de alto rendimiento con FastAPI.
- **Cola de Tareas (Broker):** Redis.
- **Worker Asíncrono:** Celery para procesar la Inteligencia Artificial en segundo plano.
- **IA y RAG:** LangChain, ChromaDB (Base de datos vectorial), Groq (LLM ultrarrápido) y Google Gemini (Embeddings).

---

## 🛠️ Requisitos Previos del Sistema

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu máquina:

1. **Python 3.10 o superior**: Asegúrate de marcar **"Add Python to PATH"** durante la instalación.
2. **Node.js (LTS)**: Necesario para levantar el entorno del Frontend (Next.js). Descárgalo desde [nodejs.org](https://nodejs.org/).
3. **Docker Desktop**: Requerido para levantar fácilmente la base de datos Redis. Descárgalo desde [docker.com](https://www.docker.com/).
4. **Git**: Para clonar el repositorio.

### Dependencias Nativas para Windows (Muy Importante)
El sistema extrae texto e imágenes complejas de los PDF. **Es estrictamente obligatorio** tener instalados a nivel de sistema operativo:
1. **Poppler** (Para el procesamiento base del PDF). Descárgalo, colócalo en `C:\poppler` y añade `C:\poppler\bin` a tus variables de entorno (PATH).
2. **Tesseract OCR** (Para leer texto incrustado en imágenes). Instálalo y añade `C:\Program Files\Tesseract-OCR` a tus variables de entorno (PATH).

> **⚠️ Advertencia:** Después de modificar el PATH en Windows, es obligatorio reiniciar tus terminales y el editor de código.

---

## 🚀 Guía de Instalación y Despliegue (Paso a Paso)

Sigue estos pasos en orden para encender todas las capas del sistema.

### PASO 1: Levantar Redis (El Broker de Mensajes)
Abre una terminal y ejecuta Docker para descargar e iniciar Redis en el puerto por defecto (6379):
```bash
docker run -d -p 6379:6379 --name redis-caces redis
```

### PASO 2: Configurar el Backend (FastAPI + Celery)
Abre una nueva terminal y navega a la carpeta del backend:
```bash
# 1. Entrar al backend
cd backend

# 2. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate   # (En Mac/Linux usa: source venv/bin/activate)

# 3. Instalar absolutamente todas las librerías
pip install -r requirements.txt
```

Crea un archivo `.env` en la carpeta `backend` con tus claves de acceso:
```env
GROQ_API_KEY=tu_api_key_de_groq_aqui
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
```

### PASO 3: Construir la "Base de Oro" (RAG)
Por única vez (o cuando se actualice la normativa), debes crear la base de conocimiento vectorial de ChromaDB:
```bash
# Estando dentro de la carpeta 'backend' y con el venv activado:
python scripts/crear_base_oro.py
```

### PASO 4: Encender la API (Servidor Web)
Deja esta terminal abierta ejecutando el backend de FastAPI:
```bash
# Estando dentro de la carpeta 'backend' y con el venv activado:
uvicorn main:app --reload
```
La API Gateway quedará escuchando en `http://127.0.0.1:8000`.

### PASO 5: Encender el Worker de Celery (Cerebro de la IA)
Abre una **NUEVA terminal**, navega a la carpeta `backend`, activa el entorno virtual y ejecuta el "obrero" que procesará los PDFs pesados en segundo plano:
```bash
cd backend
.\venv\Scripts\activate

# Comando para encender Celery en Windows:
celery -A services.tareas_ia worker --loglevel=info --pool=solo
```

### PASO 6: Encender el Frontend (Next.js)
Abre una **NUEVA terminal**, navega a la carpeta `frontend` y lanza la interfaz de usuario:
```bash
cd frontend

# 1. Instalar dependencias de Node
npm install

# 2. Levantar servidor de desarrollo
npm run dev
```

---

## 🎯 ¿Cómo usar el sistema?

1. Ve a **`http://localhost:3000`** en tu navegador.
2. Arrastra y suelta un lote completo de PDFs (ej. 5 sílabos al mismo tiempo) en la caja principal.
3. Haz clic en "Analizar y Clasificar".
4. Disfruta de la magia. Verás cómo los archivos pasan al estado "EN COLA". Celery los irá tomando uno a uno desde Redis y los procesará sin colapsar tu navegador. Las tarjetas gráficas se abrirán como un acordeón a medida que lleguen los resultados de los dictámenes generados por Llama-3.
