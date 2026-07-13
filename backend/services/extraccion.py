"""
Extracción de PDFs conservando la estructura visual.

Los documentos institucionales (sílabo, malla, guía de laboratorio) traen capa de texto:
no son escaneos. El problema nunca fue reconocer caracteres, sino que el orden de lectura
interno del PDF no corresponde a su disposición visual. `unstructured` colapsa la tabla
de DATOS GENERALES en una sola línea ("Modalidad: PRESENCIAL Departamento: Área de
Conocimiento: ..."), de modo que resulta imposible saber qué valor pertenece a qué
etiqueta y todo campo parece vacío.

Aquí se usa el mismo motor que `unstructured` emplea internamente para esos PDFs
(pdfminer.six), pidiéndole las coordenadas que aquél descarta. El OCR de `unstructured`
queda como respaldo, sólo para PDFs escaneados.
"""
import os
import re
import unicodedata
from collections import Counter

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams

# Un PDF con menos caracteres de texto que esto se considera escaneado y va a OCR.
UMBRAL_CAPA_TEXTO = 200

# El valor de una etiqueta puede estar hasta dos filas por debajo: en el sílabo, entre
# "SESIONES SEMANALES" y su valor se interpone la fila de la carga horaria.
FILAS_DE_BUSQUEDA = 2

# Código de asignatura de la malla: cinco letras y cuatro alfanuméricos (EXCTA0301).
COD_ASIGNATURA = re.compile(r"^[A-Z]{5}[0-9A-Z]{4}$")


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin dos puntos, espacios colapsados."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().replace(":", " ").split())


def comparable(texto: str) -> str:
    """
    Forma canónica para buscar marcadores de plantilla dentro del documento.

    Además de tildes y mayúsculas, neutraliza lo que rompe una comparación literal:
    el separador de celdas "|" que introduce `_texto_ordenado`, y los guiones, que Word
    escribe indistintamente como '-', '–' o '—'. Sin esto, un sílabo cuyo título quedara
    partido en dos cajas ("PROGRAMA DE ASIGNATURA - | SÍLABO") se declararía plantilla no
    reconocida.
    """
    limpio = normalizar(texto)
    for caracter in "|-–—_":
        limpio = limpio.replace(caracter, " ")
    return " ".join(limpio.split())


def _es_etiqueta(texto: str) -> bool:
    return texto.rstrip().endswith(":")


def _es_rotada(texto: str) -> bool:
    """Las etiquetas giradas 90 grados se extraen una letra por línea."""
    lineas = [l for l in texto.split("\n") if l.strip()]
    return len(lineas) > 2 and all(len(l.strip()) <= 1 for l in lineas)


# ---------------------------------------------------------------------------
# Lectura del PDF
# ---------------------------------------------------------------------------
def _cajas(ruta_pdf: str):
    """Devuelve (cajas horizontales, cajas rotadas) con sus coordenadas."""
    cajas, rotadas = [], []
    for num_pagina, pagina in enumerate(extract_pages(ruta_pdf, laparams=LAParams())):
        for elemento in pagina:
            if not isinstance(elemento, LTTextContainer):
                continue
            texto = elemento.get_text().strip()
            if not texto:
                continue
            rotada = _es_rotada(texto)
            (rotadas if rotada else cajas).append({
                "pagina": num_pagina,
                "x": elemento.x0,
                "y": elemento.y1,
                "y0": elemento.y0,
                "t": "".join(texto.split()) if rotada else " ".join(texto.split()),
            })
    return cajas, rotadas


# Altura típica de una línea de texto. Acota la tolerancia de agrupación para que una
# celda combinada verticalmente no pueda absorber las filas que atraviesa.
ALTURA_DE_LINEA = 20.0


def _agrupar_filas(cajas: list) -> list:
    """
    Agrupa las cajas en filas visuales comparando su centro vertical.

    No sirve ordenar por el borde superior: en el formulario, la celda del valor es más
    alta que la de su etiqueta y empieza por encima ("DEPARTAMENTO DE CIENCIAS DE LA
    COMPUTACION" arranca 9,6 puntos más arriba que "DEPARTAMENTO:"). Tampoco sirve el
    solapamiento simple: en la tabla de contribución al perfil de egreso hay celdas
    combinadas de 54 puntos de alto que cruzan dos filas y se las tragarían enteras.

    Dos cajas comparten fila si sus centros distan menos de media línea de texto. La
    tolerancia se acota a `ALTURA_DE_LINEA` para que una celda alta no ensanche el
    criterio en proporción a su propio tamaño.
    """
    filas = []
    for caja in sorted(cajas, key=lambda c: (c["pagina"], -c["y"], c["x"])):
        if filas:
            ancla = filas[-1][0]
            centro_ancla = (ancla["y"] + ancla["y0"]) / 2
            centro_caja = (caja["y"] + caja["y0"]) / 2
            alto = max(ancla["y"] - ancla["y0"], caja["y"] - caja["y0"])
            tolerancia = 0.5 * min(alto, ALTURA_DE_LINEA)
            if ancla["pagina"] == caja["pagina"] and abs(centro_caja - centro_ancla) <= tolerancia:
                filas[-1].append(caja)
                continue
        filas.append([caja])
    return [sorted(fila, key=lambda c: c["x"]) for fila in filas]


def _enderezar(rotadas: list, x_max: float = 700.0) -> list:
    """
    Recupera las etiquetas giradas 90 grados ("Primer PAO", "UNIDAD BASICA").

    Se extraen una letra por línea y en orden inverso. Se invierte cada fragmento y se
    encadenan los contiguos de la misma columna. pdfminer pierde las 'i' de estas
    etiquetas ("QuntoPAO"), pero el nivel sigue siendo identificable.
    """
    utiles = sorted((c for c in rotadas if c["x"] < x_max),
                    key=lambda c: (round(c["x"] / 8), c["y"]))
    etiquetas, actual, previa = [], [], None
    for caja in utiles:
        rompe = previa is not None and (
            round(caja["x"] / 8) != round(previa["x"] / 8) or caja["y"] - previa["y"] > 25
        )
        if rompe and actual:
            etiquetas.append("".join(actual))
            actual = []
        actual.append(caja["t"][::-1])
        previa = caja
    if actual:
        etiquetas.append("".join(actual))
    return [e for e in etiquetas if len(e) > 3]


# ---------------------------------------------------------------------------
# Emparejamiento etiqueta -> valor
# ---------------------------------------------------------------------------
def _casa(clave: str, mapa: dict):
    """
    Empareja el texto de una caja con el nombre de un campo. Tres formas, todas con
    límite de palabra para no confundir 'Docente' con 'Correo electrónico del docente':

    - igual:      "Modalidad"
    - calificada: "Resultado de Aprendizaje de la Carrera (Unidad de Competencia)"
    - sufijo:     "DOCENCIA" dentro de "carga horaria: DOCENCIA"

    La forma calificada exige el paréntesis. Si bastara el prefijo, el valor
    "DEPARTAMENTO DE CIENCIAS DE LA COMPUTACION" se tomaría por la etiqueta
    "Departamento" y el campo parecería vacío.
    """
    if clave in mapa:
        return mapa[clave]
    coincidencias = [n for c, n in mapa.items()
                     if clave.startswith(c + " (") or (len(clave) >= 6 and c.endswith(" " + clave))]
    return max(coincidencias, key=len) if coincidencias else None


# Pie de página del formulario: nunca es el valor de un campo.
_PIE_DE_PAGINA = re.compile(r"^(CÓDIGO:\s*SGC|Página \d+ de \d+)", re.IGNORECASE)

# Rótulos impresos en la plantilla que no llevan dos puntos y no preceden a ningún campo
# declarado, así que la regla geométrica no los detecta. En un formulario en blanco el
# resolvedor los tomaba por valor y el campo de encima parecía lleno.
ROTULOS_DE_PLANTILLA = frozenset(normalizar(r) for r in (
    "Unidad de Organización",
    "Campo de Formación",
    "Núcleos Básicos de",
    "TÍTULO Y DENOMINACIÓN",
    "PERFIL SUGERIDO DEL DOCENTE",
    "CARGA HORARIA POR COMPONENTES DE APRENDIZAJE",
    "PROGRAMA DE ASIGNATURA - SÍLABO",
    "GUIA DE USO DE LABORATORIO",
    "Rubro",
    "Nombres y Apellido",
    "Unidad / Cargo",
    "Firma",
    # Fila de fechas del sílabo: sus rótulos van SIN dos puntos, a diferencia del
    # "Fecha Elaboración:" de la cabecera. En un sílabo vacío, la carga horaria bajaba
    # hasta aquí y tomaba el rótulo por valor.
    "Fecha Elaboración",
    "Fecha de Actualización",
    "Fecha de Ejecución",
))


def _es_estructura(texto: str) -> bool:
    """
    ¿Es texto de la plantilla y no contenido escrito por el docente?

    Sólo se reconocen por su FORMA los dos casos inequívocos: las etiquetas con dos puntos
    y el pie de página. La forma no sirve para más: "PRESENCIAL" y "CIENCIAS DE LA
    COMPUTACION" son valores reales y están en mayúsculas igual que un encabezado. Las
    etiquetas huérfanas sin dos puntos ("Unidad de Organización") se detectan por posición,
    no por forma: ver la regla de la columna en `_valor_de`.
    """
    limpio = texto.strip()
    return (_es_etiqueta(limpio)
            or bool(_PIE_DE_PAGINA.match(limpio))
            or normalizar(limpio) in ROTULOS_DE_PLANTILLA)


def _valor_de(filas: list, i: int, j: int, mapa: dict):
    """
    Busca el valor de la etiqueta situada en filas[i][j]: a su derecha en la misma fila;
    si no, hasta dos filas más abajo.
    """
    fila = filas[i]
    etiqueta = fila[j]

    def es_otra_etiqueta(caja):
        return (_es_estructura(caja["t"])
                or _casa(normalizar(caja["t"]), mapa) is not None)

    for caja in fila[j + 1:]:
        if es_otra_etiqueta(caja):
            break
        return caja["t"]

    # Encabezado de sección: ocupa su fila entero y NO lleva dos puntos ("Proyecto
    # Integrador", "PERFIL SUGERIDO DEL DOCENTE"). Su contenido va debajo, sin alinear.
    # Una etiqueta con dos puntos y sola en su fila ("FECHA:") sí exige alineación: si no,
    # se tomaría por valor el encabezado de la sección siguiente y el campo parecería lleno.
    es_encabezado = len(fila) == 1 and not _es_etiqueta(etiqueta["t"])
    # Cabecera de tabla: dos o más celdas, todas etiquetas, así que la fila de valores de
    # abajo se corresponde una a una. Si la fila ya contiene algún valor no lo es, y mirar
    # abajo traería el valor de otro campo. Con una sola celda la regla degeneraría: en la
    # guía de laboratorio, "FECHA:" tomaría por valor el encabezado de la sección siguiente.
    es_cabecera = len(fila) >= 2 and all(es_otra_etiqueta(c) for c in fila)

    for k in range(i + 1, min(i + 1 + FILAS_DE_BUSQUEDA, len(filas))):
        candidatos = [c for c in filas[k] if not es_otra_etiqueta(c)]
        if not candidatos:
            continue
        if es_encabezado:
            return candidatos[0]["t"]
        if es_cabecera and len(candidatos) == len(fila):
            return candidatos[j]["t"]

        if len(fila) == 1:
            # Etiqueta sola con dos puntos ("Docente:"): su valor cuelga debajo, a su
            # derecha o a su altura, nunca a la izquierda. En la guía, "FECHA:" está en el
            # margen derecho y debajo empieza otra sección: 438 puntos a la izquierda.
            alineados = [c for c in candidatos if -10 <= c["x"] - etiqueta["x"] <= 120]
        else:
            alineados = [c for c in candidatos if abs(c["x"] - etiqueta["x"]) <= 45]
        if alineados:
            return min(alineados, key=lambda c: abs(c["x"] - etiqueta["x"]))["t"]
    return None


def resolver_campos(cajas: list, nombres) -> dict:
    """
    Para cada campo, localiza su etiqueta y devuelve el valor que la acompaña, o None si
    la etiqueta está pero no tiene nada escrito. Los campos cuya etiqueta no aparece se
    omiten del resultado: no se puede afirmar nada de ellos.

    Los rótulos impresos de la plantilla (`ROTULOS_DE_PLANTILLA`) no cuentan como valor:
    en un formulario en blanco el resolvedor bajaba hasta el rótulo del campo siguiente
    y ocho campos vacíos parecían llenos.
    """
    filas = _agrupar_filas(cajas)
    mapa = {normalizar(n): n for n in nombres if n}
    resuelto = {}
    for i, fila in enumerate(filas):
        for j, caja in enumerate(fila):
            nombre = _casa(normalizar(caja["t"]), mapa)
            if nombre is None or nombre in resuelto:
                continue
            resuelto[nombre] = _valor_de(filas, i, j, mapa)
    return resuelto


# ---------------------------------------------------------------------------
# Malla curricular: reconstrucción celda por celda
# ---------------------------------------------------------------------------
def _parece_codigo(token: str) -> bool:
    """
    Tolerante a propósito. La malla contiene códigos malformados: el prerrequisito de
    'Aseguramiento de la Calidad de Software' dice COMPAM08 cuando la asignatura es
    COMPA0M08. Con el patrón estricto ese prerrequisito se leería como vacío y el
    indicador se rechazaría por un error de tipeo, no de llenado.
    """
    return (7 <= len(token) <= 10 and token.isalnum() and token.isupper()
            and any(c.isdigit() for c in token))


def _normalizar_codigo(texto: str) -> str:
    """El kerning del PDF parte los códigos: 'EXCT A0301' -> 'EXCTA0301'."""
    texto = " ".join(texto.split())
    partes = [p.strip() for p in re.split(r"\s+O\s+", texto)]
    partes = [p.replace(" ", "") if COD_ASIGNATURA.match(p.replace(" ", "")) else p for p in partes]
    return " O ".join(partes)


def _es_prerrequisito(texto: str) -> bool:
    if texto in ("N/A", "NIVELACION"):
        return True
    return all(_parece_codigo(p) for p in texto.split(" O "))


def es_malla(cajas: list) -> bool:
    tiene_hpao = any(c["t"] == "HPAO" for c in cajas)
    return tiene_hpao and sum(1 for c in cajas if COD_ASIGNATURA.match(c["t"])) >= 10


# Paso entre celdas de la malla de referencia, medido sobre las etiquetas HPAO. Las mallas
# se exportan a pliegos distintos: la misma malla aparece a escala 1 o a escala 3,3. Y el
# escalado no siempre es uniforme: en las dos mallas reales la relación alto/ancho difiere
# un 12%, así que se deduce un factor horizontal y otro vertical.
PASO_X_REFERENCIA = 97.5
PASO_Y_REFERENCIA = 57.0


def _paso(valores, tolerancia: float = 5.0) -> float:
    """Separación típica entre líneas de una rejilla, agrupando coordenadas repetidas."""
    lineas = []
    for v in sorted(valores):
        if not lineas or v - lineas[-1] > tolerancia:
            lineas.append(v)
    separaciones = [b - a for a, b in zip(lineas, lineas[1:])]
    if not separaciones:
        return 0.0
    from statistics import median
    return median(separaciones)


def escala_de_malla(cajas: list):
    """
    Deduce (escala horizontal, escala vertical) del diagrama a partir de la rejilla que
    forman las etiquetas `HPAO`.

    Las ventanas de búsqueda de la celda estaban calibradas sobre una única malla. Otra
    malla igual de válida, exportada a un pliego 3,27 veces mayor, las dejaba todas fuera
    de rango y el sistema reconstruía cero asignaturas.
    """
    hpao = [c for c in cajas if c["t"] == "HPAO"]
    paso_x = _paso([c["x"] for c in hpao])
    paso_y = _paso([c["y"] for c in hpao])

    ex = paso_x / PASO_X_REFERENCIA if paso_x else 0.0
    ey = paso_y / PASO_Y_REFERENCIA if paso_y else 0.0
    # Una malla de una sola columna o de una sola fila no revela ese eje: se toma el otro.
    ex = ex or ey or 1.0
    ey = ey or ex
    # Límites laxos: sólo descartan valores absurdos, no acotan escalas legítimas.
    return max(0.1, min(30.0, ex)), max(0.1, min(30.0, ey))


def filas_de_malla(cajas: list) -> list:
    """
    Una fila por asignatura. Su ancla es el código; el nombre va a la derecha, el
    prerrequisito debajo, y las horas y créditos en la subcolumna de la etiqueta HPAO.
    Todas las distancias se expresan en múltiplos de la escala del diagrama.
    """
    ex, ey = escala_de_malla(cajas)
    etiquetas_hpao = [c for c in cajas if c["t"] == "HPAO"]
    filas = []
    for ancla in sorted((c for c in cajas if COD_ASIGNATURA.match(c["t"])),
                        key=lambda c: (-c["y"], c["x"])):
        hpao = next((h for h in etiquetas_hpao
                     if 58 * ex <= h["x"] - ancla["x"] <= 94 * ex
                     and -34 * ey <= h["y"] - ancla["y"] <= -16 * ey), None)
        if hpao is None:
            continue  # es un código usado como prerrequisito, no una celda de asignatura

        dx = lambda c: c["x"] - ancla["x"]
        dy = lambda c: c["y"] - ancla["y"]

        nombre = " ".join(c["t"] for c in sorted(cajas, key=dx)
                          if 18 * ex <= dx(c) <= 72 * ex and abs(dy(c)) <= 3 * ey
                          and not COD_ASIGNATURA.match(c["t"]))

        prerrequisitos = []
        for caja in sorted(cajas, key=dx):
            valor = _normalizar_codigo(caja["t"])
            if not (-8 * ex <= dx(caja) <= 58 * ex and -26 * ey <= dy(caja) <= -4 * ey
                    and _es_prerrequisito(valor)):
                continue
            # Un código que no respeta el patrón de nueve caracteres es un error de tipeo
            # de la malla, no un campo vacío. Se señala sin invalidar la fila.
            prerrequisitos.append(" O ".join(
                p if (p in ("N/A", "NIVELACION") or COD_ASIGNATURA.match(p)) else f"{p} [CÓDIGO MALFORMADO]"
                for p in valor.split(" O ")))

        numeros = [c["t"] for c in sorted(cajas, key=lambda c: -c["y"])
                   if abs(c["x"] - hpao["x"]) <= 14 * ex
                   and hpao["y"] - 24 * ey < c["y"] < hpao["y"] and c["t"].isdigit()]

        filas.append({
            "codigo": ancla["t"],
            "nombre": nombre or "VACIO",
            "prerrequisito": " O ".join(prerrequisitos) or "VACIO",
            "hpao": numeros[0] if numeros else "VACIO",
            "creditos": numeros[1] if len(numeros) > 1 else "VACIO",
        })
    return filas


def _reconstruir_malla(cajas: list, rotadas: list) -> str:
    filas = filas_de_malla(cajas)
    niveles = _enderezar(rotadas)

    nombres = {f["nombre"] for f in filas}
    vistos, contexto = set(), []
    for caja in sorted(cajas, key=lambda c: (-c["y"], c["x"])):
        t = caja["t"]
        if (len(t) <= 3 or t.isdigit() or COD_ASIGNATURA.match(t) or t in vistos or t in nombres
                or t in ("HPAO", "CD", "CPE", "CA", "HS", "N/A", "NIVELACION")):
            continue
        vistos.add(t)
        contexto.append(t)

    lineas = [f"{f['codigo']} | {f['nombre']} | PRE: {f['prerrequisito']} | "
              f"HPAO: {f['hpao']} | CR: {f['creditos']}" for f in filas]
    return "\n".join([
        "MALLA CURRICULAR (reconstruida a partir de las coordenadas del PDF)",
        f"NIVELES Y UNIDADES DETECTADOS ({len(niveles)}): " + " · ".join(niveles),
        "",
        f"ASIGNATURAS ({len(filas)}):",
        *lineas,
        "",
        "CONTEXTO (cabecera, unidades y totales declarados):",
        " · ".join(contexto),
    ])


# ---------------------------------------------------------------------------
# Texto ordenado y respaldo OCR
# ---------------------------------------------------------------------------
def _texto_ordenado(cajas: list) -> str:
    """Reconstruye el orden visual y colapsa cabeceras y pies repetidos."""
    lineas = [" | ".join(c["t"] for c in fila) for fila in _agrupar_filas(cajas)]
    repeticiones = Counter(lineas)
    vistas, salida = set(), []
    for linea in lineas:
        if repeticiones[linea] >= 3 and len(linea) < 90:
            if linea in vistas:
                continue
            vistas.add(linea)
        salida.append(linea)
    return "\n".join(salida)


def _ocr(ruta_pdf: str) -> str:
    """
    Respaldo para PDFs escaneados. Importación diferida: es la ruta cara y arrastra
    Tesseract y Poppler, que sólo hacen falta aquí.
    """
    try:
        from unstructured.partition.pdf import partition_pdf
        elementos = partition_pdf(filename=ruta_pdf, strategy="hi_res", languages=["spa"])
    except Exception as error:
        raise ValueError(
            "El PDF no tiene capa de texto y el respaldo OCR no está disponible. "
            "Instala los extras: pip install 'unstructured[pdf]' pi-heif, y añade Poppler "
            f"y Tesseract al PATH. Causa: {error}"
        ) from error
    return "\n".join(str(el) for el in elementos)


def extraer_documento(ruta_pdf: str) -> dict:
    """
    Devuelve {"texto", "cajas", "ocr", "es_malla"} con un solo parseo del PDF.

    Las cajas se devuelven para que el llamador pueda resolver campos etiqueta->valor
    sin volver a leer el fichero.
    """
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(ruta_pdf)

    cajas, rotadas = _cajas(ruta_pdf)
    if sum(len(c["t"]) for c in cajas) < UMBRAL_CAPA_TEXTO:
        print("-> [EXTRACCIÓN] Sin capa de texto. Cayendo a OCR (hi_res).")
        return {"texto": _ocr(ruta_pdf), "cajas": [], "ocr": True, "es_malla": False}

    if es_malla(cajas):
        filas = filas_de_malla(cajas)
        if filas:
            print(f"-> [EXTRACCIÓN] Malla detectada. Reconstruidas {len(filas)} asignaturas.")
            return {"texto": _reconstruir_malla(cajas, rotadas), "cajas": cajas,
                    "ocr": False, "es_malla": True}
        # Entregar "ASIGNATURAS (0)" sería afirmarle al modelo que la malla está vacía, y
        # el modelo lo creería. Ante una geometría que no sabemos leer, se envía el texto
        # en orden visual y se deja que el LLM juzgue lo que hay.
        print("-> [EXTRACCIÓN] Malla detectada pero no reconstruible. Se envía el texto ordenado.")
        return {"texto": _texto_ordenado(cajas), "cajas": cajas, "ocr": False, "es_malla": True}

    return {"texto": _texto_ordenado(cajas), "cajas": cajas, "ocr": False, "es_malla": False}
