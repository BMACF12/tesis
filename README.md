# Auditor IA — Evaluación Automatizada de Evidencias CACES

Sistema que clasifica, audita y archiva evidencias documentales de acreditación universitaria (perfiles de
egreso, proyectos curriculares, mallas curriculares, sílabos y guías de laboratorio) contra la normativa
oficial del **CACES (Ecuador, 2024)** para la carrera de **Ingeniería de Software** de la **Universidad de las Fuerzas Armadas ESPE**.

Por cada documento PDF subido produce un dictamen estructurado en JSON, un reporte individual en PDF y lo mueve físicamente a la
carpeta de su indicador correspondiente. Al terminar un lote de auditoría, genera un reporte ejecutivo global consolidado.

---

## 1. Arquitectura y Modelo de Decisión en Tres Capas

El principio rector del sistema es la **separación estricta de hechos verificables y juicios cualitativos**:

```
[Documento PDF]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1 — HECHOS (Determinista, sin LLM)                     │
│ • Extracción por coordenadas espaciales con pdfminer.six   │
│ • Verificación de marcadores de plantilla oficial           │
│ • Validación de pertinencia a la carrera (44 asignaturas)   │
│ • Detección de campos obligatorios sin llenar               │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │ ¿Pasa compuertas de cortocircuito?  │
            └──┬───────────────────────────────┬──┘
            SÍ │                            NO │ (Plantilla inválida, ajeno
               ▼                               ▼  a la carrera, o vacío >50%)
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ CAPA 2 — JUICIO (LLM Groq)   │ │ Veredicto Inmediato          │
│ • RAG híbrido en ChromaDB    │ │ (0 tokens consumidos)        │
│ • Evaluación del checklist   │ └──────────────┬───────────────┘
│   normativo con citas        │                │
└──────────────┬───────────────┘                │
               │                                │
               ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 3 — VEREDICTO DETERMINISTA Y TRIAGE                    │
│ • Cálculo matemático del puntaje y veredicto final          │
│ • Generación de reportes PDF vectoriales con fpdf2          │
│ • Enrutamiento físico a carpetas y renombrado canónico      │
└─────────────────────────────────────────────────────────────┘
```

### Tabla de Veredictos
| Condición | Veredicto | Consumo de Tokens |
|---|---|---|
| No usa la plantilla oficial del indicador | `PLANTILLA NO RECONOCIDA` | **0 tokens** |
| Asignatura ajena a la malla de Software | `NO CUMPLE` (0%) | **0 tokens** |
| Más del 50% de campos obligatorios vacíos | `NO CUMPLE` | **0 tokens** |
| Elementos fundamentales cumplidos $\le 50\%$ | `NO CUMPLE` | Juicio LLM |
| $\ge 70\%$ y ningún campo obligatorio vacío | `CUMPLE` | Juicio LLM |
| Resto de casos | `CUMPLE PARCIALMENTE` | Juicio LLM |

---

## 2. Stack Tecnológico

| Componente | Tecnología | Rol |
|---|---|---|
| **Frontend Web** | **Next.js 16** + **TailwindCSS 4** + **Framer Motion** | Interfaz drag & drop, polling reactivo y visualización de dictámenes. |
| **API Gateway** | **FastAPI** + **Pydantic v2** | Enrutamiento REST, validación multipart y despacho distribuido. |
| **Worker / Cola** | **Celery 5.x** + **Redis** | Tareas en segundo plano con orquestación `chord` y `group`. |
| **Base Vectorial** | **ChromaDB** + **Google Gemini Embeddings** | Almacenamiento persistente de la normativa ("Base de Oro"). |
| **Modelo LLM** | **Groq API** (`llama-3.3-70b-versatile`, `temp=0`) | Inferencia de alta velocidad con salida estructurada tipada. |
| **Extracción PDF** | **pdfminer.six** (con OCR fallback `unstructured`) | Parseo geométrico por coordenadas `(x0, y0, x1, y1)`. |
| **Generación PDF** | **fpdf2** | Renderizado de reportes individuales y ejecutivos de lote. |

---

## 3. Despliegue en la Nube (100% Gratuito)

El sistema está configurado para ejecutarse en plataformas *Free Tier* (Vercel + Render):

- **Frontend en Vercel:** Conectado a la carpeta `frontend/` del repositorio [Haptax/tesis_portafolio](https://github.com/Haptax/tesis_portafolio).
- **Backend en Render:** Contenedor Docker ([`backend/Dockerfile`](./backend/Dockerfile)) que arranca FastAPI, Celery Worker, Redis y la Base de Oro automáticamente en [`https://tesis-ec9m.onrender.com`](https://tesis-ec9m.onrender.com).
- **Documentación de la API:** Accede a Swagger UI en vivo en [`https://tesis-ec9m.onrender.com/docs`](https://tesis-ec9m.onrender.com/docs).

> Consulta la guía paso a paso completa en [**`docs/GUIA_DESPLIEGUE.md`**](./docs/GUIA_DESPLIEGUE.md).

---

## 4. Instalación y Ejecución Local

### 1. Clonar el repositorio y crear el entorno virtual
El entorno virtual vive en **la raíz del proyecto**:

```bash
git clone https://github.com/Haptax/tesis_portafolio.git tesis
cd tesis
python -m venv venv
.\venv\Scripts\activate          # En Linux/macOS: source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configurar variables de entorno
Crea el archivo `backend/.env`:

```env
GROQ_API_KEY=tu_api_key_de_groq
GOOGLE_API_KEY=tu_api_key_de_gemini
REDIS_URL=redis://localhost:6379/0
```

### 3. Construir la Base de Oro (ChromaDB)
```bash
cd backend
python scripts/crear_base_oro.py
python scripts/ingestar_maestro.py
```

### 4. Iniciar los servicios
En terminales separadas (con el entorno virtual activado):

```bash
# Terminal 1: Iniciar Redis con Docker
docker run -d -p 6379:6379 --name redis-caces redis

# Terminal 2: Iniciar la API FastAPI (desde backend/)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 3: Iniciar el Worker de Celery (desde backend/)
cd backend
celery -A services.tareas_ia worker --loglevel=info --pool=solo

# Terminal 4: Iniciar el Frontend Next.js (desde frontend/)
cd frontend
npm install
npm run dev
```

Abre `http://localhost:3000` en tu navegador.

---

## 5. Banco de Pruebas y Evaluación Experimental (OE3)

Para evaluar la precisión determinista y las compuertas de corte sin consumir cuota de tokens:

```bash
cd backend
python scripts/banco_pruebas.py
```

Para medir el acuerdo del checklist del LLM frente a expertos humanos (*ground truth*):

```bash
cd backend
python scripts/evaluar_jaccard.py
```

---

## 6. Estructura del Repositorio

```
tesis/
├── README.md                     # Documentación general y puesta en marcha
├── GEMINI.md                     # Guía maestra para Google Antigravity
├── AGENTS.md                     # Protocolo y gobernanza de agentes
├── backend/
│   ├── Dockerfile                # Imagen Docker multi-servicio para la nube
│   ├── start.sh                  # Script de arranque (Chroma + Celery + FastAPI)
│   ├── main.py                   # API FastAPI Gateway y CORS
│   ├── api/rutas.py              # Endpoints HTTP (/evaluar_documento/, /status/)
│   ├── services/
│   │   ├── extraccion.py         # Capa 1: Extracción geométrica por coordenadas
│   │   ├── tareas_ia.py          # Capas 1, 2 y 3: Pipeline y tareas Celery
│   │   ├── orchestrator_service.py # Triage físico y generador PDF individual
│   │   └── pdf_generator_ejecutivo.py # Reporte global consolidado de lote
│   ├── data/
│   │   ├── caces_2024_oficial.txt # Base de Oro: normativa CACES 2024
│   │   └── asignaturas_malla.txt # 44 asignaturas oficiales de Software
│   └── scripts/                  # Scripts de inicialización y evaluación
├── frontend/
│   ├── app/                      # Next.js App Router (Dashboard, Login, Polling)
│   └── package.json
├── docs/
│   ├── GUIA_DESPLIEGUE.md        # Manual de despliegue en Vercel + Render
│   ├── ANALISIS_SISTEMA_Y_PATRONES.md # Análisis arquitectónico y patrones
│   ├── ARQUITECTURA.md           # Flujo de datos y componentes
│   ├── INDICADORES.md            # Fichas técnicas de indicadores CACES
│   └── PLAN_EVALUACION.md        # Métricas y protocolo experimental OE3
└── .agents/
    ├── agents/                   # Roster de 16 subagentes especializados
    ├── rules/                    # Reglas generales del workspace
    └── skills/                   # Runbooks y procedimientos ejecutables
```

---

## 7. Documentación Adicional

- [**Guía de Despliegue en la Nube (Vercel + Render)**](./docs/GUIA_DESPLIEGUE.md)
- [**Análisis Exhaustivo del Sistema y Patrones de Diseño**](./docs/ANALISIS_SISTEMA_Y_PATRONES.md)
- [**Fichas Técnicas de Indicadores CACES**](./docs/INDICADORES.md)
- [**Protocolo Experimental y Métricas de Evaluación**](./docs/PLAN_EVALUACION.md)
