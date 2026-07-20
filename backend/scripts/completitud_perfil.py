"""
Índice de Jaccard entre el ESQUEMA del perfil de egreso (Indicador 1) y un perfil concreto.
Es el análogo de `completitud_malla.py` (malla), `completitud_guia.py` (guía) y `jaccard.py`
(sílabo). Sin auditor humano, sin ChromaDB, sin LLM y sin cuota.

    A = los elementos fundamentales EVIDENCIABLES EN EL TEXTO DEL PERFIL = {E1, E2, E4}.
    B = los elementos cuya EVIDENCIA LÉXICA aparece en el documento (`plantilla_perfil.py`).

    J(A, B) = |A ∩ B| / |A ∪ B|

Como B ⊆ A (el proxy sólo puntúa elementos que el esquema contempla), A ∪ B = A y la fórmula
se reduce a |B| / 3: la fracción del esquema EVALUABLE para la que el documento aporta
evidencia.

POR QUÉ EL DENOMINADOR ES 3 Y NO 5 (léelo antes de comparar este número con nada)
--------------------------------------------------------------------------------
La NOTA DE ALCANCE del Indicador 1 en la base de oro dice que la unidad de evidencia del
indicador es el CONJUNTO de fuentes a)-f), no una hoja suelta de perfil, y que los elementos
3 (aporte de expertos externos, organizaciones profesionales, empleadores y graduados) y 5
(seguimiento, evaluación y mejora continua) se evidencian en documentación SEPARADA —fuente
b) actas/informes/encuestas, fuentes d) y f) políticas y acciones de mejora—, NO en el texto
del perfil.

Si E3 y E5 se dejaran dentro de A, ningún perfil suelto podría pasar de 3/5 JAMÁS y el
Jaccard estaría midiendo la ausencia de documentos que a ese PDF nunca se le pidieron. Por
eso E3 y E5 quedan FUERA del cociente y se reportan aparte, nombrando la fuente que falta:

    "E3 · requiere fuente b) — no evaluable sobre este documento"

Lo que NO se hace es contarlos como incumplidos en silencio. Un 3/5 así no diría "el perfil
es mediocre", diría "no me diste el acta": son dos frases distintas y sólo una es cierta.
El detector léxico de E3/E5 se ejecuta igual y su rastro se imprime como SEÑAL INFORMATIVA
(sirve si algún día se mide un expediente completo), pero no puntúa: un rastro léxico no es
un acta.

Consecuencia directa: este J NO es comparable con el porcentaje del LLM en producción, que
dictamina sobre los 5 elementos y el expediente entero (y que declara E3/E5 NO CUMPLE por
falta de fuente, lo cual es una afirmación sobre el EXPEDIENTE, no sobre el perfil). Ver el
apartado de contraste en `docs/INDICADORES.md`.

QUÉ SIGNIFICA (Y QUÉ NO) ESTE NÚMERO
------------------------------------
Los 5 elementos del Indicador 1 son `[SEMÁNTICO]` en la base de oro: NO son verificables de
forma determinista. Este script NO los verifica; rastrea las huellas léxicas que un
documento deja cuando habla de ellos. Por tanto:

    J alto  = el documento MENCIONA los asuntos que la norma pide. No que los cumpla.
    J bajo  = el documento no deja ni rastro léxico de ellos. Esto sí es informativo.

Es decir: J bajo es evidencia razonable de incumplimiento; J alto NO es evidencia de
cumplimiento. La métrica es asimétrica y así hay que reportarla. El juez real es el LLM en
producción (`tareas_ia.py`), que además debe citar el documento textualmente.

MODOS
-----
    python scripts/completitud_perfil.py PERFILEGRESO         # un documento (fragmento)
    python scripts/completitud_perfil.py --todos              # todo el corpus del Indicador 1
    python scripts/completitud_perfil.py --base               # cada doc vs el BASE APROBADO
    python scripts/completitud_perfil.py egresado --faltan "E1, E2"   # auditor vs sistema

El modo `--base` compara cada candidato contra el DOCUMENTO BASE APROBADO
(`Perfil del Egresado prueba_*.pdf`), que es la referencia de la carrera: J = |A∩B|/|A∪B|
donde A = elementos evaluables con evidencia en el base y B = los del candidato. Ojo: aquí
Jaccard es simétrico y NO se reduce a un porcentaje. Si ambos conjuntos son vacíos, el
resultado es INDEFINIDO (0/0) y así se imprime: no se maquilla como 1,0 (mismo criterio que
`jaccard.py` y `completitud_malla.py`).

    OJO CON EL MODO --base: el documento base es la REFERENCIA DE ESTA CARRERA, no el ideal
    de la norma. Parecerse mucho al base no significa cumplir el Indicador 1; significa
    parecerse al base. Si el base no declara un elemento, el modo --base no lo penaliza en
    nadie. Para saber qué exige la norma, usa `--todos`.
"""
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plantilla_perfil import (  # noqa: E402
    ELEMENTOS_EVALUABLES, ELEMENTOS_FUENTE_EXTERNA, ELEMENTOS_PERFIL, MARCADORES_PERFIL,
    TOTAL_ELEMENTOS, elementos_detectados, universo,
)
from services.extraccion import comparable, extraer_documento, normalizar  # noqa: E402

# Sólo la carpeta FUENTE del Indicador 1. NO se incluye
# `Auditoria_CACES/Indicador_1_Perfil_de_egreso/`: esa carpeta la llena el propio sistema con
# copias `{nombre}_{timestamp}.pdf` de cada corrida, así que evaluarlas sería circular (medir
# el sistema sobre sus propias salidas) e infla el conteo con duplicados. Mismo criterio que
# `completitud_malla.py`.
CORPUS = [
    (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
     r"\INDICADOR 1 Perfil de egreso\*.pdf"),
]

# El documento base APROBADO de la carrera: la referencia contra la que compara `--base`.
BASE_APROBADO = "Perfil del Egresado prueba"


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


def _plantilla_reconocida(texto: str):
    """¿Lleva alguno de los marcadores del Indicador 1? Réplica local de `_plantilla_valida`
    (`tareas_ia.py`) sobre la forma canónica, para no importar Celery ni abrir ChromaDB."""
    documento = comparable(texto)
    return any(comparable(m) in documento for m in MARCADORES_PERFIL)


def evaluar(ruta):
    """Devuelve (reconocida, detectados, evidencias, longitud) del documento.

    `detectados` puede incluir el rastro léxico de E3/E5; para puntuar hay que intersecar
    con `universo()` (lo hace `_puntuables`).
    """
    documento = extraer_documento(ruta)
    texto = documento["texto"]
    reconocida = _plantilla_reconocida(texto)
    detectados, evidencias = elementos_detectados(normalizar(texto))
    return reconocida, detectados, evidencias, len(texto)


def _puntuables(detectados: set) -> set:
    """B: sólo lo detectado que SÍ es evidenciable en el perfil. E3/E5 nunca puntúan."""
    return detectados & universo()


def _jaccard(A: set, B: set):
    """Devuelve (j, interseccion, union). j es None si A ∪ B es vacío: INDEFINIDO."""
    interseccion, union = A & B, A | B
    return (len(interseccion) / len(union) if union else None), interseccion, union


def _imprimir_fuente_externa(detectados, evidencias):
    """E3 y E5: NO evaluables sobre el perfil. Se nombran, con su fuente, y su rastro léxico
    se da como señal informativa. Nunca se cuentan como incumplidos en silencio."""
    print(f"  ELEMENTOS QUE REQUIEREN FUENTE EXTERNA (fuera del cociente, "
          f"{len(ELEMENTOS_FUENTE_EXTERNA)}):")
    for elemento in ELEMENTOS_FUENTE_EXTERNA:
        print(f"   ? {elemento.etiqueta}")
        print(f"       NO EVALUABLE SOBRE ESTE DOCUMENTO — requiere fuente {elemento.fuente}")
        if elemento.etiqueta in detectados:
            print("       rastro léxico PRESENTE (señal informativa, NO acredita nada:")
            print("       un rastro léxico no es un acta ni una política):")
        for linea in evidencias[elemento.etiqueta]:
            print(f"       · {linea}")
        if not evidencias[elemento.etiqueta]:
            print("       · sin rastro léxico alguno en el texto (era de esperar: el perfil")
            print("         no es donde esto se evidencia)")


def informe(ruta):
    reconocida, detectados, evidencias, longitud = evaluar(ruta)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("=" * 78)
    print(f"  {longitud} caracteres extraídos")
    print()
    print("  PLANTILLA (marcadores del Indicador 1):")
    if reconocida:
        print("     RECONOCIDA: lleva un marcador de perfil de egreso.")
    else:
        print("   x NO RECONOCIDA: no aparece ninguno de los marcadores")
        print(f"     ({' | '.join(MARCADORES_PERFIL)}).")
        print("     El documento no se presenta como un perfil de egreso.")
    print()

    A = universo()
    B = _puntuables(detectados)
    j, _inter, _union = _jaccard(A, B)

    print(f"  ELEMENTOS EVIDENCIABLES EN EL PERFIL ({len(ELEMENTOS_EVALUABLES)} de "
          f"{TOTAL_ELEMENTOS} — evidencia léxica, no juicio):")
    for elemento in ELEMENTOS_EVALUABLES:
        ok = elemento.etiqueta in B
        print(f"   {' ' if ok else 'x'} {elemento.etiqueta:52} "
              f"{'con evidencia' if ok else 'SIN EVIDENCIA'}")
        for linea in evidencias[elemento.etiqueta]:
            print(f"       · {linea}")
        if not evidencias[elemento.etiqueta]:
            print("       · (ningún término de la familia aparece en el documento)")
    print()
    _imprimir_fuente_externa(detectados, evidencias)
    print()
    print("=" * 78)
    print("COBERTURA DE EVIDENCIA  —  J = |A ∩ B| / |A ∪ B|")
    print("=" * 78)
    print(f"  A (la norma exige AL PERFIL) = {len(A)} elementos (E3 y E5 fuera: fuentes b/d/f)")
    print(f"  B (el doc evidencia) = {len(B)} elementos   (B ⊆ A → A ∪ B = A)")
    if j is None:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
    else:
        print(f"  JACCARD = {len(B)} / {len(A)} = {j:.3f}")
    print()
    print("  Recordatorio: J alto NO acredita cumplimiento (el proxy es léxico); J bajo sí")
    print("  es indicio razonable de que el documento ni siquiera aborda el elemento.")
    print("  Y J = 1,000 NO es 100% del Indicador 1: es 100% de lo que un PERFIL puede")
    print("  evidenciar por sí solo. El indicador completo exige además las fuentes b/d/f.")
    return j


def todos():
    A = universo()
    print(f"{'documento':46}{'chars':>7}{'plant.':>8}{'ELEM':>6}{'JACCARD':>9}   "
          f"sin evidencia | rastro de fuente externa")
    print("-" * 118)
    jotas = []
    for ruta in _rutas_corpus():
        reconocida, detectados, _ev, longitud = evaluar(ruta)
        nombre = os.path.basename(ruta)[:44]
        B = _puntuables(detectados)
        j, _i, _u = _jaccard(A, B)
        jotas.append(j)
        faltan = sorted(e.etiqueta.split(" · ")[0] for e in ELEMENTOS_EVALUABLES
                        if e.etiqueta not in B)
        rastro = sorted(e.etiqueta.split(" · ")[0] for e in ELEMENTOS_FUENTE_EXTERNA
                        if e.etiqueta in detectados)
        texto_j = "INDEF." if j is None else f"{j:.3f}"
        print(f"{nombre:46}{longitud:>7}{'ok' if reconocida else 'NO':>8}"
              f"{len(B):>6}{texto_j:>9}   {', '.join(faltan) if faltan else '—':14} | "
              f"{', '.join(rastro) if rastro else '—'}")
    print("-" * 118)
    validas = [j for j in jotas if j is not None]
    if validas:
        print(f"Cobertura de evidencia media: {sum(validas) / len(validas):.3f}  "
              f"({len(validas)} documentos)")
    print()
    print(f"El cociente es sobre {len(A)} elementos (E1, E2, E4): son los únicos que el TEXTO")
    print("de un perfil puede evidenciar. E3 (aporte de involucrados) y E5 (seguimiento y")
    print("mejora continua) viven en las fuentes b) y d)/f) y quedan fuera: su columna de")
    print("rastro es informativa, no puntúa. Ningún documento 'aprueba' el Indicador 1 por")
    print("este número: los 5 elementos son [SEMÁNTICO] y quien dictamina es el LLM sobre el")
    print("expediente completo. Esto es la línea base determinista.")


def contra_base():
    """Jaccard de cada candidato contra el DOCUMENTO BASE APROBADO."""
    rutas = _rutas_corpus()
    base = next((r for r in rutas if BASE_APROBADO.lower() in os.path.basename(r).lower()),
                None)
    if base is None:
        print(f"No encontré el documento base aprobado ('{BASE_APROBADO}*.pdf') en el corpus.")
        raise SystemExit(1)

    _rec_b, det_b, _ev_b, len_b = evaluar(base)
    A = _puntuables(det_b)

    print("=" * 78)
    print("COMPARACIÓN CONTRA EL DOCUMENTO BASE APROBADO")
    print("=" * 78)
    print(f"  BASE: {os.path.basename(base)[:60]}  ({len_b} chars)")
    print(f"  A (elementos evaluables con evidencia en el BASE) = {len(A)}/"
          f"{len(ELEMENTOS_EVALUABLES)}")
    for etiqueta in sorted(A):
        print(f"       · {etiqueta}")
    if not A:
        print("       · (ninguno)")
    print()
    print("  E3 y E5 no entran en esta comparación: no son evaluables sobre un perfil")
    print("  (fuentes b/d/f). Compararlos aquí sería medir qué documentos NO trae ninguno")
    print("  de los dos, que es siempre lo mismo y no distingue nada.")
    print()
    print("  El base es la REFERENCIA DE LA CARRERA, no el ideal de la norma. Parecerse a")
    print("  él no acredita el Indicador 1: acredita parecerse a él.")
    print()
    print(f"{'candidato':46}{'ELEM':>6}{'∩':>4}{'∪':>4}{'JACCARD':>10}   diferencias")
    print("-" * 112)
    jotas = []
    for ruta in rutas:
        if ruta == base:
            continue
        _rec, det, _ev, _len = evaluar(ruta)
        B = _puntuables(det)
        j, inter, union = _jaccard(A, B)
        nombre = os.path.basename(ruta)[:44]
        diferencia = sorted(e.split(" · ")[0] for e in (A ^ B))
        texto_j = "INDEFINIDO" if j is None else f"{j:.3f}"
        if j is not None:
            jotas.append(j)
        print(f"{nombre:46}{len(B):>6}{len(inter):>4}{len(union):>4}{texto_j:>10}   "
              f"{', '.join(diferencia) if diferencia else 'idénticos al base'}")
    print("-" * 112)
    if jotas:
        print(f"Jaccard medio contra el base: {sum(jotas) / len(jotas):.3f}  "
              f"({len(jotas)} candidatos con A ∪ B no vacío)")
    print()
    print("Si A ∪ B es vacío para algún candidato, se imprime INDEFINIDO y NO cuenta en la")
    print("media: 0/0 no es un 1,0 merecido, es que no había nada que comparar (mismo")
    print("criterio que jaccard.py y completitud_malla.py).")


def auditor(ruta, crudo):
    """Jaccard AUDITOR (A, tu lectura del PDF) vs SISTEMA (B, lo que detecta el proxy).

    Aquí A y B son los elementos que CADA UNO da por evidenciados (no los que faltan), que
    es lo natural en un checklist. Sólo se comparan los elementos evaluables sobre el perfil:
    si pides E3 o E5, se avisa y se ignoran (no son evaluables sobre este documento).
    """
    _rec, det, _ev, _len = evaluar(ruta)
    B = _puntuables(det)
    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("ÍNDICE DE JACCARD  (auditor  vs  sistema)")
    print("=" * 78)

    evaluables = sorted(universo())
    fuera = {e.etiqueta for e in ELEMENTOS_FUENTE_EXTERNA}
    todas = sorted(e.etiqueta for e in ELEMENTOS_PERFIL)
    A = set()
    for pedido in (p.strip() for p in crudo.split(",") if p.strip()):
        candidatos = [u for u in todas if pedido.lower() in u.lower()]
        if len(candidatos) == 1:
            elegido = candidatos[0]
            if elegido in fuera:
                print(f"Aviso: '{elegido}' NO es evaluable sobre un perfil (requiere fuente")
                print("       externa b/d/f). Queda fuera del cociente. Se ignora.")
                continue
            A.add(elegido)
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es un elemento del Indicador 1. Se ignora.")
        else:
            print(f"'{pedido}' es ambiguo: {candidatos}. Escríbelo completo.")
            raise SystemExit(1)

    j, interseccion, union = _jaccard(A, B)
    print(f"  universo evaluable = {evaluables}")
    print(f"  A (auditor: lo que TÚ das por cumplido) = {sorted(A) if A else '(nada)'}")
    print(f"  B (sistema: lo que evidencia el proxy)  = {sorted(B) if B else '(nada)'}")
    print()
    if j is None:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
        print("  Ni tú ni el proxy dais por cumplido ningún elemento: no hay conjuntos que")
        print("  comparar. La convención lo contaría como 1,0, pero ese 1,0 no premia")
        print("  detectar algo, premia que no hubiera nada que detectar.")
    else:
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
        print(f"No encontré ningún documento del Indicador 1 con '{fragmento}'.")
        raise SystemExit(1)
    return encontrados[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--todos":
        todos()
    elif sys.argv[1] == "--base":
        contra_base()
    elif "--faltan" in sys.argv:
        auditor(buscar(sys.argv[1]), sys.argv[sys.argv.index("--faltan") + 1])
    else:
        informe(buscar(sys.argv[1]))
