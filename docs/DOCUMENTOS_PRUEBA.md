# Documentos de prueba reales

Tres documentos analizados carácter a carácter. Sus rarezas definieron el diseño de la
base de oro y de las métricas. Rutas originales (fuera del repo, en Descargas del usuario).

> **Nota:** estos son los 3 documentos fundacionales. El corpus de evaluación **ya es mayor**:
> `data/verdad_campos.csv` etiqueta **214 documentos** a nivel campo y `banco_pruebas.py` añade
> casos negativos (Contabilidad, Psicología, sílabo trampa vacío, asignatura fuera de malla).
> Ver `PLAN_EVALUACION.md`.

## 1. Sílabo — `INDICADOR 4`
`Silabo_NRC-22639_Auditoria-Tecnologia-Informacion-y-Comunicacion_..._Contabilidad_...pdf`

- Plantilla oficial `SGC.DI.321` v1.3, 6 páginas, **con capa de texto real** (no escaneo).
- Secciones presentes: 1,2,3,4,**6**,7,8,9,10 (no hay 5).
- **Firmado y sellado** (QR de docente, coordinador y director).
- ⚠️ **NO pertenece a Software.** `Área de Conocimiento: SISTEMAS DE INFORMACION`, resultados
  de aprendizaje sobre "procesos contables, financieros"; nombre de archivo dice `Contabilidad`.
  → **Etiqueta verdadera de pertenencia = False.** Es un caso negativo, NO un error del sistema.
- Vacíos reales: columna Edición toda en `-`, una entrada sin año/idioma, un `[*SIN AUTOR*]`.
- Incoherencia temporal: período `ABR 25 - AGO 25` pero `Fecha de Actualización 24/10/2021`;
  `Fecha Elaboración` con dos valores (`19/12/23` y `24/10/2021`).
- Trampa de vacíos: la tabla DATOS GENERALES tiene **celdas espaciadoras** vacías que NO son
  campos faltantes (junto a Código/NRC). No marcarlas como vacías.

## 2. Malla — `INDICADOR 3`
`malla isoj 202450 act.pdf`

- Diagrama apaisado, **1 página**, capa de texto real (**7328 chars**, sin necesidad de OCR).
- ⚠️ **El texto sale desordenado:** la extracción devuelve primero bloques `CD CPE CA HS` y
  `48 48 48 6` de varias asignaturas concatenados, ANTES que los nombres de las materias. Los
  prerrequisitos quedan desligados de su asignatura. Verificado empíricamente con `pypdf`.
  → Ni OCR ni `hi_res` lo arreglan: el problema es que se **descartan las coordenadas x/y**,
  no el reconocimiento de caracteres. **Por eso el sistema actual extrae por coordenadas**
  (`extraccion.py`) y **reconstruye la malla** celda por celda (`filas_de_malla`,
  `extraccion.py:367`), reasociando cada prerrequisito con su asignatura.
- Invariantes aritméticos que SÍ se pueden verificar: 8 PAO × 720 h = 5760; 8 × 15 = 120
  créditos; razón 48 h/crédito en toda asignatura (144/3, 96/2, 192/4, 240/5...).
- `N/A` y `NIVELACION` en prerrequisito = válidos.

## 3. Guía de laboratorio — `INDICADOR 6`
`3.3 Guia Laboratorio ABC ... procesamiento de lenguaje natural y Machine Learning.pdf`

- Plantilla "GUIA DE USO DE LABORATORIO", 2 páginas, **con capa de texto real (4163 chars)**.
- Carrera = SOFTWARE → pertenece = True.
- **Campos genuinamente vacíos:** `FECHA:` (cabecera), `DEPARTAMENTO:`, `LABORATORIO...`, `SALA:`,
  y las 3 celdas de la columna **Firma** en C. APROBACIÓN.
- `Aprobado por: JEFE LABORATORIO` = cargo, no nombre. Hoy esto lo detecta el **juicio del
  LLM** (elemento 5 pide "nombre y cargo"); el detector determinista de campos ve la celda llena.
- `ASIGNATURA: APL. BASADAS EN EL CONOCIMIENT` = truncado.
- `REACTIVOS: NA` y `MUESTRA / OTROS: NA` = **correctamente llenos** (software no usa reactivos).
- Demuestra el bug del diseño viejo: A✓ B✓ C✓ integridad✗ = 75% = CUMPLE, pese a no tener
  firmas. (Ya corregido: hoy el veto por plantilla/campos vacíos lo impide, `tareas_ia.py:303`.)

## Verificación técnica hecha

Con `pypdf` se confirmó que **los tres PDF tienen capa de texto** (malla 7328, guía 4163 chars).
Por eso la ruta por defecto del sistema es **pdfminer por coordenadas** (`extraccion.py`), y
`strategy="hi_res"` (Tesseract) quedó **sólo como respaldo OCR** para escaneos sin capa de
texto (`extraccion.py:462`). La ablación para el Objetivo 3 ya no es "hi_res vs fast", sino
**coordenadas (diseño actual) vs `unstructured` hi_res (diseño anterior)**: misma exactitud
esperada en estos documentos, a una fracción del tiempo/CPU.

## Ground truth mínimo sugerido

Para poder medir, cada documento del corpus necesita etiqueta humana de:
`plantilla_ok`, `pertenece_software`, `indicador`, `veredicto`, `porcentaje`, `campos_vacios[]`.
Ver plantilla CSV en `PLAN_EVALUACION.md`.
