# Las compuertas Pre-LLM, una por una: qué recibe, cómo decide, qué devuelve

Ejemplos reales tomados del log del worker del **2026-08-04 (23:25–23:30)**, del código de
`backend/services/tareas_ia.py` y de las cabeceras de máquina de
`backend/data/caces_2024_oficial.txt`.

> **Precisión necesaria antes de empezar.** Las compuertas **no reciben JSON**. Reciben valores
> de Python que produce la extracción: `texto` (str), `cajas` (lista de cajas con coordenadas) y
> `meta` (dict de metadatos de la base de oro). El JSON aparece **a la salida**: es el dict
> `resultado` (`_resultado`, `tareas_ia.py:445`) que se serializa a Redis y llega al frontend.
> Aquí la entrada se muestra en forma de JSON sólo para poder leerla; en el proceso real no lo es.

Orden de ejecución dentro de `auditar_documento_pesado` (`tareas_ia.py:490`):

```
PDF → C0 legibilidad → C1 léxico → [enrutado + RAG] → C2 plantilla
    → C3 pertinencia → C4 plantilla vacía → LLM → Etapa 3 veredicto
```

Toda compuerta que corta hace lo mismo: construye el `resultado` con
`veredicto` ya decidido y `checklist: []`, y lo pasa por `cerrar()`, que **enruta el PDF a su
carpeta física** y borra el temporal. Un documento cortado **sí se archiva y sí genera reporte**;
lo que no hace es consumir una llamada al modelo.

---

## C0 · Legibilidad del PDF

**Dónde:** `tareas_ia.py:504`. **Qué ejecuta:** `extraer_documento(ruta_pdf)`.

### Qué recibe

La ruta del temporal. Nada más. Es la única compuerta anterior a que exista texto.

```python
documento = extraer_documento(ruta_pdf)   # {"texto", "cajas", "ocr", "es_malla"}
```

Dentro, si el PDF trae menos de `UMBRAL_CAPA_TEXTO = 200` caracteres, cae al respaldo **OCR
`hi_res`** (Tesseract). Si ni así se puede leer, lanza excepción.

### Cómo actúa

```python
except Exception as error_extraccion:
    return cerrar(_resultado(nombre_original, veredicto="ERROR_LECTURA",
                             plantilla_valida=False, pertenece_software=False, ...))
```

**No se reintenta**: un PDF corrupto lo seguirá estando, y reintentar sólo gasta tiempo del
worker.

### JSON de salida

> ⚠️ **No hay ejemplo observado en el log del 04-08.** Los 12 documentos se extrajeron sin
> error. La forma de la salida se deriva del código, y hay que presentarla como tal —no como
> resultado medido—.

```json
{
  "nombre_original": "<archivo>.pdf",
  "indicador_evaluado": "Desconocido",
  "indicador_numero": null,
  "enrutado_por": null,
  "plantilla_valida": false,
  "pertenece_software": false,
  "campos_vacios": [],
  "campos_localizados": 0,
  "checklist": [],
  "veredicto": "ERROR_LECTURA",
  "porcentaje_estimado": 0,
  "justificacion": "<mensaje de la excepción>",
  "analisis_libre": "El PDF no pudo leerse: está corrupto, protegido, o es un escaneo sin capa de texto."
}
```

**Destino físico:** `99_Descarte_Errores`, **sin** reporte PDF individual — un error de lectura
no es un juicio de cumplimiento y no debe entrar en las estadísticas de auditoría.

### Lo que sí prueba el log

`sylabus-nosylabus.pdf` disparó 12 avisos
`Could not get FontBBox from font descriptor…` y **aun así se extrajo bien**. Es la prueba de
que un PDF con fuentes mal declaradas no cae por C0: pdfminer avisa y continúa.

---

## C1 · Rechazo léxico

**Dónde:** `tareas_ia.py:517`.

### Qué recibe

El `texto` extraído, y una tupla fija de **33 palabras** del vocabulario académico
(`PALABRAS_ACADEMICAS`, `:126`):

```
universidad · instituto · sílabo · syllabus · caces · asignatura · evaluación · carrera ·
educación · estudiante · aprendizaje · perfil · malla · facultad · currículo · proyecto ·
profesional · metodología · recursos · portafolio · prácticas · laboratorio · escenario ·
tecnología · virtual · afinidad · posgrado · titular · nombramiento · concurso · desempeño ·
docente · académico
```

### Cómo actúa

```python
coincidencias = sum(1 for p in PALABRAS_ACADEMICAS if p in texto.lower())
if coincidencias < 2:
    ...  veredicto="PLANTILLA NO RECONOCIDA"
```

Cuenta **cuántas palabras distintas** de la lista aparecen, no cuántas veces. El umbral es 2, no
1: una sola coincidencia puede ser casual (un recibo que dice "universidad" en la dirección).

Es la compuerta **más barata de todas**: una comprobación de subcadenas sobre texto ya en
memoria, antes de abrir ChromaDB. Un PDF que no es académico se descarta sin tocar ninguna base
de datos ni ninguna API.

### Ejemplo que pasa (real)

`pepinillo.pdf` — el nombre no dice nada, pero el contenido es un sílabo. Supera C1 sin
problema y llega hasta el final: **CUMPLE 89 %**. Es el ejemplo que demuestra que
**el nombre del archivo no se usa para decidir nada**: un sílabo llamado "pepinillo" se audita
igual, y si aprueba se renombra al formato oficial a partir de sus propios campos
(`Silabo_NRC-26429_CONSTRUCCION_Y_EVOLUCION_DEL_S_MONTALUISA_PILATASIG_EDGAR_FABIAN`).

### JSON de salida al cortar

> ⚠️ Tampoco hay ejemplo observado en este log. Forma derivada del código:

```json
{
  "plantilla_valida": false,
  "pertenece_software": false,
  "checklist": [],
  "veredicto": "PLANTILLA NO RECONOCIDA",
  "porcentaje_estimado": 0,
  "justificacion": "Sólo 1 palabra(s) del vocabulario académico.",
  "analisis_libre": "Rechazo automático: el documento no es académico. Se abortó el análisis con IA para no consumir recursos."
}
```

**Para la tesis:** si quieres evidencia medida de C1, sube un PDF no académico (una factura, un
recibo) y captura el log. Es una prueba de 2 segundos y cierra el hueco.

---

## Entre C1 y C2 · El enrutado (no corta, pero decide)

**Dónde:** `_recuperar_norma`, `tareas_ia.py:270`.

No es una compuerta —ningún documento se rechaza aquí— pero determina **contra qué norma** se
juzgará todo lo que viene después. Tres vías, en orden:

| Vía | Qué hace | Coste | En el log |
|---|---|---|---|
| `palabras_clave` | Busca los titulares de `MAPEO_INDICADORES` en los primeros **1 500 ch** | 0 llamadas | **11 de 12** |
| `palabras_clave_cuerpo` | Repite la búsqueda en **todo** el texto | 0 llamadas | 0 |
| `similitud` | `similarity_search(texto[:1000], k=1, filter={"tipo":"norma"})` | **1 llamada de embeddings** | **1 de 12** |

Si acierta una de las dos primeras, la norma se lee **por metadato exacto**
(`vector_db.get(where={"indicador": N})`): no hay recuperación difusa que pueda equivocarse.

### Ejemplo real de la rama barata

```
-> [CELERY] Indicador 4: Syllabus (palabras_clave) | norma 1919 ch | documento 10688 ch | campos vacíos 0/20
```

El documento contiene `PROGRAMA DE ASIGNATURA` en su titular → Indicador 4 directo.

### Ejemplo real de la rama de respaldo

`sylabus-nosylabus.pdf` no tiene ningún titular reconocible. Cae a similitud, se gasta
**un POST a `gemini-embedding-001:batchEmbedContents`**, y el vecino más próximo resulta ser el
Indicador 2 (proyecto curricular) — **un enrutado equivocado** para un archivo cuyo nombre
sugiere sílabo. La compuerta C2 lo cortó igualmente.

> Esto es defensa en profundidad y conviene contarlo así: el enrutador falló y el sistema no
> produjo un dictamen erróneo, porque la compuerta siguiente no depende de él. Pero es un fallo
> real del enrutador y debe aparecer en la matriz de confusión, no esconderse.

---

## C2 · Plantilla oficial

**Dónde:** `_plantilla_valida`, `tareas_ia.py:219`.

### Qué recibe

El `texto` y el campo `MARCADORES` de los metadatos del indicador al que enrutó. Los marcadores
**reales** de la base de oro:

| Ind. | `MARCADORES` |
|---|---|
| 1 | `PERFIL DE EGRESO|PERFIL EGRESO|PERFIL DEL EGRESADO|PERFIL EGRESADO|PERFIL PROFESIONAL` |
| 2 | `Datos generales de la carrera; Carrera a rediseñar|Tipo de trámite; Descripción microcurricular` |
| 3 | `MALLA CURRICULAR` |
| 4 | `PROGRAMA DE ASIGNATURA - SÍLABO; SGC.DI.321` |
| 6 | `GUIA DE USO DE LABORATORIO; A. INFORMACIÓN DE LA GUÍA` |

Gramática: **`;` separa obligatorios** (todos deben estar), **`|` separa alternativos** (basta
uno). El Indicador 2 exige por tanto **tres** cosas a la vez, y una de ellas admite dos
redacciones.

### Cómo actúa

```python
documento = comparable(texto)           # sin tildes, sin guiones, sin separador de celdas
for grupo in marcadores.split(";"):
    alternativas = [a.strip() for a in grupo.split("|") if a.strip()]
    if alternativas and not any(comparable(a) in documento for a in alternativas):
        faltan.append(" o ".join(alternativas))
return (not faltan), faltan
```

La comparación **no es literal**: se hace sobre la forma canónica. Un marcador partido en dos
cajas del PDF (`PROGRAMA DE ASIGNA` + `TURA - SÍLABO`) no debe tumbar un documento válido.

Si el indicador no declara marcadores (`MARCADORES` vacío), devuelve `True, []`: **no se puede
rechazar por una plantilla que no está definida**.

### Ejemplo real que corta

`sylabus-nosylabus.pdf`, enrutado al Indicador 2, al que le faltan los tres marcadores:

```
-> [CELERY] Plantilla no reconocida (faltan: ['Datos generales de la carrera',
   'Carrera a rediseñar o Tipo de trámite', 'Descripción microcurricular']). Sin llamada al LLM.
```

Nótese `'Carrera a rediseñar o Tipo de trámite'`: el `" o "` lo escribe el propio código al unir
las alternativas, así que el mensaje dice con exactitud qué habría bastado.

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

**Firma de esta compuerta:** `plantilla_valida: false` **y** `pertenece_software: null`. Ese
`null` es informativo: la pertinencia **nunca llegó a evaluarse**, porque C3 va después. Es
distinto de `false`, que significaría "se evaluó y no pertenece".

**Destino físico:** `12_Plantilla_No_Reconocida`, **con** reporte PDF.

### Ejemplo real que pasa

`silabus_trampa_20260702_105222.pdf` — está **completamente en blanco**, pero conserva el
membrete `PROGRAMA DE ASIGNATURA - SÍLABO` y `SGC.DI.321`. **Supera C2**, y con razón: la
plantilla *es* la oficial. Su problema es otro, y lo detectará C4. Esta separación —"documento
equivocado" ≠ "documento correcto mal llenado"— es deliberada y es la que permite dar un
diagnóstico útil al docente.

---

## C3 · Pertinencia a la carrera de Software

**Dónde:** `_pertinencia`, `tareas_ia.py:191`.

### Qué recibe

`texto` y `cajas`. Es la primera compuerta que usa **coordenadas**: resuelve etiqueta→valor
sobre las cajas del PDF.

```python
campos = resolver_campos(cajas, ["CARRERA", "Nombre Asignatura", "ASIGNATURA"])
```

### Cómo actúa — cuatro vías en cascada

| Orden | Vía | Devuelve | Ejemplo real del log |
|---|---|---|---|
| 1 | Campo `CARRERA` por coordenadas, o regex `carrera\s*:\s*(…)` en el texto | `True`/`False` + `CARRERA: <valor>` | guías (`CARRERA: CARRERA DE SOFTWARE`) y `MALLA-EDUCACION-INICIAL` |
| 2 | `Nombre Asignatura` contrastado contra `asignaturas_malla.txt` | `True`/`False` + la asignatura de la malla | `Silabo_NRC-21278` y `202650_SI_LIDERAZGO` |
| 3 | Mención de "carrera de software" / "ingeniería de software" en el texto normalizado | `True` | `malla_ingenierIa_de_software.pdf`, `PERFILEGRESO_SW` |
| 4 | Nada de lo anterior | **`None`** (indeterminado) | `silabus_trampa` |

La vía 2 admite abreviaturas y truncados, que es como los sílabos escriben de verdad:

```python
# "APL. BASADAS EN EL CONOCIMIENT" debe casar con "Aplicaciones Basadas en el Conocimiento"
if all(any(c.startswith(f) for c in candidatas) for f in fichas):
```

Cada palabra significativa del sílabo debe ser **el principio** de alguna palabra de la
asignatura de la malla. Por eso `CONOCIMIENT` casa con `Conocimiento`.

### Ejemplo real que pasa por la vía 2

```json
{
  "nombre_original": "Silabo_NRC-21278_ABC_José_Carrillo_SI_VI_Software_202550-signed-signed.pdf",
  "pertenece_software": true,
  "justificacion_software": "Nombre Asignatura: APL. BASADAS EN EL CONOCIMIENT (consta en la malla como «Aplicaciones Basadas en el Conocimiento»)"
}
```

La justificación **cita el dato exacto y la asignatura con la que casó**. Un evaluador humano
puede verificarlo abriendo la malla. Eso es lo que hace auditable la decisión.

### Ejemplo real que corta por la vía 2

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

> **Detalle que hay que saber explicar.** El valor leído es `"CÓDIGO ASIGNATURA"`, que es una
> **etiqueta** de la plantilla, no un nombre de asignatura: el resolvedor por coordenadas cogió
> la celda equivocada en ese PDF. La conclusión (no es de Software) resultó correcta —el
> archivo se llama `SI_LIDERAZGO`, es de Sistemas de Información— pero **por el motivo
> equivocado**. Si te preguntan por este caso en la defensa, no lo defiendas como acierto
> limpio: es un acierto con una lectura defectuosa detrás, y da la pista de dónde mejorar el
> resolvedor.

### Ejemplo real que corta por la vía 1

```json
{
  "nombre_original": "MALLA-EDUCACION-INICIAL-EN-LINEA.pdf",
  "indicador_evaluado": "Indicador 3: Malla curricular",
  "plantilla_valida": true,
  "pertenece_software": false,
  "justificacion_software": "CARRERA: EDUCACIÓN INICIAL MODALIDAD EN LÍNEA UCE, UFA - ESPE, UTN, U",
  "veredicto": "NO CUMPLE",
  "porcentaje_estimado": 0
}
```

Cortó en **2,09 s**. Una malla ajena es un documento grande cuya reconstrucción geométrica
completa habría costado mucho más; C3 la para antes.

### El caso `None`: lo que NO corta

`silabus_trampa` está en blanco, así que no hay `CARRERA` ni `Nombre Asignatura` que leer, y el
texto no menciona "software". `_pertinencia` devuelve `(None, "No se pudo determinar la carrera
a partir del documento")`. La condición de corte es:

```python
if pertenece is False:      # None NO entra aquí
```

Así que **no corta**: no se rechaza un documento por no haber podido leer un campo. El documento
sigue vivo hasta C4, que sí lo tumba.

**Destino físico de un corte por C3:** `11_Documentos_Rechazados`, con reporte.

---

## C4 · Plantilla oficial mayoritariamente vacía

**Dónde:** `_campos_sin_llenar` (`:246`) + `_plantilla_vacia` (`:238`).

### Qué recibe

`cajas` y el campo `CAMPOS` de los metadatos. Los **reales**:

| Ind. | `CAMPOS` | Nº |
|---|---|---|
| 1 | *(vacío)* | 0 |
| 2 | *(vacío)* | 0 |
| 3 | *(vacío)* | 0 |
| 4 | `Modalidad; Departamento; Área de Conocimiento; Nombre Asignatura; Período Académico; Código; NRC; Nivel; Docente; Sesiones Semanales; carga horaria: DOCENCIA; carga horaria: PRACTICAS…; carga horaria: APRENDIZAJE AUTÓNOMO; Descripción de la Asignatura; Contribución…; Resultado de Aprendizaje de la Carrera; Objetivo…; Resultado de Aprendizaje de la Asignatura; Proyecto Integrador; Perfil sugerido del docente` | **20** |
| 6 | `FECHA; DEPARTAMENTO; CARRERA; ASIGNATURA; PERIODO; NIVEL; DOCENTE; NRC; PRÁCTICA No; LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA; TEMA…; NUMERO DE HORAS; INTRODUCCIÓN; OBJETIVOS; EQUIPOS; MATERIALES E INSUMOS; REACTIVOS; MUESTRA / OTROS; PRECAUCIONES…; ACTIVIDADES POR DESARROLLAR; RESULTADOS OBTENIDOS; CONCLUSIONES; RECOMENDACIONES` | **23** |

**Consecuencia estructural:** los indicadores 1, 2 y 3 no declaran campos, así que
`_campos_sin_llenar` devuelve `([], 0)` y **C4 no puede dispararse nunca para ellos**. En el log
se ve literalmente: `campos vacíos 0/0` en la malla, el perfil y el proyecto curricular. No es un
fallo: son documentos narrativos sin formulario que rellenar.

### Cómo actúa

```python
def _campos_sin_llenar(cajas, campos):
    resueltos = resolver_campos(cajas, nombres)      # sólo los que se localizan
    vacios = [n for n, v in resueltos.items() if not v]
    return vacios, len(resueltos)

def _plantilla_vacia(vacios, localizados):
    return localizados >= 4 and len(vacios) > localizados / 2
```

Dos decisiones deliberadas:

1. **Un campo cuya etiqueta no aparece no se cuenta.** El denominador es "campos localizados",
   no "campos que la norma declara". De un campo que no está no se puede afirmar que esté vacío.
2. **Muestra mínima de 4.** Con uno o dos campos localizados, que estén vacíos no basta para
   tumbar el documento: probablemente el fallo es del resolvedor, no del documento.

Y un detalle que sale en el ground truth: `"No aplica"`, `"NA"` o `"-"` cuentan como **lleno**.
El campo se contestó.

### Ejemplo real que corta

```
-> [CELERY] Plantilla vacía (20/20). Sin llamada al LLM.
```

`20 >= 4` ✔ y `20 > 10` ✔ → corta. Tiempo total: **1,23 s**, el más rápido de los 12 documentos
y una cuarta parte de lo que tarda un sílabo equivalente que sí llega al LLM (≈ 4,6 s).

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
  "analisis_libre": "El documento usa la plantilla oficial pero está mayoritariamente en blanco. No constituye evidencia: hay que llenarlo antes de auditarlo."
}
```

> ⚠️ **`pertenece_software: true` aquí no significa "es de Software".** `_pertinencia` devolvió
> `None`, y la línea `pertenece_software=(pertenece is not False)` (`:561`) convierte el
> indeterminado en `true`. Significa **"no se pudo descartar"**. La lógica es correcta; el nombre
> del campo induce a error a quien lea el JSON en frío. Si alguien del tribunal lo señala, la
> respuesta honesta es esa, no defender que se verificó.

### Ejemplo real que NO corta

`3.3 Guia Laboratorio ABC…` tiene **3 de 23** campos vacíos:

```
localizados = 23 >= 4          ✔
3 > 23/2 = 11.5                ✘  → no corta
```

Sigue al LLM. Pero los tres campos vacíos **no se olvidan**: viajan en el `resultado` y reaparecen
en la Etapa 3, donde degradan el veredicto. Ver abajo.

**Destino físico de un corte por C4:** `11_Documentos_Rechazados`, con reporte.

---

## Etapa 3 · El veredicto (después del LLM)

**Dónde:** `_calcular_veredicto`, `tareas_ia.py:378`. No es una compuerta Pre-LLM, pero es donde
se toma la decisión final — **y no la toma el modelo**.

### Qué recibe

El `resultado` ya montado: los hechos de la Capa 1 **más** el `checklist` que devolvió el LLM.

```python
if not resultado["plantilla_valida"]:       return 0, "PLANTILLA NO RECONOCIDA"
if resultado["pertenece_software"] is False: return 0, "NO CUMPLE"
if not checklist:                            return 0, "ERROR_SIN_CHECKLIST"

porcentaje = round(cumplidos / len(checklist) * 100)
if _plantilla_vacia(vacios, localizados):   return porcentaje, "NO CUMPLE"
if porcentaje <= 50:                        return porcentaje, "NO CUMPLE"
if porcentaje >= 70 and not vacios:         return porcentaje, "CUMPLE"
return porcentaje, "CUMPLE PARCIALMENTE"
```

Las tres primeras líneas son **redundantes a propósito**: esos casos ya cortaron antes. Están
porque `_calcular_veredicto` debe ser correcta por sí sola, sin depender del orden de las
compuertas que la preceden.

### Las tres ramas, con ejemplo real de cada una

| Documento | % | vacíos | Rama | Veredicto |
|---|---|---|---|---|
| `pepinillo.pdf` | 89 | 0 | `>=70 and not vacios` | **CUMPLE** |
| `3.3 Guia Laboratorio…` | **100** | **3** | `>=70` pero `vacios` no vacío → else | **CUMPLE PARCIALMENTE** |
| `malla_ingenieria_de_software.pdf` | **60** | 0 | `>50` y `<70` → else | **CUMPLE PARCIALMENTE** |

**El caso de la guía 3.3 es la mejor evidencia del log.** El LLM aprobó los 3 elementos
fundamentales —100 %— y aun así el sistema **degradó el veredicto**, porque C4 había registrado
`FECHA`, `DEPARTAMENTO` y `LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA` en blanco:

```json
{
  "campos_vacios": ["FECHA", "DEPARTAMENTO", "LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA"],
  "campos_localizados": 23,
  "checklist": [
    {"numero_elemento": 1, "cumple": true, "tipo_fallo": null, "descripcion": "A. INFORMACIÓN DE LA GUÍA"},
    {"numero_elemento": 2, "cumple": true, "tipo_fallo": null, "descripcion": "Planificación pedagógica"},
    {"numero_elemento": 3, "cumple": true, "tipo_fallo": null, "descripcion": "Recursos de la práctica"}
  ],
  "veredicto": "CUMPLE PARCIALMENTE",
  "porcentaje_estimado": 100
}
```

Frase para la defensa: *«el modelo dio 100 %; el sistema dijo CUMPLE PARCIALMENTE. La última
palabra la tiene el código, y la razón está escrita en el propio dictamen»*.

Y el caso simétrico, la malla, donde el corte viene **del propio LLM**:

```json
{
  "checklist": [
    {"numero_elemento": 2, "descripcion": "Identificación de niveles", "cumple": false,
     "tipo_fallo": "AUSENTE",
     "justificacion": "No consta en el documento: No se mencionan explícitamente los ocho períodos académicos"}
  ],
  "veredicto": "CUMPLE PARCIALMENTE",
  "porcentaje_estimado": 60
}
```

El `tipo_fallo: "AUSENTE"` lo impone el esquema Pydantic (`ElementoChecklist`, `:60`), que
**obliga** al modelo a distinguir "no lo trata" de "lo trata y se queda corto", y un validador
garantiza que ningún `cumple: false` llegue al reporte sin justificación legible.

---

## Resumen: la firma JSON de cada compuerta

Cómo distinguir, mirando sólo el JSON, qué compuerta resolvió un documento:

| Compuerta | `veredicto` | `plantilla_valida` | `pertenece_software` | `campos_localizados` | `checklist` |
|---|---|---|---|---|---|
| C0 legibilidad | `ERROR_LECTURA` | `false` | `false` | 0 | `[]` |
| C1 léxico | `PLANTILLA NO RECONOCIDA` | `false` | `false` | 0 | `[]` |
| C2 plantilla | `PLANTILLA NO RECONOCIDA` | `false` | **`null`** | 0 | `[]` |
| C3 pertinencia | `NO CUMPLE` | **`true`** | `false` | 0 | `[]` |
| C4 vacía | `NO CUMPLE` | `true` | `true`/`null` | **> 0** | `[]` |
| Etapa 3 | CUMPLE / PARCIAL / NO CUMPLE | `true` | `true` | ≥ 0 | **poblado** |

La regla de oro: **`checklist: []` ⇔ el LLM no se invocó**. Es la marca inequívoca de que una
compuerta Pre-LLM resolvió el documento, y es lo que hace contable el ahorro.

Las dos únicas parejas ambiguas se separan por un campo:

- C1 vs C2 → C1 deja `pertenece_software: false`; C2 lo deja `null` (nunca se evaluó).
- C3 vs C4 → C3 deja `campos_localizados: 0`; C4 lo deja `> 0` con `campos_vacios` poblado.
