# Auditor IA — Evaluación automatizada de evidencias CACES

Sistema que clasifica, audita y archiva evidencias documentales de acreditación (sílabos,
mallas curriculares, guías de laboratorio) contra la normativa del CACES (Ecuador, 2024).

Por cada PDF produce un dictamen estructurado, un reporte individual en PDF, y lo mueve a
la carpeta de su indicador. Al terminar un lote genera un reporte ejecutivo global.

**Capas:** Next.js (UI) → FastAPI (API) → Redis (cola) → Celery (worker) → ChromaDB (RAG) +
Groq / Llama 3.3 (dictamen) + Gemini (embeddings).

---

## 1. Requisitos

| Software | Versión | Necesario para |
|---|---|---|
| Python | 3.11 | Backend y worker |
| Node.js | LTS | Frontend |
| Docker Desktop | cualquiera | Redis |
| Git | cualquiera | Clonar |

**Poppler y Tesseract no hacen falta.** Los PDFs institucionales traen capa de texto y se leen
con `pdfminer.six`, conservando las coordenadas. El OCR sólo se activaría ante un PDF escaneado;
en ese caso hay que instalar los extras comentados al final de `backend/requirements.txt` y
añadir Poppler y Tesseract al `PATH`.

---

## 2. Instalación

El entorno virtual vive en **la raíz del proyecto**, no dentro de `backend/`.

```bash
git clone <repo> tesis
cd tesis

python -m venv venv
.\venv\Scripts\activate          # macOS/Linux: source venv/bin/activate

pip install -r backend/requirements.txt
```

Para reproducir el entorno exacto de las pruebas (todas las transitivas fijadas):

```bash
pip install -r backend/requirements.lock.txt
```

Crea `backend/.env` con tus claves:

```env
GROQ_API_KEY=tu_api_key_de_groq
GOOGLE_API_KEY=tu_api_key_de_gemini
```

---

## 3. Construir la Base de Oro

La normativa vive en `backend/data/caces_2024_oficial.txt`: un bloque por indicador, más un
bloque de reglas generales. `crear_base_oro.py` **borra y recrea** el directorio `chroma_data`,
así que el orden importa:

```bash
cd backend
python scripts/crear_base_oro.py     # un vector por indicador + reglas
python scripts/ingestar_maestro.py   # perfil y malla de Ingeniería de Software
```

> Repite ambos pasos **cada vez que edites** `caces_2024_oficial.txt`. El worker lee la norma
> desde ChromaDB, no desde el archivo.

Salida esperada:

```
  [norma ] indicador  1 |  1177 chars | Perfil de egreso
  [norma ] indicador  2 |  1151 chars | Proyecto curricular
  [norma ] indicador  3 |  2352 chars | Malla curricular
  [norma ] indicador  4 |  2752 chars | Syllabus
  [norma ] indicador  6 |  2079 chars | Escenarios de prácticas formativas
  [reglas] indicador  0 |  1681 chars | Reglas generales
```

---

## 4. Levantar el sistema

Cuatro terminales, en este orden.

```bash
# 1. Redis
docker run -d -p 6379:6379 --name redis-caces redis

# 2. API  (desde tesis/backend, con el venv activo)
uvicorn main:app --reload

# 3. Worker (desde tesis/backend, con el venv activo)
celery -A services.tareas_ia worker --loglevel=info --pool=solo

# 4. Frontend (desde tesis/frontend)
npm install
npm run dev
```

Abre `http://localhost:3000`, arrastra los PDFs y pulsa *Analizar y Clasificar*.

> **El worker de Celery NO recarga el código.** `uvicorn --reload` sí, pero el worker no.
> Cada vez que toques `services/*.py` hay que pararlo con `Ctrl+C` y relanzarlo, o seguirá
> ejecutando la versión anterior. Ver §7.

---

## 5. Cómo evalúa

1. **Extracción.** `services/extraccion.py` lee la capa de texto con coordenadas y reconstruye
   el orden visual agrupando las cajas por solapamiento vertical. La malla curricular, que es
   un diagrama apaisado, se reconstruye celda por celda: una línea por asignatura con su
   código, nombre, prerrequisito, horas y créditos.
2. **Enrutado.** Palabras clave sobre los primeros 1500 caracteres deciden el indicador. Si
   aciertan, la norma se lee de ChromaDB **por metadatos** (sin llamada de embeddings). Si no,
   se cae a búsqueda por similitud filtrada a `tipo="norma"`, y el resultado queda marcado con
   `enrutado_por="similitud"` para poder excluirlo de las métricas.
3. **Dictamen.** Llama 3.3 recibe las reglas generales, el bloque del indicador, el documento
   maestro de la carrera y el documento, y devuelve salida estructurada validada con Pydantic.
4. **Veredicto.** No lo decide el LLM. Se deriva en `_calcular_veredicto`:

   | Condición | Veredicto |
   |---|---|
   | No usa la plantilla oficial | `PLANTILLA NO RECONOCIDA` |
   | No pertenece a la carrera | `NO CUMPLE` (0%) |
   | Elementos cumplidos ≤ 50% | `NO CUMPLE` |
   | ≥ 70% y ningún campo vacío | `CUMPLE` |
   | Resto | `CUMPLE PARCIALMENTE` |

   El porcentaje mide **la estructura** (elementos fundamentales). Un campo sin llenar no
   invalida el documento: sólo topa el veredicto en `CUMPLE PARCIALMENTE`, porque basta con
   llenarlo.
5. **Archivado.** `services/orchestrator_service.py` copia el PDF y su reporte a la carpeta
   del indicador, o a `11_Documentos_Rechazados`, `12_Plantilla_No_Reconocida` o
   `99_Descarte_Errores` según el caso.

---

## 6. Estructura de salida

```
backend/Auditoria_CACES/
├── Indicador_1_Perfil_de_egreso/
├── Indicador_2_Proyecto_curricular/
├── Indicador_3_Malla_curricular/
├── Indicador_4_Syllabus/
├── Indicador_6_Escenarios_de_practicas_formativas/
├── 11_Documentos_Rechazados/        # no cumple, o de otra carrera
├── 12_Plantilla_No_Reconocida/      # no es la plantilla oficial
├── 99_Descarte_Errores/             # PDF ilegible o fallo de API
└── Reportes_Ejecutivos/             # un PDF por lote
```

---

## 7. Problemas frecuentes

**El worker sigue usando código viejo.** Celery no recarga. Párale y relánzalo:

```bash
# Ctrl+C en la terminal del worker, luego:
celery -A services.tareas_ia worker --loglevel=info --pool=solo
```

**Quedan tareas encoladas o resultados viejos en Redis.** Vacía la cola y el backend de
resultados (esto borra también los estados que consulta el frontend):

```bash
celery -A services.tareas_ia purge -f          # sólo la cola de tareas
docker exec -it redis-caces redis-cli FLUSHALL # cola + resultados
```

**Groq devuelve `429 Too Many Requests`.** Estás en el techo de tokens por minuto. El cliente
reintenta solo, con esperas de ~30 s. Sube documentos en lotes más pequeños o espacia los envíos.

**El frontend muestra `EN COLA` para siempre.** Los resultados de Celery caducan en Redis a
las 24 h. Si consultas un `task_id` antiguo, el estado vuelve a `PENDING`.

**`ModuleNotFoundError` al lanzar el worker.** Estás usando el venv equivocado. El bueno está
en la raíz (`tesis/venv`), no en `tesis/backend/venv`. Si existe ese directorio, bórralo:

```bash
rm -rf backend/venv
```

---

## 8. Limitaciones conocidas

- **Los indicadores 1 y 2 no están instrumentados.** No hay plantilla institucional verificada
  para el perfil de egreso ni el proyecto curricular, así que se evalúan sólo con criterios
  semánticos y no deben usarse para métricas de precisión.
- **El sistema no es determinista.** Aunque `temperature=0`, Llama en Groq devuelve textos
  distintos entre corridas del mismo documento. El veredicto y el porcentaje sí son estables,
  porque se derivan aritméticamente del checklist.
- **La compuerta de pertinencia** distingue bien disciplinas lejanas, pero un sílabo de
  informática impartido a otra carrera puede colarse. Se decide por `Área de Conocimiento` y
  `Resultado de Aprendizaje de la Carrera`, no por el tema.
- **Una sola carrera.** El documento maestro está fijado a Ingeniería de Software en
  `scripts/ingestar_maestro.py`. Generalizar exige editar ese archivo.
- **Sin persistencia.** El único registro duradero son los PDFs con marca de tiempo. Los
  dictámenes estructurados viven en Redis y caducan.
