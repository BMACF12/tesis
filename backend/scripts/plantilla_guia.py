"""
Inventario del formulario oficial de la GUÍA DE USO DE LABORATORIO (Indicador 6).

Transcrito de la PLANTILLA VACÍA "1.1 Guía Laboratorio Plantilla.docx" y verificado contra
las 10 guías reales del corpus. Es la referencia contra la que se compara cada guía llena:
todo lo que la plantilla exige y el documento no rellena cuenta como faltante. Es el análogo
de `plantilla_silabo.py` para el sílabo; se mantiene DEDUPLICADO (una sola entrada por
elemento) para que la métrica de Jaccard no cuente dos veces lo mismo.

Cada elemento tiene:
    nombre   : cómo se llama en el informe
    seccion  : a qué parte del formulario pertenece (A / recursos / B / C)
    tipo     : "campo"      -> etiqueta con un valor al lado o debajo (resolver_campos)
               "bloque"     -> encabezado con texto libre debajo (INTRODUCCIÓN, OBJETIVOS…);
                               se resuelve igual que un campo, pero se distingue en el informe
               "tabla"      -> necesita al menos una FILA DE DATOS, no sólo su cabecera
               "aprobacion" -> fila Elaborado/Revisado/Aprobado con nombre (y cargo)
    ancla    : el texto literal con el que se localiza en el PDF

NOTA sobre los 23 campos "campo"/"bloque": son EXACTAMENTE los CAMPOS del Indicador 6 en la
base de oro (`caces_2024_oficial.txt`), incluido "LABORATORIO DONDE SE DESARROLLARÁ LA
PRÁCTICA". Así el inventario de evaluación y la verificación de producción miran lo mismo.

NOTA sobre REACTIVOS y MUESTRA / OTROS: un valor "NA" o "N/A" cuenta como LLENO (el software
no usa reactivos ni muestras); lo trata así `_campos_sin_llenar`/`resolver_campos`.
"""

# (nombre, sección, tipo, ancla)
PLANTILLA_GUIA = [
    # --- A. INFORMACIÓN DE LA GUÍA: identificación (label -> value) -----------
    ("Fecha",                        "A. Información de la guía", "campo", "FECHA"),
    ("Departamento",                 "A. Información de la guía", "campo", "DEPARTAMENTO"),
    ("Carrera",                      "A. Información de la guía", "campo", "CARRERA"),
    ("Asignatura",                   "A. Información de la guía", "campo", "ASIGNATURA"),
    ("Periodo",                      "A. Información de la guía", "campo", "PERIODO"),
    ("Nivel",                        "A. Información de la guía", "campo", "NIVEL"),
    ("Docente",                      "A. Información de la guía", "campo", "DOCENTE"),
    ("NRC",                          "A. Información de la guía", "campo", "NRC"),
    ("Práctica No",                  "A. Información de la guía", "campo", "PRÁCTICA No"),
    ("Laboratorio de la práctica",   "A. Información de la guía", "campo", "LABORATORIO DONDE SE DESARROLLARÁ LA PRÁCTICA"),
    ("Tema de la práctica",          "A. Información de la guía", "campo", "TEMA DE LA PRÁCTICA"),
    ("Número de horas",              "A. Información de la guía", "campo", "NUMERO DE HORAS"),

    # --- A. INFORMACIÓN DE LA GUÍA: planificación pedagógica (bloques) --------
    ("Introducción",                 "A. Planificación pedagógica", "bloque", "INTRODUCCIÓN"),
    ("Objetivos",                    "A. Planificación pedagógica", "bloque", "OBJETIVOS"),

    # --- A. INFORMACIÓN DE LA GUÍA: recursos de la práctica -------------------
    ("Equipos",                      "A. Recursos de la práctica", "campo", "EQUIPOS"),
    ("Materiales e insumos",         "A. Recursos de la práctica", "campo", "MATERIALES E INSUMOS"),
    ("Reactivos",                    "A. Recursos de la práctica", "campo", "REACTIVOS"),
    ("Muestra / otros",              "A. Recursos de la práctica", "campo", "MUESTRA / OTROS"),
    ("Precauciones / instrucciones", "A. Recursos de la práctica", "campo", "PRECAUCIONES/ INSTRUCCIONES"),

    # --- A. INFORMACIÓN DE LA GUÍA: desarrollo y cierre (bloques) -------------
    ("Actividades por desarrollar",  "A. Desarrollo de la práctica", "bloque", "ACTIVIDADES POR DESARROLLAR"),
    ("Resultados obtenidos",         "A. Desarrollo de la práctica", "bloque", "RESULTADOS OBTENIDOS"),
    ("Conclusiones",                 "A. Desarrollo de la práctica", "bloque", "CONCLUSIONES"),
    ("Recomendaciones",              "A. Desarrollo de la práctica", "bloque", "RECOMENDACIONES"),

    # --- B. CONTROL DE CAMBIOS -----------------------------------------------
    ("Control de cambios",           "B. Control de cambios", "tabla", "B. CONTROL DE CAMBIOS"),

    # --- C. APROBACIÓN: tres filas, cada una con nombre y cargo ---------------
    ("Elaborado por",                "C. Aprobación", "aprobacion", "Elaborado por"),
    ("Revisado por",                 "C. Aprobación", "aprobacion", "Revisado por"),
    ("Aprobado por",                 "C. Aprobación", "aprobacion", "Aprobado por"),
]

# Los 23 elementos que se resuelven como etiqueta -> valor (campo + bloque). Coinciden con
# los CAMPOS del Indicador 6 en la base de oro; los usa el resolvedor de coordenadas.
CAMPOS_GUIA = [a for _n, _s, t, a in PLANTILLA_GUIA if t in ("campo", "bloque")]

# Cabecera impresa de la tabla B. CONTROL DE CAMBIOS: no es una fila de datos.
CABECERA_CONTROL = ("Fecha", "Versión", "Unidad / Nombre", "Detalle del cambio")

# Cabecera impresa de la tabla C. APROBACIÓN.
CABECERA_APROBACION = ("Rubro", "Nombres y Apellido", "Unidad / Cargo", "Firma")

if __name__ == "__main__":
    import io
    import sys
    from collections import Counter

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 74)
    print("PLANTILLA OFICIAL DE LA GUÍA DE USO DE LABORATORIO (Indicador 6)")
    print("=" * 74)
    print(f"{len(PLANTILLA_GUIA)} elementos verificables "
          f"({len(CAMPOS_GUIA)} campos/bloques + 1 tabla + 3 filas de aprobación)")
    print()
    por_seccion = Counter(s for _n, s, _t, _a in PLANTILLA_GUIA)
    seccion_actual = None
    for i, (nombre, seccion, tipo, _ancla) in enumerate(PLANTILLA_GUIA, 1):
        if seccion != seccion_actual:
            seccion_actual = seccion
            print(f"\n  {seccion}  ({por_seccion[seccion]} elementos)")
        print(f"     {i:2}. [{tipo:10}] {nombre}")
