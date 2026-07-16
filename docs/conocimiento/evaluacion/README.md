# Conocimiento — evaluacion-pruebas

Material de referencia para la evaluación experimental (OE3). El ground truth "vivo" y los
scripts están en `backend/`; aquí guarda las copias de referencia, las notas de método y los
resultados que sustentan la tesis.

- `ground_truth/` — copia de referencia de los CSV etiquetados a mano:
  - `verdad_campos.csv` (el que usa `evaluar_campos.py`, hoy en `backend/data/`, 214 docs).
  - `ground_truth.csv` (veredicto + checklist por documento, cuando se etiquete; ver plantilla en
    `docs/PLAN_EVALUACION.md`).
- `resultados/` — salidas de las corridas: matrices de confusión, P/R/F1, Jaccard, kappas, tablas
  de recursos (tiempo/tokens/USD/CPU). Es la copia de `backend/data/resultados_evaluacion/`.
- `protocolo.md` — cómo se corrió cada evaluación: n, fecha, versión de la norma, k (repeticiones),
  modelo y `temperature`. Sin esto, un número no es reproducible.
- `expertos/` — plantillas y resultados de la validación humana: hoja de etiquetado, kappa
  humano-humano y humano-sistema, y el cuestionario SUS.

> No pongas PDFs de corpus aquí (viven fuera del repo, en Descargas y `Auditoria_CACES/`).
> Los scripts los localizan por glob. Todo `docs/conocimiento/**` está fuera de git salvo los README.
