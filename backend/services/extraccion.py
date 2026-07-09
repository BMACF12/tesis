"""
Extracción de texto de PDFs preservando el orden visual.

Los PDFs institucionales (sílabo, malla, guía de laboratorio) traen capa de texto:
no son escaneos. El problema no es reconocer caracteres sino que el orden de lectura
interno del PDF no corresponde a la disposición visual. Esto se corrige ordenando las
cajas de texto por coordenadas.

El OCR (unstructured + Tesseract) queda como respaldo, sólo si el PDF no trae texto.
"""
import os
import re
import unicodedata
from collections import Counter

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams

# Un PDF con menos caracteres que esto se considera escaneado y va a OCR.
UMBRAL_CAPA_TEXTO = 200

# Código de asignatura de la malla: cinco letras y cuatro alfanuméricos (EXCTA0301, COMPA0P01).
_COD = re.compile(r"^[A-Z]{5}[0-9A-Z]{4}$")


def _es_rotada(texto: str) -> bool:
    """Las etiquetas giradas 90 grados se extraen una letra por línea. Son ruido."""
    lineas = [l for l in texto.split("\n") if l.strip()]
    return len(lineas) > 2 and all(len(l.strip()) <= 1 for l in lineas)


def _cajas(ruta_pdf: str) -> tuple:
    """Devuelve (cajas horizontales, cajas rotadas) con sus coordenadas."""
    cajas, rotadas = [], []
    for num_pagina, pagina in enumerate(extract_pages(ruta_pdf, laparams=LAParams())):
        for elemento in pagina:
            if not isinstance(elemento, LTTextContainer):
                continue
            texto = elemento.get_text().strip()
            if not texto:
                continue
            destino = rotadas if _es_rotada(texto) else cajas
            destino.append({
                "pagina": num_pagina,
                "x": elemento.x0,
                "y": elemento.y1,
                "y0": elemento.y0,
                "t": "".join(texto.split()) if _es_rotada(texto) else " ".join(texto.split()),
            })
    return cajas, rotadas


def _enderezar(rotadas: list, x_max: float = 700.0) -> list:
    """
    Recupera las etiquetas giradas 90 grados ("Primer PAO", "UNIDAD BASICA").

    Se extraen una letra por línea y en orden inverso. Se invierte cada fragmento y
    se encadenan los que comparten columna y quedan verticalmente contiguos.
    Nota: pdfminer pierde las 'i' de estas etiquetas ("QuntoPAO"), pero el nivel
    sigue siendo identificable.
    """
    utiles = sorted((c for c in rotadas if c["x"] < x_max), key=lambda c: (round(c["x"] / 8), c["y"]))
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


def _normalizar_codigo(texto: str) -> str:
    """El kerning del PDF parte los códigos: 'EXCT A0301' -> 'EXCTA0301'."""
    texto = " ".join(texto.split())
    partes = [p.strip() for p in re.split(r"\s+O\s+", texto)]
    partes = [p.replace(" ", "") if _COD.match(p.replace(" ", "")) else p for p in partes]
    return " O ".join(partes)


def _parece_codigo(token: str) -> bool:
    """
    Tolerante a propósito. La malla contiene códigos malformados: el prerrequisito de
    'Aseguramiento de la Calidad de Software' dice COMPAM08 cuando la asignatura es
    COMPA0M08. Si se exige el patrón estricto, ese prerrequisito se lee como vacío y
    el indicador se rechaza por un error que no es de llenado sino de tipeo.
    """
    return (7 <= len(token) <= 10
            and token.isalnum() and token.isupper()
            and any(c.isdigit() for c in token))


def _es_prerrequisito(texto: str) -> bool:
    if texto in ("N/A", "NIVELACION"):
        return True
    return all(_parece_codigo(p) for p in texto.split(" O "))


def _es_malla(cajas: list) -> bool:
    tiene_hpao = any(c["t"] == "HPAO" for c in cajas)
    codigos = sum(1 for c in cajas if _COD.match(c["t"]))
    return tiene_hpao and codigos >= 10


def _reconstruir_malla(cajas: list, rotadas: list) -> str:
    """
    Reconstruye la malla celda por celda usando la geometría.

    Cada asignatura es una celda cuyo ancla es su código. Dentro de la celda:
    el nombre va a la derecha del código, el prerrequisito debajo, y las horas
    y créditos en la subcolumna de la etiqueta HPAO.
    """
    etiquetas_hpao = [c for c in cajas if c["t"] == "HPAO"]
    filas = []

    anclas = sorted((c for c in cajas if _COD.match(c["t"])), key=lambda c: (-c["y"], c["x"]))
    for ancla in anclas:
        hpao = next(
            (h for h in etiquetas_hpao
             if 58 <= h["x"] - ancla["x"] <= 94 and -34 <= h["y"] - ancla["y"] <= -16),
            None,
        )
        if hpao is None:
            continue  # es un código usado como prerrequisito, no una celda de asignatura

        dx = lambda c: c["x"] - ancla["x"]
        dy = lambda c: c["y"] - ancla["y"]

        nombre = [c["t"] for c in sorted(cajas, key=dx)
                  if 18 <= dx(c) <= 72 and abs(dy(c)) <= 3 and not _COD.match(c["t"])]

        prerrequisitos = []
        for caja in sorted(cajas, key=dx):
            valor = _normalizar_codigo(caja["t"])
            if not (-8 <= dx(caja) <= 58 and -26 <= dy(caja) <= -4 and _es_prerrequisito(valor)):
                continue
            # Un código que no respeta el patrón de nueve caracteres es un error de
            # tipeo de la malla, no un campo vacío. Se señala sin invalidar la fila.
            prerrequisitos.append(" O ".join(
                p if (p in ("N/A", "NIVELACION") or _COD.match(p)) else f"{p} [CÓDIGO MALFORMADO]"
                for p in valor.split(" O ")))

        numeros = [c["t"] for c in sorted(cajas, key=lambda c: -c["y"])
                   if abs(c["x"] - hpao["x"]) <= 14
                   and hpao["y"] - 24 < c["y"] < hpao["y"]
                   and c["t"].isdigit()]

        filas.append(
            f"{ancla['t']} | {' '.join(nombre) or 'VACIO'}"
            f" | PRE: {' O '.join(prerrequisitos) or 'VACIO'}"
            f" | HPAO: {numeros[0] if numeros else 'VACIO'}"
            f" | CR: {numeros[1] if len(numeros) > 1 else 'VACIO'}"
        )

    niveles = _enderezar(rotadas)

    # Los nombres de asignatura ya viajan en las filas: aquí sólo el texto de contexto
    # (cabecera institucional, totales, notas), deduplicado para no inflar el prompt.
    nombres = {fila.split(" | ")[1] for fila in filas}
    vistos, contexto = set(), []
    for caja in sorted(cajas, key=lambda c: (-c["y"], c["x"])):
        texto = caja["t"]
        if (len(texto) <= 3 or texto.isdigit() or _COD.match(texto)
                or texto in ("HPAO", "CD", "CPE", "CA", "HS", "N/A", "NIVELACION")
                or texto in vistos or texto in nombres):
            continue
        vistos.add(texto)
        contexto.append(texto)

    return "\n".join([
        "MALLA CURRICULAR (reconstruida a partir de las coordenadas del PDF)",
        f"NIVELES Y UNIDADES DETECTADOS ({len(niveles)}): " + " · ".join(niveles),
        "",
        f"ASIGNATURAS ({len(filas)}):",
        *filas,
        "",
        "CONTEXTO (cabecera, unidades y totales declarados):",
        " · ".join(contexto),
    ])


def _agrupar_filas(cajas: list) -> list:
    """
    Agrupa las cajas en filas visuales por solapamiento vertical.

    No sirve redondear la coordenada superior: en las tablas del formulario, la celda
    del valor es más alta que la de su etiqueta y su borde superior queda por encima
    (en la guía de laboratorio, "DEPARTAMENTO DE CIENCIAS DE LA COMPUTACION" empieza
    9,6 puntos más arriba que "DEPARTAMENTO:"). Ordenar por ese borde separa el valor
    de su etiqueta y el campo parece vacío. Dos cajas están en la misma fila si sus
    franjas verticales se solapan en al menos la mitad de la más baja de las dos.
    """
    filas = []
    for caja in sorted(cajas, key=lambda c: (c["pagina"], -c["y"], c["x"])):
        if filas:
            ancla = filas[-1][0]  # la caja más alta de la fila abierta
            solape = min(ancla["y"], caja["y"]) - max(ancla["y0"], caja["y0"])
            umbral = 0.5 * min(caja["y"] - caja["y0"], ancla["y"] - ancla["y0"])
            if ancla["pagina"] == caja["pagina"] and solape >= umbral:
                filas[-1].append(caja)
                continue
        filas.append([caja])
    return [sorted(fila, key=lambda c: c["x"]) for fila in filas]


def _texto_ordenado(cajas: list) -> str:
    """Reconstruye el orden visual y colapsa cabeceras y pies repetidos."""
    lineas = [" | ".join(c["t"] for c in fila) for fila in _agrupar_filas(cajas)]

    # Una cabecera o pie de página aparece idéntica en cada página. Basta con una.
    repeticiones = Counter(lineas)
    vistas = set()
    salida = []
    for linea in lineas:
        if repeticiones[linea] >= 3 and len(linea) < 90:
            if linea in vistas:
                continue
            vistas.add(linea)
        salida.append(linea)
    return "\n".join(salida)


# Campos que identifican a qué carrera pertenece el documento. Etiqueta y valor viven
# en filas distintas del formulario, así que el LLM tiene que emparejarlos por columna
# y se equivoca: llega a declarar vacío un campo que le contradice. Se extraen aquí.
ETIQUETAS_IDENTIFICACION = (
    "Resultado de Aprendizaje de la Carrera",
    "Área de Conocimiento",
    "Nombre Asignatura",
    "Departamento",
    "CARRERA",
    "ASIGNATURA",
)


def _es_etiqueta(texto: str) -> bool:
    return texto.rstrip().endswith(":")


FILAS_DE_BUSQUEDA = 2  # el valor puede estar hasta dos filas por debajo de su etiqueta


def _casa(clave: str, mapa: dict):
    """
    Empareja el texto de una caja con el nombre de un campo. Tres formas, todas con
    límite de palabra para no confundir 'Docente' con 'Correo electrónico del docente':

    - igual:      "Modalidad"
    - calificada: "Resultado de Aprendizaje de la Carrera (Unidad de Competencia)"
    - sufijo:     "DOCENCIA" dentro de "carga horaria de Docencia, ..."

    La forma calificada exige el paréntesis: si bastara el prefijo, el valor
    "DEPARTAMENTO DE CIENCIAS DE LA COMPUTACION" se tomaría por la etiqueta
    "Departamento" y el campo parecería vacío.
    """
    if clave in mapa:
        return mapa[clave]
    coincidencias = [n for c, n in mapa.items()
                     if clave.startswith(c + " (") or (len(clave) >= 6 and c.endswith(" " + clave))]
    return max(coincidencias, key=len) if coincidencias else None


def _valor_de(filas: list, i: int, j: int, mapa: dict):
    """
    Busca el valor de la etiqueta situada en filas[i][j].

    A su derecha en la misma fila; si no, hasta dos filas más abajo en su misma columna
    (en el sílabo, la carga horaria y las sesiones semanales tienen una fila intermedia).
    Si la etiqueta ocupa su fila entera es un encabezado de sección: entonces vale como
    contenido cualquier texto de las filas siguientes, sin exigir alineación de columna.
    """
    fila = filas[i]
    etiqueta = fila[j]

    def es_otra_etiqueta(caja):
        return _es_etiqueta(caja["t"]) or _casa(normalizar(caja["t"]), mapa) is not None

    for caja in fila[j + 1:]:
        if es_otra_etiqueta(caja):
            break
        return caja["t"]

    es_encabezado = len(fila) == 1
    # Cabecera de tabla: todas sus celdas son etiquetas, así que la fila de valores de
    # abajo se corresponde una a una. Si la fila ya contiene algún valor, no lo es: sus
    # valores viven en la propia fila y mirar abajo traería el de otro campo.
    es_cabecera = all(es_otra_etiqueta(c) for c in fila)

    for k in range(i + 1, min(i + 1 + FILAS_DE_BUSQUEDA, len(filas))):
        candidatos = [c for c in filas[k] if not es_otra_etiqueta(c)]
        if not candidatos:
            continue
        if es_encabezado:
            return candidatos[0]["t"]
        if es_cabecera and len(candidatos) == len(fila):
            return candidatos[j]["t"]
        alineados = [c for c in candidatos if abs(c["x"] - etiqueta["x"]) <= 45]
        if alineados:
            return min(alineados, key=lambda c: abs(c["x"] - etiqueta["x"]))["t"]
    return None


def _identificar_campos(cajas: list) -> dict:
    resueltos = resolver_campos(cajas, ETIQUETAS_IDENTIFICACION)
    return {etiqueta: valor[:220] for etiqueta, valor in resueltos.items() if valor}


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin dos puntos finales, espacios colapsados."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().replace(":", " ").split())


def resolver_campos(cajas: list, nombres) -> dict:
    """
    Para cada nombre de campo, busca su etiqueta en el documento y devuelve el valor
    que la acompaña, o None si la etiqueta existe pero no tiene nada escrito.
    Los campos cuya etiqueta no aparece se omiten: no se puede afirmar nada de ellos.
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


def _bloque_identificacion(cajas: list) -> str:
    campos = _identificar_campos(cajas)
    if not campos:
        return "(no se pudo extraer ningún campo de identificación del documento)"
    return "\n".join(f"- {etiqueta}: {valor}" for etiqueta, valor in campos.items())


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
            "Instala los extras: pip install 'unstructured[pdf]' pi-heif, y añade "
            f"Poppler y Tesseract al PATH. Causa: {error}"
        ) from error
    return "\n".join(str(el) for el in elementos)


def extraer_documento(ruta_pdf: str):
    """
    Devuelve (texto, bloque de identificación, cajas). Un solo parseo del PDF.

    Las cajas se devuelven para que el llamador pueda verificar después, con
    `resolver_campos`, qué campos declara la norma y cuáles están realmente vacíos.
    """
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(ruta_pdf)

    cajas, rotadas = _cajas(ruta_pdf)
    if sum(len(c["t"]) for c in cajas) < UMBRAL_CAPA_TEXTO:
        print("-> [EXTRACCIÓN] Sin capa de texto. Cayendo a OCR (hi_res).")
        return _ocr(ruta_pdf), "(documento escaneado: sin campos de identificación)", []

    identificacion = _bloque_identificacion(cajas)
    if _es_malla(cajas):
        print("-> [EXTRACCIÓN] Malla detectada. Reconstruyendo por coordenadas.")
        return _reconstruir_malla(cajas, rotadas), identificacion, cajas

    return _texto_ordenado(cajas), identificacion, cajas


def extraer_texto(ruta_pdf: str) -> str:
    return extraer_documento(ruta_pdf)[0]
