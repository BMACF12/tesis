# Arquitectura del sistema

Arquitectura de **3 capas** (hechos deterministas → juicio del LLM → veredicto determinista)
sobre un procesamiento asíncrono por lotes. La idea central: el LLM sólo emite **juicios**
(el checklist y un diagnóstico); todo hecho verificable se extrae del PDF por coordenadas y
se decide en código. Si un documento no supera las compuertas deterministas, **el LLM ni se
llama**.

```
Frontend ──POST /evaluar_documento/──► FastAPI (api/rutas.py) ──chord──► Redis (broker+backend)
   ▲                                                                        │
   │  GET /status/{task_id} (polling)                                       │
   └────────────────────────────────────────────────┐                      ▼
                                                      │   Worker Celery: auditar_documento_pesado
                                                      │            (tareas_ia.py:379)
   CAPA 1 — HECHOS (determinista, sin LLM)            │
     Extracción por coordenadas (extraccion.py) · malla reconstruida ·
     plantilla · pertinencia · campos vacíos
        │  ¿rechazo léxico? ¿plantilla inválida? ¿ajeno? ¿plantilla vacía? → corta aquí, sin LLM
        ▼
   CAPA 2 — JUICIO (LLM Groq llama-3.3-70b)  →  DictamenAuditoria { checklist, analisis_libre }
        ▼
   CAPA 3 — VEREDICTO (determinista, _calcular_veredicto)  →  triage físico (orchestrator_service.py)
        │
        └── chord callback ─► generar_reporte_ejecutivo → PDF resumen global
```

## Flujo detallado (una tarea `auditar_documento_pesado`)

Ubicación: `backend/services/tareas_ia.py:379`.

### Capa 1 — Hechos (determinista, sin LLM)

1. **Extracción por coordenadas** (`extraer_documento`, `extraccion.py:479`). Usa pdfminer.six
   y conserva las coordenadas x/y que `unstructured` descartaba. Devuelve
   `{texto, cajas, ocr, es_malla}` con un solo parseo.
   - Si el PDF no tiene capa de texto (`< UMBRAL_CAPA_TEXTO = 200` chars) → respaldo **OCR**
     `hi_res` (`extraccion.py:462`). Es la única ruta que usa Tesseract, y sólo para escaneos.
   - Si es la **malla**, se **reconstruye celda por celda** por geometría (`filas_de_malla`,
     `extraccion.py:367`), deduciendo la escala del diagrama a partir de la rejilla `HPAO`.
     Antes el texto salía desordenado y los prerrequisitos se desligaban de su asignatura;
     hoy se reasocian por coordenadas.
2. **Rechazo léxico** (`tareas_ia.py:406`): si el documento contiene menos de 2 palabras del
   vocabulario académico (`PALABRAS_ACADEMICAS`) → `PLANTILLA NO RECONOCIDA` **sin llamar al LLM**.
3. **Enrutado al indicador** (`_recuperar_norma`, `:212`):
   - Primero, enrutador por palabras clave sobre `texto[:1500].upper()` (`_detectar_indicador`,
     `:84`, con `MAPEO_INDICADORES`, `:66`). Si acierta → se lee la norma **por metadato exacto**
     `vector_db.get(where={"indicador": N})`: no gasta una llamada de embeddings.
   - Respaldo por similitud: `similarity_search(texto[:1000], k=1, filter={"tipo": "norma"})`.
     El filtro `tipo="norma"` impide devolver el documento maestro, que comparte colección.
4. **Verificación de plantilla** (`_plantilla_valida`, `:161`): busca los MARCADORES del
   indicador (de los metadatos) sobre la forma canónica del texto. Si faltan → `PLANTILLA NO
   RECONOCIDA` **sin LLM** (`:421`).
5. **Pertinencia** (`_pertinencia`, `:133`): determina si el documento es de Ingeniería de
   Software leyendo el campo `CARRERA`/`ASIGNATURA` por coordenadas y contrastando la
   asignatura contra `asignaturas_malla.txt`. Si `pertenece is False` → `NO CUMPLE` **sin LLM**
   (`:432`).
6. **Campos sin llenar** (`_campos_sin_llenar`, `:188`): localiza cada campo obligatorio
   (metadatos `campos`) y reporta cuáles están vacíos. Si la plantilla oficial está
   **mayoritariamente en blanco** (`_plantilla_vacia`, `:180`) → `NO CUMPLE` **sin LLM** (`:443`).

### Capa 2 — Juicio (LLM)

7. Se arma el prompt `PLANTILLA_AUDITOR` (`:255`) con: reglas generales (`_recuperar_reglas`,
   `:234`), la norma del indicador, el contexto de la carrera (`_recuperar_maestro`, `:239` —
   recorta la lista de asignaturas), una **hoja de hechos ya verificados** (`_hoja_de_hechos`,
   `:274`) y el documento. Se invoca
   `ChatGroq("llama-3.3-70b-versatile", temperature=0).with_structured_output(DictamenAuditoria)`
   (`:466`). El LLM devuelve **sólo** `checklist` + `analisis_libre`.

### Capa 3 — Veredicto (determinista)

8. `_calcular_veredicto` (`:303`) decide sin intervención del LLM:
   - `plantilla_valida == False` → `PLANTILLA NO RECONOCIDA` (0%).
   - `pertenece_software == False` → `NO CUMPLE` (0%).
   - checklist vacío → `ERROR_SIN_CHECKLIST`.
   - plantilla mayoritariamente vacía → `NO CUMPLE`.
   - `porcentaje = round(cumplidos/total*100)`; `≤50` → `NO CUMPLE`; `≥70` **y sin campos
     vacíos** → `CUMPLE`; en otro caso → `CUMPLE PARCIALMENTE`.
9. **Triage físico** (`enrutar_documento`, `orchestrator_service.py:186`): copia el PDF a la
   carpeta destino y genera el reporte PDF individual.
10. Limpieza del temporal (`cerrar`, `:383`).

Al terminar todo el lote, el **chord** dispara `generar_reporte_ejecutivo` (`:519`) → PDF
resumen global. Las tareas fallidas **devuelven un dict** con veredicto `ERROR_*` en vez de
re-lanzar, para que el chord no aborte el reporte del lote (`:508`).

## Esquema de salida

Hay dos estructuras distintas — no confundirlas:

**`DictamenAuditoria`** (`tareas_ia.py:50`) — lo único que emite el LLM:
- `checklist: List[ElementoChecklist]` — `{numero_elemento:int, descripcion:str, cumple:bool, justificacion:str}` (`:41`)
- `analisis_libre: str` — diagnóstico del documento en 3-5 frases.

**Dict `resultado`** (`_resultado`, `tareas_ia.py:334`) — lo que circula por Celery y alimenta
el triage y los reportes. Contiene los **hechos deterministas** más el juicio del LLM:
`nombre_original`, `indicador_evaluado`, `indicador_numero`, `enrutado_por`, `plantilla_valida`,
`pertenece_software`, `justificacion_software`, `campos_vacios`, `campos_localizados`,
`checklist`, `veredicto`, `porcentaje_estimado`, `justificacion`, `analisis_libre`.

## Triage de carpetas (orchestrator_service.py)

`enrutar_documento` (`:186`) enruta por veredicto, en este orden:

| Condición | Carpeta | ¿Reporte? |
|---|---|---|
| `ERROR_CUOTA*` | `98_Pendientes_Por_Cuota` | no |
| otro `ERROR*` | `99_Descarte_Errores` | no |
| `PLANTILLA NO RECONOCIDA` | `12_Plantilla_No_Reconocida` | sí |
| no pertenece **o** `NO CUMPLE` | `11_Documentos_Rechazados` | sí |
| `CUMPLE` / `CUMPLE PARCIALMENTE` | carpeta del indicador (`obtener_carpeta_indicador`) | sí |

⚠️ Los documentos ajenos a la carrera y los `NO CUMPLE` propios comparten `11_Documentos_Rechazados`
(ver HALLAZGOS). `obtener_carpeta_indicador` (`:168`) mapea a propósito **sólo** los 5 indicadores
de la base de oro (1 perfil, 2 proyecto curricular, 3 malla, 4 syllabus, 6 escenarios de
prácticas); enruta por `indicador_numero` fiable y sólo cae al `sanitizar_nombre()` genérico si
llega un nombre no mapeado.

## Cómo se levanta (referencia — no ejecutar sin pedirlo)

1. `docker run -d -p 6379:6379 --name redis-caces redis`
2. `cd backend && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt`
3. `.env` con `GROQ_API_KEY` y `GOOGLE_API_KEY`
4. `python scripts/crear_base_oro.py` (borra y recrea `chroma_data` con la normativa)
5. `python scripts/extraer_asignaturas.py` (genera `data/asignaturas_malla.txt` desde la malla oficial)
6. `python scripts/ingestar_maestro.py` (inserta el documento maestro; requiere el paso 5)
7. `uvicorn main:app --reload`  (API en `http://127.0.0.1:8000`)
8. `celery -A services.tareas_ia worker --loglevel=info --pool=solo`
9. `cd frontend && npm install && npm run dev`  (UI en `http://localhost:3000`)

## Archivos clave

| Archivo | Rol |
|---|---|
| `backend/main.py` | App FastAPI + CORS |
| `backend/api/rutas.py` | Endpoints `/evaluar_documento/` (chord) y `/status/{task_id}` |
| `backend/services/extraccion.py` | **Capa 1**: extracción por coordenadas, reconstrucción de la malla, resolución de campos etiqueta→valor, respaldo OCR |
| `backend/services/tareas_ia.py` | Worker Celery: orquesta las 3 capas (hechos, RAG, juicio LLM, veredicto) y el reporte ejecutivo |
| `backend/services/orchestrator_service.py` | Triage físico + generación de reportes PDF |
| `backend/scripts/crear_base_oro.py` | Ingesta de la normativa a ChromaDB (un `Document` por indicador, con metadatos; sin troceo) |
| `backend/scripts/extraer_asignaturas.py` | Genera `data/asignaturas_malla.txt` desde la malla oficial |
| `backend/scripts/ingestar_maestro.py` | Ingesta idempotente del documento maestro de Software |
| `backend/core/config.py` | Settings (rutas, CORS) |
| `backend/data/caces_2024_oficial.txt` | Base de Oro (normativa por indicador; MARCADORES y CAMPOS en cabecera de máquina) |
| `backend/data/maestro_software.txt` | Perfil + lista de asignaturas de Software (para pertinencia) |
| `backend/data/asignaturas_malla.txt` | Lista de asignaturas generada desde la malla (usada en la pertinencia) |
| `frontend/app/page.tsx` | UI: drag&drop, cola, polling, tarjetas de resultado |
