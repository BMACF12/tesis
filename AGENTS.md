# Protocolo y Gobernanza de Agentes — Auditor IA CACES

Este documento establece las políticas de delegación, reglas de interacción y coordinación entre agentes especializados en el repositorio.

---

## 1. Principio Fundamental de Delegación

**Delegar en el subagente correspondiente es el comportamiento por defecto.** Cada subagente cuenta con instrucciones especializadas, archivos de dominio, invariantes inmutables y metodologías de prueba calibradas.

Un agente coordinador (o la sesión principal) sólo debe resolver directamente si:
1. Ningún subagente cubre el dominio específico de la consulta.
2. Es una consulta trivial o de lectura directa de 1-2 líneas.
3. Se está coordinando una respuesta que sintetiza la salida de múltiples agentes (e.g. revisión cruzada de tesis o cambio que impacta Capa 1 + Capa 2 + Capa 3).

---

## 2. Matriz de Direccionamiento de Agentes

| Área de Trabajo | Subagente Especializado | Archivos Principales de Dominio |
|---|---|---|
| **Extracción geométrica / Tablas / Malla / Campos vacíos** | `capa1-extraccion` | `backend/services/extraccion.py` |
| **RAG / Recuperación Chroma / Prompts / Salida estructurada LLM** | `capa2-rag-llm` | `backend/services/tareas_ia.py`, `backend/scripts/crear_base_oro.py`, `backend/data/caces_2024_oficial.txt` |
| **Veredictos / Cálculo % / Triage a carpetas / Reportes PDF** | `capa3-veredicto-triage` | `backend/services/orchestrator_service.py`, `backend/services/pdf_generator_ejecutivo.py` |
| **API FastAPI / Tareas Celery / Redis / Concurrencia** | `orquestacion-api-celery` | `backend/main.py`, `backend/api/rutas.py`, `backend/services/tareas_ia.py` |
| **Frontend Next.js / TailwindCSS / Framer Motion** | `frontend-next` | `frontend/app/page.tsx`, `frontend/app/components/` |
| **Indicador 3 (Malla Curricular)** | `indicador-3-malla` | `backend/services/extraccion.py`, `backend/data/asignaturas_malla.txt` |
| **Indicador 4 (Syllabus SGC.DI.321)** | `indicador-4-silabo` | `backend/services/extraccion.py`, `backend/data/asignaturas_malla.txt` |
| **Indicador 6 (Guías de Laboratorio)** | `indicador-6-guia` | `backend/services/extraccion.py`, `backend/data/caces_2024_oficial.txt` |
| **Indicadores 1 y 2 (Perfil y Proyecto Curricular)** | `indicadores-1-2-semanticos` | `backend/services/recorte_proyecto.py`, `backend/services/tareas_ia.py` |
| **Normativa CACES y Plantillas Oficiales** | `formatos-caces` | `backend/data/caces_2024_oficial.txt`, `docs/INDICADORES.md` |
| **Evaluación Experimental y Banco de Pruebas (OE3)** | `evaluacion-pruebas` | `backend/scripts/banco_pruebas.py`, `backend/scripts/evaluar_*.py` |
| **Metodología y Objetivos de la Tesis** | `objetivos-tesis` | `docs/CONTEXTO_TESIS.md`, `docs/PLAN_EVALUACION.md` |
| **Redacción del Manuscrito de Tesis y Citas IEEE** | `tesis-escritura` | `docs/`, `Documentos para la tesis/` |
| **Estilo, Prosa y Coherencia Argumental** | `redaccion-academica` | Manuscrito de tesis, capítulos redactados |
| **Formato Institucional ESPE y Entrega Biblioteca** | `formato-espe` | Guías de titulación ESPE, formato de página, tablas APA, refs IEEE |
| **Curaduría Bibliográfica y Calidad de Fuentes** | `curador-fuentes` | `Documentos para la tesis/` |

---

## 3. Invariantes del Repositorio para Todos los Agentes

1. **Separación Estricta de Hechos y Juicios:** Nunca traslades lógica determinista (detección de campos vacíos, concordancia de nombres de asignatura, pertenencia a la carrera) al LLM. Los hechos se resuelven en código; el LLM sólo califica el checklist contra la evidencia.
2. **Respaldo OCR como Último Recurso:** `pdfminer.six` es el extractor primario. `unstructured` + `tesseract` sólo se invoca si el documento tiene `< 200` caracteres de texto nativo.
3. **Persistencia Vectorial Inmutable en Tiempo de Ejecución:** `chroma_data/` es de solo lectura durante la ejecución del worker de Celery. Re-indexar requiere detener el worker.
4. **Búsquedas Aisladas:** No ejecutar búsquedas recursivas desde la raíz sin excluir `venv/`.
5. **Reportes PDF Limpios:** Cualquier carácter Unicode fuera de `latin-1` debe ser sanitizado antes de enviar a `fpdf2` para prevenir `FPDFUnicodeEncodingException`.
