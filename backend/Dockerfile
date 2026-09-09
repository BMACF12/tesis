FROM python:3.11-slim

# Evitar prompts interactivos y buffers de Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema operativo (Redis local opcional, Poppler y Tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    redis-server \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del backend
COPY . .

# Dar permisos de ejecución al script de arranque
RUN chmod +x start.sh

# Exponer el puerto por defecto
EXPOSE 8000

# Arrancar los servicios
CMD ["./start.sh"]
