# Auditor IA — Evaluación Automatizada de Evidencias CACES (ESPE)

Guía de referencia y directrices operativas para **Google Antigravity / Gemini** en el proyecto de tesis: **"Sistema de Auditoría y Clasificación Automatizada de Evidencias de Acreditación Universitaria bajo el Modelo CACES 2024 mediante RAG y Modelos de Lenguaje"**.

> **Idioma:** El proyecto, la tesis, el código, los comentarios y los reportes se gestionan en **español**. Responde siempre en español.

---

## 1. Visión General del Proyecto

El sistema automatiza la clasificación, auditoría de cumplimiento normativo y ordenamiento físico de evidencias documentales universitarias (perfiles de egreso, proyectos curriculares, mallas curriculares, sílabos y guías de prácticas de laboratorio) contra los estándares oficiales del **CACES (Consejo de Aseguramiento de la Calidad de la Educación Superior - Ecuador, 2024)** para la carrera de **Ingeniería de Software** de la **Universidad de las Fuerzas Armadas ESPE**.

Por cada documento PDF subido:
1. Extrae su contenido preservando la geometría visual (coordenadas).
2. Verifica la validez de la plantilla oficial y la pertinencia a la carrera.
3. Evalúa el cumplimiento normativo mediante RAG contra la Base de Oro oficial.
4. Genera un dictamen estructurado y un reporte formal en PDF.
5. Clasifica y mueve físicamente el archivo a la carpeta de su indicador o rechazo.
6. Al completar un lote, genera un reporte ejecutivo global consolidado.

---

## 2. Stack Tecnológico

| Capa / Componente | Tecnología | Rol y Descripción |
|---|---|---|
| **API Gateway** | **FastAPI** (`backend/main.py`, `backend/api/rutas.py`) | Recepción de lotes multipart, validación de PDFs, encolado asíncrono y endpoint de polling de estado. |
| **Worker Asíncrono** | **Celery 5.x** + **Redis** (`backend/services/tareas_ia.py`) | Ejecución distribuida de tareas pesadas, reintentos exponenciales y orquestación con `chord` y `group`. |
| **Broker y Backend de Resultados** | **Redis** (Docker / Local) | Cola de mensajes para Celery y almacenamiento temporal de resultados de auditoría (TTL 24h). |
| **Extracción Geométrica** | **pdfminer.six** (`backend/services/extraccion.py`) | Parseo determinista por coordenadas espaciales `(x0, y0, x1, y1)`, reconstrucción de tablas y mallas sin OCR. |
| **Respaldo OCR** | **unstructured[pdf]** + **Tesseract** + **Poppler** | Mecanismo de contingencia (*fallback*) activado exclusivamente si el PDF carece de capa de texto nativa (< 200 caracteres). |
| **Base Vectorial (RAG)** | **ChromaDB** (`backend/chroma_data/`) | Almacenamiento persistente de la normativa CACES 2024 (Base de Oro) y documento maestro institucional. |
| **Modelo de Embeddings** | **Google Gemini** (`models/gemini-embedding-001`) | Generación de representaciones vectoriales densas para recuperación semántica en ChromaDB. |
| **LLM de Juicio Normativo** | **Groq** (`llama-3.3-70b-versatile`, `temp=0`) | Inferencia de alta velocidad para emitir el checklist de elementos fundamentales y análisis libre con *structured output*. |
| **Framework LLM / RAG** | **LangChain** (`langchain-core`, `langchain-chroma`, `langchain-groq`, `langchain-google-genai`) | Orquestación de cadenas de prompts, esquemas Pydantic y conectores de recuperación. |
| **Validación de Datos** | **Pydantic v2** | Definición de contratos estrictos (`DictamenAuditoria`, `ElementoChecklist`) y validación post-inferencia. |
| **Generación de Reportes** | **fpdf2** (`backend/services/pdf_generator.py`, `orchestrator_service.py`) | Renderizado de dictámenes individuales oficiales y reportes ejecutivos de lote en formato PDF. |
| **Frontend UI** | **Next.js 16** (App Router, React 19, TypeScript) | Interfaz web interactiva: carga drag & drop de lotes, animación de estados con **framer-motion** y diseño con **TailwindCSS 4**. |

---

## 3. Patrones de Diseño y Arquitectura

El sistema aplica rigurosamente principios de ingeniería de software para maximizar la confiabilidad y eliminar alucinaciones de IA:

### 3.1. Arquitectura de Decisión en Tres Capas (Separación Hechos / Juicios / Veredicto)
*   **Capa 1 — Hechos (Determinista, sin LLM):** Extrae texto y cajas por coordenadas con `pdfminer.six`, detecta marcadores de plantilla oficial, valida la pertinencia a la carrera (malla de asignaturas) y localiza campos obligatorios vacíos.
*   **Capa 2 — Juicio (LLM acotado):** Recibe la norma de ChromaDB, el contexto de la carrera, el documento y la *Hoja de Hechos Verificados*. Su única tarea es calificar los elementos fundamentales del checklist (`cumple`, `tipo_fallo`, `justificacion` con cita textual literal).
*   **Capa 3 — Veredicto (Determinista):** El veredicto final (`CUMPLE`, `CUMPLE PARCIALMENTE`, `NO CUMPLE`, `PLANTILLA NO RECONOCIDA`) y el porcentaje se calculan algorítmicamente combinando los hechos de la Capa 1 y el checklist de la Capa 2.

### 3.2. Compuertas de Cortocircuito (*Short-Circuiting / Token Guarding*)
Si un documento no es académico (< 2 palabras del léxico), no usa la plantilla oficial, pertenece a otra carrera, o tiene la plantilla vacía (> 50% de campos en blanco), **se emite el veredicto inmediatamente sin invocar al LLM**, ahorrando tokens y costo de API.

### 3.3. RAG Híbrido Determinista-Semántico
La recuperación de la norma no depende exclusivamente de embeddings. Primero analiza el titular (`VENTANA_TITULAR = 1500 ch`) mediante reglas de palabras clave de alta precisión; si acierta, recupera la norma por metadato exacto `get(where={"indicador": N})` a costo cero de embeddings. Si no, busca en el cuerpo y sólo como última instancia recurre a búsqueda por similitud vectorial con filtro `tipo="norma"`.

### 3.4. Orquestación Distribuida con Celery Chord
La carga de un lote de PDFs se orquesta con `chord(group(auditar_documento_pesado.s(...)))(generar_reporte_ejecutivo.s(...))`. Cada documento se audita en paralelo en workers independientes; al finalizar todos, se invoca automáticamente la generación del reporte ejecutivo global.

### 3.5. Resiliencia Diferenciada ante Rate Limits (TPM vs TPD)
El worker intercepta errores `429`:
*   Si es límite por minuto (TPM), calcula el tiempo de espera retornado por Groq y reintenta con `self.retry(countdown=...)`.
*   Si es límite diario de cuota (TPD, e.g. 100k tokens), no desperdicia reintentos y enruta el PDF a `98_Pendientes_Por_Cuota` para reanálisis posterior sin considerarlo defectuoso.

---

## 4. Estructura del Repositorio

```
tesis/
├── GEMINI.md                     # Guía maestra para Google Antigravity (este archivo)
├── AGENTS.md                     # Directrices de gobernanza de agentes
├── README.md                     # Documentación general y puesta en marcha
├── CLAUDE.md                     # Directrices de sesión previas
├── backend/
│   ├── main.py                   # Inicialización de FastAPI y middlewares
│   ├── api/                      # Endpoints HTTP (rutas.py)
│   ├── core/                     # Configuración central (config.py)
│   ├── services/
│   │   ├── extraccion.py         # Capa 1: Extracción por coordenadas y geometría de mallas
│   │   ├── tareas_ia.py          # Capas 1, 2 y 3: Tareas Celery y pipeline de auditoría
│   │   ├── orchestrator_service.py # Triage físico, carpetas y generador de PDF individual
│   │   ├── pdf_generator_ejecutivo.py # Generador del reporte de lote consolidado
│   │   └── recorte_proyecto.py   # Reducción inteligente de tokens para Proyectos Curriculares
│   ├── data/
│   │   ├── caces_2024_oficial.txt # Base de Oro: normativa oficial CACES
│   │   └── asignaturas_malla.txt # 44 asignaturas oficiales de la carrera
│   ├── scripts/                  # Scripts de inicialización, pruebas y evaluación
│   └── chroma_data/              # Directorio persistente de la base vectorial
├── frontend/
│   ├── app/                      # Next.js App Router (page.tsx, layout.tsx, etc.)
│   └── package.json
├── docs/                         # Documentación técnica y académica de la tesis
│   ├── ARQUITECTURA.md           # Flujo de datos y arquitectura detallada
│   ├── INDICADORES.md            # Fichas técnicas de los indicadores CACES
│   ├── CONTEXTO_TESIS.md         # Objetivos y alineación de la tesis
│   ├── DOCUMENTOS_PRUEBA.md      # Catálogo de documentos de prueba y trampas
│   ├── PLAN_EVALUACION.md        # Protocolo experimental y métricas (OE3)
│   └── HALLAZGOS_Y_PENDIENTES.md # Lista de tareas, mejoras e incidencias
├── .agents/
│   ├── agents/                   # Roster de 16 agentes especializados
│   ├── rules/                    # Reglas generales del workspace
│   └── skills/                   # Skills ejecutables (runbooks y procedimientos)
└── Documentos para la tesis/     # Corpus bibliográfico e investigación en PDF
```

---

## 5. Reglas Críticas de Trabajo en este Repositorio

1. **Atención con Glob y el Entorno Virtual (`venv/`):**
   * El entorno virtual vive en la raíz (`tesis/venv/`) y contiene ~26,000 archivos `.py`.
   * `ripgrep` (grep) respeta `.gitignore`, pero las búsquedas por patrón Glob **no siempre ignoran `venv`**.
   * **Regla:** En búsquedas con Glob o `find_by_name`, acota siempre la ruta a subcarpetas (`backend/**/*.py`, `scripts/*.py`, `frontend/**/*.tsx`) y **nunca uses patrones globales `**/*.py` desde la raíz**.
2. **El código manda sobre la documentación:**
   * No inventes firmas de funciones, endpoints ni rutas de archivos. Inspecciona siempre el código real antes de proponer cambios.
3. **Reinicio del Worker de Celery tras cambios:**
   * A diferencia de `uvicorn --reload`, el worker de Celery **no recarga el código automáticamente**. Cualquier modificación en `services/*.py` requiere reiniciar el worker con `Ctrl+C` y relanzarlo.
4. **Bloqueo de ChromaDB:**
   * El proceso de Celery mantiene bloqueado el directorio `chroma_data/`. Si ejecutas `scripts/crear_base_oro.py` o `scripts/ingestar_maestro.py`, debes detener Celery previamente.
5. **No ejecutar comandos o servicios pesados sin solicitud explícita:**
   * No levantes Docker, Redis, Uvicorn o Celery en segundo plano a menos que el usuario lo solicite.

---

## 6. Roster de Subagentes Especializados

Cuando abordes tareas específicas, apóyate en los subagentes especializados definidos en `.agents/agents/`:

| Subagente | Dominio y Responsabilidad |
|---|---|
| **`capa1-extraccion`** | Extracción por coordenadas, tablas, geometría de mallas, validación de plantillas y campos vacíos. |
| **`capa2-rag-llm`** | Enrutado de indicador, recuperación en ChromaDB, construcción del prompt y esquema Pydantic del LLM. |
| **`capa3-veredicto-triage`** | Cálculo de porcentajes y veredictos, enrutamiento a carpetas físicas y generación de reportes PDF. |
| **`orquestacion-api-celery`** | FastAPI, Celery, Redis, orquestación con chord/group, manejo de concurrencia y reintentos. |
| **`frontend-next`** | Interfaz Next.js, componentes TailwindCSS, animaciones framer-motion y polling de tareas. |
| **`indicador-3-malla`** | Reconstrucción celda por celda de mallas curriculares, invariantes de 8 PAO y prerrequisitos. |
| **`indicador-4-silabo`** | Plantilla SGC.DI.321, datos generales, secciones 1-10 y trampas de llenado. |
| **`indicador-6-guia`** | Guía de uso de laboratorio / prácticas formativas, secciones A/B/C y recursos. |
| **`indicadores-1-2-semanticos`** | Indicadores 1 (Perfil de egreso) y 2 (Proyecto curricular) con evaluación semántica. |
| **`formatos-caces`** | Normativa oficial CACES 2024 y literatura de acreditación universitaria. |
| **`evaluacion-pruebas`** | Banco de pruebas determinista, cálculo de métricas (F1, Jaccard, Kappa) y evaluación OE3. |
| **`objetivos-tesis`** | Alineación metodológica y avance de objetivos de la tesis (OE1, OE2, OE3). |
| **`tesis-escritura`** | Redacción académica de capítulos, estructura y citas IEEE. |
| **`redaccion-academica`** | Estilo, prosa académica formal y coherencia argumental. |
| **`formato-espe`** | Normas de formato institucional ESPE, márgenes, tablas APA y bibliografía IEEE. |
| **`curador-fuentes`** | Auditoría y control de calidad de la literatura en `Documentos para la tesis/`. |
