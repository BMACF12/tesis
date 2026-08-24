"""
Agregador de completitud/Jaccard sobre TODAS las mallas del corpus (Indicador 3).

Reutiliza el evaluador ya existente (`completitud_malla.py`) y su esquema
(`plantilla_malla.py`). NO usa ChromaDB ni cuota de LLM: sólo reconstrucción por
coordenadas. Recorre el corpus completo y, POR CADA malla, emite:

  - cabecera: archivo, Jaccard, nº asignaturas, PAO x/8, anomalías HPAO=48×CR
  - lista COMPLETA de elementos comparados: por asignatura sus 4 campos con estado
    (una línea por asignatura), y los 8 PAO con ✓/✗.

Escribe el informe a `backend/data/resultados_evaluacion/jaccard_malla.md`.
"""
import os
import sys

# `completitud_malla` reenvuelve sys.stdout en UTF-8 al importarlo; no lo hacemos aqui
# para no envolverlo dos veces sobre el mismo buffer (provoca "I/O on closed file").
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from completitud_malla import (  # noqa: E402
    _anomalias_hpao, _rutas_corpus, _universo_y_faltantes, evaluar,
)
from plantilla_malla import (  # noqa: E402
    CAMPOS_ASIGNATURA, ORDINALES_PAO, PAO_ESPERADOS, VALOR_VACIO,
)

MARCA = {True: "✓", False: "✗"}  # ✓ / ✗
SALIDA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "resultados_evaluacion", "jaccard_malla.md",
)


def _estado_campo(fila, campo):
    ok = fila.get(campo) != VALOR_VACIO
    valor = str(fila.get(campo)) if ok else "VACIO"
    return ok, valor


def procesar():
    lineas = []
    w = lineas.append

    w("# Completitud / Jaccard de las mallas curriculares (Indicador 3)")
    w("")
    w("Evaluador: `scripts/completitud_malla.py` (reconstruccion por coordenadas, "
      "sin ChromaDB ni LLM).")
    w("")
    w("## Esquema comparado (universo A) por malla")
    w("")
    w("Por CADA asignatura reconstruida se comparan **4 campos** "
      "(los que pueden salir `VACIO`):")
    w("")
    for i, c in enumerate(CAMPOS_ASIGNATURA, 1):
        w(f"{i}. `{c}`")
    w("")
    w("Mas la **estructura del pensum**: los **8 PAO** (Primer ... Octavo). Universo "
      "`A = 4 x nº_asignaturas + 8`. `Jaccard = |rellenado| / |A|`.")
    w("")
    w("El **codigo** de asignatura es el ANCLA/identificador (la malla no lleva NRC): "
      "siempre presente por construccion, se reporta pero NO puntua como campo vacio.")
    w("")
    w("El invariante **HPAO = 48 x creditos** se controla aparte: una violacion es una "
      "ANOMALIA que se reporta, NO un campo vacio.")
    w("")
    w("Leyenda de estado por campo: `✓` relleno / `✗` VACIO.")
    w("")
    w("---")
    w("")

    resumen = []  # (nombre, j, n_asig, n_pao, n_anom, n_faltan)
    descartadas = []

    for ruta in _rutas_corpus():
        nombre = os.path.basename(ruta)
        filas, niveles, presentes = evaluar(ruta)
        if filas is None:
            descartadas.append(nombre)
            continue

        A, faltan = _universo_y_faltantes(filas, presentes)
        B = A - faltan
        j = len(B) / len(A) if A else 1.0
        anomalias = _anomalias_hpao(filas)

        resumen.append((nombre, j, len(filas), len(presentes),
                        len(anomalias), len(faltan)))

        w(f"## {nombre}")
        w("")
        w(f"- **Jaccard**: {j:.3f}  (|B|={len(B)} / |A|={len(A)})")
        w(f"- **Asignaturas reconstruidas**: {len(filas)}")
        w(f"- **PAO detectados**: {len(presentes)}/{PAO_ESPERADOS}")
        w(f"- **Anomalias HPAO=48xCR**: {len(anomalias)}"
          + ("" if not anomalias else
             "  -> " + ", ".join(f"{f['codigo']} (HPAO={f['hpao']}, CR={f['creditos']})"
                                 for f in anomalias)))
        if niveles:
            w(f"- **Niveles/unidades leidos**: {' | '.join(niveles)}")
        w("")

        w("### Lista completa de elementos comparados")
        w("")
        w("Por asignatura: `CODIGO | nombre | prerrequisito | hpao | creditos`")
        w("")
        w("```")
        for fila in filas:
            partes = []
            for campo in CAMPOS_ASIGNATURA:
                ok, valor = _estado_campo(fila, campo)
                partes.append(f"{campo}[{MARCA[ok]}]={valor}")
            w(f"{fila['codigo']:11} | " + " | ".join(partes))
        w("```")
        w("")

        w("### 8 PAO (estructura del pensum)")
        w("")
        pao_marks = []
        for i in range(1, PAO_ESPERADOS + 1):
            ok = i in presentes
            pao_marks.append(f"{MARCA[ok]} {ORDINALES_PAO[i-1]}")
        w("  ".join(pao_marks))
        w("")

        if anomalias:
            w("### Anomalias del invariante HPAO = 48 x creditos")
            w("")
            for f in anomalias:
                esperado = 48 * int(f["creditos"])
                w(f"- `{f['codigo']}` {f['nombre'][:40]}: "
                  f"HPAO={f['hpao']} != 48x{f['creditos']}={esperado}")
            w("")

        if faltan:
            w("### Elementos faltantes (VACIO o PAO ausente)")
            w("")
            for e in sorted(faltan):
                w(f"- {e}")
            w("")

        w("---")
        w("")

    # --- Resumen ---
    w("# Resumen del corpus")
    w("")
    w("| Malla | Jaccard | Asig | PAO | Anom. HPAO | Faltantes |")
    w("|-------|--------:|-----:|----:|-----------:|----------:|")
    for nombre, j, n_asig, n_pao, n_anom, n_faltan in resumen:
        w(f"| {nombre} | {j:.3f} | {n_asig} | {n_pao}/8 | {n_anom} | {n_faltan} |")
    w("")

    n = len(resumen)
    completas = sum(1 for r in resumen if r[1] == 1.0)
    medio = sum(r[1] for r in resumen) / n if n else 0.0
    w(f"- **Mallas evaluadas**: {n}")
    w(f"- **Mallas completas (J = 1.000)**: {completas} de {n}")
    w(f"- **Jaccard medio**: {medio:.3f}")
    w(f"- **PDFs descartados (no es una malla)**: {len(descartadas)}")
    if descartadas:
        for d in descartadas:
            w(f"  - {d}")
    w("")

    with open(SALIDA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))

    # --- eco a stdout para el reporte al agente ---
    print(f"Informe escrito en: {SALIDA}")
    print()
    print(f"Mallas evaluadas: {n}  |  J=1.000: {completas}  |  "
          f"Jaccard medio: {medio:.3f}  |  descartados: {len(descartadas)}")
    print()
    print(f"{'malla':50}{'J':>7}{'asig':>6}{'PAO':>5}{'anom':>6}{'falt':>6}")
    print("-" * 80)
    for nombre, j, n_asig, n_pao, n_anom, n_faltan in resumen:
        print(f"{nombre[:48]:50}{j:>7.3f}{n_asig:>6}{n_pao:>4}/8{n_anom:>6}{n_faltan:>6}")
    if descartadas:
        print()
        print("Descartados (no es malla):")
        for d in descartadas:
            print(f"  - {d}")


if __name__ == "__main__":
    procesar()
