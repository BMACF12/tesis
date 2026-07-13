"""
EXPERIMENTO AISLADO — verificación de tablas vacías en el sílabo.

NO forma parte del sistema en producción. Es un script de sólo lectura: no importa nada
del pipeline salvo el extractor, no modifica la norma ni la base de oro, y ninguna de sus
conclusiones alimenta el veredicto. Sirve para responder una sola pregunta:

    ¿Cuánto mejoraría la detección de documentos incompletos si, además de los 20 campos
    de DATOS GENERALES, se comprobara que las TABLAS de las secciones 3 a 10 tienen filas
    de datos y no sólo su cabecera impresa?

MOTIVACIÓN
----------
Los 20 campos que el sistema verifica hoy cubren únicamente la sección 1 del sílabo (~35
de 176 líneas). Las secciones 2 a 10 no son pares etiqueta→valor sino TABLAS, y ahí la
pregunta correcta no es "¿este campo tiene valor?" sino "¿esta tabla tiene alguna fila?".

El sílabo trampa conserva todas las secciones, pero sus tablas están vacías:

    7. BIBLIOGRAFÍA BÁSICA
       Titulo | Autor | Edición | Año | Idioma | Editorial   <- cabecera impresa
       (nada)                                                 <- ninguna obra

El LLM aprueba esos elementos porque ve el ancla y una fila de texto: confunde la cabecera
con una obra. Por eso la trampa saca 44% en vez de ser rechazada.

Uso:
    python scripts/experimento_tablas.py            # corpus completo
    python scripts/experimento_tablas.py 21278      # un documento, con el detalle
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extraccion import extraer_documento, normalizar  # noqa: E402

SILABOS = (r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
           r"\INDICADOR 4 Syllabus\*.pdf")

# (nombre, ancla de la sección, cabecera impresa de la tabla)
# La cabecera se verificó idéntica en cuatro sílabos distintos y en la trampa.
TABLAS = (
    ("Métodos de enseñanza",      "PROYECCIÓN METODOLÓGICA",     "Metodos de Enseñanza - Aprendizaje"),
    ("Empleo de TIC",             "EMPLEO DE TICS",               "Empleo de Tics en los Procesos de Aprendizaje"),
    ("Ponderación de evaluación", "TÉCNICAS Y PONDERACION",       "Técnica de evaluación"),
    ("Bibliografía básica",       "BIBLIOGRAFÍA BÁSICA",          "Titulo"),
    ("Bibliografía complementaria", "BIBLIOGRAFÍA COMPLEMENTARIA", "Titulo"),
    ("Lecturas principales",      "LECTURAS PRINCIPALES",         "Tema"),
    ("Acuerdos del docente",      "ACUERDOS",                     "Del Docente:"),
)

# Texto de la plantilla que aparece dentro de una tabla y NO es una fila de datos.
RUIDO = tuple(normalizar(t) for t in (
    "Titulo", "Autor", "Edición", "Año", "Idioma", "Editorial",
    "Tema", "Texto", "Página", "URL",
    "Técnica de evaluación", "1er Parcial", "2do Parcial", "3er Parcial", "TOTAL:",
    "Metodos de Enseñanza - Aprendizaje", "Empleo de Tics en los Procesos de Aprendizaje",
    "Del Docente:", "De los Estudiantes:", "FIRMAS DE LEGALIZACIÓN",
))


# Encabezado de una sección numerada del sílabo ("4. RESULTADOS DEL APRENDIZAJE...").
# Marca el final de la tabla anterior.
_SECCION = re.compile(r"^\s*\d{1,2}\.\s+[A-ZÁÉÍÓÚÑ]")


def es_fila_de_datos(linea: str, exige_numero: bool = False) -> bool:
    """
    ¿Es una fila con contenido escrito por el docente, o texto impreso de la plantilla?

    Se descarta: la cabecera de columnas, la numeración huérfana ("1", "2", "3" sin texto
    al lado, como deja la trampa), el pie de página y las líneas demasiado cortas.

    `exige_numero` es para la tabla de ponderación: la trampa conserva los nombres de las
    técnicas ("Exposición", "Examen Parcial") pero sin ninguna nota. La fila existe y está
    incompleta, así que sólo cuenta si trae al menos un número.
    """
    limpio = " ".join(linea.split())
    if not limpio or "SGC.DI.321" in limpio or _SECCION.match(limpio):
        return False

    celdas = [c.strip() for c in limpio.split("|") if c.strip()]
    if not celdas:
        return False

    # Numeración huérfana: la trampa deja "1", "2", "3", "4" sin nada al lado.
    utiles = [c for c in celdas if not c.rstrip(".").isdigit()]
    if not utiles:
        return False

    # Toda la fila es texto impreso de la plantilla.
    if all(normalizar(c) in RUIDO for c in utiles):
        return False

    if exige_numero and not any(c.strip().isdigit() for c in celdas):
        return False

    return sum(len(c) for c in utiles) >= 8


def analizar_tablas(texto: str) -> dict:
    """Devuelve {nombre de la tabla: nº de filas de datos}."""
    lineas = texto.split("\n")
    en_mayusculas = [l.upper() for l in lineas]
    resultado = {}

    for nombre, ancla, cabecera in TABLAS:
        inicio = next((i for i, l in enumerate(en_mayusculas) if ancla in l), None)
        if inicio is None:
            resultado[nombre] = None  # sección ausente
            continue

        # La tabla acaba en la siguiente sección numerada o en el siguiente ancla.
        fin = len(lineas)
        otras = [a for _n, a, _c in TABLAS if a != ancla]
        for j in range(inicio + 1, len(lineas)):
            if _SECCION.match(lineas[j].strip()) or any(a in en_mayusculas[j] for a in otras):
                fin = j
                break

        cabecera_normal = normalizar(cabecera)
        filas = 0
        for j in range(inicio + 1, fin):
            linea = lineas[j]
            # La cabecera de la tabla nunca es una fila de datos... salvo cuando pdfminer
            # la fusiona con la primera obra ("Titulo Inteligencia artificial : ..."), que
            # es justo la señal de que la tabla SÍ tiene contenido.
            if normalizar(linea) == cabecera_normal:
                continue
            if es_fila_de_datos(linea, exige_numero=(nombre == "Ponderación de evaluación")):
                filas += 1
        resultado[nombre] = filas

    return resultado


def evaluar(ruta):
    texto = extraer_documento(ruta)["texto"]
    tablas = analizar_tablas(texto)
    vacias = [n for n, f in tablas.items() if f == 0]
    ausentes = [n for n, f in tablas.items() if f is None]
    return tablas, vacias, ausentes


def detalle(fragmento):
    candidatos = [r for r in sorted(glob.glob(SILABOS))
                  if "_Reporte" not in r and fragmento.lower() in os.path.basename(r).lower()]
    if not candidatos:
        print(f"No se encontró ningún sílabo que contenga '{fragmento}'.")
        raise SystemExit(1)

    ruta = candidatos[0]
    tablas, vacias, ausentes = evaluar(ruta)

    print("=" * 76)
    print("EXPERIMENTO — TABLAS CON O SIN FILAS DE DATOS")
    print("=" * 76)
    print(f"Documento: {os.path.basename(ruta)[:62]}")
    print()
    print(f"{'tabla':30} {'filas de datos':>16}   estado")
    print("-" * 76)
    for nombre, filas in tablas.items():
        if filas is None:
            estado, marca = "SECCIÓN AUSENTE", "!"
        elif filas == 0:
            estado, marca = "VACÍA (sólo cabecera)", "!"
        else:
            estado, marca = "con contenido", " "
        print(f"{marca}{nombre:29} {('—' if filas is None else filas):>16}   {estado}")
    print("-" * 76)
    print()
    print(f"Tablas vacías  : {len(vacias)}  {vacias if vacias else ''}")
    print(f"Tablas ausentes: {len(ausentes)}  {ausentes if ausentes else ''}")


def corpus():
    print("=" * 92)
    print("EXPERIMENTO — ¿CUÁNTAS TABLAS VACÍAS HAY EN CADA SÍLABO?")
    print("=" * 92)
    print("Hoy el sistema sólo verifica los 20 campos de DATOS GENERALES (sección 1).")
    print("Esta columna mide lo que NO se verifica: las tablas de las secciones 3 a 10.")
    print()
    print(f"{'documento':52} {'tablas vacías':>14} {'ausentes':>9}")
    print("-" * 92)

    limpios = con_vacias = 0
    for ruta in sorted(glob.glob(SILABOS)):
        if "_Reporte" in ruta:
            continue
        try:
            _t, vacias, ausentes = evaluar(ruta)
        except Exception as error:
            print(f"{os.path.basename(ruta)[:52]:52}   ERROR {type(error).__name__}")
            continue
        marca = " " if not vacias else "!"
        if vacias:
            con_vacias += 1
        else:
            limpios += 1
        print(f"{marca}{os.path.basename(ruta)[:51]:51} {len(vacias):>14} {len(ausentes):>9}")

    print("-" * 92)
    print(f"Sílabos con TODAS las tablas llenas : {limpios}")
    print(f"Sílabos con alguna tabla VACÍA      : {con_vacias}")
    print()
    print("CONCLUSIÓN DEL EXPERIMENTO")
    print("Si un documento tiene tablas vacías, hoy el sistema no lo detecta: sus 20 campos")
    print("de DATOS GENERALES pueden estar llenos y el LLM aprueba las secciones porque ve")
    print("el ancla y confunde la cabecera de la tabla con una fila de datos.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        detalle(sys.argv[1])
    else:
        corpus()
