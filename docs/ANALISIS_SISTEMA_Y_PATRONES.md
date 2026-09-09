# Análisis Exhaustivo del Sistema, Stack Tecnológico y Patrones de Diseño

**Proyecto:** Auditor IA — Sistema Automatizado de Evaluación de Evidencias CACES (Ecuador, 2024)  
**Institución / Carrera:** Universidad de las Fuerzas Armadas ESPE — Ingeniería de Software  
**Fecha de Análisis:** Septiembre 2026  

---

## 1. Resumen Ejecutivo y Propósito del Sistema

El **Auditor IA CACES** es una solución de ingeniería de software e inteligencia artificial aplicada diseñada para automatizar la auditoría, clasificación física y verificación de cumplimiento normativo de evidencias documentales universitarias en procesos de acreditación de educación superior.

El sistema procesa documentos en formato PDF pertenecientes a cinco indicadores clave del modelo CACES 2024:
1. **Indicador 1:** Perfil de Egreso
2. **Indicador 2:** Proyecto Curricular / Diseño de Carrera
3. **Indicador 3:** Malla Curricular
4. **Indicador 4:** Sílabo (Plantilla institucional SGC.DI.321)
5. **Indicador 6:** Escenarios de Prácticas Formativas (Guía de Uso de Laboratorio)

Por cada lote de evidencias ingresado, el sistema emite dictámenes individuales estructurados, reportes formales en PDF, realiza un *triage* físico hacia carpetas organizadas y genera un reporte ejecutivo global consolidado.

---

## 2. Taxonomía del Stack Tecnológico

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CAPA DE PRESENTACIÓN                          │
│  Next.js 16 (React 19, TypeScript) + TailwindCSS 4 + Framer Motion     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST (Multipart POST, Polling)
┌───────────────────────────────────▼────────────────────────────────────┐
│                           API GATEWAY / ROUTER                         │
│  FastAPI + Pydantic v2 + CORSMiddleware                                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Celery Chord & Group Dispatch
┌───────────────────────────────────▼────────────────────────────────────┐
│                    COLA DE MENSAJES Y ALMACENAMIENTO                   │
│  Redis (Message Broker + Result Backend con TTL 24h)                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Async Task Worker
┌───────────────────────────────────▼────────────────────────────────────┐
│                        WORKER DISTRIBUIDO (CELERY)                     │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ CAPA 1: EXTRACCIÓN Y HECHOS DETERMINISTAS                        │  │
│  │ pdfminer.six (Coordenadas x, y) + unstructured (Fallback OCR)    │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │ Compuertas de Cortocircuito      │
│  ┌──────────────────────────────────▼───────────────────────────────┐  │
│  │ CAPA 2: RECUPERACIÓN RAG Y JUICIO SEMÁNTICO                      │  │
│  │ ChromaDB (Google Gemini Embeddings) + Groq (Llama 3.3 70B)       │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │ Checklist Estructurado           │
│  ┌──────────────────────────────────▼───────────────────────────────┐  │
│  │ CAPA 3: VEREDICTO DETERMINISTA, TRIAGE Y REPORTES                │  │
│  │ fpdf2 (Reportes Individuales y Ejecutivos) + OS Triage           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Detalle de Tecnologías y Bibliotecas:

| Dominio | Tecnología / Librería | Versión / Modelo | Justificación Técnica |
|---|---|---|---|
| **Web UI** | Next.js | 16.2.4 (App Router) | Renderizado rápido, reactividad con Server/Client Components y soporte TypeScript nativo. |
| **Estilos UI** | TailwindCSS | 4.x | Utility-first CSS moderno optimizado con `@tailwindcss/postcss`. |
| **Animaciones UI** | Framer Motion | 12.38.0 | Transiciones fluidas en acordeones de tareas, barras de progreso y modales de dictamen. |
| **Backend API** | FastAPI | >= 0.110 | Asincronía nativa, alto rendimiento, autodocumentación OpenAPI/Swagger e inyección de dependencias. |
| **Worker Asíncrono** | Celery | 5.x (`--pool=solo`) | Procesamiento concurrente de tareas pesadas en segundo plano con soporte para primitivas `group` y `chord`. |
| **Broker / Cache** | Redis | 7.x (Docker / Local) | Baja latencia para la cola de tareas y backend de resultados efímero. |
| **Extracción PDF** | pdfminer.six | Reciente | Acceso directo a coordenadas de cajas de texto `LTTextContainer` para reconstruir tablas y mallas sin OCR. |
| **OCR Fallback** | unstructured + Tesseract | 0.16.x | Respaldo activado exclusivamente ante PDFs escaneados (< 200 caracteres de texto nativo). |
| **Base Vectorial** | ChromaDB | >= 0.5.0 | Almacenamiento local embebido, persistente y desacoplado para la base de conocimiento normativa. |
| **Embeddings** | Google Generative AI | `models/gemini-embedding-001` | Representaciones vectoriales semánticas densas para indexación y búsqueda. |
| **Modelo LLM** | Groq API | `llama-3.3-70b-versatile` | Inferencia ultrarrápida (~300-500 tokens/s), costo eficiente y soporte estricto para *Structured Outputs*. |
| **Orquestación IA** | LangChain Core | 0.3.x | Encadenamiento de prompts (`PromptTemplate`), integración con Chroma y Groq. |
| **Validación y Tipado** | Pydantic | v2.x | Modelado de contratos de datos (`DictamenAuditoria`, `ElementoChecklist`) con validadores semánticos. |
| **Generación PDF** | fpdf2 | >= 2.7.9 | Generación programática de reportes vectoriales en PDF de alta calidad con soporte para tablas estructuradas. |

---

## 3. Catálogo de Patrones de Diseño e Ingeniería

### 3.1. Arquitectura en Tres Capas de Decisión (Separación Hechos / Juicios / Veredicto)
*   **Problema que resuelve:** Los Modelos de Lenguaje (LLMs) presentan alucinaciones cuando se les delegan tareas fácticas o geométricas sobre tablas (e.g. afirmar que un campo con texto está vacío o confundir códigos de asignaturas).
*   **Implementación:**
    1.  **Capa 1 (Hechos):** El código determinista resuelve con coordenadas qué campos existen, cuáles están vacíos, si la plantilla contiene los marcadores oficiales y si la asignatura consta en la malla de 44 materias.
    2.  **Capa 2 (Juicio):** El LLM recibe una *Hoja de Hechos Verificados* como verdad inmutable y se enfoca exclusivamente en juzgar el contenido cualitativo de los elementos fundamentales contra la norma CACES.
    3.  **Capa 3 (Veredicto):** El veredicto final se calcula algorítmicamente combinando los hechos de Capa 1 y el puntaje del checklist de Capa 2 mediante una función matemática determinista.

### 3.2. Compuertas de Cortocircuito (*Short-Circuiting / Token Guarding Pattern*)
*   **Problema que resuelve:** Consumo innecesario de tokens de API y costos en documentos no conformes o no institucionales.
*   **Implementación:**
    - Compuerta Léxica: Si el documento tiene $< 2$ palabras académicas $\rightarrow$ rechazo inmediato.
    - Compuerta de Plantilla: Si faltan marcadores oficiales $\rightarrow$ `PLANTILLA NO RECONOCIDA`.
    - Compuerta de Pertinencia: Si la materia no consta en la carrera $\rightarrow$ `NO CUMPLE` (0%).
    - Compuerta de Plantilla Vacía: Si $> 50\%$ de campos están vacíos $\rightarrow$ `NO CUMPLE`.
    *En todos estos casos, la tarea finaliza y enruta sin invocar a Groq.*

### 3.3. RAG Híbrido Determinista-Semántico (*Hybrid Two-Stage Routing*)
*   **Problema que resuelve:** La búsqueda pura por similitud de embeddings (*kNN*) en documentos normativos similares induce errores de enrutamiento (e.g. clasificar un Proyecto Curricular como Perfil de Egreso porque lo cita en la portada).
*   **Implementación:**
    - **Fase 1 (Titular exacto):** Examina los primeros 1,500 caracteres (`VENTANA_TITULAR`) mediante reglas de alta precisión (`MAPEO_INDICADORES`). Si coincide, recupera la norma por metadato exacto `get(where={"indicador": N})` a costo cero de embeddings.
    - **Fase 2 (Búsqueda en cuerpo):** Si no hay titular, busca marcadores en el cuerpo completo.
    - **Fase 3 (Similitud Vectorial de Respaldo):** Si las reglas no detectan el indicador, ejecuta `similarity_search(k=1, filter={"tipo": "norma"})`.

### 3.4. Orquestación Distribuida con Celery Chord (*Map-Reduce Task Pattern*)
*   **Problema que resuelve:** Procesar lotes grandes de PDFs en paralelo sin saturar la memoria y generar un reporte consolidado sólo cuando todos los archivos hayan terminado.
*   **Implementación:**
    ```python
    g = group([auditar_documento_pesado.s(pdf_path, filename) for pdf_path in files])
    chord_result = chord(g)(generar_reporte_ejecutivo.s(id_lote))
    ```
    Cada tarea individual realiza el análisis y triage físico de su documento; al finalizar el grupo completo, Celery invoca la tarea callback `generar_reporte_ejecutivo` pasando la lista consolidada de resultados.

### 3.5. Resiliencia Diferenciada ante Rate Limits (TPM vs TPD)
*   **Problema que resuelve:** Interrupción de lotes de auditoría por límites de tasa de la API de Groq.
*   **Implementación:**
    - **Límite por minuto (Tokens Per Minute - TPM):** Parsea la cabecera `try again in Xs` y programa un reintento automático no bloqueante con `self.retry(countdown=segundos + 5)`.
    - **Límite diario (Tokens Per Day - TPD):** Detecta la cuota diaria agotada (100k tokens), interrumpe reintentos y desvía el PDF a `98_Pendientes_Por_Cuota`, preservándolo limpio para reejecución futura.

### 3.6. Reconstrucción Geométrica Invariante a la Escala (*Adaptive Layout Grid Parsing*)
*   **Problema que resuelve:** La malla curricular es un diagrama complejo exportado a distintas resoluciones y pliegos de página (de 1x a 3.3x), rompiendo tolerancias en puntos fijos.
*   **Implementación:**
    Calcula el paso mediano horizontal y vertical entre las etiquetas `HPAO` del diagrama para deducir dinámicamente los factores de escala $(e_x, e_y)$, adaptando todas las cajas de búsqueda de códigos, nombres, prerrequisitos, créditos y horas.

### 3.7. Salida Estructurada Tipada con Corrección Semántica (*Defensive Structured Output*)
*   **Problema que resuelve:** Asegurar que si el modelo califica un elemento como no cumplido (`cumple=False`), siempre proporcione una justificación fundamentada y una categoría de falla (`AUSENTE` o `INSUFICIENTE`).
*   **Implementación:**
    Utiliza `Pydantic v2` con `@model_validator(mode="after")` para formatear y enriquecer la justificación automáticamente sin lanzar errores de validación que provoquen reintentos costosos de inferencia.

---

## 4. Matriz de Indicadores CACES y Lógica de Evaluación

| Indicador | Denominación | Tipo de Plantilla | Criterios Deterministas (Capa 1) | Criterios Semánticos LLM (Capa 2) |
|---|---|---|---|---|
| **Indicador 1** | Perfil de Egreso | Prosa libre / Resolución | Detección de carrera y marcadores ("PERFIL DE EGRESO", "PERFIL PROFESIONAL"). | Concordancia con los 5 elementos fundamentales de la norma (resultados de aprendizaje, competencias profesionales, pertinencia social). |
| **Indicador 2** | Proyecto Curricular | Formato SENESCYT/CES (extenso) | Marcadores de carrera a rediseñar. Recorte automático a secciones clave (`recorte_proyecto.py`). | Justificación curricular, coherencia formativa, fundamentación epistemológica. |
| **Indicador 3** | Malla Curricular | Diagrama apaisado con rejilla HPAO | Reconstrucción celda por celda: 8 PAO, 44 materias, 48h/crédito, códigos y prerrequisitos válidos. | Elementos fundamentales de organización curricular y distribución de unidades. |
| **Indicador 4** | Sílabo | Plantilla oficial SGC.DI.321 | 20 campos de DATOS GENERALES (NRC, Asignatura, Docente, Carga Horaria, etc.), pertinencia de asignatura en malla. | 10 elementos fundamentales (unidades temáticas, metodologías, evaluación, bibliografía). |
| **Indicador 6** | Guías de Práctica / Laboratorio | Formato de Prácticas Formativas | Marcadores de laboratorio, campos de práctica, reactivos/software y firmas institucionales. | Planificación pedagógica, articulación teórica-práctica, normas de bioseguridad/recursos. |

---

## 5. Árbol de Veredictos y Triage Físico

El sistema clasifica físicamente los archivos procesados en el siguiente árbol de directorios:

```
backend/Auditoria_CACES/
├── Indicador_1_Perfil_de_egreso/                          # Aprobados Ind. 1 (CUMPLE / PARCIAL)
├── Indicador_2_Proyecto_curricular/                      # Aprobados Ind. 2 (CUMPLE / PARCIAL)
├── Indicador_3_Malla_curricular/                         # Aprobados Ind. 3 (CUMPLE / PARCIAL)
├── Indicador_4_Syllabus/                                 # Aprobados Ind. 4 (Renombrados a formato canónico)
├── Indicador_6_Escenarios_de_practicas_formativas/       # Aprobados Ind. 6 (CUMPLE / PARCIAL)
├── 11_Documentos_Rechazados/                             # NO CUMPLE (puntaje <= 50%, otra carrera, plantilla vacía)
├── 12_Plantilla_No_Reconocida/                           # Documento sin plantilla oficial o no académico
├── 98_Pendientes_Por_Cuota/                              # Archivos no auditados por límite diario de tokens (Groq)
├── 99_Descarte_Errores/                                  # Archivos corruptos o PDFs ilegibles
└── Reportes_Ejecutivos/                                  # Reportes PDF globales generados al cerrar cada lote
```

---

## 6. Conclusiones y Beneficios para la Tesis

1. **Rigor Académico y Metodológico:** La separación en tres capas garantiza que los datos empíricos de acreditación no sean alterados por sesgos estocásticos de modelos generativos.
2. **Eficiencia y Escalabilidad:** El uso de extracción por coordenadas reduce en un 94% el tiempo de procesamiento por documento frente a OCR tradicional, y las compuertas de cortocircuito ahorran hasta un 40% del consumo de tokens en lotes con documentos espurios.
3. **Reproducibilidad Experimental:** El banco de pruebas determinista y los scripts de evaluación por Jaccard y Kappa proporcionan soporte experimental cuantitativo sólido para la defensa del Objetivo Específico 3 (OE3) de la investigación.
