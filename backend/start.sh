#!/bin/bash
set -e

echo "=== INICIANDO AUDITOR IA CACES ==="

# 1. Verificar si la base vectorial ChromaDB existe; si no, construirla
if [ ! -d "chroma_data" ] || [ -z "$(ls -A chroma_data 2>/dev/null)" ]; then
    echo "-> Base vectorial ChromaDB no encontrada. Inicializando Base de Oro..."
    python scripts/crear_base_oro.py
    python scripts/ingestar_maestro.py
    echo "-> Base de Oro inicializada con éxito."
else
    echo "-> Base vectorial ChromaDB detectada."
fi

# 2. Si no hay REDIS_URL externa y redis-server está instalado localmente, iniciarlo
if [ -z "$REDIS_URL" ] && command -v redis-server >/dev/null 2>&1; then
    echo "-> Iniciando Redis local en segundo plano..."
    redis-server --daemonize yes
    export REDIS_URL="redis://localhost:6379/0"
fi

# 3. Iniciar el Worker de Celery en segundo plano
echo "-> Iniciando Worker de Celery..."
celery -A services.tareas_ia worker --loglevel=info --pool=solo &
CELERY_PID=$!

# Función para apagar procesos en caso de terminación del contenedor
cleanup() {
    echo "-> Deteniendo servicios..."
    kill $CELERY_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# 4. Iniciar FastAPI / Uvicorn en primer plano
PORT="${PORT:-8000}"
echo "-> Iniciando API FastAPI en puerto $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
