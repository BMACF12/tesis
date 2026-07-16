# Conocimiento — indicador-3-malla

Material para razonar y probar el Indicador 3 (Malla curricular). Coloca aquí:

- `malla_software_oficial.pdf` — la malla vigente aprobada de Ingeniería de Software (el caso de
  estudio). Es la verdad de referencia de asignaturas, PAO, prerrequisitos y créditos.
- `malla_otra_escala.pdf` — al menos una malla exportada a otro pliego/escala (para probar que
  `escala_de_malla` deduce bien los ejes; hay mallas a escala 1 y ~3,3).
- `malla_ejemplo_incompleta.pdf` — una malla con campos faltantes (para el caso NO CUMPLE), si se consigue.
- `volcado_texto_extraido.txt` — el texto que devuelve `extraer_documento` (útil para ver el
  desorden de lectura y verificar la reconstrucción).
- `verdad_referencia.md` — invariantes esperados: 8 PAO, 5760 h, 120 créditos, 48 h/crédito, y la
  lista de asignaturas con su prerrequisito (para etiquetar el ground truth).

> La lista de asignaturas que usa el sistema se genera a `backend/data/asignaturas_malla.txt` con
> `scripts/extraer_asignaturas.py`; aquí guarda el PDF fuente y la verdad humana.
