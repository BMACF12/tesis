# Indicadores CACES y cómo se evalúan

La normativa vive en `backend/data/caces_2024_oficial.txt` ("Base de Oro"), un bloque por
indicador. Cada bloque tiene **dos partes** (ver cabecera del propio archivo):

- **Cabecera de máquina** (`ESTADO`, `MARCADORES`, `CAMPOS`): la lee `crear_base_oro.py` y la
  guarda como metadatos. **No se envía al LLM.** El código la usa para comprobar de forma
  determinista la plantilla y qué campos están sin llenar.
- **Criterio** (`ESTÁNDAR`, `ELEMENTOS FUNDAMENTALES`, notas): es **lo único que ve el LLM**.

Este documento explica el diseño; **el archivo es la fuente**. El sistema separa hechos
(código) de juicio (LLM): ver `ARQUITECTURA.md`.

## Jerarquía CACES

`DIMENSIÓN → ESTÁNDAR → ELEMENTOS FUNDAMENTALES`. La dimensión de todos los indicadores
instrumentados es **Currículo**.

## Estado por indicador

El valor de `ESTADO` en el `.txt` es el que manda:

| # | Indicador | `ESTADO` | Marcadores de plantilla | Plantilla / documento |
|---|---|---|---|---|
| 1 | Perfil de egreso | `SEMANTICO` | `PERFIL DE EGRESO\|PERFIL EGRESO\|PERFIL DEL EGRESADO\|PERFIL EGRESADO\|PERFIL PROFESIONAL` | sin campos; sólo juicio semántico |
| 2 | Proyecto curricular | `INSTRUMENTADO` (estructural) | `Datos generales de la carrera; Carrera a rediseñar\|Tipo de trámite; Descripción microcurricular` | formulario de rediseño SENESCYT/CES (decenas de páginas); sin campos por coordenadas, secciones ancladas por ANCLA |
| 3 | Malla curricular | `INSTRUMENTADO` | `MALLA CURRICULAR` | diagrama apaisado 1 página |
| 4 | Syllabus | `INSTRUMENTADO` | `PROGRAMA DE ASIGNATURA - SÍLABO; SGC.DI.321` | plantilla `SGC.DI.321` (6 páginas) |
| 6 | Escenarios de prácticas | `INSTRUMENTADO` | `GUIA DE USO DE LABORATORIO; A. INFORMACIÓN DE LA GUÍA` | "GUIA DE USO DE LABORATORIO" |

`ESTADO: SEMANTICO` (sólo el 1) significa que **no hay campos que verificar de forma
determinista**: sus 5 elementos son todos `[SEMÁNTICO]` y quien dictamina es el LLM. Sigue **sin
contar como indicador instrumentado** (se reporta "3 instrumentados de 5"; ver
`CONTEXTO_TESIS.md`): lo que hay es plantilla por marcadores y una **línea base léxica**
reproducible (`scripts/completitud_perfil.py`), no una verificación. Ver la nota del indicador
más abajo.

El Indicador 2 pasó de `SEMANTICO` a **`INSTRUMENTADO` estructural**: sigue **sin campos por
coordenadas** (`CAMPOS:` vacío, no hay veto de campos vacíos), pero ahora **sí comprueba la
plantilla por MARCADORES** y **ancla 3 de sus 5 elementos a secciones literales del documento**
(elementos 2, 3 y 4 con `ANCLA`; los elementos 1 y 5 siguen siendo puro juicio `[SEMÁNTICO]`).
El rechazo de proyectos de otra carrera lo hace la pertinencia (`CARRERA: SOFTWARE`), no los
marcadores. Ver la nota del indicador más abajo.

## Principios del diseño (por qué el archivo es como es)

1. **La "integridad del documento" NO es un elemento del checklist.** En la versión original
   valía 1/n (una guía sin firmar salía CUMPLE al 75%). Hoy es un **veto determinista en
   código**, no una regla del prompt: `_calcular_veredicto` (`tareas_ia.py:303`) fuerza
   `NO CUMPLE` si la plantilla oficial está mayoritariamente en blanco, y `PLANTILLA NO
   RECONOCIDA` si faltan los marcadores.
2. **Cada elemento se marca `[ESTRUCTURAL]` o `[SEMÁNTICO]`.** Lo evalúa el **LLM** según la
   Regla 3 del `.txt`:
   - Estructural → la sección debe existir con su encabezado literal (`ANCLA: "..."`).
   - Semántico → equivalencia de propósito, sin exigir las palabras exactas.
3. **Marcadores de plantilla** (`MARCADORES`) por indicador, separados por `;` (todos
   obligatorios) o `|` (alternativos). Los comprueba el **código** (`_plantilla_valida`,
   `tareas_ia.py:161`) sobre la forma canónica del texto. Si no aparecen → `PLANTILLA NO
   RECONOCIDA` (clase propia, distinta de NO CUMPLE), sin llamar al LLM.
4. **Una sola lista `CAMPOS` de etiquetas obligatorias** por indicador (no hay niveles
   "obligatorio/secundario"). El código las localiza por coordenadas (`_campos_sin_llenar`,
   `:188`) y decide de forma determinista:
   - Plantilla oficial mayoritariamente en blanco (`_plantilla_vacia`, `:180`) → `NO CUMPLE`.
   - Cualquier campo localizado vacío → tope en `CUMPLE PARCIALMENTE` (no puede llegar a CUMPLE).
   - `%` del checklist ≤50 → `NO CUMPLE`; ≥70 y sin campos vacíos → `CUMPLE`; resto → `PARCIAL`.
5. **Anti-falsos-positivos (implementado):** un campo cuyo valor sea `No aplica`, `NA` o `N/A`
   **está lleno** (es una respuesta), tanto en el código como en la cabecera del `.txt`. En la
   malla, `N/A` y `NIVELACION` en prerrequisito son válidos.

## Notas por indicador

### Indicador 1 — Perfil de egreso

- **Documento:** prosa, no formulario. No hay etiqueta→valor que resolver por coordenadas: por
  eso `CAMPOS:` va vacío y el `ESTADO` sigue siendo `SEMANTICO`. Sus 5 elementos son todos
  `[SEMÁNTICO]`.
- **Corpus real (4 PDFs)**, en `INDICADORES PRUEBAS\INDICADOR 1 Perfil de egreso\`:
  `Perfil del Egresado prueba_*.pdf` (1.371 chars, **documento base aprobado**),
  `PERFILEGRESO_SW_*.pdf` (7.148), `informacion_carrera_isoj_ltga.pdf` (11.251) y
  `ejemplo_malo (2)_*.pdf` (221, basura de control).
- **Bug corregido (marcadores):** los `MARCADORES` sólo contemplaban
  `PERFIL DE EGRESO|PERFIL EGRESO|PERFIL PROFESIONAL`, pero el **documento base aprobado se
  titula literalmente "Perfil del Egresado"**. `comparable("perfil del egresado")` no contiene
  ninguna de las tres formas, así que el sistema **rechazaba su propio documento de referencia**
  como `PLANTILLA NO RECONOCIDA`, sin llegar a llamar al LLM. Se añadieron `PERFIL DEL EGRESADO`
  y `PERFIL EGRESADO` a la base de oro (`caces_2024_oficial.txt`, INDICADOR 1) y a
  `MAPEO_INDICADORES` (`tareas_ia.py`). Hacen falta **las dos**: `PERFIL DEL EGRESADO` no
  contiene `PERFIL EGRESADO` (el "del" está en medio).
  - **Pendiente de operación:** el cambio en el `.txt` **no surte efecto hasta regenerar Chroma**
    con `python scripts/crear_base_oro.py` (los marcadores viven en los metadatos del vector).
  - **Sin regresión de enrutado:** verificado sobre los 43 PDFs del corpus completo — ningún
    sílabo, malla, guía ni proyecto se enruta al 1 por las nuevas variantes. El orden de
    `MAPEO_INDICADORES` (4, 6, 2, 1, 3) se mantiene intacto: el 2 sigue evaluándose antes que el
    1 porque el proyecto curricular cita al perfil.
- **Bug corregido (estándar mutilado) — invalida los números anteriores de esta sección.** Al
  cotejar la base de oro con el modelo CACES oficial
  (`docs/conocimiento/formatos-caces/modelo_caces_generico_grado.txt`) se descubrió que el
  ESTÁNDAR del Indicador 1 estaba recortado y sus elementos mal transcritos:
  - **E3 medía un requisito INVENTADO.** El viejo E3 exigía saberes "redactados de forma
    observable" y lo comprobaba con un umbral de **3 verbos** de Bloom en infinitivo/futuro.
    **Ese requisito no existe en el CACES.** La norma dice, literal: *"Los saberes teóricos y
    prácticos declarados son verificables **y permiten alcanzar los resultados de aprendizaje
    establecidos en el perfil de egreso**"* — es un requisito de **coherencia (saberes → RA)**,
    no de estilo de redacción. El umbral y toda mención de "observable" están **eliminados**.
  - **La numeración estaba cruzada:** los viejos E3/E4 estaban intercambiados respecto a la
    norma. La numeración vigente es la de la base de oro: E1 RA en concordancia · E2 dominios ·
    **E3 participación de involucrados** · **E4 saberes verificables que permiten alcanzar los
    RA** · E5 seguimiento y evaluación → mejora continua.
- **Alcance (NOTA DE ALCANCE de la base de oro): la unidad de evidencia es el conjunto de
  fuentes a)–f), no una hoja suelta de perfil.** Los elementos **3 y 5 se evidencian en
  documentación SEPARADA** —fuente b) actas/informes/encuestas del aporte de expertos externos,
  organizaciones profesionales, empleadores y graduados; fuentes d) y f) políticas de
  seguimiento y acciones de mejora—, **no en el texto del perfil**. Un perfil no dice "me
  elaboraron con empleadores": eso lo dice el acta.
- **Instrumentación (línea base, NO verificación):**
  - `scripts/plantilla_perfil.py` — el esquema: los 5 elementos de la norma y, por cada uno, una
    familia léxica que delata que el documento habla de él (E1 resultados de aprendizaje;
    E2 dominios, ≥2 términos; **E3 actores externos ∧ participación**; **E4 saberes ∧ resultados
    de aprendizaje** = la coherencia que pide la norma; E5 seguimiento ∧ objeto curricular).
    E3, E4 y E5 exigen **co-ocurrencia** en 200 caracteres. Las familias de E4 se mantienen
    **disjuntas** a propósito: si "competencias" estuviera en las dos, la co-ocurrencia se
    dispararía sola y el elemento se regalaría.
  - **Falsos positivos bloqueados y medidos:** (1) el base dice que sus núcleos *"guardan
    relación con los lineamientos emitidos por … (acm-ieee)"* — eso es **alineación con un
    referente, no aporte de esa organización** a la elaboración, y **no acredita E3** (la NOTA
    DE ALCANCE lo prohíbe explícitamente); ni ACM, ni IEEE, ni "association"/"institute" están
    en la familia ACTORES, y sin un término de PARTICIPACIÓN cerca no se acredita nada.
    (2) `informacion_carrera` dice *"realizar el seguimiento y control de calidad del proyecto"*
    —función laboral del egresado, no mecanismo institucional—: la ventana de 200 caracteres lo
    bloquea (verificado: "no se refieren a lo mismo").
  - `scripts/completitud_perfil.py` — `J = |A∩B|/|A∪B|` con **A = los elementos evidenciables en
    el perfil {E1, E2, E4}** y B = los evidenciados. Modos: `--todos`, `--base` y `--faltan`.
    Sin ChromaDB y sin cuota.
  - **Es un PROXY LÉXICO, no un juicio.** Mide cobertura de evidencia, no comprensión, y es
    **asimétrico**: J bajo es indicio razonable de que el documento ni aborda el elemento; J alto
    **no acredita** nada. El juez real es el LLM en producción.
- **Por qué el denominador es 3 y no 5.** Si E3 y E5 se dejaran dentro de A, **ningún perfil
  suelto podría pasar de 3/5 jamás** y el Jaccard estaría midiendo *la ausencia de documentos
  que a ese PDF nunca se le pidieron* — el mismo error que el umbral de verbos: penalizar al
  documento por algo que no le toca. E3 y E5 quedan **fuera del cociente** y se reportan aparte
  nombrando la fuente ausente (*"requiere fuente b) — no evaluable sobre este documento"*).
  **No se cuentan como incumplidos en silencio:** un 3/5 así no diría "el perfil es mediocre",
  diría "no me diste el acta". Su detector léxico se ejecuta igual, pero **sólo como señal
  informativa** (un rastro léxico no es un acta).
- **Línea base medida (`--todos`, salida real):**

  | documento | chars | plantilla | elementos | J | sin evidencia | rastro fuente ext. |
  |---|---|---|---|---|---|---|
  | `PERFILEGRESO_SW_*` | 7.148 | ok | 3/3 | 1,000 | — | — |
  | `Perfil del Egresado prueba_*` (**base**) | 1.371 | ok | 3/3 | **1,000** | — | — |
  | `informacion_carrera_isoj_ltga` | 11.251 | ok | 3/3 | 1,000 | — | — |
  | `ejemplo_malo (2)_*` | 221 | **NO** | 0/3 | 0,000 | E1, E2, E4 | — |

  Media: 0,750 (4 documentos).
- **El viejo `J = 0,400` del documento base era un ARTEFACTO,** no un hallazgo. Se lo hundían
  dos cosas que la norma no pide: el umbral de 3 verbos observables (el base está escrito en
  prosa descriptiva — *"estos núcleos básicos articulan los saberes de la carrera…"*— y reunía
  sólo 2) y el contar E3/E5 como incumplidos cuando su evidencia vive en otras fuentes. Con la
  norma corregida el base evidencia **los 3 elementos que un perfil puede evidenciar**: E1 por
  "competencias necesarias", E2 por núcleos/saberes/campo profesional/disciplina, y E4 por la
  co-ocurrencia *núcleos + competencias declaradas* — que es exactamente la coherencia
  saberes → RA que pide la norma. Sigue siendo cierto (y se mantiene) que el base es,
  literalmente, la sección "Perfil del Egresado:" recortada de `informacion_carrera_isoj_ltga`.
- **E3 y E5 no dejan rastro léxico en NINGÚN documento del corpus** (ninguno contiene
  "empleador", "graduado", "encuesta" ni "mejora continua"). Eso **no** significa que la carrera
  no consulte a sus involucrados ni haga seguimiento: significa que **no se aportaron las
  fuentes b/d/f**, que es una afirmación sobre el expediente, no sobre el perfil.
- **Contraste con el juez real (LLM + norma corregida)** sobre el documento base:
  **60% CUMPLE PARCIALMENTE** — E1 ✓, E2 ✓, E3 ✗ (AUSENTE, fuente b no aportada), E4 ✓,
  E5 ✗ (AUSENTE, fuente d). **El proxy coincide elemento por elemento con el LLM en los 5.**
  Los números (1,000 vs 60%) difieren sólo por el **denominador**: el proxy divide entre los 3
  elementos evaluables sobre el perfil; el LLM dictamina sobre los 5 del expediente completo.
  Sobre el mismo denominador de 5, el proxy daría 3/5 = 60%: **el mismo valor**. Los dos números
  responden a preguntas distintas y **no deben compararse sin decir esto**.
- **`--base` (cada candidato vs el documento base aprobado):** `PERFILEGRESO_SW` 1,000,
  `informacion_carrera_isoj_ltga` 1,000, `ejemplo_malo` 0,000; media 0,667. Ojo: el base es la
  referencia de **esta carrera**, no el ideal de la norma; parecerse a él no acredita el
  indicador. Si `A ∪ B = ∅` se imprime **INDEFINIDO**, nunca 1,0 (mismo criterio que
  `jaccard.py`).
- **Limitación honesta:** con el denominador en 3 y familias léxicas amplias, los tres
  documentos reales saturan en 1,000 y la métrica **sólo discrimina la basura de control**. El
  proxy tampoco verifica la mitad semántica de E1 (que los RA estén *en concordancia* con el
  objeto de la carrera y el perfil profesional): eso es una relación entre dos textos que
  ninguna familia de palabras puede comprobar. Se detecta una condición **necesaria pero no
  suficiente**, y no se inventa un umbral para simular lo demás.

### Indicador 2 — Proyecto curricular
- **Documento:** el formulario oficial de **rediseño de carrera SENESCYT/CES** (el ejemplar de
  referencia aprobado es el de Ingeniería de Software - ESPE, ~113 páginas). Es mucho más grande
  y ruidoso que las plantillas de 1-6 páginas de los otros indicadores.
- **Marcadores** (todos obligatorios, `;`): `Datos generales de la carrera`,
  `Carrera a rediseñar|Tipo de trámite` (alternativos), `Descripción microcurricular`. Los tres
  identifican el *tipo* de formulario; ninguno aparece en sílabo/malla/guía. Los marcadores
  antiguos (`PROYECTO CURRICULAR|DISEÑO CURRICULAR|...`) **no existían en el documento real** y lo
  habrían rechazado como `PLANTILLA NO RECONOCIDA`.
- **Enrutado** (`MAPEO_INDICADORES`, `tareas_ia.py:70`): claves `CARRERA A REDISEÑAR`,
  `DATOS GENERALES DE LA CARRERA`, `DESCRIPCIÓN MICROCURRICULAR`. Las dos primeras caen dentro de
  los `texto[:1500]` que mira el enrutador; se evalúa **antes** que el 1 (perfil) y el 3 (malla),
  a los que el proyecto cita.
- **Pertinencia:** `_pertinencia` resuelve el campo `CARRERA` por coordenadas → `SOFTWARE`
  (verificado sobre el PDF real). Un rediseño de **otra carrera** trae el mismo formulario pero
  su `Carrera:` ≠ Software → `NO CUMPLE` por no pertinente. Doble defensa: marcadores (tipo) +
  pertinencia (carrera). Ojo: la etiqueta `Nombre completo de la carrera:` guarda un **código de
  registro** (`1079-5-...`), no el nombre; no es la que se lee para la pertinencia.
- **Elementos: son SEIS**, no cinco. La copia anterior de la base de oro tenía tres defectos
  graves que ya están **corregidos en el `.txt`** (y el código alineado con él):
  1. **Faltaba entero un elemento de la norma** — el actual E4 (académicos y profesionales con
     experiencia nacional e internacional involucrados en la conceptualización del proyecto).
  2. **Un elemento contaba dos veces.** Los viejos E3 (requisitos) y E4 (metodología e
     infraestructura) son en la norma **un solo elemento** — el actual E5, que los une con un
     *"así como"*. Partirlo hacía que el elemento **más fácil** (existen las secciones del
     formulario) pesara **2/5** del indicador.
  3. **Un elemento fundía dos.** El viejo E5 mezclaba *tener* políticas de actualización (actual
     E2) con *ejecutar* el seguimiento y evaluación (actual E6). Tener la política escrita no es
     ejecutarla: son dos elementos y dos fuentes distintas.

  Mapeo vigente (los **7 ANCLA se conservan**, verificados contra el PDF real; sólo se
  reasignaron de elemento):

  | # | clase | anclas |
  |---|---|---|
  | 1 | SEMÁNTICO | `Perfil de egreso`, `Misión` |
  | 2 | SEMÁNTICO | — (fuente b) |
  | 3 | ESTRUCTURAL | `Pertinencia` |
  | 4 | SEMÁNTICO | — (fuente d) |
  | 5 | ESTRUCTURAL | `Requisitos de ingreso`, `Requisitos de graduación`, `Metodología y ambientes de aprendizajes`, `Infraestructura y equipamiento` |
  | 6 | SEMÁNTICO | — (fuentes e y f) |
- **Alcance (NOTA DE ALCANCE del `.txt`):** la unidad de evidencia es el **conjunto de fuentes
  a)-f)**, no sólo el formulario. Los elementos **2, 4 y 6 se evidencian en documentos aparte**
  que el formulario no contiene (b: políticas de actualización; d: aporte de académicos al
  rediseño; e/f: lineamientos de seguimiento y acciones de mejora). Se marcan
  `ALCANCE_FUENTE_EXTERNA`, quedan **fuera del cociente** y se reportan aparte **nombrando la
  fuente ausente**, nunca como incumplidos en silencio — mismo criterio y misma nomenclatura que
  `plantilla_perfil.py` con los E3/E5 del Indicador 1. El **E1 es mixto**: entra en el cociente
  (sus dos secciones sí viven en el formulario), pero la coherencia con el **Modelo educativo**
  exige la fuente c), que es otro documento; se anota como `fuente_parcial`.
- **Trampa:** los encabezados del microcurrículo (`Resultados de aprendizajes`,
  `Descripción mínima de contenidos`) se repiten **decenas de veces**, una por asignatura. La
  `NOTA DE LECTURA` del `.txt` le advierte al LLM que no los use como evidencia del perfil global.
- **Sin campos por coordenadas** (la instrumentación es estructural: existencia de secciones, no
  completitud campo a campo), pero **sí con Jaccard**: `plantilla_proyecto.py` +
  `completitud_proyecto.py` (sin ChromaDB, sin Celery y sin cuota). El universo `A` son **10
  etiquetas**: 3 grupos de MARCADORES + 7 ANCLAS de sección. `B` = las presentes; como B ⊆ A,
  `J = |B|/|A|`. Los elementos 2, 4 y 6 **no aportan etiquetas**: son `[SEMÁNTICO]`, no tienen
  ancla y —lo que importa— su evidencia vive en otras fuentes; el elemento 1 aporta la
  *existencia* de sus dos secciones, no su coherencia (eso lo juzga el LLM). El universo **no
  cambió de tamaño** con la corrección de los 6 elementos (las 7 anclas son las mismas, sólo
  cambia el `(elem. N)` de su etiqueta), así que **el J del base sigue en 1,000**: era la señal
  de control de que nada se rompió. Modos: documento suelto, `--todos`,
  `--faltan` (auditor-vs-sistema) y **`--base`** (parecido estructural contra el ejemplar
  aprobado `Reporte_Carrera_Software_26072017.pdf`). Medido: el documento base da **J = 1,000**
  (3/3 marcadores, 7/7 anclas); el modelo educativo J = 0,100 y el reglamento de examen de fin
  de carrera J = 0,000 — **son un acierto**: no son proyectos curriculares de rediseño y el
  sistema los rechazaría por marcadores antes de llamar al LLM. Media del corpus: **0,367** (3
  documentos). En `--base` (parecido estructural, 14 secciones del ejemplar): base 1,000 por
  construcción, modelo educativo **0,071** (comparte sólo `Misión`), reglamento **0,000**.
- ⚠️ **El documento no cabe en la cuota: se recorta** (`services/recorte_proyecto.py`). El
  ejemplar real extrae **333.218 ch ≈ 98.000 tokens** y la cuota diaria de Groq es de **100.000**:
  mandarlo entero (`"documento": texto`) agotaba la cuota del día con **un solo documento**. El
  recorte lo deja en **18.731 ch ≈ 5.509 tokens (5,6% del original)**, un ahorro de ~92.500
  tokens por documento. Sólo se aplica al Indicador 2 (`tareas_ia.py`); los demás son plantillas
  de 1-6 páginas y caben enteras. Ver `ARQUITECTURA.md` para el diseño del recorte.
- **Rehecho: el viejo "el elemento 5 no cumple" era una frase incorrecta.** Ese E5 se desdobló
  en el **E2** (tener políticas de actualización, fuente b) y el **E6** (ejecutar el seguimiento
  y evaluación, fuentes e/f), y **ninguna de esas fuentes se aportó nunca**. Sigue siendo cierto
  el hecho medido —"seguimiento" y "mejora continua" sólo aparecen en el formulario en contextos
  ajenos (calidad del software, prácticas preprofesionales), no como políticas del currículo—,
  pero la conclusión correcta **no es "no cumple"**: es **"no se aportó la fuente b)/e)/f) que lo
  evidenciaría"**. Son dos afirmaciones distintas: la primera dice que la carrera no hace
  seguimiento; la segunda, que no se entregó el documento que lo acredita. Sólo la segunda se
  sostiene con lo que hay sobre la mesa, y es la que el `.txt` obliga a decir al LLM. Lo mismo
  para el **E4** (fuente d): que el claustro tenga docentes con experiencia internacional **no**
  lo acredita — la norma pide su aporte al *diseño*, no la nómina de quien enseña.
- **Limitación honesta:** con los elementos 2, 4 y 6 fuera del cociente, el J del Indicador 2
  mide **sólo la mitad estructural** del indicador (existen las secciones que un formulario debe
  traer) y **satura en 1,000** para el único proyecto de rediseño real del corpus. Discrimina la
  basura de control (modelo educativo 0,100; reglamento 0,000), no la calidad de un proyecto. Y
  el corpus tiene **un solo** proyecto curricular auténtico: no hay con qué medir un rediseño
  incompleto. Un J de 1,000 **no acredita el indicador**; dice que el formulario trae lo que a un
  formulario le toca traer.

### Indicador 3 — Malla
- Marcador: `MALLA CURRICULAR`. Se reconoce además por la etiqueta `HPAO` y ≥10 códigos de
  asignatura (`es_malla`, `extraccion.py:319`).
- ✅ **La malla se reconstruye por coordenadas** (`filas_de_malla`, `extraccion.py:367`): se
  entrega al LLM una línea por asignatura `CODIGO | NOMBRE | PRE: … | HPAO: … | CR: …`, con la
  palabra literal `VACIO` para un campo sin llenar (NOTA DE LECTURA del `.txt`). El LLM **sí**
  evalúa prerrequisitos (elemento 4: cumple si ninguna línea trae `VACIO` en PRE).
- Elementos: identificación institucional/carrera, los **8 PAO** + 3 unidades de organización,
  distribución de asignaturas (≥10, ninguna con nombre `VACIO`), prerrequisitos y créditos con
  **HPAO = 48 × CR**. La suma de asignaturas no cuadra con el total (integración curricular,
  prácticas y servicio comunitario no llevan código): **no** es incumplimiento.
- Un código mal escrito llega marcado `[CÓDIGO MALFORMADO]`: se reporta en `analisis_libre`,
  no como incumplimiento.
- **La malla ES texto estructurado** (hay capa de texto en el PDF), NO un escaneo ni imágenes:
  el sistema reconstruye por coordenadas una línea por asignatura con sus campos (`filas_de_malla`).
- ✅ **Jaccard de completitud instrumentado** (`plantilla_malla.py` + `completitud_malla.py`,
  sin ChromaDB ni cuota). El "esquema" de la malla no es una lista fija de casillas
  etiqueta→valor, sino el patrón por asignatura (4 campos: nombre, prerrequisito, hpao,
  créditos; el `codigo` es el ANCLA/identificador — la malla **no lleva NRC**) más los 8 PAO
  esperados. `A` = 4 campos × nº asignaturas + 8 PAO; `B` = lo relleno (descontando los `VACIO`
  y los PAO ausentes); `J = |B| / |A|`. El invariante `HPAO = 48 × CR` se reporta como anomalía
  aparte, no como campo vacío. En las mallas reales del corpus todo sale relleno (`J = 1,000`);
  la métrica caza materias/prerrequisitos/créditos/horas genuinamente faltantes o PAO no leídos.

### Indicador 4 — Sílabo
- Marcadores: `PROGRAMA DE ASIGNATURA - SÍLABO` **y** `SGC.DI.321` (ambos obligatorios).
- **9 elementos** anclados a texto literal (`ANCLA`), 8 estructurales + el 4 semántico.
- ⚠️ La numeración **salta de 4 a 6** (no hay sección 5) y el encabezado 4 está truncado
  ("…Y TÉCNICA DE"): se ancla al texto, no al número (NOTA DE NUMERACIÓN del `.txt`). El
  encabezado "SISTEMA DE CONTENIDOS…" se repite por continuación de página: es una sola sección.
- `CAMPOS` cubre DATOS GENERALES y la carga horaria por componentes. Las celdas espaciadoras
  de DATOS GENERALES no son campos (las descarta la extracción por coordenadas).

### Indicador 6 — Guía de laboratorio
- Marcadores: `GUIA DE USO DE LABORATORIO` **y** `A. INFORMACIÓN DE LA GUÍA`.
- **5 elementos** (norma): sección A (información), planificación pedagógica (semántico),
  recursos, B (control de cambios), C (aprobación: filas Elaborado/Revisado/Aprobado con
  nombre y cargo).
- `CAMPOS` (23): identificación de A + planificación + recursos. Se añadió
  **`LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA`**, que estaba en la plantilla pero no en la
  base de oro (aparece lleno en 6 de 10 guías y vacío en 4). Su valor trae un sub-rótulo
  `SALA:`; cuando la sala está vacía el resolvedor lo tomaba por otro campo y lo daba por
  lleno — corregido tensando `es_cabecera` en `_valor_de` (`extraccion.py`): sólo forma
  cabecera de tabla una fila cuyas celdas sean **todas campos declarados**, no un sub-rótulo.
- `NA`/`N/A` en REACTIVOS y MUESTRA = válidos (software no usa reactivos).
- Nota: que `Aprobado por: JEFE LABORATORIO` sea un **cargo y no un nombre** hoy lo juzga el
  **LLM** (elemento 5 pide "nombre y cargo"); el detector determinista de campos ve la celda
  llena. No es una comprobación de código.
- **Jaccard:** la guía está instrumentada igual que el sílabo. Inventario único de 27
  elementos en `plantilla_guia.py` (23 campos/bloques + control de cambios + 3 filas de
  aprobación); evaluación con `completitud_guia.py` (`--todos`, un documento, o `--faltan`
  para el Jaccard auditor-vs-sistema). El `jaccard.py` quedó **sólo para el sílabo**: antes
  mezclaba ambos y contaba dos veces el mismo elemento (una vez como sección, otra como campo).

## Reglas generales de evaluación (las ve el LLM)

Al final del `.txt`, seis reglas gobiernan al modelo: (1) los HECHOS VERIFICADOS son ciertos y
no se discuten; (2) un ítem de checklist por elemento, en orden; (3) ESTRUCTURAL exige el ANCLA
literal, SEMÁNTICO evalúa propósito; (4) justificación = cita literal, sin cita no cumple;
(5) prohibición de inferir lo no leído; (6) diagnóstico concreto en `analisis_libre`.

## Estado de implementación

Lo que antes era "pendiente para que el rediseño funcione" **ya está en el código**:
- Veto por plantilla/campos: `_calcular_veredicto` (`tareas_ia.py:303`).
- Un `Document` completo por indicador (sin troceo que parta el checklist): `crear_base_oro.py`.
- Recuperación de la norma por metadato exacto y filtro `tipo="norma"` (nunca el maestro):
  `_recuperar_norma` (`tareas_ia.py:212`).

Limitaciones vigentes (ver `HALLAZGOS_Y_PENDIENTES.md`):
- **Pendiente de ejecutar:** los marcadores del Indicador 1 se ampliaron en el `.txt`
  (`PERFIL DEL EGRESADO`, `PERFIL EGRESADO`) pero **Chroma no se ha regenerado**: hasta correr
  `python scripts/crear_base_oro.py`, el sistema en producción sigue leyendo los metadatos
  viejos y rechazando el documento base aprobado.
- No hay detección determinista de "marcadores de relleno" que parezcan llenos pero no lo sean
  (`[*SIN AUTOR*]`, un cargo donde va un nombre, texto truncado): queda al juicio del LLM.
- No hay regla de coherencia temporal (fecha de actualización vs. período): no está en el
  `.txt` ni en el código.
