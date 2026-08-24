"""
Índice de Jaccard del PROYECTO CURRICULAR (Indicador 2). Análogo de `completitud_malla.py`
(malla), `completitud_guia.py` (guía) y `completitud.py` (sílabo). Sin auditor humano, sin
LLM, sin ChromaDB y sin gastar cuota: sólo pdfminer y comparación de cadenas.

Mide dos cosas distintas, que no hay que confundir:

1) COMPLETITUD contra el ESQUEMA (modo por defecto y `--todos`)

       A = lo que el esquema del Indicador 2 exige AL FORMULARIO DE REDISEÑO
           (`plantilla_proyecto.universo()`): 3 grupos de marcadores + 7 anclas de
           sección = 10 etiquetas.
       B = las que el documento tiene realmente.

       J(A, B) = |A ∩ B| / |A ∪ B|

   Como B ⊆ A (un documento no puede traer un ancla que el esquema no contempla),
   A ∪ B = A y la fórmula se reduce a |B| / |A|: la fracción del esquema que el documento
   cumple. Mismo razonamiento que en `completitud_malla.py`.

   La norma tiene SEIS elementos fundamentales, pero sólo tres de ellos (1, 3 y 5) se
   evidencian en el formulario y aportan etiquetas. Los elementos 2, 4 y 6 son
   `[SEMÁNTICO]`, no tienen ancla y su evidencia vive en las fuentes b), d) y e)/f) —
   documentos aparte que aquí nunca se aportan—, así que quedan FUERA del cociente y se
   reportan al final del informe NOMBRANDO la fuente ausente, en vez de contarse como
   incumplidos en silencio (NOTA DE ALCANCE de la base de oro; mismo criterio que
   `completitud_perfil.py` con los E3/E5 del Indicador 1). Si entraran en el cociente, el
   Jaccard mediría "documentos que no me diste", no la calidad del proyecto.

2) PARECIDO con el DOCUMENTO BASE APROBADO (`--base`)

       A = las secciones del ejemplar aprobado de referencia (`DOCUMENTO_BASE`).
       B = las secciones del documento evaluado.

       J(A, B) = |A ∩ B| / |A ∪ B|

   Aquí B ⊄ A no está garantizado (un documento puede traer secciones que el base no tiene),
   así que el Jaccard es el completo, no la reducción. Es el caso clásico de "parecido con un
   documento de referencia". El base contra sí mismo da 1,000 por construcción.

Si A ∪ B es vacío el índice es INDEFINIDO y así se informa: NO se maquilla como 1,0 (criterio
ya establecido en `jaccard.py` y `completitud_malla.py`).

Sobre los otros dos PDF de la carpeta
-------------------------------------
`2023 MODELO EDUCATIVO ESPE.pdf` y `2026 LNM ELABORACION Y APLICACION EX FIN CARRERA v4.pdf`
NO son proyectos curriculares de rediseño: son el modelo educativo institucional y un
reglamento de examen de fin de carrera. Que salgan con J bajo y sin marcadores es un ACIERTO
del sistema (los rechazaría como PLANTILLA NO RECONOCIDA antes de llamar al LLM), no un fallo.
Se incluyen en el corpus precisamente para comprobar que se rechazan.

Uso:
    python scripts/completitud_proyecto.py Reporte_Carrera        # un documento
    python scripts/completitud_proyecto.py --todos                # todo el corpus
    python scripts/completitud_proyecto.py --base                 # cada doc vs el base aprobado
    python scripts/completitud_proyecto.py Reporte --faltan "..." # auditor vs sistema
"""
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plantilla_proyecto import (  # noqa: E402
    ANCLAS, ELEMENTOS, ELEMENTOS_EVALUABLES, ELEMENTOS_FUENTE_EXTERNA, MARCADORES,
    TOTAL_ELEMENTOS, etiqueta_ancla, etiqueta_marcador, universo,
)
from services.extraccion import comparable, extraer_documento  # noqa: E402
from services.recorte_proyecto import resumen_recorte, secciones_de_proyecto  # noqa: E402

CARPETA = (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
           r"\INDICADOR 2 Proyecto curricular")
CORPUS = [os.path.join(CARPETA, "*.pdf")]

# Ejemplar aprobado de referencia contra el que compara `--base`.
DOCUMENTO_BASE = "Reporte_Carrera_Software_26072017.pdf"

# En español el ratio medido ronda 3,4 caracteres por token. Es una ESTIMACIÓN para dimensionar
# la cuota, no el contador real del tokenizador de Groq.
CHARS_POR_TOKEN = 3.4


def _rutas_corpus():
    vistos, salida = set(), []
    for patron in CORPUS:
        for ruta in sorted(glob.glob(patron)):
            clave = os.path.basename(ruta).lower()
            if clave in vistos:
                continue
            vistos.add(clave)
            salida.append(ruta)
    return salida


def _tokens(chars: int) -> int:
    return int(chars / CHARS_POR_TOKEN)


def evaluar(ruta):
    """Devuelve (texto, secciones_encontradas, presentes, recorte).

    presentes = subconjunto de `universo()` que el documento SÍ tiene (el conjunto B).
    """
    documento = extraer_documento(ruta)
    texto = documento["texto"]
    canonico = comparable(texto)

    presentes = set()
    for grupo in MARCADORES:
        if any(comparable(m) in canonico for m in grupo):
            presentes.add(etiqueta_marcador(grupo))

    secciones = secciones_de_proyecto(texto)
    for ancla in ANCLAS:
        if ancla in secciones:
            presentes.add(etiqueta_ancla(ancla))

    return texto, secciones, presentes, resumen_recorte(texto)


def informe(ruta):
    texto, secciones, B, recorte = evaluar(ruta)
    A = universo()

    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("=" * 78)

    print("\n  MARCADORES DE PLANTILLA:")
    for grupo in MARCADORES:
        etiqueta = etiqueta_marcador(grupo)
        print(f"   {' ' if etiqueta in B else '!'} {' | '.join(grupo)}")

    print("\n  SECCIONES EXIGIDAS (ANCLAS):")
    for ancla in ANCLAS:
        etiqueta = etiqueta_ancla(ancla)
        tam = len(secciones.get(ancla, ""))
        estado = f"{tam:>7} ch" if ancla in secciones else "  AUSENTE"
        print(f"   {' ' if etiqueta in B else '!'} {ancla:42}{estado}")

    print(f"\n  ELEMENTOS FUNDAMENTALES ({len(ELEMENTOS_EVALUABLES)} de {TOTAL_ELEMENTOS} "
          f"evaluables sobre este documento):")
    for elemento in ELEMENTOS:
        if elemento in ELEMENTOS_FUENTE_EXTERNA:
            estado = "requiere fuente externa (ver abajo)"
        elif not elemento.anclas:
            estado = "sin ancla (lo juzga el LLM)"
        else:
            faltan = [a for a in elemento.anclas if etiqueta_ancla(a) not in B]
            estado = "anclas presentes" if not faltan else f"FALTA: {', '.join(faltan)}"
        marca = " " if elemento in ELEMENTOS_EVALUABLES else "*"
        print(f"  {marca}{elemento.numero}. [{elemento.clase:11}] "
              f"{elemento.descripcion[:44]:44} {estado}")

    print("\n  FUERA DEL COCIENTE — no se evidencian en el formulario de rediseño:")
    for elemento in ELEMENTOS_FUENTE_EXTERNA:
        print(f"   * E{elemento.numero} {elemento.descripcion}")
        print(f"       NO APORTADA la fuente {elemento.fuente}")
    print("   No es que la carrera incumpla: es que no se aportó la fuente que lo evidencia.")
    for elemento in ELEMENTOS:
        if elemento.fuente_parcial:
            print(f"   ~ E{elemento.numero} entra en el cociente, pero su juicio completo "
                  f"exige además la fuente\n       {elemento.fuente_parcial}")

    interseccion, union = A & B, A | B
    print()
    print("=" * 78)
    print("1) COMPLETITUD CONTRA EL ESQUEMA DEL INDICADOR 2")
    print("=" * 78)
    if not union:
        print("  JACCARD = 0 / 0 = INDEFINIDO (no hay nada que comparar).")
    else:
        j = len(interseccion) / len(union)
        print(f"  A (esquema) = {len(A)}   B (documento) = {len(B)}")
        print(f"  |A ∩ B| = {len(interseccion)}   |A ∪ B| = {len(union)}")
        print(f"  JACCARD = {len(interseccion)} / {len(union)} = {j:.3f}")
        if A - B:
            print(f"  x  le faltan {len(A - B)} etiqueta(s):")
            for etiqueta in sorted(A - B):
                print(f"      - {etiqueta}")
        else:
            print("     cumple todo lo que el esquema puede verificar sobre este documento.")
            print("     (No acredita el indicador: faltan por juzgar los elementos 2, 4 y 6,")
            print("      cuya evidencia son las fuentes b), d) y e)/f) — no aportadas.)")

    print()
    print("=" * 78)
    print("2) RECORTE PARA EL LLM  (services/recorte_proyecto.py)")
    print("=" * 78)
    original, recortado = recorte["original"], recorte["recortado"]
    print(f"  original  {original:>8} ch  ≈ {_tokens(original):>6} tokens")
    print(f"  recorte   {recortado:>8} ch  ≈ {_tokens(recortado):>6} tokens"
          f"   ({100 * recortado / original:.2f}% del original)")
    if recorte["por_defecto"]:
        print("  ! recorte POR DEFECTO: no se hallaron las secciones esperadas; se entrega la")
        print("    cabeza del texto. (Es lo que toca si el documento no es el formulario.)")
    else:
        print(f"  secciones entregadas ({len(recorte['entregadas'])}):")
        for nombre, (crudo, corto) in recorte["secciones"].items():
            marca = "=" if crudo == corto else "→"
            print(f"      {nombre:42}{crudo:>8} {marca}{corto:>7} ch")
        if recorte["omitidas"]:
            print(f"  secciones omitidas (no son evidencia del indicador): "
                  f"{', '.join(recorte['omitidas'])}")
    ahorro = original - recortado
    print(f"  ahorro: {ahorro} ch ≈ {_tokens(ahorro)} tokens por documento")
    return (len(interseccion) / len(union)) if union else None


def todos():
    A = universo()
    print(f"{'documento':46}{'MARC':>5}{'ANCL':>5}{'JACCARD':>9}{'orig ch':>9}{'recorte':>9}"
          f"{'tok':>7}   le falta")
    print("-" * 118)
    jotas = []
    for ruta in _rutas_corpus():
        _texto, _secciones, B, recorte = evaluar(ruta)
        nombre = os.path.basename(ruta)[:44]
        marc = sum(1 for g in MARCADORES if etiqueta_marcador(g) in B)
        ancl = sum(1 for a in ANCLAS if etiqueta_ancla(a) in B)
        union = A | B
        j = len(A & B) / len(union) if union else None
        if j is not None:
            jotas.append(j)
        falta = ", ".join(sorted(e.split(" · ")[1].split(" (")[0] for e in (A - B)))[:28] or "—"
        jtxt = f"{j:>9.3f}" if j is not None else "INDEFINIDO"
        print(f"{nombre:46}{marc:>3}/{len(MARCADORES)}{ancl:>3}/{len(ANCLAS)}{jtxt}"
              f"{recorte['original']:>9}{recorte['recortado']:>9}"
              f"{_tokens(recorte['recortado']):>7}   {falta}")
    print("-" * 118)
    if jotas:
        print(f"Jaccard medio contra el esquema: {sum(jotas) / len(jotas):.3f}")
    print("Recuerda: el modelo educativo y el reglamento de examen NO son proyectos")
    print("curriculares. Su J bajo es un ACIERTO (se rechazan por marcadores), no un fallo.")
    print(f"El J sólo cubre {len(ELEMENTOS_EVALUABLES)} de los {TOTAL_ELEMENTOS} elementos de "
          f"la norma: los elementos "
          f"{', '.join('%d' % e.numero for e in ELEMENTOS_FUENTE_EXTERNA)} se evidencian en las")
    print("fuentes b), d) y e)/f), que no son este documento. Un J de 1,000 NO acredita el")
    print("indicador: dice que el formulario trae todo lo que a un formulario le toca traer.")


def base():
    """Compara cada documento del corpus contra el ejemplar aprobado de referencia.

    A = secciones del documento base; B = secciones del documento evaluado. Se usan TODAS las
    secciones conocidas que aparecen (útiles y descartadas), porque lo que se mide aquí es el
    parecido estructural con el ejemplar aprobado, no la completitud del indicador.
    """
    ruta_base = os.path.join(CARPETA, DOCUMENTO_BASE)
    if not os.path.exists(ruta_base):
        print(f"No encuentro el documento base: {ruta_base}")
        raise SystemExit(1)

    A = set(secciones_de_proyecto(extraer_documento(ruta_base)["texto"]))
    print("=" * 78)
    print("PARECIDO CON EL DOCUMENTO BASE APROBADO")
    print("=" * 78)
    print(f"  base: {DOCUMENTO_BASE}")
    print(f"  A = {len(A)} secciones: {', '.join(sorted(A))}")
    print()
    print(f"{'documento':46}{'|A∩B|':>7}{'|A∪B|':>7}{'JACCARD':>9}   le falta del base")
    print("-" * 112)
    for ruta in _rutas_corpus():
        B = set(secciones_de_proyecto(extraer_documento(ruta)["texto"]))
        interseccion, union = A & B, A | B
        nombre = os.path.basename(ruta)[:44]
        if not union:
            print(f"{nombre:46}{0:>7}{0:>7}{'INDEFINIDO':>11}   (ninguno tiene secciones)")
            continue
        j = len(interseccion) / len(union)
        falta = ", ".join(sorted(A - B))[:40] or "—"
        print(f"{nombre:46}{len(interseccion):>7}{len(union):>7}{j:>9.3f}   {falta}")
    print("-" * 112)
    print("El base contra sí mismo da 1,000 por construcción: es la referencia, no una medida")
    print("de acierto. Lo informativo es lo lejos que quedan los documentos que NO son un")
    print("proyecto curricular de rediseño.")


def auditor(ruta, crudo):
    """Jaccard AUDITOR (A, tu lectura del PDF) vs SISTEMA (B, lo que él detecta que falta)."""
    _texto, _secciones, presentes, _recorte = evaluar(ruta)
    esquema = universo()
    B = esquema - presentes            # lo que el sistema dice que falta

    print("=" * 78)
    print(f"  {os.path.basename(ruta)[:68]}")
    print("ÍNDICE DE JACCARD  (auditor  vs  sistema)")
    print("=" * 78)

    universo_ordenado = sorted(esquema)
    A = set()
    for pedido in (p.strip() for p in crudo.split(",") if p.strip()):
        candidatos = [u for u in universo_ordenado if pedido.lower() in u.lower()]
        if len(candidatos) == 1:
            A.add(candidatos[0])
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es un elemento del esquema. Se ignora.")
        else:
            print(f"'{pedido}' es ambiguo: {candidatos[:5]}… Escríbelo completo.")
            raise SystemExit(1)

    interseccion, union = A & B, A | B
    print(f"  A (auditor: lo que TÚ ves faltar)  = {sorted(A) if A else '(nada)'}")
    print(f"  B (sistema: lo que él detecta)     = {sorted(B) if B else '(nada)'}")
    print()
    if not union:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
        print("  El documento está completo y el sistema tampoco reporta nada: no hay lista de")
        print("  faltantes que comparar. La convención lo cuenta como 1,0, pero ese 1,0 no")
        print("  premia detectar algo, premia que no hubiera nada que detectar.")
    else:
        print(f"  |A ∩ B| = {len(interseccion)}      |A ∪ B| = {len(union)}")
        print(f"  JACCARD = {len(interseccion)} / {len(union)} = {len(interseccion) / len(union):.3f}")
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
        print(f"No encontré ningún documento con '{fragmento}'.")
        raise SystemExit(1)
    return encontrados[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--todos":
        todos()
    elif sys.argv[1] == "--base":
        base()
    elif "--faltan" in sys.argv:
        auditor(buscar(sys.argv[1]), sys.argv[sys.argv.index("--faltan") + 1])
    else:
        informe(buscar(sys.argv[1]))
