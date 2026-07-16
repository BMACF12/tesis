"""
Índice de Jaccard entre la PLANTILLA OFICIAL de la guía de laboratorio y una guía concreta.
Es el análogo de `completitud.py` (que hace lo mismo para el sílabo). Sin auditor humano.

    A = los 27 elementos que exige el formulario de la guía (plantilla vacía)
    B = los elementos que ESTE documento tiene realmente rellenados

    J(A, B) = |A ∩ B| / |A ∪ B|

Como B siempre está contenido en A (una guía no puede rellenar algo que la plantilla no
contempla), A ∪ B = A y la fórmula se reduce a |B| / |A|: la fracción de la plantilla que el
documento cumple. Es Jaccard legítimo —el caso clásico de "parecido con un documento de
referencia"— y en esta configuración equivale a un porcentaje de completitud.

A diferencia de `completitud.py`, este script NO abre ChromaDB ni gasta cuota: reconoce la
plantilla por sus marcadores y resuelve los campos por coordenadas. Se puede correr sobre
todo el corpus sin arrancar nada.

Además del Jaccard plantilla-vs-documento, admite el Jaccard AUDITOR-vs-sistema (como el
`jaccard.py` del sílabo): pásale con `--faltan` lo que TÚ ves faltar al abrir el PDF y
compara tu lista (A) con la que detecta el sistema (B). Es el único tool de guías: reemplaza
la rama de guía que tenía `jaccard.py` (que contaba dos veces sección y campo).

Uso:
    python scripts/completitud_guia.py 3.3            # una guía (fragmento del nombre)
    python scripts/completitud_guia.py --todos        # todo el corpus de guías
    python scripts/completitud_guia.py 3.1 --faltan "Fecha, Departamento, Laboratorio"
    python scripts/completitud_guia.py 1.1 --faltan ""   # el auditor dice: no falta nada
"""
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plantilla_guia import (  # noqa: E402
    CABECERA_APROBACION, CABECERA_CONTROL, CAMPOS_GUIA, PLANTILLA_GUIA,
)
from services.extraccion import (  # noqa: E402
    comparable, extraer_documento, normalizar, resolver_campos,
)

GUIAS = r"C:\Users\User\Downloads\GUIAS\GUIAS\*.pdf"

# Marcadores de la plantilla de la guía (los mismos de la base de oro, Indicador 6).
MARCADORES = ("GUIA DE USO DE LABORATORIO", "A. INFORMACIÓN DE LA GUÍA")

SECCION_DE = {n: s for n, s, _t, _a in PLANTILLA_GUIA}
TIPO_DE = {n: t for n, _s, t, _a in PLANTILLA_GUIA}
ANCLA_DE = {n: a for n, _s, _t, a in PLANTILLA_GUIA}
# El resolvedor devuelve el resultado bajo la ETIQUETA del PDF; se traduce al nombre corto.
NOMBRE_DE_ANCLA = {a: n for n, _s, t, a in PLANTILLA_GUIA if t in ("campo", "bloque")}

_RUIDO_CONTROL = frozenset(normalizar(c) for c in CABECERA_CONTROL)
_RUIDO_APROBACION = frozenset(normalizar(c) for c in CABECERA_APROBACION)


def es_plantilla(texto: str) -> bool:
    doc = comparable(texto)
    return all(comparable(m) in doc for m in MARCADORES)


def _celdas(linea: str) -> list:
    return [c.strip() for c in linea.split("|") if c.strip()]


def _tabla_con_filas(lineas: list, ancla: str, corte: str, ruido: frozenset) -> bool:
    """¿La tabla que empieza en `ancla` trae al menos una fila de datos antes de `corte`?"""
    mayus = [l.upper() for l in lineas]
    inicio = next((i for i, l in enumerate(mayus) if ancla.upper() in l), None)
    if inicio is None:
        return None  # sección ausente
    for j in range(inicio + 1, len(lineas)):
        if corte.upper() in mayus[j]:
            break
        celdas = _celdas(lineas[j])
        utiles = [c for c in celdas if normalizar(c) not in ruido]
        # Descarta el encabezado impreso, el ruido de pie de página y las líneas cortas.
        if utiles and sum(len(c) for c in utiles) >= 6 and "GUIA DE USO" not in mayus[j]:
            return True
    return False


def _fila_aprobacion(lineas: list, rubro: str) -> str:
    """Estado de una fila de C. APROBACIÓN: AUSENTE, VACÍA (sin nombre) o el nombre."""
    for linea in lineas:
        if linea.strip().upper().startswith(rubro.upper()):
            celdas = _celdas(linea)
            # celdas[0] es el rubro ("Elaborado por:"); el nombre es la siguiente celda útil.
            resto = [c for c in celdas[1:] if normalizar(c) not in _RUIDO_APROBACION]
            if resto and len(resto[0]) >= 3:
                return resto[0][:34]
            return "VACÍA"
    return "AUSENTE"


def evaluar(ruta):
    """Devuelve {elemento: estado} o None si no es la plantilla de la guía."""
    documento = extraer_documento(ruta)
    if not es_plantilla(documento["texto"]):
        return None

    lineas = documento["texto"].split("\n")
    crudos = resolver_campos(documento["cajas"], CAMPOS_GUIA)
    valores = {NOMBRE_DE_ANCLA[a]: v for a, v in crudos.items() if a in NOMBRE_DE_ANCLA}

    estado = {}
    for nombre, _seccion, tipo, ancla in PLANTILLA_GUIA:
        if tipo in ("campo", "bloque"):
            if nombre not in valores:
                estado[nombre] = "AUSENTE"          # ni siquiera está la etiqueta
            elif not valores[nombre]:
                estado[nombre] = "VACÍO"
            else:
                estado[nombre] = str(valores[nombre])[:34]
        elif tipo == "tabla":
            con_filas = _tabla_con_filas(lineas, ancla, "C. APROBACI", _RUIDO_CONTROL)
            estado[nombre] = "AUSENTE" if con_filas is None else ("1+ filas" if con_filas else "VACÍA")
        else:  # aprobacion
            estado[nombre] = _fila_aprobacion(lineas, ancla)
    return estado


def faltantes(estado: dict) -> set:
    return {n for n, e in estado.items() if e in ("AUSENTE", "VACÍO", "VACÍA")}


def informe(ruta):
    estado = evaluar(ruta)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("=" * 78)
    if estado is None:
        print("\nNo usa la plantilla oficial de la guía (faltan los marcadores).")
        return None

    A = set(ANCLA_DE)                     # los 27 elementos de la plantilla
    faltan = faltantes(estado)
    B = A - faltan                        # los que el documento sí rellena

    seccion = None
    for nombre, _s, _t, _a in PLANTILLA_GUIA:
        if SECCION_DE[nombre] != seccion:
            seccion = SECCION_DE[nombre]
            print(f"\n  {seccion}")
        valor = estado[nombre]
        vacio = valor in ("AUSENTE", "VACÍO", "VACÍA")
        print(f"   {'!' if vacio else ' '} {nombre[:42]:44}{valor}")

    j = len(A & B) / len(A | B)
    print()
    print("=" * 78)
    print("ÍNDICE DE JACCARD  (plantilla oficial de la guía  vs  este documento)")
    print("=" * 78)
    print(f"  A = plantilla de la guía        : {len(A)} elementos")
    print(f"  B = elementos rellenados aquí   : {len(B)} elementos")
    print()
    print(f"  |A ∩ B| = {len(A & B)}      |A ∪ B| = {len(A | B)}")
    print()
    print(f"  JACCARD = {len(A & B)} / {len(A | B)} = {j:.3f}")
    print()
    if faltan:
        print(f"  LE FALTAN {len(faltan)} ELEMENTOS:")
        for nombre in sorted(faltan, key=lambda n: list(ANCLA_DE).index(n)):
            print(f"      - {nombre}   ({estado[nombre]})")
    else:
        print("  El documento rellena TODA la plantilla.")
    return j


def todos():
    print(f"{'documento':52}{'B':>4}{'A':>4}{'JACCARD':>10}   le falta")
    print("-" * 108)
    resultados = []
    for ruta in sorted(glob.glob(GUIAS)):
        if "_Reporte" in ruta:
            continue
        estado = evaluar(ruta)
        nombre = os.path.basename(ruta)[:50]
        if estado is None:
            print(f"{nombre:52}   plantilla no reconocida")
            continue
        A = set(ANCLA_DE)
        faltan = faltantes(estado)
        B = A - faltan
        j = len(B) / len(A)
        resultados.append(j)
        lista = ", ".join(sorted(faltan))[:36] if faltan else ""
        print(f"{nombre:52}{len(B):>4}{len(A):>4}{j:>10.3f}   {lista}")
    print("-" * 108)
    if resultados:
        print(f"Jaccard medio del corpus: {sum(resultados) / len(resultados):.3f}")
        print(f"Guías completas (J = 1,000): {sum(1 for j in resultados if j == 1.0)}"
              f" de {len(resultados)}")


def auditor(ruta, crudo):
    """Jaccard AUDITOR (A, tu lectura del PDF) vs SISTEMA (B, lo que detecta)."""
    estado = evaluar(ruta)
    if estado is None:
        print("No usa la plantilla oficial de la guía. No hay elementos que comparar.")
        return

    B = faltantes(estado)
    universo = list(ANCLA_DE)
    A = set()
    for pedido in (p.strip() for p in crudo.split(",") if p.strip()):
        candidatos = [u for u in universo if pedido.lower() in u.lower()]
        if len(candidatos) == 1:
            A.add(candidatos[0])
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es un elemento de esta guía. Se ignora.")
        else:
            print(f"'{pedido}' es ambiguo: {candidatos}. Escríbelo completo.")
            raise SystemExit(1)

    interseccion, union = A & B, A | B
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("ÍNDICE DE JACCARD  (auditor  vs  sistema)")
    print("=" * 78)
    print(f"  A (auditor: lo que TÚ ves faltar)  = {sorted(A) if A else '(nada)'}")
    print(f"  B (sistema: lo que él detecta)     = {sorted(B) if B else '(nada)'}")
    print()
    if not union:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
        print("  La guía está completa y el sistema tampoco reporta nada: no hay lista de")
        print("  faltantes que comparar. La convención lo cuenta como 1,0, pero ese 1,0 no")
        print("  premia detectar algo, premia que no hubiera nada que detectar.")
    else:
        j = len(interseccion) / len(union)
        print(f"  |A ∩ B| = {len(interseccion)}      |A ∪ B| = {len(union)}")
        print(f"  JACCARD = {len(interseccion)} / {len(union)} = {j:.3f}")
    falsos_negativos, falsos_positivos = A - B, B - A
    print()
    if falsos_negativos:
        print(f"  SE LE ESCAPAN ({len(falsos_negativos)}): {sorted(falsos_negativos)}")
    if falsos_positivos:
        print(f"  SE INVENTA ({len(falsos_positivos)}): {sorted(falsos_positivos)}")
    if not falsos_negativos and not falsos_positivos and union:
        print("  Sin falsos positivos ni falsos negativos.")


def buscar(fragmento):
    encontrados = [r for r in sorted(glob.glob(GUIAS))
                   if "_Reporte" not in r and fragmento.lower() in os.path.basename(r).lower()]
    if not encontrados:
        print(f"No encontré ninguna guía con '{fragmento}'.")
        raise SystemExit(1)
    return encontrados[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--todos":
        todos()
    elif "--faltan" in sys.argv:
        ruta = buscar(sys.argv[1])
        auditor(ruta, sys.argv[sys.argv.index("--faltan") + 1])
    else:
        informe(buscar(sys.argv[1]))
