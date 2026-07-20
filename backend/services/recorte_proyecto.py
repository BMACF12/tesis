"""
Recorte del PROYECTO CURRICULAR (Indicador 2) para que quepa en la ventana del LLM.

El problema que resuelve
------------------------
El documento del Indicador 2 no es una plantilla de 1-6 páginas como el sílabo, la malla o la
guía: es el formulario oficial de rediseño de carrera (SENESCYT/CES). El ejemplar aprobado de
referencia (`Reporte_Carrera_Software_26072017.pdf`, 113 páginas) extrae **333.218 caracteres**
≈ 95.000 tokens. La cuota diaria de Groq es de 100.000 tokens: enviar el texto íntegro
(`"documento": texto`) agota la cuota del día entero con UN solo documento, y además desborda
la ventana del modelo. Este módulo reduce ese texto a ~20.000 caracteres (~6.000 tokens)
quedándose sólo con lo que los cinco elementos fundamentales del indicador necesitan.

Por qué se recorta por SECCIONES y no por los primeros N caracteres
-------------------------------------------------------------------
Un `texto[:20000]` se quedaría en la sección "Pertinencia" (que sola son ~117.000 caracteres) y
nunca llegaría a "Perfil de egreso", "Requisitos de graduación" ni "Infraestructura", que están
en las páginas 30-90. Los elementos 3 y 4 saldrían incumplidos por un corte nuestro, no por un
defecto del documento. Se corta por secciones reales del formulario.

Cómo se localizan las secciones (a principio de línea, con la caja alta exacta)
------------------------------------------------------------------------------
Los encabezados se reconocen SÓLO al principio de línea del texto que devuelve
`extraccion._texto_ordenado`. No es un capricho: medido sobre el PDF real, "Pertinencia"
aparece 8 veces y "Misión" 8 veces en el cuerpo del texto (dentro de párrafos, citas de la LOES
y resultados de aprendizaje), pero **una sola vez a principio de línea** — el encabezado de la
sección de verdad. Buscar la palabra suelta partiría el documento por donde no es.

Cómo se trunca cada sección (lo que NO se hace: cortar por la cabeza)
--------------------------------------------------------------------
Cada sección del formulario es una sucesión de preguntas oficiales (`¿…?`, líneas cortas) con su
respuesta debajo (líneas de prosa de hasta 7.000 caracteres). La evidencia NO está siempre al
principio: en "Pertinencia", "demanda ocupacional" está en el carácter 99.396 y "escenarios
laborables" en el 113.387 de una sección de 116.965 — es decir, al FINAL. Un truncado por la
cabeza (`seccion[:cap]`) cortaría exactamente la evidencia del elemento 2.

Por eso el recorte es de "esqueleto + cata":
  1. Se tira el ruido de paginación ("Página 10 de 113").
  2. Se conservan ENTERAS todas las líneas cortas (≤ `UMBRAL_LINEA_CORTA`): son las preguntas
     oficiales del formulario y los sub-encabezados. Son baratas y son el índice de la sección:
     gracias a ellas sobrevive "¿Cuáles son las funciones y roles de los escenarios laborales…?"
     aunque esté en la última línea de una sección de 117k.
  3. El presupuesto que sobra se reparte A PARTES IGUALES entre las líneas largas (la prosa), y
     de cada una se toma su cabeza. Repartir en vez de cortar por el final garantiza que la
     cata cubra la sección de principio a fin.

Honestidad con el modelo
------------------------
Todo truncado va marcado en el texto que se entrega (`MARCA_LINEA`, `MARCA_SECCION`) y el
recorte lleva una cabecera que le dice al LLM qué se omitió y por qué. Un recorte silencioso
haría que el modelo tomara nuestro corte por una sección incompleta y generara incumplimientos
espurios: el elemento diría "no cumple" por culpa del recortador, no del documento.

Qué se descarta y por qué
-------------------------
`SECCIONES_DESCARTADAS` no sirve a ningún elemento del Indicador 2:
  - "Convenios" (9.671 ch): una lista de nombres de ficheros PDF adjuntos. Ruido puro.
  - "Descripción microcurricular" (76.292 ch): la ficha de cada asignatura, repetida decenas de
    veces. La NOTA DE LECTURA de la base de oro ya advierte al LLM de que no la tome como
    evidencia del perfil ni del currículo global.
  - "Personal académico y administrativo" y "Estudio técnico para la fijación del arancel":
    son de otras dimensiones del modelo CACES (docencia, gestión), no de Currículo.

Este módulo NO importa `tareas_ia` ni Celery: es texto puro, así que se puede probar y medir
sin worker, sin Redis y sin gastar cuota (mismo criterio que `completitud_malla.py`).
"""
import re

# --- Presupuesto -------------------------------------------------------------
# Objetivo global del recorte. 20.000 caracteres ≈ 6.000 tokens (en español el ratio medido
# ronda 3,4 ch/token): frente a los ~95.000 tokens del texto íntegro, deja sitio de sobra para
# la norma, las reglas, el maestro y la respuesta dentro de la cuota diaria de 100.000.
OBJETIVO_TOTAL = 20_000

# Una línea de hasta este tamaño se conserva entera: es una pregunta del formulario o un
# sub-encabezado. Medido sobre el PDF real, la pregunta oficial más larga tiene 248 caracteres.
UMBRAL_LINEA_CORTA = 260

# Ninguna línea larga baja de aquí: por debajo, la cata deja de ser citable y el LLM no puede
# justificar con una cita literal (Regla 4 de la base de oro).
MINIMO_POR_LINEA = 120

# Recorte de emergencia cuando el documento no trae ningún encabezado conocido.
RECORTE_POR_DEFECTO = OBJETIVO_TOTAL

MARCA_LINEA = " [… truncado …]"
MARCA_SECCION = "[... sección truncada: se entregan {vistos} de {total} caracteres ...]"

# Ruido de paginación del formulario ("Página 10 de 113").
_PAGINACION = re.compile(r"^Página \d+ de \d+$")

# --- Mapa de secciones -------------------------------------------------------
# Encabezados reales del formulario, EN EL ORDEN EN QUE APARECEN, con el tope de caracteres que
# se le concede a cada uno. `None` = sección descartada (no es evidencia de ningún elemento).
#
# Los topes no son redondeos a ojo: se reparten según lo que cada elemento necesita citar.
# Pertinencia es la más generosa (5.000) porque es la ÚNICA evidencia del elemento 2 y trae 8
# preguntas oficiales que hay que cubrir enteras. Perfil de egreso (4.200) sostiene el elemento
# 1. Las secciones de identidad (Datos institucionales, Misión) caben enteras y son baratas.
# La suma de los topes (21.000) es el peor caso; el recorte real del documento base mide menos
# porque varias secciones no llegan a su tope.
SECCIONES = (
    ("Datos institucionales", 900),
    ("Misión", 900),
    ("Datos generales de la carrera", 900),
    ("Convenios", None),
    ("Requisitos de ingreso", 700),
    ("Requisitos de graduación", 2_200),
    ("Pertinencia", 4_600),
    ("Planificación curricular", 2_000),
    ("Perfil de egreso", 3_800),
    ("Metodología y ambientes de aprendizajes", 2_400),
    ("Descripción microcurricular", None),
    ("Infraestructura y equipamiento", 1_900),
    ("Personal académico", None),
    ("Estudio técnico", None),
)

SECCIONES_UTILES = tuple(nombre for nombre, tope in SECCIONES if tope is not None)
SECCIONES_DESCARTADAS = tuple(nombre for nombre, tope in SECCIONES if tope is None)
TOPES = {nombre: tope for nombre, tope in SECCIONES}

CABECERA = (
    "[RECORTE AUTOMÁTICO DEL PROYECTO CURRICULAR]\n"
    "Este documento original tiene {original} caracteres y no cabe entero en la ventana. Se te\n"
    "entregan {recortado} caracteres: sólo las secciones que los elementos fundamentales del\n"
    "Indicador 2 necesitan, cada una recortada a una muestra de su contenido.\n"
    "Secciones entregadas: {entregadas}.\n"
    "Secciones omitidas por no ser evidencia de este indicador: {omitidas}.\n"
    "IMPORTANTE: donde leas «… truncado …» el texto CONTINÚA en el documento original. Es un\n"
    "corte de esta herramienta, NO una sección incompleta del proyecto: no lo cites como\n"
    "defecto ni declares por ello que un elemento no se cumple. Las preguntas oficiales del\n"
    "formulario (las líneas «¿…?») se conservan íntegras; lo truncado son sus respuestas.\n"
)


def _encabezado_de(linea: str):
    """Devuelve el encabezado de sección que abre esta línea, o None.

    Se compara a principio de línea y con la caja alta exacta del formulario: en el PDF real
    "Pertinencia" y "Misión" aparecen 8 veces cada una dentro del cuerpo del texto, pero sólo
    una a principio de línea. Comparar sin distinguir mayúsculas o buscando la subcadena suelta
    partiría el documento por un párrafo cualquiera.
    """
    for nombre, _tope in SECCIONES:
        if linea.startswith(nombre):
            return nombre
    return None


def secciones_de_proyecto(texto: str) -> dict:
    """Parte el texto en {encabezado: cuerpo}, respetando el orden del formulario.

    Una sección va desde su encabezado hasta el encabezado conocido siguiente, sea útil o
    descartado: por eso `SECCIONES` incluye también los descartados. Si no fuera así,
    "Pertinencia" se comería "Planificación curricular" y el recorte entregaría 117k.

    Un encabezado repetido (p. ej. "Personal académico" aparece 2 veces) se queda con su
    PRIMERA aparición; las siguientes sólo sirven para cerrar la sección anterior.
    """
    lineas = texto.splitlines()
    marcas = []
    for indice, linea in enumerate(lineas):
        nombre = _encabezado_de(linea)
        if nombre:
            marcas.append((indice, nombre))

    encontradas = {}
    for posicion, (indice, nombre) in enumerate(marcas):
        fin = marcas[posicion + 1][0] if posicion + 1 < len(marcas) else len(lineas)
        if nombre in encontradas:
            continue
        encontradas[nombre] = "\n".join(lineas[indice:fin])
    return encontradas


def _muestrear(indices: list, coste: dict, presupuesto: int) -> list:
    """Elige un subconjunto de `indices` que quepa en `presupuesto`, repartido por toda la lista.

    Muestrea con paso uniforme (1 de cada k) en vez de cortar por el final. Es la diferencia
    entre enseñarle al modelo los 30 primeros laboratorios y enseñarle laboratorios del
    principio, del medio y del final del catálogo (incluidos los de la Extensión Latacunga, que
    están al final). Devuelve los índices elegidos, en orden.
    """
    if not indices:
        return []
    for paso in range(1, len(indices) + 1):
        elegidos = indices[::paso]
        if sum(coste[i] for i in elegidos) <= presupuesto:
            return elegidos
    return indices[:1]


def _recortar_seccion(cuerpo: str, tope: int) -> str:
    """Recorta una sección a `tope` caracteres conservando su esqueleto. Respeta el tope.

    Tres casos, en orden de preferencia (siempre se conserva el encabezado de la sección):

    A) Caben todas las líneas cortas y sobra presupuesto para dar al menos `MINIMO_POR_LINEA`
       a cada línea larga: se conservan TODAS las líneas y se trunca la cabeza de las largas
       con una cuota igual para todas. Es el caso de las secciones de prosa (Pertinencia,
       Perfil de egreso): sobreviven íntegras las preguntas oficiales del formulario y se cata
       la respuesta de cada una, de principio a fin de la sección.

    B) Caben las cortas pero no queda para todas las largas: se conservan todas las cortas (el
       esqueleto: las preguntas) y se MUESTREAN las largas con paso uniforme.

    C) Ni las líneas cortas caben: la sección es un catálogo (Infraestructura son ~140 líneas
       cortas del tipo "Nombre del laboratorio | Laboratorio General 7"). Se muestrean con paso
       uniforme para enseñar el patrón a lo largo de todo el catálogo.
    """
    lineas = [l for l in cuerpo.splitlines() if not _PAGINACION.match(l.strip())]
    if not lineas:
        return cuerpo[:tope]

    original = sum(len(l) + 1 for l in lineas)
    if original <= tope:
        return "\n".join(lineas)

    encabezado, resto = lineas[0], lineas[1:]
    disponible = tope - (len(encabezado) + 1) - (len(MARCA_SECCION) + 1)

    cortos = [i for i, l in enumerate(resto) if len(l) <= UMBRAL_LINEA_CORTA]
    largos = [i for i, l in enumerate(resto) if len(l) > UMBRAL_LINEA_CORTA]
    gasto_cortos = sum(len(resto[i]) + 1 for i in cortos)

    if gasto_cortos > disponible:
        # Caso C: catálogo de líneas cortas. Se muestrean las cortas y se tiran las largas.
        coste = {i: len(resto[i]) + 1 for i in cortos}
        elegidos = set(_muestrear(cortos, coste, disponible))
        cuerpo_final = [resto[i] for i in sorted(elegidos)]
    else:
        presupuesto = disponible - gasto_cortos
        # Cada línea larga no cuesta sólo su cuota de texto: cuesta además la marca de truncado
        # y su salto de línea. Sin descontarlos, el tope se desborda (medido: la sección
        # "Metodología y ambientes de aprendizajes" entregaba 2.533 ch contra un tope de 2.400).
        coste_fijo = len(MARCA_LINEA) + 1
        cuota = (presupuesto // len(largos)) - coste_fijo if largos else 0
        if not largos or cuota >= MINIMO_POR_LINEA:
            # Caso A: entran todas las líneas; las largas se catan con cuota igual.
            elegidos = set(range(len(resto)))
        else:
            # Caso B: se conservan las cortas enteras y se muestrean las largas al mínimo.
            cuota = MINIMO_POR_LINEA
            coste = {i: cuota + len(MARCA_LINEA) + 1 for i in largos}
            elegidos = set(cortos) | set(_muestrear(largos, coste, presupuesto))
        cuerpo_final = []
        for i in sorted(elegidos):
            linea = resto[i]
            if len(linea) <= UMBRAL_LINEA_CORTA:
                cuerpo_final.append(linea)
            else:
                cuerpo_final.append(linea[:cuota].rstrip() + MARCA_LINEA)

    salida = [encabezado] + cuerpo_final
    entregado = sum(len(l) + 1 for l in salida)
    salida.append(MARCA_SECCION.format(vistos=entregado, total=original))
    return "\n".join(salida)


def resumen_recorte(texto: str) -> dict:
    """Devuelve el recorte y sus medidas, sin imprimir nada.

    Lo usan `tareas_ia` (para el print de diagnóstico) y `completitud_proyecto.py` (para medir
    la reducción real sobre el corpus). Claves:
        recorte, original, recortado, por_defecto, secciones (nombre → (crudo, recortado)),
        entregadas, omitidas, ausentes.
    """
    encontradas = secciones_de_proyecto(texto)
    utiles = [n for n in SECCIONES_UTILES if n in encontradas]

    if not utiles:
        # Degradación con gracia: el documento no trae los encabezados esperados (no es el
        # formulario de rediseño, o la extracción falló). Se entrega la cabeza del texto en vez
        # de reventar o de mandar una cadena vacía, que el LLM leería como documento en blanco.
        recorte = texto[:RECORTE_POR_DEFECTO]
        if len(texto) > RECORTE_POR_DEFECTO:
            recorte += "\n" + MARCA_SECCION.format(vistos=RECORTE_POR_DEFECTO, total=len(texto))
        return {"recorte": recorte, "original": len(texto), "recortado": len(recorte),
                "por_defecto": True, "secciones": {}, "entregadas": [],
                "omitidas": [n for n in SECCIONES_DESCARTADAS if n in encontradas],
                "ausentes": list(SECCIONES_UTILES)}

    partes, detalle = [], {}
    for nombre in utiles:
        cuerpo = encontradas[nombre]
        recortada = _recortar_seccion(cuerpo, TOPES[nombre])
        detalle[nombre] = (len(cuerpo), len(recortada))
        partes.append(recortada)

    cuerpo_final = "\n\n".join(partes)
    omitidas = [n for n in SECCIONES_DESCARTADAS if n in encontradas]
    cabecera = CABECERA.format(
        original=len(texto), recortado=len(cuerpo_final),
        entregadas=", ".join(utiles),
        omitidas=", ".join(omitidas) if omitidas else "(ninguna)")
    recorte = cabecera + "\n" + cuerpo_final
    return {"recorte": recorte, "original": len(texto), "recortado": len(recorte),
            "por_defecto": False, "secciones": detalle, "entregadas": utiles,
            "omitidas": omitidas,
            "ausentes": [n for n in SECCIONES_UTILES if n not in encontradas]}


def recortar_proyecto(texto: str) -> str:
    """Texto del proyecto curricular listo para el prompt. Es la función que usa `tareas_ia`."""
    return resumen_recorte(texto)["recorte"]
