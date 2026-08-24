"""
Índice de Jaccard entre el ESQUEMA OFICIAL de la malla curricular (Indicador 3) y una malla
concreta. Es el análogo de `completitud.py` (sílabo) y `completitud_guia.py` (guía). Sin
auditor humano y sin LLM.

    A = todo lo que el esquema de la malla exige para ESTE documento:
          por cada asignatura reconstruida, sus 4 campos {nombre, prerrequisito, hpao,
          creditos}, MÁS los 8 PAO esperados (Primer … Octavo).
    B = lo que el documento tiene realmente relleno (A menos los "VACIO" y los PAO ausentes).

    J(A, B) = |A ∩ B| / |A ∪ B|

Como B ⊆ A (una malla no puede rellenar algo que el esquema no contempla), A ∪ B = A y la
fórmula se reduce a |B| / |A|: la fracción del esquema que el documento cumple. Es Jaccard
legítimo —el caso clásico de "parecido con un documento de referencia"— y en esta
configuración equivale a un porcentaje de completitud.

    J = 1,000  el documento rellena TODO el esquema (todas las asignaturas con sus 4 campos
               y los 8 PAO presentes)
    J < 1,000  le faltan materias, prerrequisitos, horas, créditos o algún PAO

Honestidad sobre esta métrica
-----------------------------
En las mallas reales actuales del corpus (Software y sus variantes) el sistema reconstruye
las asignaturas SIN ningún campo "VACIO" y con los 8 PAO presentes, así que J = 1,000. Eso NO
es un defecto de la métrica: es que esas mallas están completas. La métrica sirve para cazar
una malla que SÍ tenga materias sin nombre, prerrequisitos en blanco, o créditos/horas que no
se leen — o a la que le falten PAO. La "trampa" de `malla trampa` NO está en campos de
asignatura (sale igual de completa); esta métrica de completitud no la penaliza, y así debe
ser.

La malla NO lleva NRC: el identificador de cada materia es su CÓDIGO de asignatura. El código
es el ANCLA de la fila reconstruida, siempre presente por construcción, así que NO se cuenta
como campo que pueda salir vacío (se reporta, pero no puntúa).

El invariante HPAO = 48 × créditos se controla aparte: una violación es una ANOMALÍA que se
reporta como tal, NO como campo vacío (coherente con INDICADORES.md).

A diferencia de `completitud.py`, este script NO abre ChromaDB ni gasta cuota: reconoce la
malla por sus marcadores geométricos (`es_malla`) y la reconstruye por coordenadas.

Uso:
    python scripts/completitud_malla.py malla_ingenierIa      # una malla (fragmento del nombre)
    python scripts/completitud_malla.py --todos               # todo el corpus de mallas
    python scripts/completitud_malla.py "malla trampa" --faltan ""       # auditor vs sistema
    python scripts/completitud_malla.py isoj --faltan "EXCTA0301 · nombre"
"""
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plantilla_malla import (  # noqa: E402
    CAMPOS_ASIGNATURA, HORAS_POR_CREDITO, MIN_ASIGNATURAS, ORDINALES_PAO,
    PAO_ESPERADOS, VALOR_VACIO, paos_detectados,
)
from services.extraccion import (  # noqa: E402
    _cajas, _enderezar, es_malla, filas_de_malla,
)

# Sólo la carpeta FUENTE de mallas etiquetadas. NO se incluye
# `Auditoria_CACES/Indicador_3_Malla_curricular/`: esa carpeta la llena el propio sistema con
# copias `{nombre}_{timestamp}.pdf` de cada corrida, así que evaluarlas sería circular (medir
# el sistema sobre sus propias salidas) e infla el conteo con decenas de duplicados de la misma
# malla. El corpus real son las pocas mallas distintas: isoj (vigente), la de software (versión
# anterior) y la trampa. (MALLA-EDUCACION-INICIAL está aquí pero `es_malla` la rechaza hoy.)
CORPUS = [
    (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
     r"\INDICADOR 3 Malla curricular\*.pdf"),
]


def _rutas_corpus():
    vistos, salida = set(), []
    for patron in CORPUS:
        for ruta in sorted(glob.glob(patron, recursive=True)):
            if "_Reporte" in ruta:
                continue
            clave = os.path.basename(ruta).lower()
            if clave in vistos:
                continue
            vistos.add(clave)
            salida.append(ruta)
    return salida


# --- Etiquetas de los elementos del esquema (para Jaccard y para el modo auditor) ---
def _etiqueta_campo(codigo: str, campo: str) -> str:
    return f"{codigo} · {campo}"


def _etiqueta_pao(indice: int) -> str:
    return f"PAO · {ORDINALES_PAO[indice - 1]}"


def evaluar(ruta):
    """Devuelve (filas, niveles, presentes) o (None, None, None) si no es una malla.

    filas     : list[dict] con codigo/nombre/prerrequisito/hpao/creditos (o "VACIO").
    niveles   : etiquetas de nivel detectadas (`_enderezar`).
    presentes : set de números de PAO (1..8) detectados.
    """
    cajas, rotadas = _cajas(ruta)
    if not es_malla(cajas):
        return None, None, None
    filas = filas_de_malla(cajas)
    niveles = _enderezar(rotadas)
    presentes = paos_detectados(niveles)
    return filas, niveles, presentes


def _universo_ausentes_vacios(filas, presentes):
    """Devuelve (A, ausentes, vacios) — las dos medidas, separadas.

    ausentes = un PAO que no se detecta: la ESTRUCTURA del pénsum no está → incumple plantilla.
    vacios   = un campo de asignatura en VALOR_VACIO: la fila está, el dato no → cálculo aparte.
    El código de asignatura es el ancla: nunca es ausente (si no está, no hay fila).
    """
    A, aus, vac = set(), set(), set()
    for fila in filas:
        for campo in CAMPOS_ASIGNATURA:
            etiqueta = _etiqueta_campo(fila["codigo"], campo)
            A.add(etiqueta)
            if fila.get(campo) == VALOR_VACIO:
                vac.add(etiqueta)
    for indice in range(1, PAO_ESPERADOS + 1):
        etiqueta = _etiqueta_pao(indice)
        A.add(etiqueta)
        if indice not in presentes:
            aus.add(etiqueta)
    return A, aus, vac


def _universo_y_faltantes(filas, presentes):
    """Compat: A y todo lo que falta o está vacío (ausentes ∪ vacíos). Lo usa el modo auditor."""
    A, aus, vac = _universo_ausentes_vacios(filas, presentes)
    return A, aus | vac


def _anomalias_hpao(filas):
    """Asignaturas que violan HPAO = 48 × créditos (anomalía, NO campo vacío)."""
    malas = []
    for fila in filas:
        hpao, cr = fila.get("hpao"), fila.get("creditos")
        if hpao == VALOR_VACIO or cr == VALOR_VACIO:
            continue
        try:
            if int(hpao) != HORAS_POR_CREDITO * int(cr):
                malas.append(fila)
        except ValueError:
            continue
    return malas


def informe(ruta):
    filas, niveles, presentes = evaluar(ruta)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("=" * 78)
    if filas is None:
        print("\nNo es una malla curricular (falta el marcador HPAO y ≥10 códigos).")
        return None

    A, aus, vac = _universo_ausentes_vacios(filas, presentes)

    print(f"\n  ASIGNATURAS RECONSTRUIDAS ({len(filas)}):")
    print(f"   {'':1} {'CÓDIGO':11} {'NOMBRE':34} {'PRE':16} {'HPAO':>5} {'CR':>4}")
    for fila in filas:
        vacio = any(fila.get(c) == VALOR_VACIO for c in CAMPOS_ASIGNATURA)
        print(f"   {'!' if vacio else ' '} {fila['codigo']:11} {fila['nombre'][:34]:34} "
              f"{fila['prerrequisito'][:16]:16} {str(fila['hpao']):>5} {str(fila['creditos']):>4}")

    print("\n  ESTRUCTURA DEL PÉNSUM:")
    ok_asig = len(filas) >= MIN_ASIGNATURAS
    print(f"   {' ' if ok_asig else '!'} asignaturas: {len(filas)} "
          f"({'≥' if ok_asig else '<'} {MIN_ASIGNATURAS} → {'ok' if ok_asig else 'INSUFICIENTE'})")
    ok_pao = len(presentes) >= PAO_ESPERADOS
    faltan_pao = [ORDINALES_PAO[i - 1] for i in range(1, PAO_ESPERADOS + 1) if i not in presentes]
    print(f"   {' ' if ok_pao else '!'} PAO detectados: {len(presentes)}/{PAO_ESPERADOS} "
          f"({'ok' if ok_pao else 'faltan: ' + ', '.join(faltan_pao)})")
    print(f"     niveles/unidades leídos: {' · '.join(niveles) if niveles else '(ninguno)'}")

    anomalias = _anomalias_hpao(filas)
    print("\n  INVARIANTE HPAO = 48 × créditos:")
    if not anomalias:
        print(f"     todas las asignaturas con horas y créditos legibles lo cumplen.")
    else:
        print(f"   ! {len(anomalias)} asignatura(s) lo VIOLAN (anomalía, NO campo vacío):")
        for fila in anomalias:
            print(f"       - {fila['codigo']} {fila['nombre'][:28]}: "
                  f"HPAO={fila['hpao']} ≠ 48×{fila['creditos']}={48 * int(fila['creditos'])}")

    jp = (len(A) - len(aus)) / len(A) if A else 1.0
    print()
    print("=" * 78)
    print("1) CUMPLIMIENTO DE PLANTILLA  (¿está la estructura: asignaturas y 8 PAO?)")
    print("=" * 78)
    print(f"  A = {len(filas)}×{len(CAMPOS_ASIGNATURA)} campos + {PAO_ESPERADOS} PAO = {len(A)} elementos")
    print(f"  presentes {len(A) - len(aus)} / {len(A)}   →   JACCARD plantilla = {jp:.3f}")
    if aus:
        print(f"  x  NO CUMPLE: faltan {len(aus)} elemento(s) de estructura:")
        for etiqueta in sorted(aus):
            print(f"      - {etiqueta}")
    else:
        print("     CUMPLE: las asignaturas y los 8 PAO están presentes.")
    print()
    print("=" * 78)
    print("2) VACÍOS  (campos de asignatura sin dato — cálculo aparte)")
    print("=" * 78)
    if vac:
        print(f"  o  {len(vac)} campo(s) en VACIO:")
        for etiqueta in sorted(vac):
            print(f"      - {etiqueta}")
    else:
        print("     ningún campo de asignatura quedó vacío.")
    return jp


def todos():
    print(f"{'documento':44}{'ASIG':>5}{'PAO':>5}{'PLANTILLA':>11}{'vacíos':>8}   le falta")
    print("-" * 108)
    jotas, cumplen, total = [], 0, 0
    for ruta in _rutas_corpus():
        filas, _niveles, presentes = evaluar(ruta)
        nombre = os.path.basename(ruta)[:42]
        if filas is None:
            print(f"{nombre:44}   no es una malla")
            continue
        A, aus, vac = _universo_ausentes_vacios(filas, presentes)
        jp = (len(A) - len(aus)) / len(A) if A else 1.0
        jotas.append(jp)
        total += 1
        if not aus:
            cumplen += 1
        lista = ", ".join(sorted(aus))[:30] if aus else "—"
        print(f"{nombre:44}{len(filas):>5}{len(presentes):>5}{jp:>11.3f}{len(vac):>8}   {lista}")
    print("-" * 108)
    if jotas:
        print(f"Cumplimiento de plantilla medio: {sum(jotas) / len(jotas):.3f}")
        print(f"Mallas que cumplen la plantilla (sin ausentes): {cumplen} de {total}")
        print("(los 'vacíos' son un cálculo aparte: campos de asignatura sin dato)")


def auditor(ruta, crudo):
    """Jaccard AUDITOR (A, tu lectura del PDF) vs SISTEMA (B, lo que detecta)."""
    filas, _niveles, presentes = evaluar(ruta)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("ÍNDICE DE JACCARD  (auditor  vs  sistema)")
    print("=" * 78)
    if filas is None:
        print("No es una malla curricular. No hay elementos que comparar.")
        return

    universo, B = _universo_y_faltantes(filas, presentes)
    universo = sorted(universo)
    A = set()
    for pedido in (p.strip() for p in crudo.split(",") if p.strip()):
        candidatos = [u for u in universo if pedido.lower() in u.lower()]
        if len(candidatos) == 1:
            A.add(candidatos[0])
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es un elemento de esta malla. Se ignora.")
        else:
            print(f"'{pedido}' es ambiguo: {candidatos[:5]}… Escríbelo completo.")
            raise SystemExit(1)

    interseccion, union = A & B, A | B
    print(f"  A (auditor: lo que TÚ ves faltar)  = {sorted(A) if A else '(nada)'}")
    print(f"  B (sistema: lo que él detecta)     = {sorted(B) if B else '(nada)'}")
    print()
    if not union:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
        print("  La malla está completa y el sistema tampoco reporta nada: no hay lista de")
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
    encontrados = [r for r in _rutas_corpus()
                   if fragmento.lower() in os.path.basename(r).lower()]
    if not encontrados:
        print(f"No encontré ninguna malla con '{fragmento}'.")
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
