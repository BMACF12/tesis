"""
Extrae la lista de asignaturas de la malla curricular oficial y la guarda en
`data/asignaturas_malla.txt`.

Es la fuente de verdad para decidir si un sílabo pertenece a la carrera: el resumen
escrito a mano en `ingestar_maestro.py` omitía asignaturas reales (por ejemplo
"Aplicaciones Basadas en el Conocimiento"), de modo que sus sílabos no podían
verificarse contra nada.

Uso:
    python scripts/extraer_asignaturas.py "ruta/a/malla.pdf"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extraccion import _cajas, es_malla, filas_de_malla  # noqa: E402

CABECERA = (
    "# Asignaturas de la malla curricular vigente de Ingeniería de Software.\n"
    "# Generado por scripts/extraer_asignaturas.py a partir de la malla oficial.\n"
    "# Fuente única para validar la pertinencia de un sílabo a la carrera.\n"
)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)

    ruta_malla = sys.argv[1]
    cajas, _ = _cajas(ruta_malla)
    if not es_malla(cajas):
        print(f"Error: {ruta_malla} no parece una malla curricular (faltan HPAO y códigos).")
        raise SystemExit(1)

    filas = filas_de_malla(cajas)
    nombres = sorted({f["nombre"] for f in filas if f["nombre"] != "VACIO"})

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(base_dir, "data", "asignaturas_malla.txt")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(CABECERA + "\n".join(nombres) + "\n")

    print(f"{len(filas)} asignaturas leídas de la malla, {len(nombres)} nombres únicos.")
    print(f"Escrito en {destino}")
    incompletas = [f for f in filas if "VACIO" in (f["nombre"], f["prerrequisito"], f["hpao"], f["creditos"])]
    if incompletas:
        print(f"Aviso: {len(incompletas)} asignatura(s) con algún campo vacío: "
              + ", ".join(f["codigo"] for f in incompletas))


if __name__ == "__main__":
    main()
