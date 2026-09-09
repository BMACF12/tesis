---
name: caces-audit-pipeline
description: >-
  Runbook integral para arrancar, operar, depurar y probar el pipeline distribuido de auditoría de evidencias CACES
  (FastAPI + Celery + Redis + ChromaDB + Groq LLM + Triage físico y Reportes PDF).
---

# Runbook: Pipeline de Auditoría CACES

Este skill describe el procedimiento estándar para operar, levantar y verificar el ciclo completo de auditoría distribuida de documentos de acreditación.

---

## 1. Arquitectura del Flujo de Datos

```
[Usuario / Drag & Drop]
        │
        ▼ (POST /evaluar_documento/ multipart)
  [FastAPI Gateway]
        │
        ├─► Guarda temporal en backend/temp/
        ├─► Genera ID de lote (LOTE_XXXXXXXX)
        └─► Encola en Celery usando Chord:
                 chord(group(auditar_documento_pesado.s(doc_i)))(generar_reporte_ejecutivo.s(id_lote))
                        │
                        ▼ (Procesamiento distribuido en paralelo)
            [Worker Celery (tareas_ia.py)]
                 ├─► Capa 1: pdfminer.six (coordenadas, plantilla, pertenencia, vacíos)
                 ├─► Compuertas de corte (Léxico, Plantilla, Carrera, Vacíos)
                 ├─► Capa 2: RAG ChromaDB + LLM Groq (llama-3.3-70b) -> Checklist
                 ├─► Capa 3: Veredicto algorítmico y Reporte PDF individual
                 └─► Triage físico: Copia a Auditoria_CACES/<Carpeta_Indicador>/
                        │
                        ▼ (Callback al terminar todo el grupo)
            [generar_reporte_ejecutivo]
                 └─► Genera PDF consolidado en Auditoria_CACES/Reportes_Ejecutivos/
```

---

## 2. Secuencia de Arranque de Servicios

Sigue este orden estricto para iniciar el entorno de desarrollo:

### Paso 1: Levantar Redis (Broker y Backend de Resultados)
```bash
docker run -d -p 6379:6379 --name redis-caces redis
```
*Si ya está creado:*
```bash
docker start redis-caces
```

### Paso 2: Iniciar la API Gateway (FastAPI)
Desde la raíz del repositorio con el entorno virtual activado:
```bash
.\venv\Scripts\activate
cd backend
uvicorn main:app --reload --port 8000
```
*Verificación:* Acceder a `http://localhost:8000/docs` (Swagger UI).

### Paso 3: Iniciar el Worker de Celery
En una terminal separada (con venv activado):
```bash
.\venv\Scripts\activate
cd backend
celery -A services.tareas_ia worker --loglevel=info --pool=solo
```
> [!IMPORTANT]
> Celery **no recarga automáticamente** al editar archivos en `services/`. Ante cualquier cambio en código Python del worker, reinicia el proceso con `Ctrl+C` y relánzalo.

### Paso 4: Iniciar el Frontend (Next.js)
En una terminal separada:
```bash
cd frontend
npm run dev
```
*Verificación:* Abrir `http://localhost:3000`.

---

## 3. Comandos de Operación y Diagnóstico

### Limpiar colas de Celery y resultados residuales en Redis
```bash
# Limpiar tareas pendientes en la cola Celery
celery -A services.tareas_ia purge -f

# Limpiar toda la memoria de Redis (cola + resultados cacheados)
docker exec -it redis-caces redis-cli FLUSHALL
```

### Probar un análisis puntual mediante HTTP (cURL)
```bash
curl -X POST "http://localhost:8000/evaluar_documento/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@\"C:/ruta/a/tu/silabo_prueba.pdf\""
```

### Consultar estado de una tarea
```bash
curl -X GET "http://localhost:8000/status/<TASK_ID>"
```

---

## 4. Matriz de Triage y Salida Física de Documentos

Los documentos procesados se clasifican y archivan automáticamente en `backend/Auditoria_CACES/`:

| Veredicto / Condición | Carpeta de Destino | Reporte Generado |
|---|---|---|
| `CUMPLE` o `CUMPLE PARCIALMENTE` (Ind. 1) | `Indicador_1_Perfil_de_egreso/` | Sí (Individual) |
| `CUMPLE` o `CUMPLE PARCIALMENTE` (Ind. 2) | `Indicador_2_Proyecto_curricular/` | Sí (Individual) |
| `CUMPLE` o `CUMPLE PARCIALMENTE` (Ind. 3) | `Indicador_3_Malla_curricular/` | Sí (Individual) |
| `CUMPLE` o `CUMPLE PARCIALMENTE` (Ind. 4) | `Indicador_4_Syllabus/` | Sí (Individual + Renombrado a `Silabo_NRC-XXXX_...`) |
| `CUMPLE` o `CUMPLE PARCIALMENTE` (Ind. 6) | `Indicador_6_Escenarios_de_practicas_formativas/` | Sí (Individual) |
| `NO CUMPLE` / Otra carrera / Plantilla vacía | `11_Documentos_Rechazados/` | Sí (Individual) |
| `PLANTILLA NO RECONOCIDA` / No académico | `12_Plantilla_No_Reconocida/` | Sí (Individual) |
| `ERROR_CUOTA_API` (Límite diario de Groq) | `98_Pendientes_Por_Cuota/` | No (Se preserva para reintento) |
| `ERROR_LECTURA` / Archivo corrupto | `99_Descarte_Errores/` | No |
| Finalización de Lote | `Reportes_Ejecutivos/` | Sí (Reporte global consolidado) |

---

## 5. Manejo de Incidencias Comunes

1. **Error `429 rate_limit_exceeded` en Groq:**
   - Si el mensaje incluye `try again in Xs`, Celery calculará el tiempo de espera y reintentará automáticamente.
   - Si es límite de tokens diarios (TPD, límite de 100,000 tokens en tier gratuito), el archivo irá a `98_Pendientes_Por_Cuota`. No reintentar hasta que expire la ventana diaria.
2. **El Frontend queda en estado `EN COLA` permanente:**
   - Verifica si el worker de Celery está corriendo y sin excepciones bloqueantes.
   - Los resultados en Redis expiran tras 24 horas.
3. **`ModuleNotFoundError` al arrancar el worker:**
   - Asegúrate de activar el entorno virtual desde la raíz (`tesis/venv/Scripts/activate`) y no uno secundario dentro de `backend/`.
