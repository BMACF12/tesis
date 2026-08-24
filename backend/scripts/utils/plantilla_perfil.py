"""
Esquema del PERFIL DE EGRESO (Indicador 1).

Qué es esto y qué NO es
-----------------------
El perfil de egreso NO tiene formulario. No hay 39 casillas como en el sílabo
(`plantilla_silabo.py`), ni 27 como en la guía (`plantilla_guia.py`), ni un diagrama por
coordenadas como en la malla (`plantilla_malla.py`). Es PROSA. Su cabecera de máquina en la
base de oro (`caces_2024_oficial.txt`, INDICADOR 1) lleva `CAMPOS:` vacío y
`ESTADO: SEMANTICO` precisamente por eso: no hay nada etiqueta→valor que resolver.

Su único "esquema" son los 5 ELEMENTOS FUNDAMENTALES de la norma, y los cinco están marcados
`[SEMÁNTICO]`: sólo un lector que entienda el texto puede decir si se cumplen. Este módulo
NO pretende sustituir ese juicio.

    ADVERTENCIA DE HONESTIDAD (léela antes de citar cualquier número de aquí)

    Lo que este módulo define es un PROXY LÉXICO de un juicio semántico. Por cada elemento
    fija una familia de términos/regex cuya presencia DELATA que el documento habla de ese
    asunto. Mide COBERTURA DE EVIDENCIA LÉXICA, no comprensión:

      - No distingue "el estudiante identificará los requisitos" (resultado de aprendizaje
        declarado) de "se identifican los núcleos estructurantes" (frase descriptiva). Las
        dos contienen el mismo lexema.
      - No sabe si lo que encuentra está bien redactado, si es pertinente a la carrera o si
        es una declaración vacía.
      - Un FALSO NEGATIVO es perfectamente posible: un perfil puede declarar resultados de
        aprendizaje impecables con un vocabulario que estas familias no contemplan.

    El JUEZ REAL en producción es el LLM (`tareas_ia.py`), que recibe el criterio de la
    norma y debe citar textualmente el documento. Este script sirve para (a) tener una
    lectura determinista, reproducible y sin cuota del corpus del Indicador 1, y (b) poder
    contrastar después el dictamen del LLM contra una línea base explícita. NO sirve para
    acreditar a nadie.

QUÉ SE CORRIGIÓ EN ESTA VERSIÓN (y por qué el 0,400 anterior era basura)
-----------------------------------------------------------------------
La versión anterior de este módulo se escribió contra un ESTÁNDAR mutilado del Indicador 1.
Al cotejar la base de oro con el modelo CACES oficial
(`docs/conocimiento/formatos-caces/modelo_caces_generico_grado.txt`) aparecieron dos errores
que viciaban todos los números publicados:

  1. UN REQUISITO INVENTADO. El viejo E3 exigía saberes "redactados de forma observable" y
     lo medía con `MIN_VERBOS_OBSERVABLES = 3` (tres verbos distintos en infinitivo o
     futuro). ESE REQUISITO NO EXISTE EN EL CACES. La norma dice, literalmente: "Los saberes
     teóricos y prácticos declarados son verificables y permiten alcanzar los resultados de
     aprendizaje establecidos en el perfil de egreso". Es un requisito de COHERENCIA
     (saberes → resultados de aprendizaje), NO de estilo de redacción. El documento base
     APROBADO de la carrera está escrito en prosa descriptiva ("estos núcleos básicos
     articulan los saberes de la carrera…") y por eso reunía sólo 2 verbos frente a un
     umbral de 3: se le penalizaba por su estilo, no por su contenido. Ese umbral es lo que
     hundía al base a J = 0,400. Está ELIMINADO, junto con todo rastro de "observable".
  2. LA NUMERACIÓN ESTABA CRUZADA. Los viejos E3/E4 estaban intercambiados respecto a la
     norma. La numeración de este módulo es ahora la de la base de oro, literal.

Alcance: qué puede y qué no puede evidenciar una hoja de perfil
--------------------------------------------------------------
La base de oro lleva una NOTA DE ALCANCE (bloque INDICADOR 1) que manda sobre este módulo:
la unidad de evidencia del indicador es el CONJUNTO de las fuentes a)-f), no una hoja suelta
de perfil. En concreto, los elementos 3 y 5 se evidencian en documentación SEPARADA:

    E3 → fuente b) actas, informes o encuestas que acrediten el aporte de expertos
         académicos externos, organizaciones profesionales, empleadores y graduados
         (y fuente e) para la publicación en la web institucional).
    E5 → fuentes d) políticas y procedimientos de seguimiento y evaluación, y
         f) acciones de mejora continua derivadas de ese seguimiento.

Ninguna de esas cosas se escribe DENTRO del texto de un perfil de egreso. Un perfil no dice
"me elaboraron con empleadores": eso lo dice el acta. Consecuencia para la métrica: si E3 y
E5 se dejan en el conjunto A, NINGÚN perfil suelto puede pasar de 3/5 jamás, y el Jaccard
acaba midiendo la ausencia de documentos que a ese PDF nunca se le pidieron. Es exactamente
el mismo error que el umbral de verbos: penalizar al documento por algo que no le toca.

DECISIÓN DE DISEÑO (opción (a) del planteamiento):

    A = los elementos EVIDENCIABLES EN EL PERFIL = {E1, E2, E4}.  El cociente es sobre 3.
    E3 y E5 se marcan `ALCANCE_FUENTE_EXTERNA`, quedan FUERA del cociente y se reportan
    aparte, nombrando la fuente ausente ("requiere fuente b) — no evaluable sobre este
    documento").

Lo que NO se hace, y era la tentación: contarlos como incumplidos en silencio. Un 3/5 así
no dice "el perfil es mediocre", dice "no me diste el acta", y son dos frases distintas.
Por qué el denominador es FIJO (3) y no depende de lo que el documento traiga: para que el
número sea comparable entre documentos. El detector léxico de E3/E5 SÍ se ejecuta igual y su
rastro se imprime como señal informativa —útil si algún día se evalúa un expediente completo
o un proyecto curricular que sí incorpore la fuente b—, pero un rastro léxico NO es el acta:
no puntúa.

Ojo: esto NO significa que la carrera no consulte a sus involucrados ni haga seguimiento.
Significa que este documento no es el sitio donde eso se evidencia. El dictamen del LLM sobre
el conjunto de fuentes sigue siendo el que manda, y ése sí declara E3/E5 NO CUMPLE por falta
de la fuente, que es una afirmación sobre el EXPEDIENTE, no sobre el perfil.

Los 5 elementos y cómo se rastrea cada uno
------------------------------------------
    1. [en el perfil] Resultados de aprendizaje declarados de forma clara y específica, en
       concordancia con el objeto de la carrera, tendencias, expectativas, necesidades de la
       sociedad y el perfil profesional.
       Familia RESULTADOS, basta 1 término distinto.
       LIMITACIÓN DECLARADA: el proxy sólo ve la mitad del elemento. Que los RA estén
       DECLARADOS deja huella léxica; que estén "en CONCORDANCIA con el objeto de la
       carrera y el perfil profesional" es una relación semántica entre dos textos y NINGUNA
       familia de palabras la verifica. Se detecta, pues, una condición NECESARIA pero NO
       SUFICIENTE. No se inventa un umbral para simular lo demás: se dice y ya.

    2. [en el perfil] Dominios teóricos, metodológicos y técnico-pedagógicos que responden al
       área de conocimiento de la carrera y a la profesión.
       Familia DOMINIOS. Se exigen MIN_TERMINOS_DOMINIOS (2) términos DISTINTOS: la norma
       pide dominios en plural (teóricos Y metodológicos Y técnicos), y una mención suelta de
       "metodología" no es eso. El umbral es decisión de diseño, no mandato de la norma.

    3. [FUENTE EXTERNA b, e] Elaborado participativamente con, por lo menos, el aporte de
       expertos académicos externos, organizaciones profesionales, empleadores y graduados;
       y disponible en la página web institucional.
       CONJUNCIÓN de ACTORES Y PARTICIPACIÓN en una ventana de VENTANA_COOCURRENCIA (200)
       caracteres. La conjunción no es adorno: la norma no pide que el perfil MENCIONE
       empleadores, pide que se evidencie que APORTARON.

           EL FALSO POSITIVO ACM-IEEE (prohibido explícitamente por la NOTA DE ALCANCE).
           El documento base dice que sus núcleos "guardan relación con los lineamientos
           emitidos por la association for computing machinery – institute of electrical and
           electronics engineers (acm-ieee)". Eso es ALINEACIÓN CON UN REFERENTE, no aporte
           de esa organización a la elaboración del perfil: NO acredita E3. Por eso ni
           "IEEE", ni "ACM", ni "association"/"institute" están en FAMILIA_ACTORES, y
           "organización profesional" exige la palabra "profesional" pegada (no la casa
           "association for computing machinery"). La regla de co-ocurrencia de la versión
           anterior sigue siendo válida y se conserva: aunque un actor apareciera, sin un
           término de PARTICIPACIÓN cerca no se acredita nada.

       La segunda mitad ("disponible en la página web institucional") tampoco se evidencia en
       el texto del perfil: es la fuente e) (medios digitales o material de difusión). No se
       proxia. Otra razón más para que E3 no puntúe sobre una hoja suelta.

    4. [en el perfil] Los saberes teóricos y prácticos declarados son verificables y PERMITEN
       ALCANZAR los resultados de aprendizaje establecidos en el perfil.
       CONJUNCIÓN de SABERES Y RESULTADOS en la misma ventana. Esto es COHERENCIA, no
       estilo: el elemento se cumple cuando el documento ata un saber (núcleos, contenidos,
       conocimientos, formación) a un resultado de aprendizaje (competencias, RA, "será capaz
       de"). Las dos familias se mantienen DISJUNTAS a propósito: si "competencias" estuviera
       en las dos, la co-ocurrencia se satisfaría sola y el elemento sería un regalo.
       Aquí es donde el viejo `MIN_VERBOS_OBSERVABLES` medía lo que no era.

    5. [FUENTE EXTERNA d, f] Seguimiento y evaluación del cumplimiento del perfil y de los RA,
       cuyos resultados se usan para la mejora continua de la carrera.
       CONJUNCIÓN de SEGUIMIENTO Y OBJETO_CURRICULAR en la misma ventana. Sin el segundo
       conjunto, "realizar el seguimiento y control de calidad del proyecto" —una función
       laboral del egresado, no un mecanismo institucional— daría el elemento por cumplido.
       Es un falso positivo REAL y MEDIDO del corpus (`informacion_carrera_isoj_ltga.pdf`).
       La ventana lo mitiga, no lo elimina: ver el informe de `completitud_perfil.py`.

Marcadores de plantilla
-----------------------
`MARCADORES_PERFIL` replica los marcadores de la base de oro (INDICADOR 1) para poder
comprobar la plantilla sin abrir ChromaDB. Incluye "PERFIL DEL EGRESADO"/"PERFIL EGRESADO":
sin esas variantes el sistema rechazaba el propio documento base aprobado del corpus, que se
titula "Perfil del Egresado". La comparación se hace sobre la forma canónica (`comparable`),
igual que `_plantilla_valida` en `tareas_ia.py`.
"""
import re

# --- Marcadores de plantilla (espejo de caces_2024_oficial.txt, INDICADOR 1) -----------
# Alternativos: basta uno. "PERFIL DEL EGRESADO" no contiene "PERFIL EGRESADO", hacen falta
# las dos formas.
MARCADORES_PERFIL = (
    "PERFIL DE EGRESO",
    "PERFIL EGRESO",
    "PERFIL DEL EGRESADO",
    "PERFIL EGRESADO",
    "PERFIL PROFESIONAL",
)

# --- Alcance de cada elemento (lo manda la NOTA DE ALCANCE de la base de oro) ----------
# PERFIL         : se evidencia en el texto del perfil de egreso → entra en el cociente.
# FUENTE_EXTERNA : se evidencia en documentación separada (fuentes b/d/e/f) → NO evaluable
#                  sobre una hoja de perfil y, por tanto, FUERA del cociente. Se reporta
#                  aparte nombrando la fuente. Nunca se cuenta como incumplido en silencio.
ALCANCE_PERFIL = "PERFIL"
ALCANCE_FUENTE_EXTERNA = "FUENTE_EXTERNA"

# --- Umbrales de diseño (NO salen de la norma; son decisiones explícitas) --------------
# Ya NO existe ningún umbral de "verbos observables": medía un requisito inventado.
MIN_TERMINOS_DOMINIOS = 2      # elemento 2: dominios en plural, no una mención suelta
VENTANA_COOCURRENCIA = 200     # elementos 3, 4 y 5: caracteres entre los dos términos

# --- Familias léxicas ------------------------------------------------------------------
# Todas las expresiones se aplican sobre `normalizar(texto)` de `services.extraccion`:
# minúsculas, SIN TILDES, sin ':' y con espacios colapsados. Por eso aquí no hay tildes.

FAMILIA_RESULTADOS = {
    "resultados de aprendizaje": r"resultados? de(l)? aprendizaje",
    "RA numerado":               r"\bra\s?\d",
    "competencias declaradas":   r"competencias? (necesarias|profesionales|genericas|"
                                 r"especificas|del perfil|de(l)? egreso)",
    "logros de aprendizaje":     r"logros de(l)? aprendizaje",
    "al término de la formación": r"al (termino|finalizar|culminar|concluir|egresar)\b",
    "capacidades declaradas":    r"(sera|seran) capaces? de|tendran? las capacidades",
}

FAMILIA_DOMINIOS = {
    "dominio":                r"\bdominios?\b",
    "campo de la profesión":  r"campo (profesional|ocupacional|de accion|de estudio|laboral)",
    "núcleos":                r"nucleos? (basicos?|estructurantes?)",
    "áreas de conocimiento":  r"areas? de(l)? conocimiento",
    "disciplina":             r"\bdisciplinas?\b|multidisciplinar|interdisciplinar",
    "metodología":            r"metodolog(ia|ias|ico|ica|icos|icas)",
    "saberes":                r"saberes\b",
    "dominio teórico":        r"\bteoric(o|a|os|as)\b",
    "dominio técnico":        r"tecnico[ -]pedagogic|\btecnic(o|a|os|as)\b",
    "unidad de organización curricular": r"unidad(es)? de organizacion curricular",
}

# E4 — SABERES: lo que el egresado APRENDE (contenidos, núcleos, conocimientos, formación).
# DISJUNTA de FAMILIA_RESULTADOS a propósito: E4 pide que los saberes PERMITAN ALCANZAR los
# RA, o sea una relación entre DOS cosas distintas. Si las familias compartieran un lexema
# ("competencias" en ambas), la co-ocurrencia se dispararía sola y el elemento se regalaría.
FAMILIA_SABERES = {
    "saberes":            r"saberes\b",
    "conocimientos":      r"conocimientos?\b",
    "contenidos":         r"contenidos?\b",
    "núcleos":            r"nucleos? (basicos?|estructurantes?)",
    "formación":          r"formacion (profesional|integral|academica|solida|humana)|"
                          r"solida formacion|proceso de formacion",
    "asignaturas":        r"asignaturas?\b|catedras?\b",
    "destrezas y habilidades": r"destrezas?\b|habilidades?\b",
    "aprendizajes":       r"aprendizajes\b",
    "teóricos y prácticos": r"teoric(o|os|a|as) y practic(o|os|a|as)|"
                            r"practic(o|os|a|as) y teoric(o|os|a|as)",
}

# Actores EXTERNOS a la universidad que la norma nombra (fuente b). Ni "IEEE", ni "ACM", ni
# "association", ni "institute", ni "comunidad de ingenieros" están aquí: citar sus
# lineamientos NO es que hayan aportado a elaborar el perfil (NOTA DE ALCANCE, prohibición
# explícita del falso positivo ACM-IEEE).
FAMILIA_ACTORES = {
    "empleadores":              r"empleador(es)?\b",
    "graduados":                r"graduad(o|os|a|as)\b",
    "expertos académicos externos": r"expertos? (academicos?|externos?)|"
                                    r"pares? (academicos?|externos?)",
    "colegio profesional":      r"colegios? profesional(es)?",
    "gremio":                   r"gremi(o|os|al)\b",
    "organización profesional": r"(organizacion|asociacion)(es)? profesional(es)?",
    "cámara":                   r"camaras? (de comercio|de industrias|empresarial)",
    "sector productivo":        r"sector(es)? (productiv|empresarial|extern|laboral)",
    "grupos de interés":        r"grupos? de interes",
    "actores externos":         r"actores (externos|sociales|del entorno|clave)",
    "empresas empleadoras":     r"empresas? (empleadoras|del sector|receptoras)",
}

FAMILIA_PARTICIPACION = {
    "participación":            r"participacion|participaron|participado",
    "consulta":                 r"consulta(s|do|da|ron)?\b",
    "encuesta":                 r"encuesta(s|do|da|ron)?\b",
    "entrevista":               r"entrevista(s|do|da|ron)?\b",
    "mesa de trabajo":          r"mesas? de trabajo",
    "grupo focal":              r"grupos? focal(es)?",
    "taller":                   r"talleres? (de|con)\b",
    "socialización":            r"socializacion|socializad",
    "levantamiento de información": r"levantamiento de informacion",
    "validación con":           r"validacion (con|por)\b|validado (con|por)\b",
    "elaborado con":            r"elaborad(o|a) (con|por|junto)\b",
    "aportes":                  r"aportes? de\b",
    "acta o informe":           r"actas? de\b|informes? de (taller|mesa|reunion|consulta)",
}

FAMILIA_SEGUIMIENTO = {
    "seguimiento":       r"seguimiento\b",
    "monitoreo":         r"monitore(o|ar|a)\b",
    "evaluación periódica": r"evaluacion (periodica|permanente|continua|anual)",
    "revisión periódica":   r"revision (periodica|permanente|continua|anual)",
    "actualización":     r"actualizacion\b",
    "mejora continua":   r"mejora(miento)? continu(a|o)",
    "retroalimentación": r"retroalimentacion\b",
    "rediseño":          r"redisen(o|ar|a)\b",
    "vigencia":          r"vigencia\b",
}

FAMILIA_OBJETO_CURRICULAR = {
    "perfil":           r"perfil(es)?\b",
    "currículo":        r"curricul(o|ar|um|ares)\b",
    "malla":            r"malla\b",
    "carrera":          r"carrera\b",
    "graduados":        r"graduad(o|os|a|as)\b",
    "plan de estudios": r"plan(es)? de estudios?",
    "programa académico": r"programa(s)? academic(o|os)",
}


class Elemento:
    """Un elemento fundamental del Indicador 1 y su proxy léxico.

    familias : 1 familia  → se detecta si aparecen `minimo` términos DISTINTOS de ella.
               2 familias → se detecta si un término de cada una co-ocurre dentro de
                            `ventana` caracteres (los elementos 3, 4 y 5, que exigen relación
                            entre dos cosas, no la mera presencia de una).
    alcance  : ALCANCE_PERFIL         → entra en el cociente de Jaccard.
               ALCANCE_FUENTE_EXTERNA → NO evaluable sobre el perfil; se reporta aparte
                                        nombrando `fuente`. Su detector se ejecuta igual,
                                        pero sólo como señal informativa.
    """

    def __init__(self, numero, nombre, familias, minimo=1, ventana=VENTANA_COOCURRENCIA,
                 alcance=ALCANCE_PERFIL, fuente=None):
        self.numero = numero
        self.nombre = nombre
        self.familias = familias
        self.minimo = minimo
        self.ventana = ventana
        self.alcance = alcance
        self.fuente = fuente

    @property
    def etiqueta(self):
        return f"E{self.numero} · {self.nombre}"

    @property
    def evaluable_en_perfil(self):
        return self.alcance == ALCANCE_PERFIL

    def __repr__(self):
        return f"<Elemento {self.etiqueta}>"


ELEMENTOS_PERFIL = [
    Elemento(1, "Resultados de aprendizaje declarados",
             [("RESULTADOS", FAMILIA_RESULTADOS)], minimo=1),
    Elemento(2, "Dominios teóricos, metodológicos y técnicos",
             [("DOMINIOS", FAMILIA_DOMINIOS)], minimo=MIN_TERMINOS_DOMINIOS),
    Elemento(3, "Elaboración participativa con involucrados",
             [("ACTORES", FAMILIA_ACTORES), ("PARTICIPACIÓN", FAMILIA_PARTICIPACION)],
             alcance=ALCANCE_FUENTE_EXTERNA,
             fuente="b) actas/informes/encuestas del aporte de expertos externos, "
                    "organizaciones profesionales, empleadores y graduados; "
                    "e) publicación en la web"),
    Elemento(4, "Saberes verificables que permiten alcanzar los RA",
             [("SABERES", FAMILIA_SABERES), ("RESULTADOS", FAMILIA_RESULTADOS)]),
    Elemento(5, "Seguimiento y evaluación → mejora continua",
             [("SEGUIMIENTO", FAMILIA_SEGUIMIENTO),
              ("OBJETO CURRICULAR", FAMILIA_OBJETO_CURRICULAR)],
             alcance=ALCANCE_FUENTE_EXTERNA,
             fuente="d) políticas y procedimientos de seguimiento y evaluación; "
                    "f) acciones de mejora continua"),
]

TOTAL_ELEMENTOS = len(ELEMENTOS_PERFIL)
ELEMENTOS_EVALUABLES = [e for e in ELEMENTOS_PERFIL if e.evaluable_en_perfil]
ELEMENTOS_FUENTE_EXTERNA = [e for e in ELEMENTOS_PERFIL if not e.evaluable_en_perfil]


def _aciertos(familia: dict, texto_normalizado: str) -> dict:
    """{término: [posiciones]} de cada término de la familia presente en el texto."""
    encontrados = {}
    for termino, patron in familia.items():
        posiciones = [m.start() for m in re.finditer(patron, texto_normalizado)]
        if posiciones:
            encontrados[termino] = posiciones
    return encontrados


def _cooccurren(a: dict, b: dict, ventana: int):
    """Primer par (término_a, término_b) de las dos familias a menos de `ventana`
    caracteres. Devuelve None si no hay ninguno: las familias hablan de cosas distintas."""
    for termino_a, pos_a in a.items():
        for termino_b, pos_b in b.items():
            for i in pos_a:
                for j in pos_b:
                    if abs(i - j) <= ventana:
                        return termino_a, termino_b
    return None


def evaluar_elemento(elemento: Elemento, texto_normalizado: str):
    """Devuelve (detectado: bool, evidencia: list[str]).

    La evidencia son los términos que lo dispararon: es lo que hay que poder auditar a mano
    contra el PDF. Si la evidencia no convence a un lector humano, la detección es un falso
    positivo y así debe reportarse.

    OJO: para los elementos de ALCANCE_FUENTE_EXTERNA (3 y 5) este `detectado` NO es un
    veredicto: es sólo el rastro léxico. No lo uses para puntuar (ver `universo()`).
    """
    aciertos = [(nombre, _aciertos(familia, texto_normalizado))
                for nombre, familia in elemento.familias]

    if len(aciertos) == 1:
        _nombre, encontrados = aciertos[0]
        detectado = len(encontrados) >= elemento.minimo
        evidencia = sorted(encontrados)
        return detectado, evidencia

    (nombre_a, enc_a), (nombre_b, enc_b) = aciertos
    if not enc_a or not enc_b:
        # Se informa lo que sí hay, para que se vea POR QUÉ no cumple: casi siempre es que
        # aparece el actor pero nunca su participación (o el seguimiento pero de otra cosa).
        parcial = []
        if enc_a:
            parcial.append(f"{nombre_a}: {', '.join(sorted(enc_a))} (sin {nombre_b})")
        if enc_b:
            parcial.append(f"{nombre_b}: {', '.join(sorted(enc_b))} (sin {nombre_a})")
        return False, parcial

    par = _cooccurren(enc_a, enc_b, elemento.ventana)
    if par is None:
        return False, [f"{nombre_a}: {', '.join(sorted(enc_a))} y "
                       f"{nombre_b}: {', '.join(sorted(enc_b))} aparecen, pero a más de "
                       f"{elemento.ventana} caracteres: no se refieren a lo mismo"]
    return True, [f"{par[0]} + {par[1]} (a menos de {elemento.ventana} caracteres)"]


def elementos_detectados(texto_normalizado: str):
    """Devuelve (detectados: set[etiqueta], evidencias: dict[etiqueta -> list[str]]).

    `detectados` incluye el rastro de E3/E5 si lo hubiera. Quien puntúa debe intersecar con
    `universo()`, que sólo contiene los elementos evidenciables en el perfil.
    """
    detectados, evidencias = set(), {}
    for elemento in ELEMENTOS_PERFIL:
        ok, evidencia = evaluar_elemento(elemento, texto_normalizado)
        evidencias[elemento.etiqueta] = evidencia
        if ok:
            detectados.add(elemento.etiqueta)
    return detectados, evidencias


def universo() -> set:
    """A: los elementos EVIDENCIABLES EN EL PERFIL (E1, E2, E4).

    E3 y E5 NO están aquí: se evidencian en las fuentes b) y d)/f), no en el texto del
    perfil (NOTA DE ALCANCE de la base de oro). Incluirlos convertiría el Jaccard en una
    medida de "documentos que no me diste", con techo estructural de 3/5 para cualquier
    perfil del mundo. Se reportan aparte, nunca como incumplidos en silencio.
    """
    return {e.etiqueta for e in ELEMENTOS_EVALUABLES}


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 78)
    print("ESQUEMA DEL PERFIL DE EGRESO (Indicador 1)")
    print("=" * 78)
    print("El perfil NO es un formulario: es prosa. No tiene campos etiqueta→valor (por eso")
    print("CAMPOS: va vacío en la base de oro). Su esquema son los 5 elementos de la norma,")
    print("los 5 marcados [SEMÁNTICO].")
    print()
    print("  AVISO: lo que sigue es un PROXY LÉXICO de un juicio semántico. Mide cobertura")
    print("  de evidencia (¿el documento habla de esto?), NO comprensión (¿lo cumple?).")
    print("  El juez real en producción es el LLM. Estos umbrales son decisiones de diseño,")
    print("  no mandatos de la norma.")
    print()

    print(f"  MARCADORES DE PLANTILLA ({len(MARCADORES_PERFIL)}, alternativos: basta uno):")
    for marcador in MARCADORES_PERFIL:
        print(f"     · {marcador}")
    print()
    print("  UMBRALES DE DISEÑO:")
    print(f"     - términos distintos para 'dominios' (E2): {MIN_TERMINOS_DOMINIOS}")
    print(f"     - ventana de co-ocurrencia (E3, E4, E5):   {VENTANA_COOCURRENCIA} caracteres")
    print("     - (ya NO hay umbral de 'verbos observables': medía un requisito inventado")
    print("        que el CACES no pide. Ver el docstring de este módulo.)")
    print()
    print("  ALCANCE (NOTA DE ALCANCE de la base de oro):")
    print(f"     - evidenciables en el perfil → cociente sobre {len(ELEMENTOS_EVALUABLES)}: "
          f"{', '.join('E%d' % e.numero for e in ELEMENTOS_EVALUABLES)}")
    print(f"     - requieren fuente externa (fuera del cociente): "
          f"{', '.join('E%d' % e.numero for e in ELEMENTOS_FUENTE_EXTERNA)}")
    print()
    print(f"  LOS {TOTAL_ELEMENTOS} ELEMENTOS FUNDAMENTALES Y SU PROXY:")
    for elemento in ELEMENTOS_PERFIL:
        print()
        marca = "  " if elemento.evaluable_en_perfil else " *"
        print(f"  {marca} {elemento.etiqueta}")
        if not elemento.evaluable_en_perfil:
            print(f"      * NO EVALUABLE sobre el perfil: requiere fuente {elemento.fuente}")
        if len(elemento.familias) == 1:
            nombre, familia = elemento.familias[0]
            print(f"      regla: ≥{elemento.minimo} término(s) DISTINTO(S) de {nombre} "
                  f"({len(familia)} en la familia)")
        else:
            nombres = " + ".join(n for n, _f in elemento.familias)
            print(f"      regla: co-ocurrencia {nombres} a ≤{elemento.ventana} caracteres")
        for nombre, familia in elemento.familias:
            print(f"      {nombre} ({len(familia)}): {', '.join(sorted(familia))}")
    print()
    print("  Para medirlo sobre PDFs reales:  python scripts/completitud_perfil.py --todos")
