# Auditor IA — Evaluación automatizada de evidencias CACES

Sistema que clasifica, audita y archiva evidencias documentales de acreditación (perfiles de
egreso, proyectos curriculares, mallas, sílabos y guías de laboratorio) contra la normativa
del CACES (Ecuador, 2024).

Por cada PDF produce un dictamen estructurado, un reporte individual en PDF y lo mueve a la
carpeta de su indicador. Al terminar un lote genera un reporte ejecutivo global.

**Capas:** Next.js (UI) → FastAPI (API) → Redis (cola) → Celery (worker) → ChromaDB (RAG) +
Groq / Llama 3.3 (dictamen) + Gemini (embeddings).

---

## 1. Cómo evalúa: tres capas

El sistema separa **hechos** de **juicios**. Es la decisión de diseño central.

**Capa 1 — Hechos (determinista, sin LLM).** Extracción del PDF conservando coordenadas,
verificación de la plantilla por sus marcadores, pertinencia a la carrera y detección de
campos sin llenar. Todo esto son datos verificables, y pedírselos al LLM producía
alucinaciones: declaraba vacíos campos que estaban llenos y afirmaba pertenencias
inexistentes, porque el extractor le entregaba las tablas desordenadas.

**Capa 2 — Juicio (LLM).** Recibe la norma recuperada de ChromaDB, los hechos ya verificados
y el documento. Devuelve únicamente el checklist con su cita textual y el diagnóstico.

**Capa 3 — Veredicto (determinista).**

| Condición | Veredicto |
|---|---|
| No usa la plantilla oficial del indicador | `PLANTILLA NO RECONOCIDA` |
| No pertenece a la carrera | `NO CUMPLE` (0%) |
| Más de la mitad de los campos obligatorios en blanco | `NO CUMPLE` |
| Elementos cumplidos ≤ 50% | `NO CUMPLE` |
| ≥ 70% y ningún campo sin llenar | `CUMPLE` |
| Resto | `CUMPLE PARCIALMENTE` |

Si la plantilla no es válida o el documento es de otra carrera, **no se llama al LLM**: el
veredicto se emite sin consumir tokens.

---

## 2. Extracción: por qué no se usa OCR

Los documentos institucionales conservan capa de texto nativa; no son escaneos. Ejecutar OCR
sobre ellos multiplica por 18 el tiempo de extracción (28 s frente a 1,5 s por sílabo),
degrada los códigos de asignatura (`EXCTA0301` se lee `EXCTAO301`), pierde las etiquetas
rotadas de la malla (los ocho PAO) y **colapsa la tabla de datos generales en una sola
línea**, de modo que resulta imposible asociar cada etiqueta con su valor.

Por eso la ruta principal usa `pdfminer.six` —el mismo motor que `unstructured` emplea
internamente para PDFs con texto— pidiéndole las coordenadas que aquél descarta. El OCR de
`unstructured` queda como respaldo, y sólo se activa ante un PDF escaneado.

La malla curricular, que es un diagrama apaisado, se reconstruye celda por celda: una línea
por asignatura con su código, nombre, prerrequisito, horas y créditos.

---

## 3. Requisitos

| Software | Versión | Necesario para |
|---|---|---|
| Python | 3.11 | Backend y worker |
| Node.js | LTS | Frontend |
| Docker Desktop | cualquiera | Redis |

**Poppler y Tesseract sólo hacen falta para el respaldo OCR**, es decir, para PDFs
escaneados. Ninguno de los documentos institucionales probados los necesita.

---

## 4. Instalación

El entorno virtual vive en **la raíz del proyecto**, no dentro de `backend/`.

```bash
git clone <repo> tesis
cd tesis
python -m venv venv
.\venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r backend/requirements.txt
```

Crea `backend/.env`:

```env
GROQ_API_KEY=tu_api_key_de_groq
GOOGLE_API_KEY=tu_api_key_de_gemini
```

---

## 5. Construir la Base de Oro

```bash
cd backend
python scripts/extraer_asignaturas.py "ruta/a/malla_oficial.pdf"   # sólo si cambia la malla
python scripts/crear_base_oro.py                                   # un vector por indicador
python scripts/ingestar_maestro.py                                 # documento maestro
```

`crear_base_oro.py` **borra y recrea** `chroma_data`, así que el orden importa. Repite ambos
pasos cada vez que edites `data/caces_2024_oficial.txt`: el worker lee la norma desde
ChromaDB, no desde el archivo.

> Si el worker de Celery está corriendo, tendrá bloqueado `chroma_data` y el script abortará
> con un mensaje claro. Párale primero.

`data/asignaturas_malla.txt` contiene las 44 asignaturas de la malla vigente y es la fuente
de verdad para decidir si un sílabo pertenece a la carrera.

---

## 6. Levantar el sistema

```bash
docker run -d -p 6379:6379 --name redis-caces redis   # 1. Redis
uvicorn main:app --reload                              # 2. API (desde backend/)
celery -A services.tareas_ia worker --loglevel=info --pool=solo   # 3. Worker (desde backend/)
npm install && npm run dev                             # 4. Frontend (desde frontend/)
```

Abre `http://localhost:3000`, arrastra los PDFs y pulsa *Analizar y Clasificar*.

> **El worker de Celery no recarga el código.** `uvicorn --reload` sí; el worker no. Cada vez
> que toques `services/*.py` hay que pararlo con `Ctrl+C` y relanzarlo.

---

## 7. Banco de pruebas

Verifica toda la capa determinista sin gastar cuota de la API:

```bash
python scripts/banco_pruebas.py
```

Comprueba enrutado al indicador, validez de plantilla, pertinencia y campos sin llenar sobre
un corpus de documentos correctos, trampas y de otras carreras. Lo único que no cubre es el
juicio del checklist, que es lo único que queda en manos del LLM.

---

## 8. Estructura de salida

```
backend/Auditoria_CACES/
├── Indicador_1_Perfil_de_egreso/
├── Indicador_2_Proyecto_curricular/
├── Indicador_3_Malla_curricular/
├── Indicador_4_Syllabus/
├── Indicador_6_Escenarios_de_practicas_formativas/
├── 11_Documentos_Rechazados/        # no cumple, o de otra carrera
├── 12_Plantilla_No_Reconocida/      # no es la plantilla oficial del indicador
├── 98_Pendientes_Por_Cuota/         # sin defecto: se agotó la cuota de la API
├── 99_Descarte_Errores/             # PDF ilegible
└── Reportes_Ejecutivos/             # un PDF por lote
```

---

## 9. Problemas frecuentes

**El worker usa código viejo.** Celery no recarga; párale y relánzalo.

**Quedan tareas o resultados antiguos en Redis.**

```bash
celery -A services.tareas_ia purge -f            # sólo la cola
docker exec -it redis-caces redis-cli FLUSHALL   # cola + resultados
```

**Groq devuelve `429`.** Hay dos límites distintos. El de tokens por minuto se reintenta solo
con la espera que indica la API. El de tokens por día (100.000 en el plan gratuito, unos 15
sílabos) no se reintenta: el documento se aparta en `98_Pendientes_Por_Cuota` y basta con
volver a subirlo cuando el contador se recargue.

**El frontend muestra `EN COLA` para siempre.** Los resultados de Celery caducan en Redis a
las 24 h.

**`ModuleNotFoundError` al lanzar el worker.** Estás usando el venv equivocado: el bueno está
en la raíz (`tesis/venv`), no en `tesis/backend/venv`.

---

## 10. Limitaciones conocidas

- **El sílabo de la ESPE no declara la carrera.** La pertinencia se decide comparando la
  asignatura contra la malla vigente. Acierta en 22 de 24 sílabos etiquetados. Falla en dos
  casos comprensibles: una asignatura que no consta en la malla (`TEC Y SIS DE LA
  INFORMACION`) y otra compartida con otra carrera (`APLICACIONES MOVILES`, que también se
  imparte en Tec. Redes y Telecomunicaciones).
- **El LLM no es determinista.** Aunque `temperature=0`, Llama en Groq devuelve textos
  distintos entre corridas del mismo documento. Por eso el veredicto, la pertinencia y los
  campos vacíos se calculan en código: sólo el checklist y el diagnóstico varían.
- **Los indicadores 1 y 2 se evalúan sólo con criterios semánticos.** El perfil de egreso y
  el proyecto curricular son prosa, sin plantilla de campos etiquetados que verificar.
- **En un PDF escaneado no se pueden verificar los campos.** El OCR no conserva la
  disposición de la tabla, así que la detección de campos vacíos se desactiva y el sistema
  se lo dice al modelo explícitamente en lugar de afirmar que no hay campos.
- **Una sola carrera.** El documento maestro y la lista de asignaturas están fijados a
  Ingeniería de Software.
- **Sin persistencia.** El único registro duradero son los PDFs con marca de tiempo y sus
  reportes. Los dictámenes estructurados viven en Redis y caducan a las 24 h.
