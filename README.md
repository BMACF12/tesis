# Sistema de Evaluación Normativa CACES (RAG + FastAPI)

Este proyecto implementa un sistema automatizado de evaluación de documentos académicos (como Sílabos, Mallas Curriculares, etc.) basado en la normativa del CACES (Ecuador). Utiliza una arquitectura de Generación Aumentada por Recuperación (RAG) integrando FastAPI para el backend, bases de datos vectoriales (ChromaDB) y modelos de lenguaje de gran tamaño (LLMs) para dictámenes automatizados.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

1. **Python 3.10 o superior**: Puedes descargarlo desde [python.org](https://www.python.org/downloads/). 
   > **⚠️ CRÍTICO:** Durante el instalador de Python, **DEBES marcar la casilla que dice "Add Python to PATH"** en la primera pantalla. Si no lo haces, los comandos no funcionarán en tu terminal y no podrás levantar el entorno.
2. **Git**: Para clonar el repositorio. Descárgalo e instálalo desde [git-scm.com](https://git-scm.com/).

## Dependencias del Sistema para Windows (Muy Importante)

Nuestro sistema utiliza la estrategia `hi_res` (alta resolución) de la librería `unstructured` para leer tablas, formatos y estructuras complejas dentro de los PDFs. Para que esto funcione correctamente en Windows, **es estrictamente obligatorio** instalar herramientas de procesamiento visual y OCR a nivel de sistema operativo.

### 1. Poppler (Para procesamiento de PDF)
1. Descarga los binarios compilados de Poppler para Windows (busca "Poppler for Windows" y descarga el archivo `.zip` más reciente).
2. Extrae el contenido del archivo `.zip`.
3. Mueve la carpeta extraída a la raíz de tu disco C:, de modo que te quede exactamente así: `C:\poppler`.
4. **Agregar al PATH:** 
   - Presiona la tecla Windows, escribe "Variables de entorno" y selecciona **Editar las variables de entorno del sistema**.
   - Haz clic en el botón **Variables de entorno...**.
   - En la sección "Variables del sistema", busca la variable llamada **Path** y haz doble clic sobre ella.
   - Haz clic en **Nuevo** y agrega la ruta exacta hacia la subcarpeta `bin` de poppler: `C:\poppler\bin`.
   - Haz clic en Aceptar en todas las ventanas.

### 2. Tesseract OCR (Para reconocimiento óptico de caracteres)
1. Descarga el instalador de Tesseract OCR para Windows (busca "Tesseract at UB Mannheim").
2. Ejecuta el instalador y deja la ruta de instalación por defecto: `C:\Program Files\Tesseract-OCR`.
3. **Agregar al PATH:**
   - Vuelve a abrir las **Variables de entorno** siguiendo los mismos pasos detallados arriba.
   - Edita la variable **Path**.
   - Haz clic en **Nuevo** y agrega la ruta exacta de instalación: `C:\Program Files\Tesseract-OCR`.
   - Haz clic en Aceptar para guardar todos los cambios.

> **⚠️ Advertencia:** Después de modificar el PATH, **es obligatorio cerrar y volver a abrir cualquier terminal o editor de código** (como VS Code) para que el sistema reconozca los nuevos comandos.

## Clonación y Entorno Virtual

Abre una nueva terminal (PowerShell o CMD) y ejecuta los siguientes comandos para preparar el proyecto:

```bash
# 1. Clonar el repositorio (ajusta la URL a tu repositorio real)
git clone https://github.com/BMACF12/tesis.git
cd tesis

# 2. Crear un entorno virtual aislado para no afectar tu sistema
python -m venv venv

# 3. Activar el entorno virtual (Comando para Windows)
.\venv\Scripts\activate
```

*(Nota: Si usas PowerShell y te da un error de ejecución de scripts, abre PowerShell como Administrador y corre `Set-ExecutionPolicy Unrestricted`, luego intenta activar el entorno de nuevo).*

## Instalación de Librerías

Con el entorno virtual activado (notarás que aparece un `(venv)` al inicio de la línea en tu consola), instálalo todo ejecutando:

```bash
cd backend
pip install -r requirements.txt
```

## Variables de Entorno

El motor RAG depende de APIs externas. En la raíz de tu carpeta `backend`, crea un archivo llamado `.env` y añade tus credenciales secretas siguiendo este formato exacto:

```env
GROQ_API_KEY=tu_api_key_de_groq_aqui
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
```

## Inicialización de la Base de Datos Vectorial

Antes de levantar el servidor por primera vez, necesitas crear la base de conocimiento que usará la IA (nuestra "Base de Oro"). Este paso descarga/activa los modelos de embeddings y le dice a ChromaDB que procese la normativa y la guarde en disco.

Asegúrate de estar en la carpeta `backend` (con el venv activado) y ejecuta:

```bash
python scripts/crear_base_oro.py
```
*(Si tu archivo está en la raíz del backend, ejecuta simplemente `python crear_base_oro.py`).*

Verás mensajes en consola confirmando que la base de datos se ha creado exitosamente en la carpeta `chroma_data`.

## Ejecución del Servidor

Una vez que todo está configurado y la base de datos existe, levanta el API de FastAPI:

```bash
# Estando dentro de la carpeta 'backend'
uvicorn main:app --reload
```

¡Felicidades! Tu servidor backend estará corriendo en `http://127.0.0.1:8000`. 
Puedes visitar **`http://127.0.0.1:8000/docs`** en tu navegador para ver la documentación interactiva Swagger y probar el endpoint `/evaluar_documento/`.
