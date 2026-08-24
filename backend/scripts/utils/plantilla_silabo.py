"""
Inventario del formulario oficial SGC.DI.321 (sílabo de la ESPE).

Transcrito de la PLANTILLA VACÍA. Es la referencia contra la que se compara cada sílabo
lleno: todo lo que la plantilla exige y el documento no rellena, cuenta como faltante.

Cada elemento tiene:
    nombre   : cómo se llama en el informe
    seccion  : a qué sección del formulario pertenece
    tipo     : "campo"  -> etiqueta con un valor al lado (se busca por coordenadas)
               "tabla"  -> necesita al menos una FILA DE DATOS, no sólo su cabecera
               "lista"  -> necesita al menos un ítem escrito
               "bloque" -> necesita texto libre debajo del encabezado
    ancla    : el texto literal con el que se localiza en el PDF
"""

# (nombre, sección, tipo, ancla)
PLANTILLA_SILABO = [
    # --- 1. DATOS GENERALES -------------------------------------------------
    ("Modalidad",                            "1. Datos generales", "campo", "Modalidad"),
    ("Departamento",                         "1. Datos generales", "campo", "Departamento"),
    ("Área de Conocimiento",                 "1. Datos generales", "campo", "Área de Conocimiento"),
    ("Nombre Asignatura",                    "1. Datos generales", "campo", "Nombre Asignatura"),
    ("Período Académico",                    "1. Datos generales", "campo", "Período Académico"),
    ("Fecha Elaboración",                    "1. Datos generales", "campo", "Fecha Elaboración"),
    ("Código",                               "1. Datos generales", "campo", "Código"),
    ("NRC",                                  "1. Datos generales", "campo", "NRC"),
    ("Nivel",                                "1. Datos generales", "campo", "Nivel"),
    ("Docente",                              "1. Datos generales", "campo", "Docente"),
    ("Unidad de Organización",               "1. Datos generales", "campo", "Unidad de Organización"),
    ("Campo de Formación",                   "1. Datos generales", "campo", "Campo de Formación"),
    ("Núcleos Básicos",                      "1. Datos generales", "campo", "Núcleos Básicos de"),
    ("Carga horaria: docencia",              "1. Datos generales", "campo", "DOCENCIA"),
    ("Carga horaria: prácticas",             "1. Datos generales", "campo", "PRACTICAS DE APLICACIÓN Y EXPERIMENTACIÓN"),
    ("Carga horaria: aprendizaje autónomo",  "1. Datos generales", "campo", "APRENDIZAJE AUTÓNOMO"),
    ("Sesiones semanales",                   "1. Datos generales", "campo", "SESIONES SEMANALES"),
    ("Fecha de Actualización",               "1. Datos generales", "campo", "Fecha de Actualización"),
    ("Fecha de Ejecución",                   "1. Datos generales", "campo", "Fecha de Ejecución"),
    ("Descripción de la Asignatura",         "1. Datos generales", "campo", "Descripción de la Asignatura"),
    ("Contribución de la Asignatura",        "1. Datos generales", "campo", "Contribución de la Asignatura"),
    ("Resultado de Aprendizaje de la Carrera", "1. Datos generales", "campo", "Resultado de Aprendizaje de la Carrera"),
    ("Objetivo de la Asignatura",            "1. Datos generales", "campo", "Objetivo de la Asignatura"),
    ("Resultado de Aprendizaje de la Asignatura", "1. Datos generales", "campo", "Resultado de Aprendizaje de la Asignatura"),
    ("Proyecto Integrador",                  "1. Datos generales", "bloque", "=PROYECTO INTEGRADOR"),
    ("Perfil del docente: GRADO",            "1. Datos generales", "campo", "GRADO"),
    ("Perfil del docente: POSGRADO",         "1. Datos generales", "campo", "POSGRADO"),

    # --- 2. SISTEMA DE CONTENIDOS -------------------------------------------
    ("Contenidos por unidad",                "2. Sistema de contenidos", "tabla", "2. SISTEMA DE CONTENIDOS"),
    ("Horas por unidad",                     "2. Sistema de contenidos", "tabla", "ACTIVIDADES DE APRENDIZAJE / HORAS CLASE"),

    # --- 3. PROYECCIÓN METODOLÓGICA -----------------------------------------
    ("Métodos de enseñanza",                 "3. Proyección metodológica", "lista", "METODOS DE ENSEÑANZA"),
    ("Empleo de TIC",                        "3. Proyección metodológica", "lista", "EMPLEO DE TICS"),

    # --- 4. CONTRIBUCIÓN AL PERFIL DE EGRESO --------------------------------
    ("Resultados de aprendizaje por unidad", "4. Contribución al perfil", "tabla", "4. RESULTADOS DEL APRENDIZAJE"),

    # --- 6. EVALUACIÓN -------------------------------------------------------
    ("Ponderación de la evaluación",         "6. Evaluación", "tabla-num", "6. TÉCNICAS Y PONDERACION"),

    # --- 7, 8, 9. BIBLIOGRAFÍA Y LECTURAS -----------------------------------
    ("Bibliografía básica",                  "7. Bibliografía básica", "tabla", "7. BIBLIOGRAFÍA BÁSICA"),
    ("Bibliografía complementaria",          "8. Bibliografía complementaria", "tabla", "8. BIBLIOGRAFÍA COMPLEMENTARIA"),
    ("Lecturas principales",                 "9. Lecturas principales", "tabla", "9. LECTURAS PRINCIPALES"),

    # --- 10. ACUERDOS Y FIRMAS ----------------------------------------------
    ("Acuerdos del docente",                 "10. Acuerdos", "lista", "=DEL DOCENTE:"),
    ("Acuerdos de los estudiantes",          "10. Acuerdos", "lista", "=DE LOS ESTUDIANTES:"),
    ("Firmas de legalización",               "Firmas", "bloque", "FIRMAS DE LEGALIZACIÓN"),
]

# Texto impreso en la plantilla: si aparece dentro de una sección, NO es contenido escrito.
RUIDO_SILABO = (
    "Titulo", "Autor", "Edición", "Año", "Idioma", "Editorial",
    "Tema", "Texto", "Página", "URL",
    "Técnica de evaluación", "1er Parcial", "2do Parcial", "3er Parcial", "TOTAL:",
    "Exposición", "Laboratorios/Informes", "Examen Parcial", "Tareas o guías",
    "Metodos de Enseñanza - Aprendizaje", "Empleo de Tics en los Procesos de Aprendizaje",
    "Del Docente:", "De los Estudiantes:", "FIRMAS DE LEGALIZACIÓN",
    "CONTENIDOS", "HORAS DE TRABAJO AUTÓNOMO", "HORAS DE TRABAJO AUTONOMO",
    "ACTIVIDADES DE APRENDIZAJE / HORAS CLASE", "COMPONENTES DE DOCENCIA",
    "PRÁCTICAS DE APLICACIÓN Y EXPERIMENTACIÓN", "TOTAL HORAS POR UNIDAD",
    "PROYECTO INTEGRADOR DEL NIVEL RESULTADO DE APRENDIZAJE POR UNIDAD CURRICULAR",
    "Niveles de logro: Alta(A), Media (B), C(Baja).", "ACTIVIDADES INTEGRADORAS",
    "TÍTULO Y DENOMINACIÓN", "PERFIL SUGERIDO DEL DOCENTE",
    "PROGRAMA DE ASIGNATURA - SÍLABO", "Prácticas de Aplicación y Experimentación",
)

if __name__ == "__main__":
    import io
    import sys
    from collections import Counter

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 74)
    print("PLANTILLA OFICIAL DEL SÍLABO (SGC.DI.321)")
    print("=" * 74)
    print(f"{len(PLANTILLA_SILABO)} elementos verificables")
    print()
    por_seccion = Counter(s for _n, s, _t, _a in PLANTILLA_SILABO)
    seccion_actual = None
    for i, (nombre, seccion, tipo, _ancla) in enumerate(PLANTILLA_SILABO, 1):
        if seccion != seccion_actual:
            seccion_actual = seccion
            print(f"\n  {seccion}  ({por_seccion[seccion]} elementos)")
        print(f"     {i:2}. [{tipo:9}] {nombre}")
