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
| 1 | Perfil de egreso | `SEMANTICO` | `PERFIL DE EGRESO\|PERFIL EGRESO\|PERFIL PROFESIONAL` | sin campos; sólo juicio semántico |
| 2 | Proyecto curricular | `INSTRUMENTADO` (estructural) | `Datos generales de la carrera; Carrera a rediseñar\|Tipo de trámite; Descripción microcurricular` | formulario de rediseño SENESCYT/CES (decenas de páginas); sin campos por coordenadas, secciones ancladas por ANCLA |
| 3 | Malla curricular | `INSTRUMENTADO` | `MALLA CURRICULAR` | diagrama apaisado 1 página |
| 4 | Syllabus | `INSTRUMENTADO` | `PROGRAMA DE ASIGNATURA - SÍLABO; SGC.DI.321` | plantilla `SGC.DI.321` (6 páginas) |
| 6 | Escenarios de prácticas | `INSTRUMENTADO` | `GUIA DE USO DE LABORATORIO; A. INFORMACIÓN DE LA GUÍA` | "GUIA DE USO DE LABORATORIO" |

`ESTADO: SEMANTICO` (sólo el 1) significa que no hay plantilla ni campos que verificar de forma
determinista: sólo se evalúan los elementos por juicio semántico del LLM. No se prueba en esta
tesis (no se cuenta con ese documento); ver `CONTEXTO_TESIS.md`.

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
- **Elementos:** 3 de 5 anclados a secciones literales — 2 `ANCLA "Pertinencia"`,
  3 `ANCLA "Requisitos de ingreso"`/`"Requisitos de graduación"`,
  4 `ANCLA "Metodología y ambientes de aprendizajes"`/`"Infraestructura y equipamiento"`. Los
  elementos 1 (coherencia con modelo/misión/perfil) y 5 (políticas de seguimiento y mejora)
  quedan `[SEMÁNTICO]`: no hay un encabezado fiable para ellos y forzar un ANCLA generaría
  incumplimientos espurios.
- **Trampa:** los encabezados del microcurrículo (`Resultados de aprendizajes`,
  `Descripción mínima de contenidos`) se repiten **decenas de veces**, una por asignatura. La
  `NOTA DE LECTURA` del `.txt` le advierte al LLM que no los use como evidencia del perfil global.
- **Sin campos por coordenadas ni Jaccard:** a diferencia de malla/sílabo/guía, este indicador
  **no** tiene `plantilla_proyecto.py`/`completitud_proyecto.py`. La instrumentación es
  estructural (existencia de secciones), no de completitud campo a campo.

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
- No hay detección determinista de "marcadores de relleno" que parezcan llenos pero no lo sean
  (`[*SIN AUTOR*]`, un cargo donde va un nombre, texto truncado): queda al juicio del LLM.
- No hay regla de coherencia temporal (fecha de actualización vs. período): no está en el
  `.txt` ni en el código.
