"""
Evaluación con índice de Jaccard de la detección de elementos incompletos en el sílabo.

QUÉ ES JACCARD
--------------
Jaccard NO es una medida de "parecido entre dos documentos". Eso es sólo UNA de sus
aplicaciones (donde los conjuntos son las palabras de cada texto). Jaccard compara DOS
CONJUNTOS cualesquiera:

    J(A, B) = |A ∩ B| / |A ∪ B|

Aquí los dos conjuntos son dos OPINIONES SOBRE EL MISMO DOCUMENTO:

    A = los elementos incompletos que ve el AUDITOR humano
    B = los elementos incompletos que reporta el SISTEMA

Es el uso estándar en clasificación multietiqueta: la salida no es una etiqueta, sino un
subconjunto de etiquetas posibles.

QUÉ SE EVALÚA
-------------
Cada sílabo tiene 27 elementos verificables:

    20 CAMPOS  de la sección 1 (DATOS GENERALES): pares etiqueta -> valor.
     7 TABLAS  de las secciones 3 a 10: métodos, TIC, ponderación, bibliografía básica,
               bibliografía complementaria, lecturas principales, acuerdos.

El SISTEMA EN PRODUCCIÓN sólo verifica los 20 campos. Las 7 tablas las juzga el LLM, que
confunde la cabecera impresa con una fila de datos. Este script mide las dos cosas:

    (1) el sistema actual   -> 20 campos
    (2) sistema + tablas    -> 27 elementos (la propuesta del experimento)

y compara sus Jaccard contra la misma verdad de referencia.

Uso:
    python scripts/evaluar_jaccard.py
"""
import glob
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experimento_tablas import TABLAS, evaluar as evaluar_tablas  # noqa: E402
from services.extraccion import extraer_documento  # noqa: E402
from services.tareas_ia import (  # noqa: E402
    _abrir_base, _campos_sin_llenar, _plantilla_valida, _recuperar_norma,
)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SILABOS = (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
           r"\INDICADOR 4 Syllabus\*.pdf")

# ---------------------------------------------------------------------------
# VERDAD DE REFERENCIA — leída de los PDF, no de la salida del sistema.
# ---------------------------------------------------------------------------
# Los 24 sílabos institucionales tienen sus 20 campos llenos (verificado uno a uno).
# `silabus_trampa` es el formulario en blanco: los 20 campos vacíos y 6 de las 7 tablas.
# Tres sílabos reales tienen secciones genuinamente AUSENTES (verificado abriendo el PDF:
# el 21495 tiene 5 páginas en vez de 7 y no llega a la sección 9).
TABLAS_INCOMPLETAS = {
    "silabus_trampa": {"Métodos de enseñanza", "Empleo de TIC", "Ponderación de evaluación",
                       "Bibliografía básica", "Bibliografía complementaria",
                       "Lecturas principales"},
    "Silabo_NRC-21495": {"Empleo de TIC", "Lecturas principales", "Acuerdos del docente"},
    "Silabo_NRC-22670": {"Empleo de TIC"},
    "Silabo_NRC_21413": {"Lecturas principales"},
}

NOMBRES_TABLA = [n for n, _a, _c in TABLAS]


def verdad_de(nombre_fichero: str, campos: list):
    """Conjunto de elementos incompletos que ve el auditor humano."""
    incompletos = set()
    if "trampa" in nombre_fichero:
        incompletos |= set(campos)  # formulario en blanco: los 20 campos
    for clave, tablas in TABLAS_INCOMPLETAS.items():
        if nombre_fichero.startswith(clave):
            incompletos |= tablas
    return incompletos


def jaccard(a: set, b: set):
    """None si ambos son vacíos: 0/0 no es 1, es 'no hay nada que medir'."""
    union = a | b
    return None if not union else len(a & b) / len(union)


def main():
    vector_db = _abrir_base()

    filas = []
    for ruta in sorted(glob.glob(SILABOS)):
        nombre = os.path.basename(ruta)
        if "_Reporte" in nombre:
            continue

        documento = extraer_documento(ruta)
        _norma, meta = _recuperar_norma(vector_db, documento["texto"])
        valida, _faltan = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
        if not valida:
            continue  # no es la plantilla oficial: la Compuerta 5 no llega a ejecutarse

        campos = [c.strip() for c in meta["campos"].split(";") if c.strip()]
        vacios_sistema, _loc = _campos_sin_llenar(documento["cajas"], meta["campos"])
        tablas, tablas_vacias, tablas_ausentes = evaluar_tablas(ruta)

        A = verdad_de(nombre, campos)                       # auditor
        B_hoy = set(vacios_sistema)                         # sistema actual: 20 campos
        B_exp = B_hoy | set(tablas_vacias) | set(tablas_ausentes)  # + las 7 tablas

        filas.append({
            "nombre": nombre, "universo": len(campos) + len(NOMBRES_TABLA),
            "A": A, "B_hoy": B_hoy, "B_exp": B_exp,
        })

    def resumen(clave: str, titulo: str):
        tp = fp = fn = tn = exactos = 0
        jaccards, jaccards_reales = [], []
        for f in filas:
            A, B = f["A"], f[clave]
            tp += len(A & B); fp += len(B - A); fn += len(A - B)
            tn += f["universo"] - len(A | B)
            j = jaccard(A, B)
            jaccards.append(1.0 if j is None else j)
            if A:
                jaccards_reales.append(j)
            if A == B:
                exactos += 1

        n = len(filas)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

        print(f"\n{titulo}")
        print("-" * 74)
        print(f"  Verdaderos positivos (incompleto, y lo detecta) : {tp}")
        print(f"  Falsos positivos     (está lleno y dice vacío)  : {fp}")
        print(f"  Falsos negativos     (incompleto y NO lo ve)    : {fn}")
        print(f"  Verdaderos negativos                            : {tn}")
        print()
        print(f"  Precisión : {precision:.3f}    Recall : {recall:.3f}    F1 : {f1:.3f}")
        print(f"  Exact-match : {exactos}/{n} = {exactos / n:.3f}")
        print(f"  Jaccard medio (0/0 = 1)                    : {sum(jaccards) / n:.3f}")
        if jaccards_reales:
            media = sum(jaccards_reales) / len(jaccards_reales)
            print(f"  Jaccard SÓLO donde hay incompletos (n={len(jaccards_reales)})   : {media:.3f}")
        return recall, sum(jaccards) / n, (sum(jaccards_reales) / len(jaccards_reales)
                                           if jaccards_reales else 0.0)

    print("=" * 74)
    print("EVALUACIÓN CON ÍNDICE DE JACCARD — SÍLABOS")
    print("=" * 74)
    print(f"Sílabos con plantilla válida : {len(filas)}")
    print(f"Elementos verificables       : 20 campos + 7 tablas = 27 por documento")
    print(f"Total de decisiones          : {sum(f['universo'] for f in filas)}")
    con_incompletos = sum(1 for f in filas if f["A"])
    print(f"Documentos con algún elemento incompleto (según el auditor): {con_incompletos}")

    r1, j1, jr1 = resumen("B_hoy", "(1) SISTEMA ACTUAL — sólo verifica los 20 campos")
    r2, j2, jr2 = resumen("B_exp", "(2) SISTEMA + TABLAS — el experimento (27 elementos)")

    print()
    print("=" * 74)
    print("COMPARACIÓN")
    print("=" * 74)
    print(f"{'':34}{'actual':>12}{'+ tablas':>12}{'mejora':>12}")
    print(f"{'Recall':34}{r1:>12.3f}{r2:>12.3f}{r2 - r1:>+12.3f}")
    print(f"{'Jaccard medio':34}{j1:>12.3f}{j2:>12.3f}{j2 - j1:>+12.3f}")
    print(f"{'Jaccard (sólo con incompletos)':34}{jr1:>12.3f}{jr2:>12.3f}{jr2 - jr1:>+12.3f}")

    print()
    print("DETALLE POR DOCUMENTO (sólo los que tienen algo incompleto)")
    print("-" * 74)
    for f in filas:
        if not f["A"] and not f["B_exp"]:
            continue
        j_hoy, j_exp = jaccard(f["A"], f["B_hoy"]), jaccard(f["A"], f["B_exp"])
        print(f"  {f['nombre'][:52]}")
        print(f"      auditor  ({len(f['A']):2}) : {', '.join(sorted(f['A']))[:60] or '(ninguno)'}")
        print(f"      actual   ({len(f['B_hoy']):2}) : Jaccard {'—' if j_hoy is None else f'{j_hoy:.3f}'}")
        print(f"      + tablas ({len(f['B_exp']):2}) : Jaccard {'—' if j_exp is None else f'{j_exp:.3f}'}")

    print()
    print("POR QUÉ EL JACCARD MEDIO ENGAÑA")
    print("-" * 74)
    sin = len(filas) - con_incompletos
    print(f"En {sin} de {len(filas)} sílabos el auditor no halló NINGÚN elemento incompleto.")
    print("Ahí Jaccard es 0/0 (indefinido) y la convención lo cuenta como 1,0. Ese 1,0 no")
    print("premia haber detectado algo: premia que no hubiera nada que detectar. Un sistema")
    print("que nunca reportara nada sacaría 1,0 en todos ellos. Por eso hay que mirar la")
    print("segunda cifra, la de los documentos que SÍ tienen elementos incompletos.")


if __name__ == "__main__":
    main()
