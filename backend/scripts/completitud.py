"""
Índice de Jaccard entre la PLANTILLA OFICIAL y un sílabo concreto. Sin auditor.

    A = los 39 elementos que exige el formulario SGC.DI.321 (plantilla vacía)
    B = los elementos que ESTE documento tiene realmente rellenados

    J(A, B) = |A ∩ B| / |A ∪ B|

Como B siempre está contenido en A (un sílabo no puede tener elementos que la plantilla no
contemple), A ∪ B = A y la fórmula se reduce a |B| / |A|: la fracción de la plantilla que
el documento cumple. Es Jaccard legítimo —el caso clásico de "parecido con un documento de
referencia"— y conviene decirlo así: en esta configuración equivale a un porcentaje de
completitud.

    J = 1,000  el documento rellena TODA la plantilla
    J < 1,000  le faltan elementos; cuanto más bajo, más incompleto

Uso:
    python scripts/completitud.py 21278           # un documento
    python scripts/completitud.py --todos         # todo el corpus de sílabos
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plantilla_silabo import PLANTILLA_SILABO, RUIDO_SILABO  # noqa: E402
from services.extraccion import (  # noqa: E402
    _agrupar_filas, _valor_de, extraer_documento, normalizar, resolver_campos,
)
from services.tareas_ia import _abrir_base, _plantilla_valida, _recuperar_norma  # noqa: E402

SILABOS = (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
           r"\INDICADOR 4 Syllabus\*.pdf")

RUIDO = tuple(normalizar(t) for t in RUIDO_SILABO)
_SECCION_NUM = re.compile(r"^\s*\d{1,2}\.\s+[A-ZÁÉÍÓÚÑ]")

CAMPOS = [n for n, _s, t, _a in PLANTILLA_SILABO if t == "campo"]
# El PDF lleva la ETIQUETA (p. ej. "POSGRADO"), no el nombre de mi inventario ("Perfil del
# docente: POSGRADO"). Se busca por el ancla y luego se traduce al nombre.
ANCLAS_DE_CAMPO = {a: n for n, _s, t, a in PLANTILLA_SILABO if t == "campo"}
ANCLA_DE = {n: a for n, _s, _t, a in PLANTILLA_SILABO}
TIPO_DE = {n: t for n, _s, t, _a in PLANTILLA_SILABO}
SECCION_DE = {n: s for n, s, _t, _a in PLANTILLA_SILABO}


def _tiene_contenido(linea: str, exige_numero: bool = False) -> bool:
    """¿Es contenido escrito por el docente, o texto impreso de la plantilla?"""
    limpio = " ".join(linea.split())
    if not limpio or "SGC.DI.321" in limpio or _SECCION_NUM.match(limpio):
        return False
    celdas = [c.strip() for c in limpio.split("|") if c.strip()]
    utiles = [c for c in celdas if not c.rstrip(".").isdigit()]
    if not utiles:
        return False  # numeración huérfana: "1", "2", "3" sin nada al lado
    if all(normalizar(c) in RUIDO for c in utiles):
        return False  # sólo la cabecera impresa de la tabla
    if exige_numero and not any(c.strip().isdigit() for c in celdas):
        return False  # una técnica de evaluación sin ninguna nota está incompleta
    return sum(len(c) for c in utiles) >= 8


def _coincide(linea: str, ancla: str) -> bool:
    """Un ancla con '=' delante exige que la línea sea EXACTAMENTE ese texto."""
    return linea.strip() == ancla[1:] if ancla.startswith("=") else ancla in linea


def _campos_fusionados(cajas, campos, ya_resueltos):
    """
    Rescata los campos cuya ETIQUETA Y VALOR viven en la MISMA caja de texto.

    pdfminer a veces no separa la celda: devuelve "Fecha de Actualización 27/11/2020" o
    "POSGRADO: Maestría y/o Doctorado..." como un único bloque. El resolvedor de producción
    busca una caja que SEA la etiqueta y luego el valor en otra: con la caja fusionada no
    encuentra ninguna de las dos cosas y el campo parece ausente.

    Sólo se usa para los campos que el resolvedor normal no supo resolver.
    """
    rescatados = {}
    pendientes = [c for c in campos if not ya_resueltos.get(c)]
    for caja in cajas:
        texto = " ".join(caja["t"].split())
        for campo in pendientes:
            if campo in rescatados:
                continue
            # La caja debe EMPEZAR por la etiqueta y traer algo más detrás. Se exige que
            # empiece, no que contenga: si no, "GRADO" casaría con "PREGRADO S-I ABR 25".
            for separador in (": ", " "):
                prefijo = campo + separador
                if texto.upper().startswith(prefijo.upper()) and len(texto) > len(prefijo):
                    resto = texto[len(prefijo):].strip()
                    if resto:
                        rescatados[campo] = resto[:34]
                    break
    return rescatados


# Cabeceras de tabla de DATOS GENERALES cuyos valores están en la fila de abajo, alineados
# por índice de columna. El resolvedor general no los alcanza porque entre la cabecera y los
# valores se interpone otra fila.
CABECERAS_DE_TABLA = {
    "DOCENCIA": "Carga horaria: docencia",
    "PRACTICAS DE APLICACIÓN Y EXPERIMENTACIÓN": "Carga horaria: prácticas",
    "APRENDIZAJE AUTÓNOMO": "Carga horaria: aprendizaje autónomo",
}


def _celdas_de_tabla(cajas, ya_resueltos):
    """
    Resuelve la fila de carga horaria: tres cabeceras y, dos filas más abajo, sus tres
    valores ("48 | 48 | 48"). Se emparejan por índice de columna, no por distancia.
    """
    filas = _agrupar_filas(cajas)
    rescatados = {}
    for i, fila in enumerate(filas):
        etiquetas = [c["t"].strip().upper() for c in fila]
        if not all(e in CABECERAS_DE_TABLA for e in etiquetas) or len(fila) < 2:
            continue
        # La fila de valores es la primera de abajo con tantos números como columnas.
        for k in range(i + 1, min(i + 4, len(filas))):
            numeros = [c["t"] for c in filas[k] if c["t"].strip().isdigit()]
            if len(numeros) == len(fila):
                for etiqueta, valor in zip(etiquetas, numeros):
                    rescatados[CABECERAS_DE_TABLA[etiqueta]] = valor
                break
    return {k: v for k, v in rescatados.items() if not ya_resueltos.get(k)}


def evaluar(ruta):
    """Devuelve (metadatos, {elemento: estado}) o (metadatos, None) si no es la plantilla."""
    documento = extraer_documento(ruta)
    _norma, meta = _recuperar_norma(_abrir_base(), documento["texto"])
    valida, faltan = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
    if not valida or meta.get("indicador") != 4:
        return meta, None, faltan

    lineas = documento["texto"].split("\n")
    mayusculas = [l.upper() for l in lineas]
    anclas = [ANCLA_DE[n] for n in ANCLA_DE]

    anclas_campo = list(ANCLAS_DE_CAMPO)
    crudos = resolver_campos(documento["cajas"], anclas_campo)
    crudos.update(_campos_fusionados(documento["cajas"], anclas_campo, crudos))
    # Traducir de la etiqueta del PDF al nombre del inventario.
    valores = {ANCLAS_DE_CAMPO[a]: v for a, v in crudos.items() if a in ANCLAS_DE_CAMPO}
    valores.update(_celdas_de_tabla(documento["cajas"], valores))
    estado = {}

    for nombre, _seccion, tipo, ancla in PLANTILLA_SILABO:
        if tipo == "campo":
            valor = valores.get(nombre)
            if nombre not in valores:
                estado[nombre] = "AUSENTE"       # ni siquiera está la etiqueta
            elif not valor:
                estado[nombre] = "VACÍO"
            else:
                estado[nombre] = valor[:34]
            continue

        # tabla, lista o bloque: hay que contar filas de contenido
        inicio = next((i for i, l in enumerate(mayusculas) if _coincide(l, ancla.upper())), None)
        if inicio is None:
            estado[nombre] = "AUSENTE"
            continue

        fin = len(lineas)
        for j in range(inicio + 1, len(lineas)):
            linea = mayusculas[j].strip()
            otras = [a.upper() for a in anclas if a != ancla]
            if _SECCION_NUM.match(linea) or any(
                    linea == a[1:] if a.startswith("=") else linea.startswith(a) for a in otras):
                fin = j
                break

        filas = sum(1 for j in range(inicio + 1, fin)
                    if _tiene_contenido(lineas[j], exige_numero=(tipo == "tabla-num")))
        estado[nombre] = f"{filas} filas" if filas else "VACÍA"

    return meta, estado, []


def faltantes(estado: dict) -> set:
    return {n for n, e in estado.items() if e in ("AUSENTE", "VACÍO", "VACÍA")}


def informe(ruta):
    _meta, estado, faltan_marcadores = evaluar(ruta)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("=" * 78)

    if estado is None:
        print(f"\nNo usa la plantilla oficial del sílabo. Faltan: {'; '.join(faltan_marcadores)}")
        return None

    A = set(ANCLA_DE)                    # los 39 elementos de la plantilla
    faltan = faltantes(estado)
    B = A - faltan                       # los que el documento sí rellena

    seccion = None
    for nombre, _s, _t, _a in PLANTILLA_SILABO:
        if SECCION_DE[nombre] != seccion:
            seccion = SECCION_DE[nombre]
            print(f"\n  {seccion}")
        valor = estado[nombre]
        vacio = valor in ("AUSENTE", "VACÍO", "VACÍA")
        print(f"   {'!' if vacio else ' '} {nombre[:42]:44}{valor}")

    interseccion, union = A & B, A | B
    j = len(interseccion) / len(union)

    print()
    print("=" * 78)
    print("ÍNDICE DE JACCARD  (plantilla oficial  vs  este documento)")
    print("=" * 78)
    print(f"  A = plantilla SGC.DI.321        : {len(A)} elementos")
    print(f"  B = elementos rellenados aquí   : {len(B)} elementos")
    print()
    print(f"  |A ∩ B| = {len(interseccion)}      |A ∪ B| = {len(union)}")
    print()
    print(f"  JACCARD = {len(interseccion)} / {len(union)} = {j:.3f}")
    print()
    if faltan:
        print(f"  LE FALTAN {len(faltan)} ELEMENTOS:")
        for nombre in sorted(faltan, key=lambda n: list(ANCLA_DE).index(n)):
            print(f"      - {nombre}   ({estado[nombre]})")
    else:
        print("  El documento rellena TODA la plantilla.")
    return j


def todos():
    print(f"{'documento':46}{'B':>4}{'A':>4}{'JACCARD':>10}   le falta")
    print("-" * 100)
    resultados = []
    for ruta in sorted(glob.glob(SILABOS)):
        if "_Reporte" in ruta:
            continue
        _meta, estado, _f = evaluar(ruta)
        nombre = os.path.basename(ruta)[:44]
        if estado is None:
            print(f"{nombre:46}   plantilla no reconocida")
            continue
        A = set(ANCLA_DE)
        faltan = faltantes(estado)
        B = A - faltan
        j = len(B) / len(A)
        resultados.append(j)
        lista = ", ".join(sorted(faltan))[:44] if faltan else ""
        print(f"{nombre:46}{len(B):>4}{len(A):>4}{j:>10.3f}   {lista}")
    print("-" * 100)
    if resultados:
        print(f"Jaccard medio del corpus: {sum(resultados) / len(resultados):.3f}")
        print(f"Sílabos completos (J = 1,000): {sum(1 for j in resultados if j == 1.0)}"
              f" de {len(resultados)}")


def buscar(fragmento):
    encontrados = [r for r in sorted(glob.glob(SILABOS))
                   if "_Reporte" not in r and fragmento.lower() in os.path.basename(r).lower()]
    if not encontrados:
        print(f"No encontré ningún sílabo con '{fragmento}'.")
        raise SystemExit(1)
    return encontrados[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--todos":
        todos()
    else:
        informe(buscar(sys.argv[1]))
