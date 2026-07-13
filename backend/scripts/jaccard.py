"""
Métrica de Jaccard para un documento cualquiera (sílabo o guía de laboratorio).

QUÉ ES JACCARD AQUÍ
-------------------
No compara dos documentos entre sí. Compara DOS CONJUNTOS:

    A = las secciones/campos que faltan según el AUDITOR (tú, leyendo el PDF)
    B = las secciones/campos que el SISTEMA detecta como faltantes

    J(A, B) = |A ∩ B| / |A ∪ B|

Si ambos conjuntos son vacíos (documento completo y el sistema no reporta nada) el
cociente es 0/0: INDEFINIDO. No es un 1,0 merecido, es que no había nada que medir.

USO
---
    python scripts/jaccard.py 21278                  # ver qué detecta el sistema
    python scripts/jaccard.py 21278 --faltan ""      # el auditor dice: no falta nada
    python scripts/jaccard.py 21495 --faltan "Empleo de TIC, Lecturas principales, Acuerdos"

El argumento --faltan es TU lectura del PDF: la lista de lo que de verdad falta.
Acepta nombres parciales (basta con que sean inequívocos).
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extraccion import extraer_documento, normalizar  # noqa: E402
from services.tareas_ia import (  # noqa: E402
    _abrir_base, _campos_sin_llenar, _plantilla_valida, _recuperar_norma,
)

CORPUS = [
    r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS\**\*.pdf",
    r"C:\Users\User\Downloads\GUIAS\GUIAS\*.pdf",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "Auditoria_CACES", "**", "*.pdf"),
]

# ---------------------------------------------------------------------------
# Inventario del formulario oficial. Cada entrada es una sección o tabla que un
# documento COMPLETO debe tener con contenido. Verificado cruzando 5 sílabos completos
# y 10 guías: lo que aparece en todos es la plantilla, no el contenido de uno.
# ---------------------------------------------------------------------------
SECCIONES_SILABO = [
    ("Datos generales",             "1. DATOS GENERALES",              None),
    # Ojo: la cabecera de la tabla de la sección 4 empieza también por "PROYECTO
    # INTEGRADOR" ("PROYECTO INTEGRADOR DEL NIVEL RESULTADO DE APRENDIZAJE..."). El ancla
    # debe ser la línea EXACTA, o corta la sección 4 y la deja vacía.
    ("Proyecto integrador",         "=PROYECTO INTEGRADOR",            None),
    ("Perfil sugerido del docente", "PERFIL SUGERIDO DEL DOCENTE",     None),
    ("Sistema de contenidos",       "2. SISTEMA DE CONTENIDOS",        None),
    ("Métodos de enseñanza",        "METODOS DE ENSEÑANZA",            None),
    ("Empleo de TIC",               "EMPLEO DE TICS",                  None),
    ("Contribución al perfil",      "4. RESULTADOS DEL APRENDIZAJE",   None),
    ("Ponderación de evaluación",   "6. TÉCNICAS Y PONDERACION",       "numero"),
    ("Bibliografía básica",         "7. BIBLIOGRAFÍA BÁSICA",          None),
    ("Bibliografía complementaria", "8. BIBLIOGRAFÍA COMPLEMENTARIA",  None),
    ("Lecturas principales",        "9. LECTURAS PRINCIPALES",         None),
    ("Acuerdos del docente",        "DEL DOCENTE",                     None),
    ("Acuerdos de los estudiantes", "DE LOS ESTUDIANTES",              None),
    ("Firmas de legalización",      "FIRMAS DE LEGALIZACIÓN",          None),
]

SECCIONES_GUIA = [
    ("Información de la guía", "A. INFORMACIÓN DE LA GUÍA", None),
    ("Introducción",           "INTRODUCCIÓN",              None),
    ("Objetivos",              "OBJETIVOS",                 None),
    ("Equipos y materiales",   "EQUIPOS",                   None),
    ("Precauciones",           "PRECAUCIONES",              None),
    ("Actividades",            "ACTIVIDADES POR DESARROLLAR", None),
    ("Resultados obtenidos",   "RESULTADOS OBTENIDOS",      None),
    ("Conclusiones",           "CONCLUSIONES",              None),
    ("Recomendaciones",        "RECOMENDACIONES",           None),
    ("Control de cambios",     "B. CONTROL DE CAMBIOS",     None),
    ("Aprobación",             "C. APROBACIÓN",             None),
]

# Texto impreso de la plantilla: aparece dentro de una sección y NO es contenido.
RUIDO = tuple(normalizar(t) for t in (
    "Titulo", "Autor", "Edición", "Año", "Idioma", "Editorial",
    "Tema", "Texto", "Página", "URL",
    "Técnica de evaluación", "1er Parcial", "2do Parcial", "3er Parcial", "TOTAL:",
    "Metodos de Enseñanza - Aprendizaje", "Empleo de Tics en los Procesos de Aprendizaje",
    "Del Docente:", "De los Estudiantes:", "FIRMAS DE LEGALIZACIÓN", "CONTENIDOS",
    "PROYECTO INTEGRADOR DEL NIVEL RESULTADO DE APRENDIZAJE POR UNIDAD CURRICULAR",
    "Rubro", "Nombres y Apellido", "Unidad / Cargo", "Firma", "Fecha", "Versión",
    "Elaborado por:", "Revisado por:", "Aprobado por:",
))

_SECCION_NUM = re.compile(r"^\s*\d{1,2}\.\s+[A-ZÁÉÍÓÚÑ]")


def _es_contenido(linea: str, exige_numero: bool = False) -> bool:
    """¿Es contenido escrito, o texto impreso de la plantilla?"""
    limpio = " ".join(linea.split())
    if not limpio or "SGC.DI.321" in limpio or _SECCION_NUM.match(limpio):
        return False

    celdas = [c.strip() for c in limpio.split("|") if c.strip()]
    utiles = [c for c in celdas if not c.rstrip(".").isdigit()]
    if not utiles:
        return False  # numeración huérfana: "1", "2", "3" sin nada al lado
    if all(normalizar(c) in RUIDO for c in utiles):
        return False  # sólo la cabecera impresa
    if exige_numero and not any(c.strip().isdigit() for c in celdas):
        return False  # una técnica de evaluación sin ninguna nota está incompleta
    return sum(len(c) for c in utiles) >= 8


def analizar(ruta):
    """Devuelve (indicador, secciones, faltantes según el sistema)."""
    documento = extraer_documento(ruta)
    vector_db = _abrir_base()
    _norma, meta = _recuperar_norma(vector_db, documento["texto"])

    valida, faltan_marcadores = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
    if not valida:
        return meta, None, None, faltan_marcadores

    indicador = meta["indicador"]
    plantilla = SECCIONES_SILABO if indicador == 4 else SECCIONES_GUIA
    lineas = documento["texto"].split("\n")
    mayusculas = [l.upper() for l in lineas]

    def coincide(linea, ancla):
        """Un ancla con '=' delante exige coincidencia EXACTA de la línea."""
        return linea.strip() == ancla[1:] if ancla.startswith("=") else ancla in linea

    anclas = [a for _n, a, _m in plantilla]
    estado = {}
    for nombre, ancla, modo in plantilla:
        inicio = next((i for i, l in enumerate(mayusculas) if coincide(l, ancla)), None)
        if inicio is None:
            estado[nombre] = "AUSENTE"
            continue

        # La sección acaba en la siguiente sección numerada o en otro ancla. Cuidado: el
        # ancla "PROYECTO INTEGRADOR" también aparece dentro de la cabecera de la tabla de
        # la sección 4 ("PROYECTO INTEGRADOR DEL NIVEL RESULTADO DE APRENDIZAJE..."), y
        # cortaba la sección de golpe haciéndola parecer vacía. Sólo corta si el ancla
        # empieza la línea.
        fin = len(lineas)
        for j in range(inicio + 1, len(lineas)):
            linea = mayusculas[j].strip()
            if _SECCION_NUM.match(linea) or \
                    any(linea.startswith(a) for a in anclas if a != ancla):
                fin = j
                break

        con_datos = sum(1 for j in range(inicio + 1, fin)
                        if _es_contenido(lineas[j], exige_numero=(modo == "numero")))
        estado[nombre] = con_datos if con_datos else "VACÍA"

    # Los campos de DATOS GENERALES los verifica el sistema en producción.
    campos_vacios, _loc = _campos_sin_llenar(documento["cajas"], meta.get("campos", ""))

    faltantes = {n for n, e in estado.items() if e in ("AUSENTE", "VACÍA")}
    faltantes |= set(campos_vacios)
    return meta, estado, faltantes, campos_vacios


def buscar(fragmento):
    encontrados, vistos = [], set()
    for patron in CORPUS:
        for ruta in sorted(glob.glob(patron, recursive=True)):
            nombre = os.path.basename(ruta)
            if "_Reporte" in nombre or nombre in vistos:
                continue
            vistos.add(nombre)
            if fragmento.lower() in nombre.lower():
                encontrados.append(ruta)

    if not encontrados:
        print(f"No encontré ningún documento con '{fragmento}'.")
        raise SystemExit(1)
    if len(encontrados) > 1:
        tamanos = {os.path.getsize(r) for r in encontrados}
        if len(tamanos) > 1:
            print(f"'{fragmento}' coincide con varios documentos distintos:")
            for r in encontrados[:10]:
                print("   ", os.path.basename(r)[:66])
            raise SystemExit(1)
    return encontrados[0]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(0)

    ruta = buscar(sys.argv[1])
    meta, estado, B, campos_vacios = analizar(ruta)

    print("=" * 76)
    print(f"  {os.path.basename(ruta)[:66]}")
    print("=" * 76)

    if estado is None:
        print(f"\nPLANTILLA NO RECONOCIDA — faltan los marcadores: {'; '.join(campos_vacios)}")
        print("El documento no usa la plantilla oficial. No hay secciones que comparar.")
        raise SystemExit(0)

    print(f"Indicador {meta['indicador']} — {meta['nombre']}")
    print()
    print(f"{'sección':32} {'estado':>18}")
    print("-" * 76)
    for nombre, valor in estado.items():
        if valor == "AUSENTE":
            marca, texto = "!", "SECCIÓN AUSENTE"
        elif valor == "VACÍA":
            marca, texto = "!", "VACÍA (sin contenido)"
        else:
            marca, texto = " ", f"{valor} líneas"
        print(f"{marca}{nombre:31} {texto:>18}")
    if campos_vacios:
        print()
        print(f"  Campos de DATOS GENERALES sin llenar: {', '.join(sorted(campos_vacios))}")
    print("-" * 76)
    print()
    print(f"EL SISTEMA DETECTA {len(B)} elemento(s) faltante(s):")
    print(f"   B = {sorted(B) if B else '(ninguno: el documento está completo)'}")

    if "--faltan" not in sys.argv:
        print()
        print("Abre el PDF y compruébalo. Después, dime qué falta DE VERDAD:")
        lista = ", ".join(sorted(B))
        print(f'   python scripts/jaccard.py {sys.argv[1]} --faltan "{lista}"')
        print(f'   python scripts/jaccard.py {sys.argv[1]} --faltan ""      (si no falta nada)')
        raise SystemExit(0)

    # ---- Jaccard ----
    crudo = sys.argv[sys.argv.index("--faltan") + 1]
    universo = list(estado) + [c for c in campos_vacios if c not in estado]
    A = set()
    for pedido in (p.strip() for p in crudo.split(",") if p.strip()):
        candidatos = [u for u in universo if pedido.lower() in u.lower()]
        if len(candidatos) == 1:
            A.add(candidatos[0])
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es una sección de este documento. Se ignora.")
        else:
            print(f"'{pedido}' es ambiguo: {candidatos}. Escríbelo completo.")
            raise SystemExit(1)

    interseccion, union = A & B, A | B

    print()
    print("=" * 76)
    print("ÍNDICE DE JACCARD")
    print("=" * 76)
    print(f"  A (auditor: lo que TÚ ves faltar)   = {sorted(A) if A else '(nada)'}")
    print(f"  B (sistema: lo que él detecta)      = {sorted(B) if B else '(nada)'}")
    print()
    print(f"  A ∩ B = {sorted(interseccion) if interseccion else '{}'}    |A ∩ B| = {len(interseccion)}")
    print(f"  A ∪ B = {sorted(union) if union else '{}'}    |A ∪ B| = {len(union)}")
    print()

    if not union:
        print("  JACCARD = 0 / 0 = INDEFINIDO")
        print()
        print("  El documento está completo y el sistema tampoco reporta nada. Jaccard no")
        print("  puede medir esto: sólo compara listas de elementos faltantes, y aquí no hay")
        print("  ninguna. La convención lo cuenta como 1,0, pero ese 1,0 no premia haber")
        print("  detectado algo: premia que no hubiera nada que detectar.")
        print()
        print(f"  Métrica honesta: ACIERTO — el sistema coincide contigo ({len(universo)} secciones OK).")
    else:
        j = len(interseccion) / len(union)
        print(f"  JACCARD = {len(interseccion)} / {len(union)} = {j:.3f}")
        print()
        if j == 1.0:
            print("  Coincidencia perfecta: el sistema detectó exactamente lo que falta.")
        elif j == 0.0:
            print("  Las dos listas no comparten nada: el sistema falló por completo.")
        else:
            print(f"  Las listas se solapan en {len(interseccion)} de {len(union)} elementos.")

    falsos_negativos, falsos_positivos = A - B, B - A
    print()
    if falsos_negativos:
        print(f"  SE LE ESCAPAN ({len(falsos_negativos)}): {sorted(falsos_negativos)}")
    if falsos_positivos:
        print(f"  SE INVENTA ({len(falsos_positivos)}): {sorted(falsos_positivos)}")
    if not falsos_negativos and not falsos_positivos:
        print("  Sin falsos positivos ni falsos negativos.")


if __name__ == "__main__":
    main()
