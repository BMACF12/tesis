# Contexto de la tesis

## Tema

Diseño e implementación de un sistema automatizado para gestionar y mantener ordenadas
las evidencias de acreditación universitaria por criterio, estándar e indicador, con
clasificación y evaluación asistida por LLMs, aplicado a la normativa **CACES (Ecuador) 2024**.

Caso de estudio: **Carrera de Ingeniería de Software** (ESPE).

## Objetivo General

Diseñar e implementar un sistema automatizado para gestionar y mantener ordenadas las
evidencias de acreditación por criterio, estándar e indicador, garantizando su
**disponibilidad, trazabilidad y actualización permanente**.

## Objetivos Específicos

**OE1 — Investigación.** Recopilar información sobre sistemas de gestión documental para
acreditación, criterios/indicadores de CACES u organismos equivalentes, metodologías de
automatización (RPA/IPA), uso de LLMs y APIs para clasificación/etiquetado de documentos,
y buenas prácticas de organización de evidencias.

**OE2 — Implementación.** Analizar, diseñar e implementar un sistema automatizado que
ejecute tareas repetitivas de gestión de evidencias:
1. Creación de estructura de carpetas por criterio/indicador.
2. Nombrado automático de archivos.
3. Verificación de evidencias faltantes.
4. Generación de alertas al responsable.
5. Elaboración automática de checklist.
Todo con LLMs y scripts integrados a los repositorios institucionales.

**OE3 — Evaluación.** Evaluar con un protocolo experimental basado en métricas cuantitativas
(tiempo de organización, reducción de errores de clasificación, % de evidencias completas,
uso de recursos), comparación manual vs. automatizado, validación por expertos, análisis de
errores, reproducibilidad y experiencia de usuario.

---

## Estado de cumplimiento (re-verificado 2026-07-15 contra el código de 3 capas)

Se usa la propia escala del sistema (CUMPLE / CUMPLE PARCIALMENTE / NO CUMPLE) por honestidad.

| Objetivo | Veredicto | Aprox. |
|---|---|---|
| General | CUMPLE PARCIALMENTE | ~60% |
| OE1 (investigación) | No evaluable por código | — |
| OE2 (implementación) | CUMPLE PARCIALMENTE | ~60% |
| OE3 (evaluación) | CUMPLE PARCIALMENTE | ~35% |

### Objetivo General — las tres promesas
- **Disponibilidad:** ✅ los aprobados van a carpetas por indicador en `Auditoria_CACES/` con su reporte PDF.
- **Trazabilidad:** ⚠️ débil. Único rastro persistente = nombre de archivo con timestamp.
  Los resultados estructurados viven en Redis (backend de Celery) y **expiran ~24 h**. No hay
  base de datos; `sqlalchemy` está en `requirements.txt` pero no se usa.
- **Actualización permanente:** ❌ no existe. No hay watcher, cron, scheduler ni versionado.
  El sistema es reactivo (alguien sube PDFs a mano).

### OE2 — las cinco tareas
1. Estructura de carpetas por indicador — ✅ se crean bajo demanda. `CARPETAS_POR_INDICADOR`
   (`orchestrator_service.py:159`) mapea a propósito sólo los 5 indicadores de la base de oro
   (1,2,3,4,6) y enruta por `indicador_numero`; el fallback genérico `sanitizar_nombre()` ya
   casi no se alcanza. (La fragmentación de carpetas que antes causaba el mapeo incompleto
   quedó resuelta.)
2. Nombrado automático — ✅ `{nombre}_{timestamp}.pdf` + `_Reporte.pdf`.
3. Verificación de evidencias faltantes — ❌ no existe (no hay inventario esperado).
4. Alertas al responsable — ❌ cero código (sin smtp/email/webhook).
5. Checklist automático — ✅ y sólido (esquema Pydantic + recálculo determinista del %).
- "Integrado a repositorios institucionales" — ❌ todo es filesystem local + upload multipart.

### OE3 — evaluación experimental
⚠️ **En curso, no inexistente.** Ya hay infraestructura de evaluación en `backend/scripts/`:
- **Corpus etiquetado:** `data/verdad_campos.csv` — 4 342 pares (documento, campo) sobre
  **214 documentos**, con `vacio_real` corregido a mano vs `prediccion_sistema`.
- **Banco de casos de la capa determinista:** `banco_pruebas.py` — casos con etiqueta esperada
  de indicador, plantilla y pertinencia, incluidos negativos (Contabilidad, Psicología, sílabo
  trampa vacío, asignatura fuera de malla). No llama al LLM (no gasta cuota).
- **Métricas de la Compuerta 5 (campos vacíos):** `evaluar_campos.py` — micro P/R/F1, matriz de
  confusión, Hamming loss, exact-match y Jaccard (con la salvedad honesta del 0/0).
- **Completitud por elementos/secciones (sílabo):** `jaccard.py`, `evaluar_jaccard.py`,
  `completitud.py` e inventario `plantilla_silabo.py` (39 elementos de `SGC.DI.321`).
- **Completitud por elementos (guía, Ind. 6):** `plantilla_guia.py` (27 elementos) y
  `completitud_guia.py` (lote / individual / auditor).
- **Completitud por elementos (malla, Ind. 3):** `plantilla_malla.py` (esquema por asignatura
  + 8 PAO) y `completitud_malla.py` (lote / individual / auditor; sin ChromaDB ni cuota). La
  malla ES texto estructurado que el sistema reconstruye por coordenadas (44 asignaturas): se
  mide completitud de materias, niveles PAO, prerrequisitos, créditos y horas. No lleva NRC (el
  identificador es el código de asignatura); `HPAO = 48 × CR` se reporta como anomalía aparte.

**Lo que aún falta del OE3:** evaluación del **checklist del LLM** (kappa de Cohen, protocolo
k=5 de reproducibilidad); **métricas de sistema** (tiempo p50/p95, tokens, USD/doc, CPU, RAM);
matriz de confusión formal del **enrutador de indicador**; **validación con expertos** (kappa
humano-humano y humano-sistema, SUS); persistir resultados a `data/resultados_evaluacion/`; y
un runner único `evaluar.py`. Además `requirements.txt` **sigue sin fijar versiones**
(reproducibilidad comprometida). Ver `PLAN_EVALUACION.md` para el detalle.

---

## Alcance de las pruebas (decidido con el usuario)

- **Indicadores instrumentados y a probar:** 3 (Malla), 4 (Sílabo), 6 (Escenarios de
  prácticas / guías de laboratorio).
- **Indicador 2 (Proyecto curricular) — instrumentado a nivel estructural (2026-07-16):** se pasó
  de `SEMANTICO` a `INSTRUMENTADO` con marcadores del formulario de rediseño SENESCYT/CES y 3 de 5
  elementos anclados a secciones (ver `INDICADORES.md`). Se cuenta con **un único ejemplar de
  referencia** (el rediseño de Ingeniería de Software aprobado por el CACES), que es el "correcto":
  cualquier otro proyecto que no sea similar debe rechazarse (marcadores + pertinencia). Como sólo
  hay un documento, **no forma un corpus para métricas de completitud**; su prueba es de extremo a
  extremo (enruta → plantilla válida → pertinente → checklist), no un Jaccard sobre lote.
- **No se prueba:** 1 (Perfil de egreso) — no se cuenta con ese documento. Lleva `ESTADO:
  SEMANTICO` en la base de oro. Cobertura instrumentada: **4 de 5** (1,2,3,4,6 salvo el 1).
- **Requisito central de la validación:** garantizar que exista cada indicador, que sus
  documentos usen la **plantilla oficial específica**, y detectar **qué campos están vacíos**.

## Enfoque de evaluación (arquitectura de 3 capas)

- **Los hechos son deterministas; el LLM sólo juzga.** El sistema NO le pide al modelo
  hechos verificables (plantilla, pertenencia, campos vacíos): los extrae por coordenadas
  del PDF (`services/extraccion.py`) y sólo le entrega el checklist de elementos
  fundamentales a evaluar. El veredicto y el porcentaje se recalculan de forma determinista
  (`_calcular_veredicto`, `tareas_ia.py:303`). Si la plantilla es inválida o el documento no
  pertenece a la carrera, el LLM ni se llama.
- Por eso la base de oro lleva MARCADORES y CAMPOS en los **metadatos** (los usa el código,
  no el LLM) y el criterio en el texto (lo lee el LLM). Ver `INDICADORES.md`.
