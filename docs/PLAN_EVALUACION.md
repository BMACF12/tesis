# Plan de evaluación (Objetivo 3)

El OE3 está **en curso**: ya existe corpus etiquetado y parte de las métricas (ver "Estado
actual" abajo). Este documento es el plan completo; lo ya hecho se marca ✅ y lo pendiente ⬜.
Los bugs que obligaban a re-medir (filtro de Chroma, veto por campos, troceo) **ya están
resueltos** (ver `HALLAZGOS_Y_PENDIENTES.md`), así que se mide sobre el código actual sin
pre-condiciones.

## Estado actual (ya implementado en `backend/scripts/`)

- ✅ **Corpus etiquetado a nivel campo:** `data/verdad_campos.csv` — 4 342 pares
  (documento, campo) sobre **214 documentos**, `vacio_real` corregido a mano.
- ✅ **Banco de la capa determinista:** `banco_pruebas.py` — extracción, enrutado, plantilla,
  pertinencia y campos, con etiquetas esperadas y casos negativos. No usa LLM.
- ✅ **Métricas Compuerta 5 (campos vacíos):** `evaluar_campos.py` — micro P/R/F1, matriz de
  confusión, Hamming, exact-match y Jaccard (0/0 tratado con honestidad).
- ✅ **Completitud por elementos (sílabo):** `jaccard.py`, `evaluar_jaccard.py`, `completitud.py`,
  `plantilla_silabo.py` (inventario de los 39 elementos de `SGC.DI.321`).
- ✅ **Completitud por elementos (guía, Ind. 6):** `plantilla_guia.py` (inventario único de 27
  elementos, deduplicado) y `completitud_guia.py` (Jaccard plantilla-vs-doc en lote `--todos`,
  un documento, o auditor-vs-sistema `--faltan`; sin ChromaDB ni cuota). Se añadió el campo
  `LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA` a la base de oro y se corrigió el resolvedor
  (`es_cabecera`) para su sub-rótulo `SALA:`. La **malla (Ind. 3)** SÍ está instrumentada
  para Jaccard de completitud: es texto estructurado que el sistema reconstruye por coordenadas
  (44 asignaturas en las mallas reales). `plantilla_malla.py` (esquema por asignatura + 8 PAO) y
  `completitud_malla.py` (`--todos` / individual / auditor `--faltan`; sin ChromaDB ni cuota)
  miden materias, niveles PAO, prerrequisitos, créditos y horas. La malla no lleva NRC: el
  identificador es el código de asignatura. `HPAO = 48 × CR` se reporta como anomalía, no como
  campo vacío.
- ⬜ **Pendiente:** checklist del LLM (kappa, k=5), métricas de sistema (tiempo/tokens/USD/CPU/RAM),
  matriz de confusión formal del enrutador, validación con expertos (kappa, SUS), persistir a
  `data/resultados_evaluacion/`, runner único `evaluar.py`, y fijar versiones en `requirements.txt`.

## Principio: el sistema toma varias decisiones, y casi todas son deterministas

No reportar un solo número de "precisión". Cada decisión se mide por separado, y hay que
distinguir **qué las decide** (crucial para atribuir errores):

| Decisión | ¿Quién decide? | Reproducible |
|---|---|---|
| 1. ¿Plantilla oficial? | Código (`_plantilla_valida`) | sí |
| 2. ¿Pertenece a Software? | Código (`_pertinencia`) | sí |
| 3. ¿Qué indicador? | Enrutador keywords + metadato; similitud sólo de respaldo | sí (rama keyword) |
| 4. ¿Cumple cada elemento? | **LLM** (`checklist`) | **no** (única fuente de varianza) |
| 5. ¿Qué campos vacíos? | Código (`_campos_sin_llenar`) | sí |
| Veredicto | Código (`_calcular_veredicto`, `tareas_ia.py:303`) | sí (dado 1–5) |

Implicación para la tesis: **4 de las 5 decisiones son 100% reproducibles** (extractor
determinista sobre coordenadas). Sólo el checklist del LLM tiene varianza. El **veredicto NO
es una decisión independiente**: se deriva de 1, 2, 4 y 5. Medir "exactitud del veredicto" mide
la regla de composición y sus entradas, no al modelo.

## Métricas por decisión

| Decisión | Métrica | Por qué |
|---|---|---|
| Plantilla (código) | Exactitud; `PLANTILLA NO RECONOCIDA` como **clase propia** en la matriz | "Doc equivocado" ≠ "doc mal llenado"; mide el emparejador de marcadores |
| Pertinencia (código) | **Recall + tasa de falsos negativos** (no exactitud) | FN destruye evidencia válida (va a rechazados sin auditar); coste asimétrico |
| Indicador (código) | **F1 macro** + matriz de confusión | Corpus desbalanceado; exactitud global engaña |
| Enrutador keywords | Tasa de acierto (rama keyword) vs caída a respaldo por similitud | Aísla cuánto trabajo hace el enrutador barato |
| RAG (respaldo) | **Recall@1 / Recall@3** del chunk normativo correcto, **sólo en la rama de fallback** | Cuando el enrutador acierta se lee por metadato exacto; no hay recuperación difusa que medir |
| Checklist (LLM) | Precisión/Recall/F1 sobre "cumple" + **kappa de Cohen** | Es la única decisión del modelo; ~240 juicios binarios; kappa lo reconocen los expertos |
| Campos vacíos (código) | Precisión/Recall a **nivel campo** + FP por categoría | La tabla de FP por categoría (N/A, NA, `-`, espaciadores) es material de tesis; mide el extractor |
| Veredicto (compuesto) | **Kappa ponderado cuadrático** | Es ordinal: confundir CUMPLE↔NO CUMPLE penaliza más que ↔PARCIAL |
| Porcentaje | MAE + Spearman contra el experto | Error absoluto + ordenamiento |

## Métricas de sistema (las 4 del objetivo)

- **Tiempo:** p50 y p95 por documento. Throughput del lote (docs/min con N workers).
- **Ahorro real de tiempo humano** = `T_manual − (T_sistema + T_revisión_de_errores)`.
  NO el speedup bruto `T_manual/T_sistema` (el sistema reduce, no elimina, el trabajo humano).
- **Recursos:** tokens in/out por doc, USD/doc y extrapolado a 100, llamadas API, seg CPU,
  pico RAM. **Ablación coordenadas (actual) vs `unstructured` hi_res (anterior)** sobre el mismo
  corpus: misma exactitud esperada en documentos con capa de texto, a una fracción del CPU (no
  arranca Tesseract). Nota: hoy `hi_res` sólo se usa como respaldo OCR para escaneos.
- **% evidencias completas / cobertura:** indicadores con ≥1 evidencia válida / instrumentados.
  Reportar "3/5 (2 SEMANTICO, sin documento)", no 3/3.

## Reproducibilidad
Las capas de hechos (1) y de veredicto (3) son **deterministas por construcción**: dado el mismo
PDF producen el mismo resultado. La única fuente de varianza es el checklist del LLM. Por eso el
protocolo `k=5` con `temperature=0` **aísla exactamente esa varianza**: correr cada documento 5
veces y reportar % de corridas con checklist idéntico, veredicto idéntico y desviación estándar
del %. (`temperature=0` no garantiza determinismo con un modelo alojado; demostrarlo es un
resultado, y aquí se demuestra sobre una superficie acotada.)

## Análisis de errores
Clasificar cada fallo por **capa/etapa responsable**: extracción por coordenadas / enrutamiento /
recuperación de norma / juicio del LLM (checklist) / composición del veredicto. La arquitectura
de 3 capas facilita la atribución: un campo vacío mal detectado es de la capa 1, un elemento mal
juzgado es del LLM. Requiere la métrica Recall@1 del respaldo RAG para atribuir los fallos de la
rama de fallback.

## Validación con expertos
- Medir **primero el kappa entre los dos auditores humanos**. Si ellos no coinciden, no hay
  ground truth y nada de lo demás significa. Luego kappa humano-vs-sistema.
- Experiencia de usuario: **SUS** (System Usability Scale), 10 ítems, 0-100 comparable a normas.

## Honestidad estadística (decirlo en la defensa)
- Con ~40 docs, el IC del F1 macro ≈ ±10 puntos. Declarar tamaños de muestra e intervalos.
- Con **1 sola malla**, no se puede reportar F1 de esa clase (n=1 no es medición).
- Incluir un **baseline trivial**: enrutador de keywords sin LLM. Si clasifica casi igual, la
  contribución está en el checklist y la detección determinista de campos vacíos, no en la
  clasificación del indicador.

## Corpus y ground truth

Objetivo: 30-50 PDFs etiquetados a mano. **Ya superado a nivel campo:** `data/verdad_campos.csv`
cubre 214 documentos (4 342 pares documento-campo) para la Compuerta 5. Falta el ground truth
del **veredicto** y del **checklist** por documento (la plantilla CSV de abajo), y el corpus de
los indicadores no instrumentados (1, 2). Los PDFs fuente viven fuera del repo (Descargas del
usuario y `Auditoria_CACES/`); `banco_pruebas.py` y `evaluar_campos.py` los localizan por glob.

### Plantilla CSV de etiquetado (`data/ground_truth.csv`)
```csv
archivo,plantilla_ok,pertenece_software,indicador,veredicto,porcentaje,campos_vacios,notas
Silabo_NRC-22639_...Contabilidad.pdf,1,0,4,,,,"caso negativo: es de Contabilidad/SI"
malla_isoj_202450.pdf,1,1,3,CUMPLE,100,,"1 sola malla; no da F1 de clase"
3.3_Guia_Laboratorio_ABC_NLP_ML.pdf,1,1,6,NO CUMPLE,,"FECHA;DEPARTAMENTO;SALA;firmas C.APROBACION","sin firmas"
```
Campos: `plantilla_ok` (0/1), `pertenece_software` (0/1), `indicador` (1-10),
`veredicto` (CUMPLE|CUMPLE PARCIALMENTE|NO CUMPLE|PLANTILLA NO RECONOCIDA),
`porcentaje` (0-100), `campos_vacios` (lista separada por `;`), `notas`.

## Scripts de evaluación

**Ya implementados** (llaman a la lógica de `tareas_ia`/`extraccion` sin Celery ni cuota de LLM):
- `banco_pruebas.py` — verifica la capa determinista (indicador, plantilla, pertinencia, campos)
  contra etiquetas esperadas, con casos negativos.
- `evaluar_campos.py` — Compuerta 5 con P/R/F1, confusión, Hamming, exact-match y Jaccard, sobre
  `verdad_campos.csv`. Modos `ver` / `uno` / `todo` / `--plantilla`.
- `jaccard.py`, `evaluar_jaccard.py`, `completitud.py`, `plantilla_silabo.py` — completitud por
  elementos/secciones del **sílabo** frente a la plantilla oficial. `jaccard.py` quedó sólo para
  el sílabo (Ind. 4); redirige las guías a `completitud_guia.py`.
- `plantilla_guia.py`, `completitud_guia.py` — lo mismo para la **guía** (Ind. 6): inventario
  único de 27 elementos y evaluación en lote / individual / auditor, sin ChromaDB ni cuota.

**Pendiente:** un runner único `backend/scripts/evaluar.py` que corra cada doc **k=5** por el
pipeline completo (incluido el LLM), capture **tiempo/tokens/USD** y emita en un solo informe:
matriz de confusión de indicador, **kappa** de veredicto y de checklist, P/R/F1 de campos
(reusando lo de `evaluar_campos.py`), tabla de recursos y reporte de reproducibilidad, con salida
persistida a `data/resultados_evaluacion/`.
> Confirmar con el usuario el formato antes de escribirlo.
