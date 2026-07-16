# Roster de agentes especializados — Auditor IA CACES

Agentes de proyecto (Claude Code los descubre automáticamente). Cada uno es experto en una
parte del sistema y sabe qué archivos leer y qué invariantes respetar.

## Por capa del proyecto
| Agente | Dominio |
|---|---|
| `capa1-extraccion` | Hechos deterministas: extracción por coordenadas, malla, plantilla, pertinencia, campos vacíos (`extraccion.py`) |
| `capa2-rag-llm` | Juicio del LLM y RAG: enrutado, recuperación, prompt, base de oro (`tareas_ia.py`, `crear_base_oro.py`) |
| `capa3-veredicto-triage` | Veredicto determinista y triage físico + reportes (`_calcular_veredicto`, `orchestrator_service.py`) |
| `orquestacion-api-celery` | FastAPI + Celery + Redis + config (`main.py`, `rutas.py`, `config.py`) |
| `frontend-next` | UI Next.js: drag&drop, cola, polling, tarjetas (`frontend/app/page.tsx`) |

## Por indicador
| Agente | Indicador |
|---|---|
| `indicador-3-malla` | 3 — Malla curricular (INSTRUMENTADO) |
| `indicador-4-silabo` | 4 — Syllabus SGC.DI.321 (INSTRUMENTADO) |
| `indicador-6-guia` | 6 — Guía de uso de laboratorio (INSTRUMENTADO) |
| `indicadores-1-2-semanticos` | 1 Perfil de egreso y 2 Proyecto curricular (SEMANTICO, no probados) |

## Expertos transversales
| Agente | Dominio |
|---|---|
| `formatos-caces` | Formatos oficiales por modelo CACES 2024 **y** por paper académico |
| `objetivos-tesis` | Objetivos General/OE1/OE2/OE3 y su cumplimiento honesto; plan de evaluación |
| `evaluacion-pruebas` | Banco de pruebas y evaluación experimental (OE3): scripts, corpus, métricas |

## Carpetas de conocimiento
Los agentes que necesitan material externo apuntan a `docs/conocimiento/<tema>/`. Cada carpeta
tiene un `README.md` que describe qué documentos colocar allí. Ver `docs/conocimiento/README.md`.
