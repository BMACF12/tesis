"""
Esquema oficial del PROYECTO CURRICULAR (Indicador 2).

Es el análogo de `plantilla_malla.py` (malla) y `plantilla_guia.py` (guía), pero el documento
es de otra naturaleza: el formulario oficial de rediseño de carrera (SENESCYT/CES), ~113
páginas. Por eso su "plantilla" NO es una lista de casillas etiqueta→valor que resolver por
coordenadas — la base de oro deja `CAMPOS:` vacío a propósito y no hay veto de campos vacíos —
sino una expectativa ESTRUCTURAL:

    - Los MARCADORES que identifican el tipo de formulario (los comprueba `_plantilla_valida`
      en `tareas_ia.py`; si faltan → PLANTILLA NO RECONOCIDA, sin llamar al LLM).
    - Las ANCLAS: las secciones literales que exigen los elementos fundamentales 3 y 5, más
      las dos que sostienen el elemento 1.

Este módulo fija ese inventario y lo comparte con `completitud_proyecto.py`. La fuente es la
base de oro (`backend/data/caces_2024_oficial.txt`, bloque "INDICADOR 2"): si el `.txt` cambia,
manda el `.txt` y hay que actualizar esto.

QUÉ SE CORRIGIÓ EN ESTA VERSIÓN (y por qué la anterior medía mal)
-----------------------------------------------------------------
La versión anterior se escribió contra una copia MUTILADA del Indicador 2. Al cotejar la base
de oro con el modelo CACES oficial
(`docs/conocimiento/formatos-caces/modelo_caces_generico_grado.txt`) aparecieron tres defectos
que viciaban el reparto de elementos (el `.txt` ya está corregido; esto sólo se alinea con él):

  1. LA NORMA TIENE 6 ELEMENTOS, teníamos 5. Faltaba entero el actual E4 (académicos y
     profesionales con experiencia nacional e internacional involucrados en la
     conceptualización y estructuración del proyecto).
  2. UN ELEMENTO CONTABA DOS VECES. Los viejos E3 (requisitos) y E4 (metodología e
     infraestructura) son, en la norma, UN SOLO elemento —el actual E5, que los une con un
     "así como"—. Partirlo en dos hacía que el elemento más fácil (existen las secciones del
     formulario) pesara 2/5 del indicador. Ahora es un único elemento con sus 4 anclas.
  3. UN ELEMENTO FUNDÍA DOS. El viejo E5 mezclaba "tener políticas de actualización" (actual
     E2) con "ejecutar el seguimiento y evaluación del proyecto" (actual E6). Tener la
     política escrita NO es ejecutarla: son dos elementos y dos fuentes distintas.

Los 7 ANCLA se CONSERVAN íntegros (están verificados contra el PDF real de 113 páginas): sólo
se reasignan de elemento. No se inventa ninguna. Consecuencia deliberada: el universo `A` sigue
teniendo 10 etiquetas (3 marcadores + 7 anclas) y el documento base sigue en J = 1,000. Lo que
cambia es a qué elemento sirve cada ancla, no qué se busca en el PDF.

Alcance: qué puede y qué no puede evidenciar el formulario de rediseño
----------------------------------------------------------------------
La base de oro lleva una NOTA DE ALCANCE (bloque INDICADOR 2) que manda sobre este módulo: la
unidad de evidencia del indicador es el CONJUNTO de las fuentes a)-f), no sólo el formulario.
Los elementos 2, 4 y 6 se evidencian en documentación SEPARADA que el formulario no contiene:

    E2 → fuente b) políticas y procedimientos que guían la actualización y mejora continua
         del currículo.
    E4 → fuente d) documentación del aporte de académicos y profesionales nacionales e
         internacionales al diseño o rediseño del proyecto.
    E6 → fuentes e) lineamientos o directrices de seguimiento y evaluación del proyecto
         curricular, y f) acciones de mejora continua derivadas de ese seguimiento.

Ninguna de esas cosas se escribe DENTRO del formulario de rediseño: el formulario no dice "me
consultaron académicos internacionales", eso lo dice el acta. Se marcan, pues, con
`ALCANCE_FUENTE_EXTERNA`, quedan FUERA del cociente y se reportan aparte NOMBRANDO la fuente
ausente ("requiere fuente b) — no evaluable sobre este documento"), en vez de contarse como
incumplidos en silencio. Es el mismo criterio (y la misma nomenclatura) que `plantilla_perfil.py`
aplica a los E3/E5 del Indicador 1; ser coherente entre indicadores es parte del criterio.

Que aquí el efecto sobre el número sea nulo NO lo hace decorativo. Los elementos 2, 4 y 6 son
`[SEMÁNTICO]` y no tienen ancla, así que ya no aportaban etiquetas al universo: antes quedaban
fuera POR CASUALIDAD (no se les encontró encabezado) y ahora quedan fuera POR MOTIVO DECLARADO
(su evidencia vive en otro documento). La diferencia se ve en el informe: donde antes se leía
"sin ancla (lo juzga el LLM)" —que sugiere que el LLM lo juzgará sobre este PDF— ahora se lee
"requiere fuente b)/d)/e)+f) — no aportada". Y evita la tentación de "arreglar" la métrica
inventándoles un ancla: buscar "mejora continua" en el formulario para acreditar E2 sería
exactamente el falso positivo que la NOTA DE ALCANCE prohíbe.

El elemento 1 es un caso MIXTO y se declara así: entra en el cociente porque sus dos secciones
("Perfil de egreso" y "Misión") sí viven en el formulario, pero su otra mitad —la coherencia
con el Modelo educativo— exige la fuente c), que es un documento aparte. Se anota en
`fuente_parcial` y se imprime en el informe. Que las secciones EXISTAN no significa que sean
coherentes entre sí: eso lo juzga el LLM, no esto.

Ojo con lo que este módulo NO dice: no dice que la carrera no actualice el currículo, que no
consultara a académicos externos ni que no haga seguimiento. Dice que este documento no es el
sitio donde eso se evidencia. El dictamen del LLM sobre el conjunto de fuentes sigue siendo el
que manda, y ése sí declara E2/E4/E6 NO CUMPLE por falta de la fuente: una afirmación sobre el
EXPEDIENTE, no sobre el formulario.

Medido sobre el ejemplar aprobado de referencia (`Reporte_Carrera_Software_26072017.pdf`) las
10 etiquetas de este inventario están presentes: J = 1,000. Eso no es que la métrica sea
complaciente, es que el documento base está completo; la métrica sirve para cazar un proyecto
al que le falte una sección obligatoria, y para rechazar documentos que no son un proyecto
curricular de rediseño.
"""
import unicodedata
from collections import namedtuple

# --- Marcadores de la plantilla (cabecera de máquina de la base de oro) ------
# Separados por ';' son todos obligatorios; dentro de un grupo, '|' son alternativos.
# Copia literal de `MARCADORES:` del bloque INDICADOR 2 del .txt.
MARCADORES = (
    ("Datos generales de la carrera",),
    ("Carrera a rediseñar", "Tipo de trámite"),
    ("Descripción microcurricular",),
)

# --- Alcance de cada elemento (lo manda la NOTA DE ALCANCE de la base de oro) -
# FORMULARIO     : se evidencia en el formulario de rediseño (fuente a) → entra en el cociente.
# FUENTE_EXTERNA : se evidencia en documentación separada (fuentes b/d/e/f) → NO evaluable
#                  sobre este documento y, por tanto, FUERA del cociente. Se reporta aparte
#                  nombrando la fuente. Nunca se cuenta como incumplido en silencio.
# Mismos nombres que en `plantilla_perfil.py` (Indicador 1), a propósito.
ALCANCE_FORMULARIO = "FORMULARIO"
ALCANCE_FUENTE_EXTERNA = "FUENTE_EXTERNA"

# `anclas` vacío = no verificable por estructura. `fuente` = la que haría falta y no se aporta.
# `fuente_parcial` = el elemento SÍ es evaluable aquí, pero una parte de su juicio exige otra
# fuente (sólo el E1, con el Modelo educativo).
Elemento = namedtuple(
    "Elemento", "numero clase anclas descripcion alcance fuente fuente_parcial",
)
Elemento.__new__.__defaults__ = (ALCANCE_FORMULARIO, None, None)

# --- Elementos fundamentales y las secciones (ANCLAS) que exigen -------------
# Orden y contenido literales del bloque INDICADOR 2 de la base de oro.
ELEMENTOS = (
    Elemento(1, "SEMÁNTICO", ("Perfil de egreso", "Misión"),
             "Coherencia con el modelo educativo, la misión institucional y el perfil de egreso",
             fuente_parcial="c) Modelo educativo y pedagógico vigente (para la coherencia con "
                            "el modelo educativo)"),
    Elemento(2, "SEMÁNTICO", (),
             "Aplica políticas y procedimientos de actualización y mejora del currículo",
             alcance=ALCANCE_FUENTE_EXTERNA,
             fuente="b) políticas y procedimientos que guían y orientan la actualización y "
                    "mejora continua del currículo"),
    Elemento(3, "ESTRUCTURAL", ("Pertinencia",),
             "Pertinencia: problemáticas que atiende, tendencias y demanda ocupacional"),
    Elemento(4, "SEMÁNTICO", (),
             "Académicos y profesionales con experiencia nacional e internacional en el diseño",
             alcance=ALCANCE_FUENTE_EXTERNA,
             fuente="d) documentación del aporte de académicos y profesionales a nivel "
                    "nacional e internacional en el diseño o rediseño del proyecto"),
    Elemento(5, "ESTRUCTURAL", ("Requisitos de ingreso", "Requisitos de graduación",
                                "Metodología y ambientes de aprendizajes",
                                "Infraestructura y equipamiento"),
             "Requisitos de ingreso/egreso y evaluación, así como metodologías, ambientes y "
             "recursos pedagógicos"),
    Elemento(6, "SEMÁNTICO", (),
             "Seguimiento y evaluación del proyecto curricular → mejora continua",
             alcance=ALCANCE_FUENTE_EXTERNA,
             fuente="e) lineamientos o directrices para el seguimiento y evaluación del "
                    "proyecto curricular; f) acciones de mejora continua"),
)

TOTAL_ELEMENTOS = len(ELEMENTOS)
ELEMENTOS_EVALUABLES = tuple(e for e in ELEMENTOS if e.alcance == ALCANCE_FORMULARIO)
ELEMENTOS_FUENTE_EXTERNA = tuple(e for e in ELEMENTOS if e.alcance == ALCANCE_FUENTE_EXTERNA)

# Todas las anclas exigidas, sin repetir y en el orden de los elementos.
ANCLAS = tuple(dict.fromkeys(a for e in ELEMENTOS for a in e.anclas))

# Elemento(s) al que sirve cada ancla (para el informe).
ELEMENTO_DE_ANCLA = {}
for _e in ELEMENTOS:
    for _a in _e.anclas:
        ELEMENTO_DE_ANCLA.setdefault(_a, []).append(_e.numero)


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


# --- Etiquetas del universo A ------------------------------------------------
def etiqueta_marcador(grupo: tuple) -> str:
    return "MARCADOR · " + "|".join(grupo)


def etiqueta_ancla(ancla: str) -> str:
    elementos = ",".join(str(n) for n in ELEMENTO_DE_ANCLA.get(ancla, []))
    return f"ANCLA · {ancla} (elem. {elementos})"


def universo() -> set:
    """`A`: todo lo que el esquema del Indicador 2 exige AL FORMULARIO DE REDISEÑO.

    3 grupos de marcadores + 7 anclas de sección = 10 etiquetas. Los elementos 2, 4 y 6 no
    aportan ninguna: son `[SEMÁNTICO]`, no tienen ancla y —lo que importa— su evidencia vive
    en las fuentes b), d) y e)/f), que son documentos aparte (NOTA DE ALCANCE de la base de
    oro). Incluirlos convertiría el Jaccard en una medida de "documentos que no me diste".
    Se reportan aparte, nombrando la fuente ausente, nunca como incumplidos en silencio.
    """
    A = {etiqueta_marcador(g) for g in MARCADORES}
    A |= {etiqueta_ancla(a) for a in ANCLAS}
    return A


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 78)
    print("ESQUEMA OFICIAL DEL PROYECTO CURRICULAR (Indicador 2)")
    print("=" * 78)
    print("El documento es el formulario de rediseño de carrera SENESCYT/CES (~113 páginas).")
    print("Su plantilla NO son casillas etiqueta→valor (la base de oro deja CAMPOS: vacío):")
    print("son MARCADORES de tipo de formulario + ANCLAS de sección por elemento.")
    print()
    print(f"  MARCADORES DE PLANTILLA ({len(MARCADORES)} grupos, todos obligatorios):")
    for i, grupo in enumerate(MARCADORES, 1):
        print(f"     {i}. {' | '.join(grupo)}" + ("   (alternativos)" if len(grupo) > 1 else ""))
    print()
    print("  ALCANCE (NOTA DE ALCANCE de la base de oro):")
    print(f"     - evidenciables en el formulario → entran en el cociente: "
          f"{', '.join('E%d' % e.numero for e in ELEMENTOS_EVALUABLES)}")
    print(f"     - requieren fuente externa (fuera del cociente): "
          f"{', '.join('E%d' % e.numero for e in ELEMENTOS_FUENTE_EXTERNA)}")
    print()
    print(f"  ELEMENTOS FUNDAMENTALES ({TOTAL_ELEMENTOS}) Y SUS ANCLAS:")
    for elemento in ELEMENTOS:
        marca = "  " if elemento.alcance == ALCANCE_FORMULARIO else " *"
        print(f"   {marca} {elemento.numero}. [{elemento.clase}] {elemento.descripcion}")
        for ancla in elemento.anclas:
            print(f"          ANCLA «{ancla}»")
        if elemento.fuente:
            print(f"          * NO EVALUABLE sobre el formulario: requiere fuente "
                  f"{elemento.fuente}")
        if elemento.fuente_parcial:
            print(f"          (parcial: requiere además la fuente {elemento.fuente_parcial})")
    print()
    print(f"  UNIVERSO A = {len(universo())} etiquetas verificables:")
    for etiqueta in sorted(universo()):
        print(f"     - {etiqueta}")
    print()
    print("  NOTA: los elementos 2, 4 y 6 no aportan etiquetas: son semánticos, no tienen")
    print("        ancla y su evidencia vive en las fuentes b), d) y e)/f) — documentos que")
    print("        el formulario no contiene. El elemento 1 aporta la EXISTENCIA de sus dos")
    print("        secciones; su coherencia la juzga el LLM, no esto.")
