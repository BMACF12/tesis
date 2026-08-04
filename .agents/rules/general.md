---
description: "Reglas generales del proyecto Auditor IA CACES y el entorno de tesis"
alwaysApply: true
---

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

Este proyecto tiene un roster de subagentes expertos en `.agents/agents/`. **Delegar es el comportamiento por defecto, no la excepción.** En cuanto una tarea encaje en el dominio de un agente de la tabla de abajo, **invócalo (o menciónalo/invoca subagente) en vez de resolverla tú directamente** —aunque parezca rápida—: cada agente ya conoce sus archivos, sus invariantes y sus trampas, y trabajar en solitario donde hay un experto es justamente lo que este README busca evitar. Trabaja tú sin delegar sólo cuando: (a) ninguna fila encaja, (b) es una pregunta trivial de una línea, o (c) estás **coordinando** a varios agentes y sintetizando su salida. Si dudas, delega. Direccionamiento:

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
| Redactar/revisar capítulos, citas IEEE, bibliografía, papers de `Documentos para la tesis/` | `tesis-escritura` |
| Estilo y prosa (persona, gerundios, tiempos, sobreventa) y coherencia argumental de un texto | `redaccion-academica` |
| Formato oficial ESPE (márgenes, fuente, títulos, tablas/figuras APA, IEEE en refs) y entrega en biblioteca | `formato-espe` |
| Validar una fuente nueva: ¿es buena, sirve, está repetida?, ¿qué número le toca? | `curador-fuentes` |

**Trabajo sobre el manuscrito escrito → empieza siempre por el trío de la tesis:**
`tesis-escritura` (contenido, estructura, citas IEEE y corpus), `redaccion-academica` (estilo, prosa y líneas argumentales) y `formato-espe` (formato oficial ESPE y entrega en biblioteca). Se reparten el trabajo y se cruzan; para una revisión completa de un capítulo, invócalos y sintetiza tú el resultado.

Para tareas que cruzan capas (p. ej. un cambio de campos que toca extracción + base de oro + veredicto), coordina a los agentes relevantes y sintetiza tú el resultado. Su material de referencia vive en `docs/conocimiento/<tema>/` (cada carpeta tiene un README de qué contener).

## Stack (resumen)

- **Backend API:** FastAPI (`backend/main.py`, `backend/api/rutas.py`)
- **Worker asíncrono:** Celery + Redis (`backend/services/tareas_ia.py`)
- **Orquestación física / triage:** `backend/services/orchestrator_service.py`
- **RAG:** ChromaDB (embeddings Google `gemini-embedding-001`) + LLM Groq `llama-3.3-70b-versatile`
- **Extracción PDF:** pdfminer.six por coordenadas (`backend/services/extraccion.py`). `unstructured` con `strategy="hi_res"` (Tesseract/Poppler) quedó **sólo como respaldo OCR** para escaneos sin capa de texto.
- **Frontend:** Next.js + TailwindCSS + framer-motion (`frontend/app/page.tsx`)
- **Base de conocimiento normativa:** `backend/data/caces_2024_oficial.txt` ("Base de Oro")

## Reglas de trabajo en este repo

- **No inventes rutas ni funciones.** Verifica en el código antes de recomendar. Este README de contexto puede quedar desactualizado; el código manda.
- **El frontend usa una versión de Next.js con breaking changes** (ver `frontend/AGENTS.md`): lee `node_modules/next/dist/docs/` antes de escribir código de Next.
- **No arranques servicios pesados sin pedirlo** (Redis en Docker, worker Celery, uvicorn, `npm run dev`).
- **Búsquedas y el venv (25 974 `.py` en `venv/` de la raíz, el 99,9 % del repo):** *Grep* está limpio — ripgrep respeta `.gitignore` (que excluye `venv/`), así que las búsquedas de contenido nunca lo tocan. *Glob*, en cambio, **NO respeta `.gitignore`**: un `**/*.py` desde la raíz devuelve ~26 000 archivos del venv y entierra los ~33 reales del proyecto. **Regla: en Glob acota siempre a la subcarpeta** (`backend/**/*.py`, `scripts/*.py`, `frontend/**/*.tsx`) y **nunca uses `**` desde la raíz**. Lo mismo con `find` en Bash: añade `-not -path "./venv/*"`.
- **El bug del filtro de Chroma (B1) ya está resuelto** (`_recuperar_norma`, `tareas_ia.py:212`): la norma se lee por metadato exacto y el respaldo por similitud filtra `tipo="norma"`. Ya se puede medir sobre el código actual (ver `docs/PLAN_EVALUACION.md` y los scripts de evaluación).
- Claves en `backend/.env` (`GROQ_API_KEY`, `GOOGLE_API_KEY`), fuera de git.
