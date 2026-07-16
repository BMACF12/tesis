"""
Esquema oficial de la MALLA CURRICULAR (Indicador 3).

A diferencia del sílabo (`plantilla_silabo.py`) o de la guía (`plantilla_guia.py`), la malla
NO es un formulario con una lista fija de campos etiqueta→valor: es un diagrama por
coordenadas. Su "plantilla" no son 39 ni 27 casillas, sino un ESQUEMA que se repite por cada
asignatura, más una expectativa estructural del pénsum. Este módulo fija ese esquema y las
constantes que comparte con `completitud_malla.py` (el evaluador de Jaccard por completitud).

La malla ES texto estructurado (hay capa de texto en el PDF); el sistema la reconstruye con
`filas_de_malla` (`extraccion.py`), que entrega una línea por asignatura
`CODIGO | NOMBRE | PRE: … | HPAO: … | CR: …` usando la palabra literal "VACIO" para un campo
sin llenar. Esa reconstrucción es la que este esquema evalúa.

Esquema por asignatura
----------------------
    codigo         : IDENTIFICADOR / ANCLA. La malla NO lleva NRC; el identificador de la
                     materia es el código de asignatura (5 letras + 4 alfanuméricos,
                     p. ej. EXCTA0301). Por construcción una fila reconstruida siempre tiene
                     código (es su ancla), así que NO se cuenta como campo que pueda salir
                     VACIO; se reporta, pero no puntúa.
    nombre         : nombre de la materia.
    prerrequisito  : código(s) de la(s) materia(s) previa(s); "N/A" y "NIVELACION" son
                     válidos (la materia no tiene prerrequisito), no cuentan como vacío.
    hpao           : horas por período académico (horas de la asignatura).
    creditos       : créditos de la asignatura.

Los 4 campos verificables por asignatura (los que pueden salir "VACIO") son
`CAMPOS_ASIGNATURA`. El invariante aritmético `HPAO = 48 × créditos` se controla aparte: una
violación es una ANOMALÍA que se reporta en el análisis libre, NO un campo vacío (coherente
con INDICADORES.md e INDICADOR 3 de la base de oro).

Expectativa estructural del pénsum
----------------------------------
    - 8 PAO (Primer … Octavo período académico ordinario). pdfminer pierde las 'i' de estas
      etiquetas giradas ("QuntoPAO" = "Quinto PAO"): se reconocen igual, normalizando.
    - 3 unidades de organización curricular (Básica, Profesional, Integración Curricular).
    - ≥10 asignaturas con código y nombre.
    - Invariante HPAO = 48 × créditos en cada asignatura (8 PAO × 720 h = 5760 h;
      8 × 15 = 120 créditos; razón 48 h/crédito).

La suma de asignaturas con código NO cuadra con el total declarado del pénsum: integración
curricular, prácticas preprofesionales y servicio comunitario no llevan código. Eso NO es
incumplimiento y este esquema no lo trata como tal.
"""
import unicodedata

# --- Esquema por asignatura -------------------------------------------------
# El código es el ancla/identificador (la malla no tiene NRC); no puntúa como campo vacío.
CODIGO_ANCLA = "codigo"

# Los 4 campos que SÍ pueden salir "VACIO" y por tanto puntúan en la completitud.
CAMPOS_ASIGNATURA = ["nombre", "prerrequisito", "hpao", "creditos"]

# Marca literal de un campo sin llenar que devuelve `filas_de_malla`.
VALOR_VACIO = "VACIO"

# Prerrequisitos que son válidos aunque no sean un código: la materia no tiene prerrequisito.
PRERREQUISITO_SIN_PREVIA = ("N/A", "NIVELACION")

# --- Expectativa estructural del pénsum -------------------------------------
PAO_ESPERADOS = 8               # Primer … Octavo período académico ordinario
UNIDADES_ESPERADAS = 3          # Básica, Profesional, Integración Curricular
MIN_ASIGNATURAS = 10            # umbral de "distribución de asignaturas" (elemento 3)
HORAS_POR_CREDITO = 48          # invariante HPAO = 48 × créditos

# Ordinales de los 8 PAO. Se guardan CON 'i' para el informe; la detección los normaliza
# quitando las 'i' porque pdfminer las pierde en las etiquetas giradas ("Qunto", "Septmo").
ORDINALES_PAO = [
    "Primer", "Segundo", "Tercer", "Cuarto",
    "Quinto", "Sexto", "Séptimo", "Octavo",
]

UNIDADES_ORGANIZACION = [
    "Unidad Básica",
    "Unidad Profesional",
    "Unidad de Integración Curricular",
]


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def _clave_nivel(texto: str) -> str:
    """Normaliza una etiqueta de nivel para comparar: sin tildes, sin 'i', sin espacios,
    en mayúsculas. Así 'Quinto PAO', 'QuntoPAO' y 'quinto' colapsan a la misma clave."""
    return sin_tildes(texto).upper().replace("I", "").replace(" ", "")


# Clave normalizada de cada ordinal (índice 0 = Primer PAO, … 7 = Octavo PAO).
_CLAVES_ORDINAL = [_clave_nivel(o) for o in ORDINALES_PAO]


def paos_detectados(niveles: list) -> set:
    """Números de PAO (1..8) presentes en las etiquetas de nivel que trae `_enderezar`.

    Un PAO n se cuenta presente si alguna etiqueta que contenga 'PAO' (ya sin tildes/espacios)
    incluye el ordinal n normalizado. Robusto a la pérdida de 'i' ('QuntoPAO' = Quinto PAO)."""
    claves = [_clave_nivel(n) for n in niveles]
    con_pao = [k for k in claves if "PAO" in k]
    presentes = set()
    for i, ordinal in enumerate(_CLAVES_ORDINAL, start=1):
        if any(ordinal in k for k in con_pao):
            presentes.add(i)
    return presentes


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 74)
    print("ESQUEMA OFICIAL DE LA MALLA CURRICULAR (Indicador 3)")
    print("=" * 74)
    print("La malla NO es un formulario de campos fijos: es un diagrama por coordenadas.")
    print("Su plantilla es el esquema que se repite por asignatura + la estructura del pénsum.")
    print()

    print(f"  IDENTIFICADOR / ANCLA (no puntúa como vacío):")
    print(f"     - {CODIGO_ANCLA}  (código de asignatura; la malla NO lleva NRC)")
    print()
    print(f"  CAMPOS VERIFICABLES POR ASIGNATURA ({len(CAMPOS_ASIGNATURA)}, pueden salir '{VALOR_VACIO}'):")
    for i, campo in enumerate(CAMPOS_ASIGNATURA, 1):
        print(f"     {i}. {campo}")
    print()
    print("  EXPECTATIVA ESTRUCTURAL DEL PÉNSUM:")
    print(f"     - {PAO_ESPERADOS} PAO (períodos académicos ordinarios):")
    for i, ordinal in enumerate(ORDINALES_PAO, 1):
        print(f"         {i}. {ordinal} PAO   (clave normalizada: {_CLAVES_ORDINAL[i-1]})")
    print(f"     - {UNIDADES_ESPERADAS} unidades de organización curricular:")
    for unidad in UNIDADES_ORGANIZACION:
        print(f"         · {unidad}")
    print(f"     - ≥ {MIN_ASIGNATURAS} asignaturas con código y nombre")
    print(f"     - invariante  HPAO = {HORAS_POR_CREDITO} × créditos  (anomalía si no cuadra,")
    print(f"       NO campo vacío)")
    print()
    print("  NOTA: prerrequisito 'N/A' o 'NIVELACION' = válido (la materia no tiene previa).")
    print("  NOTA: la suma de asignaturas con código no cuadra con el total del pénsum")
    print("        (integración curricular, prácticas y servicio comunitario no llevan")
    print("        código): NO es incumplimiento.")
