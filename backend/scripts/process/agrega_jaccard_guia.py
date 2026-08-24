"""
Agrega la evaluación de completitud/Jaccard sobre TODAS las guías del corpus y emite,
POR CADA guía, la lista completa de los 27 elementos de la plantilla con su estado.

No abre ChromaDB ni gasta cuota LLM: reutiliza `evaluar()` de completitud_guia.py, que
reconoce la plantilla por marcadores y resuelve campos por coordenadas.

Salida:
    backend/data/resultados_evaluacion/jaccard_guia.md   (informe completo, todas las guías)
    + resumen por consola (inventario, una línea por guía, totales).
"""
import glob
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from completitud_guia import ANCLA_DE, GUIAS, SECCION_DE, evaluar, faltantes  # noqa: E402
from plantilla_guia import PLANTILLA_GUIA  # noqa: E402

VACIOS = ("AUSENTE", "VACÍO", "VACÍA")
ORDEN = list(ANCLA_DE)  # los 27 elementos en el orden de la plantilla


def secciones_en_orden():
    """Secciones únicas preservando el orden de PLANTILLA_GUIA."""
    vistas = []
    for _n, s, _t, _a in PLANTILLA_GUIA:
        if s not in vistas:
            vistas.append(s)
    return vistas


def marca(estado_valor):
    return "x" if estado_valor in VACIOS else "OK"


def main():
    salida_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "resultados_evaluacion",
    )
    os.makedirs(salida_dir, exist_ok=True)
    destino = os.path.join(salida_dir, "jaccard_guia.md")

    rutas = [r for r in sorted(glob.glob(GUIAS)) if "_Reporte" not in r]

    lineas_md = []
    lineas_md.append("# Evaluación de completitud (Jaccard) — Guías de laboratorio\n")
    lineas_md.append(
        "Indicador 6 — Escenarios de prácticas formativas. "
        "Cada guía se compara contra los **27 elementos** de la plantilla oficial "
        "(`plantilla_guia.py`). "
        "Jaccard = |elementos rellenados| / |27 de la plantilla|. "
        "Estado por elemento: valor detectado / `1+ filas` (LLENO), o "
        "`VACÍO` / `VACÍA` / `AUSENTE` (no cuenta).\n"
    )

    # --- Inventario (una vez) -------------------------------------------------
    lineas_md.append("## Inventario: los 27 elementos comparados (por sección)\n")
    inventario_txt = []
    n = 0
    for seccion in secciones_en_orden():
        lineas_md.append(f"**{seccion}**\n")
        inventario_txt.append(f"  {seccion}")
        for nombre, s, tipo, _a in PLANTILLA_GUIA:
            if s == seccion:
                n += 1
                lineas_md.append(f"{n}. `[{tipo}]` {nombre}")
                inventario_txt.append(f"     {n:2}. [{tipo:10}] {nombre}")
        lineas_md.append("")

    resumen = []       # (nombre, j, faltan_lista)
    no_plantilla = []

    for ruta in rutas:
        nombre_archivo = os.path.basename(ruta)
        estado = evaluar(ruta)
        if estado is None:
            no_plantilla.append(nombre_archivo)
            lineas_md.append(f"## {nombre_archivo}\n")
            lineas_md.append("> No usa la plantilla oficial de la guía "
                             "(faltan los marcadores). No se evalúa.\n")
            continue

        A = set(ANCLA_DE)
        faltan = faltantes(estado)
        B = A - faltan
        j = len(B) / len(A)
        resumen.append((nombre_archivo, j, sorted(faltan, key=ORDEN.index)))

        lineas_md.append(f"## {nombre_archivo}\n")
        lineas_md.append(
            f"**Jaccard = {len(B)} / {len(A)} = {j:.3f}**  ·  "
            f"27 elementos  ·  rellenados: {len(B)}  ·  faltantes: {len(faltan)}\n"
        )

        idx = 0
        for seccion in secciones_en_orden():
            lineas_md.append(f"### {seccion}")
            for nombre, s, _t, _a in PLANTILLA_GUIA:
                if s != seccion:
                    continue
                idx += 1
                valor = estado[nombre]
                simbolo = "✗" if valor in VACIOS else "✓"
                lineas_md.append(f"- {simbolo} **{nombre}** — `{valor}`")
            lineas_md.append("")

    # --- Totales --------------------------------------------------------------
    js = [j for _n, j, _f in resumen]
    n_guias = len(resumen)
    completas = sum(1 for j in js if j == 1.0)
    medio = sum(js) / len(js) if js else 0.0

    lineas_md.append("## Totales\n")
    lineas_md.append(f"- Guías evaluadas: **{n_guias}**")
    lineas_md.append(f"- Completas (J = 1.000): **{completas}**")
    lineas_md.append(f"- Jaccard medio del corpus: **{medio:.3f}**")
    if no_plantilla:
        lineas_md.append(f"- Archivos sin plantilla reconocida: {len(no_plantilla)} "
                        f"({', '.join(no_plantilla)})")
    lineas_md.append("")

    with io.open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_md))

    # ======================= REPORTE POR CONSOLA =============================
    print("=" * 78)
    print("INVENTARIO — los 27 elementos comparados (universo de la plantilla)")
    print("=" * 78)
    for linea in inventario_txt:
        print(linea)

    print()
    print("=" * 78)
    print("RESUMEN POR GUÍA")
    print("=" * 78)
    for nombre_archivo, j, faltan in resumen:
        lista = ", ".join(faltan) if faltan else "—"
        print(f"{nombre_archivo[:44]:46} | J={j:.3f} | 27 elementos | vacíos: [{lista}]")
    for nombre_archivo in no_plantilla:
        print(f"{nombre_archivo[:44]:46} | plantilla NO reconocida")

    print()
    print("=" * 78)
    print("TOTALES")
    print("=" * 78)
    print(f"  Guías evaluadas          : {n_guias}")
    print(f"  Completas (J = 1.000)    : {completas}")
    print(f"  Jaccard medio del corpus : {medio:.3f}")
    if no_plantilla:
        print(f"  Sin plantilla reconocida : {len(no_plantilla)} -> {no_plantilla}")
    print()
    print(f"  Informe completo escrito en:\n    {destino}")


if __name__ == "__main__":
    main()
