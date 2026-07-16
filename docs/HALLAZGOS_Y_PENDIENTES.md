# Hallazgos (bugs) y trabajo pendiente

Empieza por aquí si vas a programar. Los bugs que corrompían resultados (B1–B4, B6, B7) y las
optimizaciones (O1, O2) **ya están resueltos**: ver el changelog al final. Lo que queda son un
bug funcional acotado y la funcionalidad de tesis que aún no existe.

## Bugs vigentes

### B5 — Rechazados: ajeno y NO CUMPLE comparten carpeta
`orchestrator_service.py:225` manda a la **misma** `11_Documentos_Rechazados` tanto los
documentos ajenos a la carrera (`pertenece_software == False`) como los `NO CUMPLE` propios.
Un sílabo de Software que reprueba queda indistinguible de uno de otra carrera.
Ya se separaron los otros casos (`12_Plantilla_No_Reconocida`, `98_Pendientes_Por_Cuota`,
`99_Descarte_Errores`), pero estos dos siguen juntos.
**Fix:** separar carpetas (`11_No_Pertinentes` vs `12_No_Cumple`), o subcarpeta por indicador
dentro de rechazados para no perder el rastro del indicador evaluado.

## Pendientes de tesis (funcionalidad que exigen los objetivos y no existe)

- **Verificación de evidencias faltantes (OE2.3):** crear `data/inventario_esperado.json` que
  declare, por indicador, qué documentos y cuántos se esperan; contrastar contra disco. Para el
  indicador 6, N guías (una por asignatura con laboratorio), no "una".
- **Alertas al responsable (OE2.4):** no existe nada. `smtplib` + tabla responsable-por-indicador.
- **Persistencia / trazabilidad:** tabla SQLite `(documento, hash, indicador, veredicto,
  porcentaje, timestamp, version_normativa)`. Sobrevive al expiry de Redis y da gratis la
  detección de faltantes y los datos del OE3. (`sqlalchemy` está en `requirements.txt` pero
  sin usar.)
- **Fijar versiones en `requirements.txt`** (hoy 0 pins) — requisito de reproducibilidad.
- **OE3 (parcial):** ya existe corpus etiquetado (`data/verdad_campos.csv`, 214 docs) y las
  métricas de la capa determinista (`banco_pruebas.py`, `evaluar_campos.py`, `jaccard.py`,
  `completitud.py`). **Falta** la evaluación del checklist del LLM (kappa, k=5), las métricas de
  sistema (tiempo/tokens/USD/CPU), la validación con expertos y persistir resultados. Ver
  `PLAN_EVALUACION.md`.

### Nota de generalización (para el capítulo de limitaciones)
El documento maestro es una **constante de Python** en `ingestar_maestro.py:23`
(`PERFIL_DE_EGRESO`), y la lista de asignaturas se genera desde la malla de Software. El
sistema está cableado a la carrera de Software; generalizar a otra carrera hoy requiere editar
código y regenerar la base.

---

## Changelog: resueltos (material para el capítulo de evolución)

La arquitectura pasó de "todo lo decide el LLM sobre texto plano `hi_res`" a **3 capas**
(hechos deterministas → juicio LLM → veredicto determinista). En el camino se cerraron:

### B1 — Chroma: colección compartida sin filtro (era CRÍTICO) → ✅ resuelto
La norma se recupera por metadato exacto `vector_db.get(where={"indicador": N})` y el respaldo
por similitud filtra `filter={"tipo": "norma"}` (`_recuperar_norma`, `tareas_ia.py:212`). Ya no
puede devolver el documento maestro, que comparte colección.

### B2 — El veredicto ignoraba el veto por campo obligatorio → ✅ resuelto
`_calcular_veredicto` (`tareas_ia.py:303`) aplica el veto de forma determinista: plantilla
inválida → `PLANTILLA NO RECONOCIDA`; no pertenece → `NO CUMPLE`; plantilla mayoritariamente en
blanco → `NO CUMPLE`; cualquier campo vacío → tope `PARCIAL`. El LLM ya no emite el veredicto.

### B3 — chunk_size partía los indicadores → ✅ resuelto
`crear_base_oro.py` ingesta **un `Document` completo por indicador** (sin `TextSplitter`), con
metadatos `tipo/indicador/marcadores/campos`. El checklist ya no sale truncado.

### B4 — El reporte ejecutivo no se generaba si un documento fallaba → ✅ resuelto
Las tareas hijas **devuelven un dict** con veredicto `ERROR_*` en vez de re-lanzar
(`tareas_ia.py:508`), así que el chord no aborta el callback. `generar_reporte_ejecutivo`
filtra dicts y cuenta `errores` por el string del veredicto (`:543`), ya no da 0.

### B6 — Reintentos sobre archivo inexistente → ✅ resuelto
Un PDF ilegible **retorna** un resultado `ERROR_LECTURA` sin reintentar (`tareas_ia.py:395`);
el temporal se conserva hasta después de enrutarlo.

### B7 — Mapeo de carpetas incompleto → ✅ resuelto
`CARPETAS_POR_INDICADOR` (`orchestrator_service.py:159`) cubre los 5 indicadores de la base de
oro (1,2,3,4,6), incluido el 6 que sí se prueba. El fallback genérico casi no se alcanza.

### O1 — hi_res innecesario → ✅ hecho
La ruta por defecto es pdfminer por coordenadas (`extraccion.py`); `hi_res` (Tesseract) quedó
**sólo como respaldo OCR** para escaneos sin capa de texto (`extraccion.py:462`). Queda como
ablación limpia para el OE3: coordenadas (actual) vs `unstructured` hi_res (anterior).

### O2 — Tokens de la compuerta de pertinencia → ✅ superado
La pertinencia ya **no usa LLM**: se decide por coordenadas leyendo `CARRERA`/`ASIGNATURA` y
contrastando contra la malla (`_pertinencia`, `tareas_ia.py:133`). Además el contexto maestro
que sí ve el LLM se recorta (se le quita la lista de asignaturas, `_recuperar_maestro`, `:239`).
