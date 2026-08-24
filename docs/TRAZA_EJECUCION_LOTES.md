# Traza de ejecución — 12 documentos, 5 lotes

Extracción del log del worker Celery del **2026-08-04, 23:25–23:30**. Cada documento se
clasifica por la **compuerta que lo resolvió** y se transcribe el JSON que devolvió la tarea
`auditar_documento_pesado`.

> El "JSON" de cada fila es el **dict `resultado`** que devuelve la tarea (`_resultado`,
> `tareas_ia.py:445`) y que viaja por Redis hasta el frontend. Las únicas llamadas JSON a una
> API externa en este log son **8 POST a Groq** (`/openai/v1/chat/completions`) y **1 POST a
> Google** (`gemini-embedding-001:batchEmbedContents`).

---

## 1. Las compuertas, en el orden en que se evalúan

Orden real del código (`auditar_documento_pesado`, `tareas_ia.py:490`):

| # | Compuerta | Función | Línea | Veredicto si corta | ¿Aparece en este log? |
|---|---|---|---|---|---|
| 0 | Legibilidad del PDF | `extraer_documento` | 505 | `ERROR_LECTURA` | no |
| 1 | Rechazo léxico (< 2 palabras académicas) | `PALABRAS_ACADEMICAS` | 517 | `PLANTILLA NO RECONOCIDA` | no |
| — | *Enrutado al indicador + RAG* | `_recuperar_norma` | 528 | *(no corta)* | sí, 12/12 |
| 2 | Plantilla oficial | `_plantilla_valida` | 531 | `PLANTILLA NO RECONOCIDA` | **sí, 1** |
| 3 | Pertinencia a Software | `_pertinencia` | 542 | `NO CUMPLE` | **sí, 2** |
| 4 | Plantilla mayoritariamente vacía | `_plantilla_vacia` | 554 | `NO CUMPLE` | **sí, 1** |
| — | Etapa 2: juicio del LLM | `ChatGroq` | 588 | — | sí, 8 |
| — | Etapa 3: veredicto | `_calcular_veredicto` | 602 | CUMPLE / PARCIAL / NO CUMPLE | sí, 8 |

**Dato de cabecera:** 4 de 12 documentos (33 %) se resolvieron **sin gastar una sola llamada
al LLM**. El enrutador barato de palabras clave acertó en 11 de 12 (91,7 %); sólo un documento
cayó al respaldo por similitud, y es el único que consumió una llamada de embeddings.

---

## 2. Reparto de los 12 documentos

| # | Documento | Ind. | Enrutado | Resuelto por | Veredicto | % | LLM | Tiempo |
|---|---|---|---|---|---|---|---|---|
| 1 | `202650_SI_LIDERAZGO_26680_…MONICA SALAZAR_ (1).pdf` | 4 | palabras_clave | **Compuerta 3** | NO CUMPLE | 0 | no | 4,23 s |
| 2 | `pepinillo.pdf` | 4 | palabras_clave | Etapa 3 | CUMPLE | 89 | sí | 4,97 s |
| 3 | `Silabo_NRC-21278_ABC_José_Carrillo…-signed-signed.pdf` | 4 | palabras_clave | Etapa 3 | CUMPLE | 89 | sí | 4,49 s |
| 4 | `silabus_trampa_20260702_105222.pdf` | 4 | palabras_clave | **Compuerta 4** | NO CUMPLE | 0 | no | **1,23 s** |
| 5 | `sylabus-nosylabus.pdf` | 2 | **similitud** | **Compuerta 2** | PLANTILLA NO RECONOCIDA | 0 | no | 5,50 s |
| 6 | `1.1 Guía Laboratorio ABC…búsqueda.pdf` | 6 | palabras_clave | Etapa 3 | CUMPLE | 100 | sí | 4,34 s |
| 7 | `1.2 Guía Laboratorio ABC…programación lógica.pdf` | 6 | palabras_clave | Etapa 3 | CUMPLE | 100 | sí | 4,49 s |
| 8 | `3.3 Guia Laboratorio ABC…NLP y Machine Learning.pdf` | 6 | palabras_clave | Etapa 3 | **CUMPLE PARCIALMENTE** | 100 | sí | 4,64 s |
| 9 | `malla_ingenierIa_de_software.pdf` | 3 | palabras_clave | Etapa 3 | CUMPLE PARCIALMENTE | 60 | sí | **10,69 s** |
| 10 | `MALLA-EDUCACION-INICIAL-EN-LINEA.pdf` | 3 | palabras_clave | **Compuerta 3** | NO CUMPLE | 0 | no | 2,09 s |
| 11 | `PERFILEGRESO_SW_20260702_000642.pdf` | 1 | palabras_clave | Etapa 3 | CUMPLE | 100 | sí | 4,50 s |
| 12 | `Reporte_Carrera_Software_26072017.pdf` | 2 | palabras_clave | Etapa 3 | CUMPLE | 80 | sí | **16,31 s** |

Cobertura por indicador en este log: **1** (1 doc), **2** (2), **3** (2), **4** (4), **6** (3) —
los cinco indicadores instrumentados.

---

## 3. JSON por compuerta

### Compuerta 2 — Plantilla oficial no reconocida

Único caso: `sylabus-nosylabus.pdf`. El enrutador por palabras clave **no acertó**, cayó al
respaldo por similitud, que lo mandó al Indicador 2 (proyecto curricular). La compuerta de
plantilla lo cortó igualmente: no están los marcadores de esa plantilla.

Log:
```
-> [CELERY] Plantilla no reconocida (faltan: ['Datos generales de la carrera',
   'Carrera a rediseñar o Tipo de trámite', 'Descripción microcurricular']). Sin llamada al LLM.
```

```json
{
  "nombre_original": "sylabus-nosylabus.pdf",
  "indicador_evaluado": "Indicador 2: Proyecto curricular",
  "indicador_numero": 2,
  "enrutado_por": "similitud",
  "plantilla_valida": false,
  "pertenece_software": null,
  "justificacion_software": "",
  "campos_vacios": [],
  "campos_localizados": 0,
  "checklist": [],
  "veredicto": "PLANTILLA NO RECONOCIDA",
  "porcentaje_estimado": 0,
  "justificacion": "No se hallaron los marcadores de la plantilla oficial: Datos generales de la carrera; Carrera a rediseñar o Tipo de trámite; Descripción microcurricular.",
  "analisis_libre": "El documento no usa la plantilla oficial de este indicador. Es un problema distinto de una plantilla correcta mal llenada."
}
```

**Marcas de esta compuerta:** `plantilla_valida: false`, `pertenece_software: null` (nunca se
llegó a evaluar), `checklist: []`.

---

### Compuerta 3 — Ajeno a la carrera

Dos casos, y por dos vías de detección distintas.

**3a · Por contraste contra la malla** (`202650_SI_LIDERAZGO…`, sílabo de otra carrera):

```
-> [CELERY] Ajeno a la carrera (Nombre Asignatura: CÓDIGO ASIGNATURA
   (no consta en la malla de Software)). Sin llamada al LLM.
```

```json
{
  "nombre_original": "202650_SI_LIDERAZGO_26680_sSOFTWARE_MONICA SALAZAR_ (1).pdf",
  "indicador_evaluado": "Indicador 4: Syllabus",
  "indicador_numero": 4,
  "enrutado_por": "palabras_clave",
  "plantilla_valida": true,
  "pertenece_software": false,
  "justificacion_software": "Nombre Asignatura: CÓDIGO ASIGNATURA (no consta en la malla de Software)",
  "campos_vacios": [],
  "campos_localizados": 0,
  "checklist": [],
  "veredicto": "NO CUMPLE",
  "porcentaje_estimado": 0,
  "justificacion": "El documento no pertenece a la carrera de Ingeniería de Software.",
  "analisis_libre": "Descartado de la auditoría: Nombre Asignatura: CÓDIGO ASIGNATURA (no consta en la malla de Software)."
}
```

**3b · Por lectura del campo CARRERA** (`MALLA-EDUCACION-INICIAL-EN-LINEA.pdf`):

```json
{
  "nombre_original": "MALLA-EDUCACION-INICIAL-EN-LINEA.pdf",
  "indicador_evaluado": "Indicador 3: Malla curricular",
  "indicador_numero": 3,
  "enrutado_por": "palabras_clave",
  "plantilla_valida": true,
  "pertenece_software": false,
  "justificacion_software": "CARRERA: EDUCACIÓN INICIAL MODALIDAD EN LÍNEA UCE, UFA - ESPE, UTN, U",
  "campos_vacios": [],
  "campos_localizados": 0,
  "checklist": [],
  "veredicto": "NO CUMPLE",
  "porcentaje_estimado": 0,
  "justificacion": "El documento no pertenece a la carrera de Ingeniería de Software.",
  "analisis_libre": "Descartado de la auditoría: CARRERA: EDUCACIÓN INICIAL MODALIDAD EN LÍNEA UCE, UFA - ESPE, UTN, U."
}
```

**Marcas de esta compuerta:** `plantilla_valida: true` (la plantilla *sí* era la correcta),
`pertenece_software: false`, `checklist: []`. La `justificacion_software` cita el dato exacto
que motivó el descarte — es la trazabilidad que un evaluador puede verificar a mano.

---

### Compuerta 4 — Plantilla oficial mayoritariamente vacía

Único caso: `silabus_trampa_20260702_105222.pdf`. **20 de 20 campos vacíos.** Es el corte más
barato del log: **1,23 s**, frente a los 4,3–4,9 s de un sílabo que sí llega al LLM.

```
-> [CELERY] Plantilla vacía (20/20). Sin llamada al LLM.
```

```json
{
  "nombre_original": "silabus_trampa_20260702_105222.pdf",
  "indicador_evaluado": "Indicador 4: Syllabus",
  "indicador_numero": 4,
  "enrutado_por": "palabras_clave",
  "plantilla_valida": true,
  "pertenece_software": true,
  "justificacion_software": "No se pudo determinar la carrera a partir del documento",
  "campos_vacios": [
    "Modalidad", "Departamento", "Área de Conocimiento", "Nombre Asignatura",
    "Período Académico", "Código", "NRC", "Nivel", "Docente", "Sesiones Semanales",
    "carga horaria: DOCENCIA",
    "carga horaria: PRACTICAS DE APLICACIÓN Y EXPERIMENTACIÓN",
    "carga horaria: APRENDIZAJE AUTÓNOMO",
    "Descripción de la Asignatura", "Contribución de la Asignatura",
    "Resultado de Aprendizaje de la Carrera", "Objetivo de la Asignatura",
    "Resultado de Aprendizaje de la Asignatura", "Proyecto Integrador",
    "Perfil sugerido del docente"
  ],
  "campos_localizados": 20,
  "checklist": [],
  "veredicto": "NO CUMPLE",
  "porcentaje_estimado": 0,
  "justificacion": "20 de 20 campos obligatorios están sin llenar.",
  "analisis_libre": "El documento usa la plantilla oficial pero está mayoritariamente en blanco. …"
}
```

> ⚠️ **Ojo con `pertenece_software: true` en este JSON.** La `justificacion_software` dice
> *«No se pudo determinar la carrera»*: `_pertinencia` devolvió `None` (indeterminado), y el
> código escribe `pertenece_software=(pertenece is not False)` (`tareas_ia.py:561`), que
> convierte el indeterminado en `true`. **No significa «se verificó que es de Software»**, sino
> «no se pudo descartar». Es lógicamente correcto —no hay que rechazar por no poder leer un
> campo— pero el nombre del campo induce a error si alguien lee el JSON en frío.

---

### Etapa 3 — Veredicto compuesto (8 documentos)

Los que superan las cuatro compuertas llegan al LLM y su veredicto lo decide
`_calcular_veredicto` (`tareas_ia.py:391-401`) **en código**, no el modelo:

```python
porcentaje = round(cumplidos / total * 100)
if _plantilla_vacia(vacios, localizados):  return porcentaje, "NO CUMPLE"
if porcentaje <= 50:                       return porcentaje, "NO CUMPLE"
if porcentaje >= 70 and not vacios:        return porcentaje, "CUMPLE"
return porcentaje, "CUMPLE PARCIALMENTE"
```

Los tres caminos que ejercita este log:

| Documento | % checklist | campos vacíos | Regla aplicada | Veredicto |
|---|---|---|---|---|
| `pepinillo.pdf` | 89 | 0 | `≥70 y sin vacíos` | CUMPLE |
| `3.3 Guia Laboratorio…` | **100** | **3** | `≥70 pero con vacíos` → cae al else | **CUMPLE PARCIALMENTE** |
| `malla_ingenieria_de_software.pdf` | **60** | 0 | `>50 y <70` → else | CUMPLE PARCIALMENTE |

**El caso 8 es el que hay que enseñar en la defensa.** El LLM aprobó los 3 elementos
fundamentales (100 %), pero la Capa 1 había detectado tres campos vacíos —`FECHA`,
`DEPARTAMENTO`, `LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA`— y el código **degradó el
veredicto por su cuenta**. Es la demostración de que el modelo no tiene la última palabra:

```json
{
  "nombre_original": "3.3 Guia Laboratorio ABC Implementa un sistema inteligente utilizando procesamiento de lenguaje natural y Machine Learning.pdf",
  "indicador_evaluado": "Indicador 6: Escenarios de prácticas formativas",
  "indicador_numero": 6,
  "enrutado_por": "palabras_clave",
  "plantilla_valida": true,
  "pertenece_software": true,
  "justificacion_software": "CARRERA: CARRERA DE SOFTWARE",
  "campos_vacios": ["FECHA", "DEPARTAMENTO", "LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA"],
  "campos_localizados": 23,
  "checklist": [
    {"numero_elemento": 1, "descripcion": "A. INFORMACIÓN DE LA GUÍA", "cumple": true, "tipo_fallo": null,
     "justificacion": "La sección A. INFORMACIÓN DE LA GUÍA existe con sus campos de identificación, aunque algunos campos como la fecha y el departamento están sin llenar."},
    {"numero_elemento": 2, "descripcion": "Planificación pedagógica", "cumple": true, "tipo_fallo": null,
     "justificacion": "La introducción, objetivos, actividades por desarrollar y resultados obtenidos son coherentes entre sí…"},
    {"numero_elemento": 3, "descripcion": "Recursos de la práctica", "cumple": true, "tipo_fallo": null, "justificacion": "…"}
  ],
  "veredicto": "CUMPLE PARCIALMENTE",
  "porcentaje_estimado": 100
}
```

Y el caso simétrico, la malla: el LLM **sí** marcó un incumplimiento
(`"cumple": false, "tipo_fallo": "AUSENTE"`), lo que baja el porcentaje a 60 y produce el
mismo veredicto por la otra rama:

```json
{
  "nombre_original": "malla_ingenierIa_de_software.pdf",
  "indicador_numero": 3,
  "checklist": [
    {"numero_elemento": 1, "descripcion": "Identificación institucional y de la carrera",
     "cumple": true,  "tipo_fallo": null,      "justificacion": "El documento menciona la carrera de Ingeniería de Software y la universidad"},
    {"numero_elemento": 2, "descripcion": "Identificación de niveles",
     "cumple": false, "tipo_fallo": "AUSENTE", "justificacion": "No consta en el documento: No se mencionan explícitamente los ocho períodos académicos"},
    {"numero_elemento": 3, "descripcion": "Distribución de asignaturas",
     "cumple": true,  "tipo_fallo": null,      "justificacion": "Se enumeran al menos diez asignaturas con código y nombre"}
  ],
  "veredicto": "CUMPLE PARCIALMENTE",
  "porcentaje_estimado": 60
}
```

---

## 4. Los cinco callbacks del chord

Cada lote cerró con `generar_reporte_ejecutivo`. Su JSON es la agregación del lote:

| Lote | Docs | Cumplen | Parciales | No cumplen | Sin plantilla | Errores | Tiempo |
|---|---|---|---|---|---|---|---|
| `LOTE_af9b5c18` | 5 | 2 | 0 | 2 | 1 | 0 | 0,016 s |
| `LOTE_c7625866` | 3 | 2 | 1 | 0 | 0 | 0 | 0,047 s |
| `LOTE_780912e4` | 2 | 0 | 1 | 1 | 0 | 0 | 0,015 s |
| `LOTE_a8e9ed37` | 1 | 1 | 0 | 0 | 0 | 0 | 0,015 s |
| `LOTE_78c9d91e` | 1 | 1 | 0 | 0 | 0 | 0 | 0,015 s |

```json
{
  "reporte_ejecutivo": "./Auditoria_CACES\\Reportes_Ejecutivos\\Reporte_Ejecutivo_LOTE_af9b5c18.pdf",
  "estadisticas": {"total": 5, "cumplen": 2, "parciales": 0, "no_cumplen": 2,
                   "sin_plantilla": 1, "pendientes": 0, "errores": 0}
}
```

El callback tarda **15–47 ms**: la consolidación es gratis comparada con la auditoría. Todo el
coste del lote está en las tareas paralelas, que es exactamente lo que justifica el `chord`.

---

## 5. Lo que este log sirve como evidencia (y lo que no)

**Sirve para:**

- **Ahorro por compuertas.** 4 de 12 documentos (33 %) cortados sin llamada al LLM. El corte por
  plantilla vacía costó 1,23 s frente a los ~4,6 s de un documento equivalente que sí llega al
  modelo: **73 % menos de tiempo** y cero tokens.
- **Enrutador barato.** 11 de 12 por palabras clave (91,7 %); una sola llamada de embeddings en
  todo el log.
- **El LLM no decide el veredicto.** El caso 8 (checklist 100 % → CUMPLE PARCIALMENTE) lo
  demuestra en una sola línea de log.
- **Recorte del Indicador 2.** `333 218 ch → 18 731 ch` (5,6 %) en el proyecto curricular, y aun
  así CUMPLE al 80 %. Sin el recorte, ese documento solo agota la cuota diaria.
- **Reconstrucción geométrica de la malla.** `Reconstruidas 44 asignaturas`, que coincide con las
  44 asignaturas del ground truth de `completitud_malla.py`.
- **Coste de los extremos.** El más rápido, 1,23 s (compuerta 4); el más lento, 16,31 s
  (proyecto curricular, con extracción de 113 páginas + recorte + LLM).

**No sirve para:**

- Medir exactitud: no hay ground truth de veredicto asociado a estos 12 documentos.
- Hablar de concurrencia: el worker corrió con `--pool=solo`, es decir, **las tareas se
  ejecutaron en serie**, no en paralelo. El `chord` estaba activo, pero este log no demuestra
  throughput. Para la prueba 4 de la Tabla 9 (ráfagas de 20 documentos) hace falta relanzarlo
  con un pool concurrente.
- Reproducibilidad: cada documento se corrió una vez, no `k=5`.

---

## 6. Ruido que conviene silenciar antes de capturar el log para la tesis

`sylabus-nosylabus.pdf` generó 12 líneas de
`Could not get FontBBox from font descriptor because None cannot be parsed as 4 floats`.
Es un aviso de pdfminer sobre una fuente mal declarada en el PDF, **no un error del sistema**:
la extracción terminó bien. Si el log va a ir como figura al Capítulo IV, conviene filtrar ese
`WARNING` para que no parezca un fallo.
