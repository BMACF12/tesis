"""
Agrega la evaluacion de completitud/Jaccard sobre TODO el corpus de silabos y
emite un informe markdown con los 39 elementos y su estado por cada silabo.

Abre ChromaDB UNA sola vez (cachea _abrir_base) para no reabrirla por documento.
"""
import glob
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import completitud  # noqa: E402
from completitud import ANCLA_DE, SECCION_DE, SILABOS, evaluar, faltantes  # noqa: E402
from plantilla_silabo import PLANTILLA_SILABO  # noqa: E402

# --- Abrir ChromaDB una sola vez ------------------------------------------
_BASE = None
_abrir_real = completitud._abrir_base


def _abrir_cacheada():
    global _BASE
    if _BASE is None:
        _BASE = _abrir_real()
    return _BASE


completitud._abrir_base = _abrir_cacheada

SALIDA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "resultados_evaluacion", "jaccard_silabo.md",
)

ORDEN = list(ANCLA_DE)  # los 39 elementos, en orden de la plantilla


def marca(estado_valor):
    return "x" if estado_valor in ("AUSENTE", "VACÍO", "VACÍA") else " "


def main():
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    rutas = [r for r in sorted(glob.glob(SILABOS)) if "_Reporte" not in r]

    lineas = []
    lineas.append("# Evaluacion de completitud / Jaccard — Indicador 4 (Silabo SGC.DI.321)\n")
    lineas.append("Cada silabo se compara contra el inventario oficial de **39 elementos** de la "
                  "plantilla SGC.DI.321.\n")
    lineas.append("`J = |elementos rellenados| / |39 de la plantilla|`. "
                  "Marca `[x]` = vacio/ausente, `[✓]` = relleno.\n")

    resumen = []
    jotas = []
    n_no_plantilla = 0

    for ruta in rutas:
        nombre = os.path.basename(ruta)
        _meta, estado, faltan_marc = evaluar(ruta)

        if estado is None:
            n_no_plantilla += 1
            lineas.append("\n---\n")
            lineas.append(f"\n## {nombre}\n")
            detalle = "; ".join(faltan_marc) or "(marcadores presentes pero no enruta al Indicador 4)"
            lineas.append(f"\n**NO usa la plantilla oficial del silabo.** "
                          f"Faltan marcadores: {detalle}\n")
            resumen.append(f"{nombre} | NO USA PLANTILLA OFICIAL")
            continue

        faltan = faltantes(estado)
        j = (len(ORDEN) - len(faltan)) / len(ORDEN)
        jotas.append(j)

        lineas.append("\n---\n")
        lineas.append(f"\n## {nombre}\n")
        lineas.append(f"\n**Jaccard = {j:.3f}**  ({len(ORDEN) - len(faltan)}/{len(ORDEN)} "
                      f"elementos rellenados)\n")

        seccion = None
        for nombre_el, _s, tipo, _a in PLANTILLA_SILABO:
            if SECCION_DE[nombre_el] != seccion:
                seccion = SECCION_DE[nombre_el]
                lineas.append(f"\n### {seccion}\n")
            valor = estado[nombre_el]
            lineas.append(f"- [{marca(valor)}] **{nombre_el}** ({tipo}) — {valor}")

        vacios = sorted(faltan, key=lambda n: ORDEN.index(n))
        resumen.append(
            f"{nombre} | J={j:.3f} | 39 elementos | "
            f"vacios: [{', '.join(vacios) if vacios else 'ninguno'}]"
        )

    # Resumen global al inicio del cuerpo (lo insertamos tras la cabecera)
    cabecera = lineas[:4]
    cuerpo = lineas[4:]

    resumen_md = ["\n## Resumen por silabo\n"]
    for r in resumen:
        resumen_md.append(f"- {r}")
    if jotas:
        resumen_md.append(f"\n**Totales:** {len(rutas)} silabos evaluados "
                          f"({len(jotas)} con plantilla oficial, {n_no_plantilla} sin plantilla). "
                          f"Completos (J=1.000): {sum(1 for j in jotas if j == 1.0)}. "
                          f"Jaccard medio: {sum(jotas) / len(jotas):.3f}.\n")

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(cabecera) + "\n")
        f.write("\n".join(resumen_md) + "\n")
        f.write("\n".join(cuerpo) + "\n")

    # ---- Salida por consola para el reporte ----
    print("INVENTARIO (39 elementos por seccion):")
    seccion = None
    for i, (nombre_el, _s, tipo, _a) in enumerate(PLANTILLA_SILABO, 1):
        if SECCION_DE[nombre_el] != seccion:
            seccion = SECCION_DE[nombre_el]
            print(f"\n  {seccion}")
        print(f"    {i:2}. [{tipo:9}] {nombre_el}")

    print("\n\nRESUMEN POR SILABO:")
    for r in resumen:
        print(f"  {r}")

    if jotas:
        print(f"\nTOTALES: {len(rutas)} silabos | {len(jotas)} con plantilla, "
              f"{n_no_plantilla} sin plantilla | completos J=1.000: "
              f"{sum(1 for j in jotas if j == 1.0)} | Jaccard medio: "
              f"{sum(jotas) / len(jotas):.3f}")
    print(f"\nArchivo: {SALIDA}")


if __name__ == "__main__":
    main()
