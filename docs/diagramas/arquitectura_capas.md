# Arquitectura en capas — diagramas Mermaid

Diagramas de la **vista técnica N-capas** del Auditor IA CACES, en Mermaid.

Dos avisos antes de usarlos:

- **Vocabulario.** "Capa" se reserva para la vista técnica (las cinco de aquí). El pipeline de
  decisión se llama **auditoría en 3 etapas**, y su filtro determinista, **compuertas de
  seguridad Pre-LLM**. Es el mismo criterio que sigue la presentación de defensa.
- **OCR, no pdfminer.** Los diagramas describen la versión que documenta el manuscrito.

Para exportarlos: pegar el bloque en <https://mermaid.live> y descargar en PNG o SVG. En SVG
entran en PowerPoint como vector y se ven nítidos al proyectar.

---

## 1. Diagrama completo — capas y flujo de una auditoría

Es el que sirve para explicar la arquitectura de verdad: muestra las cinco capas **y** por dónde
circula un documento.

```mermaid
flowchart TB

  subgraph C1["CAPA 1 — PRESENTACIÓN"]
    UI["Interfaz web · Next.js / React<br/>Carga de PDF por lotes, cola de tareas<br/>y semáforos de resultado"]
  end

  subgraph C2["CAPA 2 — APLICACIÓN"]
    API["API REST · FastAPI<br/>POST /evaluar_documento · GET /status<br/>Validación de tipos con Pydantic"]
  end

  subgraph C3["CAPA 3 — LÓGICA DE NEGOCIO"]
    direction LR
    E1["ETAPA 1<br/>Compuertas de seguridad Pre-LLM<br/>OCR · léxico · enrutado · plantilla<br/>pertinencia · campos vacíos"]
    E2["ETAPA 2<br/>Juicio cognitivo<br/>LLM + RAG<br/>checklist de elementos"]
    E3["ETAPA 3<br/>Veredicto determinista<br/>porcentaje, veredicto<br/>y triage"]
    E1 -->|"supera las 5 compuertas"| E2
    E2 --> E3
  end

  subgraph C4["CAPA 4 — INTEGRACIÓN"]
    direction LR
    GROQ["Groq · Llama 3.3 70B<br/>Inferencia del dictamen"]
    EMB["Google · gemini-embedding-001<br/>Vectorización de la normativa"]
  end

  subgraph C5["CAPA 5 — PERSISTENCIA"]
    direction LR
    RD["Redis<br/>Broker del lote y<br/>resultados temporales"]
    CH["ChromaDB<br/>Base de Oro:<br/>normativa CACES 2024"]
    FS["Sistema de archivos<br/>Carpetas por indicador<br/>y reportes PDF"]
  end

  UI <-->|"HTTP / JSON"| API
  API -->|"encola el lote como chord"| RD
  RD -->|"el worker Celery consume cada tarea"| E1
  E1 -->|"lee la norma por metadato exacto"| CH
  E2 -->|"prompt: norma + hechos + documento"| GROQ
  E3 -->|"copia el PDF y genera el reporte"| FS
  E3 -->|"devuelve el dictamen"| RD
  E1 -.->|"rechazo: el LLM no se invoca"| FS
  EMB -.->|"ingesta previa de la Base de Oro"| CH

  classDef capa fill:#F9FAFB,stroke:#E5E7EB,color:#111827
  classDef etapaDet fill:#ECFDF5,stroke:#006644,color:#111827
  classDef etapaLLM fill:#EEF2FF,stroke:#172C68,color:#111827
  classDef infra fill:#FFFFFF,stroke:#6B7280,color:#111827

  class UI,API infra
  class E1,E3 etapaDet
  class E2 etapaLLM
  class GROQ,EMB,RD,CH,FS infra

  style C1 fill:#F9FAFB,stroke:#172C68,stroke-width:1px
  style C2 fill:#F9FAFB,stroke:#172C68,stroke-width:1px
  style C3 fill:#F9FAFB,stroke:#006644,stroke-width:2px
  style C4 fill:#F9FAFB,stroke:#172C68,stroke-width:1px
  style C5 fill:#F9FAFB,stroke:#006644,stroke-width:1px
```

**Lo que hay que saber leerle:** la flecha punteada de la ETAPA 1 al sistema de archivos es el
aporte defendible de la arquitectura. Un documento que no supera las compuertas se archiva y se
reporta **sin llegar nunca a la capa 4**: el modelo no se invoca, no gasta cuota y no puede
alucinar sobre un documento que no leyó.

---

## 2. Variante compacta — sólo la pila de capas

Para una diapositiva donde sólo hace falta enseñar el apilamiento y quién depende de quién.

```mermaid
flowchart TB
  L1["<b>CAPA 1 · PRESENTACIÓN</b><br/>Next.js / React<br/><i>Captura la interacción y muestra el dictamen</i>"]
  L2["<b>CAPA 2 · APLICACIÓN</b><br/>FastAPI + Pydantic<br/><i>Expone la API REST y valida la entrada</i>"]
  L3["<b>CAPA 3 · LÓGICA DE NEGOCIO</b><br/>Worker Celery — auditoría en 3 etapas<br/><i>Compuertas Pre-LLM, juicio del modelo y veredicto</i>"]
  L4["<b>CAPA 4 · INTEGRACIÓN</b><br/>Groq · Google<br/><i>Consumo controlado de los servicios de IA</i>"]
  L5["<b>CAPA 5 · PERSISTENCIA</b><br/>ChromaDB · Redis · Sistema de archivos<br/><i>Normativa vectorizada, cola y repositorio CACES</i>"]

  L1 --> L2 --> L3 --> L4
  L3 --> L5
  L4 --> L5

  classDef navy fill:#EEF2FF,stroke:#172C68,color:#111827
  classDef verde fill:#ECFDF5,stroke:#006644,color:#111827
  class L1,L2,L4 navy
  class L3,L5 verde
```

Nota: la capa 3 apunta a la 4 **y** a la 5 porque el worker consulta los servicios de IA y
persiste el resultado; no es una pila estrictamente lineal.

---

## 3. Correspondencia entre las dos vistas

Responde a la pregunta que el tribunal hará si ve "5 capas" en un sitio y "3 etapas" en otro.

```mermaid
flowchart LR
  subgraph T["VISTA TÉCNICA — dónde vive el código"]
    direction TB
    A1["Capa 1 · Presentación"]
    A2["Capa 2 · Aplicación"]
    A3["Capa 3 · Lógica de negocio"]
    A4["Capa 4 · Integración"]
    A5["Capa 5 · Persistencia"]
  end

  subgraph D["VISTA DE DECISIÓN — quién decide y con qué evidencia"]
    direction TB
    B1["Etapa 1 · Compuertas Pre-LLM<br/><i>determinista, sin modelo</i>"]
    B2["Etapa 2 · Juicio cognitivo<br/><i>único punto donde decide el LLM</i>"]
    B3["Etapa 3 · Veredicto determinista<br/><i>recalculado en código</i>"]
  end

  A3 --> B1
  A5 --> B1
  A3 --> B2
  A4 --> B2
  A3 --> B3
  A5 --> B3

  classDef navy fill:#EEF2FF,stroke:#172C68,color:#111827
  classDef verde fill:#ECFDF5,stroke:#006644,color:#111827
  class A1,A2,A3,A4,A5 navy
  class B1,B3 verde
  class B2 navy
```

No son dos arquitecturas: son dos cortes del mismo sistema. El de la izquierda responde *dónde
vive el código*; el de la derecha, *quién toma cada decisión y con qué evidencia*.
