# Auditor IA — Sistema de Evaluación de Evidencias CACES

Proyecto de tesis. Sistema automatizado que clasifica, evalúa y ordena evidencias
documentales de acreditación universitaria (sílabos, mallas, guías de laboratorio)
contra la normativa del **CACES (Ecuador) 2024**, usando RAG + LLM.

> **Idioma:** el proyecto, la tesis y el usuario trabajan en español. Responde en español.

## Arranque de sesión — lee esto primero

Antes de tocar código o dar recomendaciones, lee los archivos de `docs/` en este orden:

1. **`docs/CONTEXTO_TESIS.md`** — objetivos de la tesis y estado de cumplimiento por objetivo.
2. **`docs/ARQUITECTURA.md`** — cómo está construido el sistema y el flujo de datos real.
3. **`docs/INDICADORES.md`** — los indicadores CACES instrumentados y cómo se evalúan.
4. **`docs/DOCUMENTOS_PRUEBA.md`** — los documentos reales de prueba y sus trampas (los 3 originales, analizados a fondo; el corpus etiquetado ya es mayor, ver `PLAN_EVALUACION.md`).
5. **`docs/HALLAZGOS_Y_PENDIENTES.md`** — bugs conocidos y trabajo pendiente (empieza aquí si vas a programar).
6. **`docs/PLAN_EVALUACION.md`** — métricas para el Objetivo 3 (evaluación experimental).

## Agentes especializados — úsalos por defecto

Este proyecto tiene un roster de subagentes expertos en `.claude/agents/` (índice en
`.claude/agents/README.md`). **Cuando una tarea encaje en el dominio de un agente, delégala en
él con la herramienta Agent** en vez de trabajarla en solitario: cada agente ya conoce sus
archivos, sus invariantes y sus trampas. Direccionamiento:

| Si la tarea trata de… | Usa el agente |
|---|---|
| Extracción por coordenadas, malla, resolución de campos, plantilla, campos vacíos | `capa1-extraccion` |
| Enrutado al indicador, RAG (norma/maestro/reglas), prompt, base de oro, esquema del LLM | `capa2-rag-llm` |
| Veredicto/porcentaje, triage a carpetas, reportes PDF | `capa3-veredicto-triage` |
| FastAPI, Celery/Redis, chord, reintentos, config | `orquestacion-api-celery` |
| UI Next.js (drag&drop, cola, polling, tarjetas) | `frontend-next` |
| Indicador 3 (Malla) / 4 (Sílabo) / 6 (Guía) / 1-2 (semánticos) | `indicador-3-malla` · `indicador-4-silabo` · `indicador-6-guia` · `indicadores-1-2-semanticos` |
| Formatos oficiales por modelo CACES 2024 o por paper académico | `formatos-caces` |
| Objetivos de la tesis y su cumplimiento honesto | `objetivos-tesis` |
| Banco de pruebas, métricas, corpus, ground truth (OE3) | `evaluacion-pruebas` |

Para tareas que cruzan capas (p. ej. un cambio de campos que toca extracción + base de oro +
veredicto), coordina a los agentes relevantes y sintetiza tú el resultado. Su material de
referencia vive en `docs/conocimiento/<tema>/` (cada carpeta tiene un README de qué contener).

## Stack (resumen)

- **Backend API:** FastAPI (`backend/main.py`, `backend/api/rutas.py`)
- **Worker asíncrono:** Celery + Redis (`backend/services/tareas_ia.py`)
- **Orquestación física / triage:** `backend/services/orchestrator_service.py`
- **RAG:** ChromaDB (embeddings Google `gemini-embedding-001`) + LLM Groq `llama-3.3-70b-versatile`
- **Extracción PDF:** pdfminer.six por coordenadas (`backend/services/extraccion.py`). `unstructured` con `strategy="hi_res"` (Tesseract/Poppler) quedó **sólo como respaldo OCR** para escaneos sin capa de texto.
- **Frontend:** Next.js + TailwindCSS + framer-motion (`frontend/app/page.tsx`)
- **Base de conocimiento normativa:** `backend/data/caces_2024_oficial.txt` ("Base de Oro")

## Reglas de trabajo en este repo

- **No inventes rutas ni funciones.** Verifica en el código antes de recomendar. Este
  README de contexto puede quedar desactualizado; el código manda.
- **El frontend usa una versión de Next.js con breaking changes** (ver `frontend/AGENTS.md`):
  lee `node_modules/next/dist/docs/` antes de escribir código de Next.
- **No arranques servicios pesados sin pedirlo** (Redis en Docker, worker Celery, uvicorn, `npm run dev`).
- **El bug del filtro de Chroma (B1) ya está resuelto** (`_recuperar_norma`, `tareas_ia.py:212`):
  la norma se lee por metadato exacto y el respaldo por similitud filtra `tipo="norma"`. Ya se
  puede medir sobre el código actual (ver `docs/PLAN_EVALUACION.md` y los scripts de evaluación).
- Claves en `backend/.env` (`GROQ_API_KEY`, `GOOGLE_API_KEY`), fuera de git.
