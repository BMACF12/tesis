# Conocimiento — indicador-4-silabo

Material para razonar y probar el Indicador 4 (Syllabus SGC.DI.321). Coloca aquí:

- `plantilla_SGC.DI.321_vacia.pdf` — el formulario oficial en blanco (referencia de los 39
  elementos; ver `backend/scripts/plantilla_silabo.py`).
- `silabos_positivos/` — sílabos de Software bien llenados (ej. NRC 21278, 21306). Casos CUMPLE.
- `silabos_negativos/` — sílabos de OTRA carrera con plantilla correcta (ej. 22639 Contabilidad,
  22670 Tec. y Sist. de la Información). Casos de **no pertinencia** (etiqueta pertenece=0).
- `silabos_trampa/` — sílabo con la plantilla oficial pero **tablas/campos vacíos** (saca 44% hoy).
- `casos_limite/` — el 22745 (asignatura compartida entre carreras, sin campo carrera → indistinguible).
- `verdad_campos.md` — para cada sílabo, qué campos y qué tablas están vacíos DE VERDAD (leídos del
  PDF). Es el ground truth de la evaluación por Jaccard (`scripts/evaluar_campos.py`,
  `evaluar_jaccard.py`); el CSV vive en `backend/data/verdad_campos.csv`.

> Recuerda: la numeración salta de 4 a 6 (no hay sección 5); las celdas espaciadoras de DATOS
> GENERALES no son campos; `-` en Edición/Año/Idioma no es vacío.
