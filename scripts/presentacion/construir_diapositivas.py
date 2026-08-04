# -*- coding: utf-8 -*-
"""
Construye la version v3 de la presentacion de defensa del Auditor IA CACES.

Toma el .pptx original, lo copia y le anade 12 diapositivas nuevas dibujadas con
formas nativas de PowerPoint (editables por los autores), reutilizando el layout
ESPE del propio mazo para conservar fondo, logo y tema.

Bloques:
  A1..A4  Arquitectura (dos vistas) y modelo C4 niveles 1 y 2
  B1..B3  Delimitacion de indicadores (criterio, alcance, rechazo)
  C1..C2  BPMN del proceso y comparativa AS-IS / TO-BE
  D1..D3  Scrum, IPA y su entrelazado

Ademas: libera la palabra "capas" (renombrado a compuertas/etapas) en las
diapositivas 20, 23, 24 y 29, elimina las diapositivas 12, 19 y 21, y reordena.

Uso:  venv/Scripts/python.exe scripts/presentacion/construir_diapositivas.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# --------------------------------------------------------------------------- #
# Rutas
# --------------------------------------------------------------------------- #
RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "Documentos para la tesis" / "00_manuscrito"
ORIGEN = CARPETA / "Presentación_Flores Brian_Morales Miguel.pptx"
DESTINO = CARPETA / "Presentación_Flores Brian_Morales Miguel (v3 diagramas).pptx"

# --------------------------------------------------------------------------- #
# Sistema visual (muestreado de la diapositiva 23 del mazo original)
# --------------------------------------------------------------------------- #
FUENTE = "Inter"
FUENTE_TIT = "Inter ExtraBold"

TINTA = RGBColor(0x11, 0x18, 0x27)      # texto principal
GRIS = RGBColor(0x6B, 0x72, 0x80)       # texto secundario
BORDE = RGBColor(0xE5, 0xE7, 0xEB)      # borde de tarjeta
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
VERDE = RGBColor(0x00, 0x66, 0x44)      # acento ESPE (barra de la dia. 23)
NAVY = RGBColor(0x17, 0x2C, 0x68)       # acento secundario (barra de la dia. 23)
ROJO = RGBColor(0xB9, 0x1C, 0x1C)
AMBAR = RGBColor(0xB4, 0x53, 0x09)

VERDE_SUAVE = RGBColor(0xEC, 0xFD, 0xF5)
NAVY_SUAVE = RGBColor(0xEE, 0xF2, 0xFF)
ROJO_SUAVE = RGBColor(0xFE, 0xF2, 0xF2)
AMBAR_SUAVE = RGBColor(0xFF, 0xFB, 0xEB)
GRIS_SUAVE = RGBColor(0xF9, 0xFA, 0xFB)

# rejilla
X0, X1 = 0.54, 9.46          # margenes laterales del contenido
ANCHO = X1 - X0              # 8.92
Y_TIT = 0.47
Y_SUB = 1.03


# --------------------------------------------------------------------------- #
# Utilidades de bajo nivel
# --------------------------------------------------------------------------- #
def _sld_lst(prs):
    return prs.slides._sldIdLst


def nueva(prs, layout):
    """Anade una diapositiva con el layout dado y sin marcadores de posicion."""
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def borrar_slide(prs, idx):
    lst = _sld_lst(prs)
    el = list(lst)[idx]
    prs.part.drop_rel(el.get(qn("r:id")))
    lst.remove(el)


def reordenar(prs, orden):
    """orden = lista de indices actuales, en la secuencia deseada."""
    lst = _sld_lst(prs)
    els = list(lst)
    for el in els:
        lst.remove(el)
    for i in orden:
        lst.append(els[i])


def _sin_autofit(tf):
    tf.word_wrap = True
    try:
        tf.auto_size = MSO_AUTO_SIZE.NONE
    except Exception:
        pass


def _margenes(tf, izq=0.08, der=0.08, arr=0.04, aba=0.04):
    tf.margin_left = Inches(izq)
    tf.margin_right = Inches(der)
    tf.margin_top = Inches(arr)
    tf.margin_bottom = Inches(aba)


def escribir(shape, lineas, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             interlineado=0.95):
    """lineas = [(texto, pt, negrita, color, espacio_antes_pt), ...]"""
    tf = shape.text_frame
    _sin_autofit(tf)
    tf.vertical_anchor = anchor
    primero = True
    for texto, pt, bold, color, antes in lineas:
        p = tf.paragraphs[0] if primero else tf.add_paragraph()
        primero = False
        p.alignment = align
        if antes:
            p.space_before = Pt(antes)
        p.space_after = Pt(0)
        try:
            p.line_spacing = interlineado
        except Exception:
            pass
        r = p.add_run()
        r.text = texto
        r.font.name = FUENTE
        r.font.size = Pt(pt)
        r.font.bold = bold
        r.font.color.rgb = color
    return shape


def caja(slide, x, y, w, h, relleno=None, borde=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE,
         radio=0.10, grosor=1.0, sombra=False):
    sh = slide.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radio
        except Exception:
            pass
    if relleno is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = relleno
    if borde is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = borde
        sh.line.width = Pt(grosor)
    if not sombra:
        sh.shadow.inherit = False
    _margenes(sh.text_frame)
    _sin_autofit(sh.text_frame)
    return sh


def texto(slide, x, y, w, h, lineas, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    _margenes(tb.text_frame, 0.02, 0.02, 0.01, 0.01)
    return escribir(tb, lineas, align=align, anchor=anchor)


def _punta(conn):
    ln = conn.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)


def flecha(slide, x1, y1, x2, y2, color=GRIS, grosor=1.25, codo=False, punta=True):
    tipo = MSO_CONNECTOR.ELBOW if codo else MSO_CONNECTOR.STRAIGHT
    c = slide.shapes.add_connector(tipo, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(grosor)
    if punta:
        _punta(c)
    return c


# El logo ESPE del patron ocupa la esquina superior derecha (a partir de ~6.9 in):
# los titulos no pueden pasar de aqui o quedan por debajo del logo.
ANCHO_TIT = 6.30


def titulo(slide, tit, sub=None):
    texto(slide, X0, Y_TIT, ANCHO_TIT, 0.5,
          [(tit, 20, True, TINTA, 0)])
    # la tipografia ExtraBold del mazo se aplica a mano sobre la corrida
    for p in slide.shapes[-1].text_frame.paragraphs:
        for r in p.runs:
            r.font.name = FUENTE_TIT
    if sub:
        texto(slide, X0, Y_SUB, ANCHO, 0.34, [(sub, 9.5, False, GRIS, 0)])
    return slide


def tarjeta(slide, x, y, w, h, acento, relleno=BLANCO, radio=0.06):
    """Tarjeta blanca con barra de acento superior, como las del mazo original."""
    c = caja(slide, x, y, w, h, relleno=relleno, borde=BORDE, radio=radio)
    barra = caja(slide, x, y, w, 0.09, relleno=acento, borde=None,
                 forma=MSO_SHAPE.RECTANGLE)
    return c, barra


def chip(slide, x, y, w, h, etiqueta, relleno, color_texto=BLANCO, pt=9, radio=0.25):
    c = caja(slide, x, y, w, h, relleno=relleno, borde=None, radio=radio)
    escribir(c, [(etiqueta, pt, True, color_texto, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return c


def vertical(shape):
    shape.text_frame._txBody.bodyPr.set("vert", "vert270")


# --------------------------------------------------------------------------- #
# BLOQUE A — Arquitectura y C4
# --------------------------------------------------------------------------- #
def slide_A1(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Dos vistas del mismo sistema",
           "La vista N-capas responde DÓNDE VIVE EL CÓDIGO. La vista de tres etapas responde "
           "QUIÉN DECIDE Y CON QUÉ EVIDENCIA. Se cruzan; no compiten.")

    izq_x, izq_w = X0, 4.16
    der_x, der_w = 5.00, 4.46

    ca = caja(s, izq_x, 1.55, izq_w, 0.36, relleno=NAVY, borde=None, radio=0.14)
    escribir(ca, [("VISTA TÉCNICA · Arquitectura N-Capas", 9.5, True, BLANCO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cb = caja(s, der_x, 1.55, der_w, 0.36, relleno=VERDE, borde=None, radio=0.14)
    escribir(cb, [("VISTA DE DECISIÓN · Auditoría en 3 etapas", 9.5, True, BLANCO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    capas = [
        ("1 · Presentación", "Next.js / React — carga de PDF y semáforos de resultado"),
        ("2 · Aplicación", "FastAPI — endpoints REST y validación con Pydantic"),
        ("3 · Lógica de negocio", "Orquestación del flujo, prompts y reglas de decisión"),
        ("4 · Integración", "Groq (Llama 3.3 70B) · Google (embeddings)"),
        ("5 · Persistencia", "ChromaDB · repositorio de carpetas CACES"),
    ]
    y = 2.05
    for nombre, desc in capas:
        c = caja(s, izq_x, y, izq_w, 0.50, relleno=GRIS_SUAVE, borde=BORDE, radio=0.10)
        escribir(c, [(nombre, 9.5, True, TINTA, 0), (desc, 7.5, False, GRIS, 1)],
                 anchor=MSO_ANCHOR.MIDDLE)
        y += 0.57

    etapas = [
        (VERDE, "ETAPA 1 · Compuertas de seguridad (Pre-LLM)",
         "Extracción del texto y cinco verificaciones deterministas. No interviene el modelo.",
         "se ejecuta en las capas 2, 3 y 5"),
        (NAVY, "ETAPA 2 · Juicio cognitivo (LLM + RAG)",
         "Único punto en que decide el modelo: el checklist de elementos fundamentales.",
         "se ejecuta en las capas 3 y 4"),
        (VERDE, "ETAPA 3 · Veredicto determinista",
         "Porcentaje, veredicto y triage físico recalculados en código, no por el modelo.",
         "se ejecuta en las capas 3 y 5"),
    ]
    y = 2.05
    for acento, nombre, desc, tag in etapas:
        c = caja(s, der_x, y, der_w, 0.88, relleno=BLANCO, borde=BORDE, radio=0.08)
        caja(s, der_x, y, 0.07, 0.88, relleno=acento, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(c, [(nombre, 10, True, acento, 0),
                     (desc, 8, False, TINTA, 2),
                     ("› " + tag, 7.5, True, GRIS, 2)],
                 anchor=MSO_ANCHOR.MIDDLE)
        c.text_frame.margin_left = Inches(0.16)
        y += 0.95
    return s


def slide_A2(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Modelo C4 · Nivel 1 — Contexto",
           "Quién usa el sistema y con qué actores externos intercambia información.")

    # Persona
    caja(s, 1.28, 2.24, 0.32, 0.32, relleno=NAVY, borde=None, forma=MSO_SHAPE.OVAL)
    p = caja(s, 0.54, 2.60, 1.80, 0.95, relleno=NAVY, borde=None, radio=0.10)
    escribir(p, [("Auditor académico", 10, True, BLANCO, 0),
                 ("Docente responsable de las evidencias de la carrera", 7.5, False,
                  RGBColor(0xC7, 0xD2, 0xFE), 2),
                 ("[Persona]", 7, True, RGBColor(0x9C, 0xA3, 0xC4), 2)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Sistema en alcance
    sis = caja(s, 3.55, 2.30, 2.60, 1.55, relleno=VERDE, borde=None, radio=0.08)
    escribir(sis, [("Sistema Auditor IA CACES", 12, True, BLANCO, 0),
                   ("Clasifica, evalúa y ordena las evidencias de acreditación contra la "
                    "normativa CACES 2024", 8, False, RGBColor(0xD1, 0xFA, 0xE5), 3),
                   ("[Sistema en alcance]", 7, True, RGBColor(0xA7, 0xE3, 0xCF), 3)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    flecha(s, 2.34, 3.08, 3.55, 3.08, color=NAVY, grosor=1.5)
    texto(s, 2.30, 2.72, 1.30, 0.32,
          [("Carga PDF y", 7, True, NAVY, 0), ("consulta dictámenes", 7, True, NAVY, 0)],
          align=PP_ALIGN.CENTER)

    externos = [
        (1.52, "Groq · Llama 3.3 70B",
         "Inferencia del dictamen. Envío del prompt con la norma y el documento."),
        (2.52, "Google · gemini-embedding-001",
         "Vectorización de la normativa CACES para la recuperación semántica."),
        (3.52, "Repositorio de evidencias CACES",
         "Carpetas por criterio e indicador donde se archiva el PDF y su reporte."),
        (4.52, "Modelo genérico CACES 2024",
         "Fuente normativa: estándares y elementos fundamentales por indicador."),
    ]
    for y, nombre, rel in externos:
        c = caja(s, 6.75, y, 2.71, 0.86, relleno=GRIS_SUAVE, borde=GRIS, radio=0.08)
        escribir(c, [(nombre, 9, True, TINTA, 0),
                     ("[Sistema externo]", 6.5, True, GRIS, 1),
                     (rel, 7, False, GRIS, 1)], anchor=MSO_ANCHOR.MIDDLE)
        flecha(s, 6.15, 3.08, 6.75, y + 0.43, color=GRIS, grosor=1.1)
    return s


def slide_A3(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Modelo C4 · Nivel 2 — Contenedores",
           "Las piezas ejecutables del sistema y el protocolo con que se comunican.")

    lim = caja(s, X0, 1.48, ANCHO, 3.42, relleno=None, borde=NAVY, radio=0.03,
               forma=MSO_SHAPE.ROUNDED_RECTANGLE, grosor=1.0)
    lim.line.dash_style = 4  # MSO_LINE_DASH_STYLE.DASH
    texto(s, 0.66, 1.53, 3.4, 0.24,
          [("Sistema Auditor IA CACES", 8, True, NAVY, 0)])

    def contenedor(x, y, w, h, nombre, tec, resp, acento):
        c = caja(s, x, y, w, h, relleno=BLANCO, borde=BORDE, radio=0.08)
        caja(s, x, y, w, 0.07, relleno=acento, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(c, [(nombre, 9.5, True, TINTA, 0),
                     ("[Contenedor: " + tec + "]", 6.5, True, acento, 1),
                     (resp, 7.5, False, GRIS, 1)], anchor=MSO_ANCHOR.MIDDLE)
        return c

    y1, y2, h = 1.90, 3.72, 0.90
    contenedor(0.85, y1, 2.35, h, "Interfaz web", "Next.js / React",
               "Arrastre de PDF, cola de tareas y tarjetas de resultado", NAVY)
    contenedor(3.85, y1, 2.35, h, "API", "FastAPI",
               "Recibe el lote, lanza el chord y expone el estado", NAVY)
    contenedor(6.85, y1, 2.30, h, "Broker y resultados", "Redis",
               "Cola de tareas del lote y almacén temporal de resultados", NAVY)
    contenedor(0.85, y2, 2.35, h, "Base de conocimiento", "ChromaDB",
               "Normativa CACES vectorizada, un documento por indicador", VERDE)
    contenedor(3.85, y2, 2.35, h, "Worker de auditoría", "Celery",
               "Ejecuta las tres etapas sobre cada documento del lote", VERDE)
    contenedor(6.85, y2, 2.30, h, "Repositorio de evidencias", "Sistema de archivos",
               "Carpetas por indicador, más rechazos y reportes PDF", VERDE)

    def rotulo(x, y, w, t):
        texto(s, x, y, w, 0.30, [(t, 6.5, True, GRIS, 0)], align=PP_ALIGN.CENTER)

    # fila 1: interfaz <-> API -> Redis (rotulos dentro de la canaleta entre cajas)
    flecha(s, 3.20, 2.44, 3.85, 2.44, color=NAVY)
    flecha(s, 3.85, 2.62, 3.20, 2.62, color=NAVY)
    rotulo(3.205, 2.03, 0.64, "POST /evaluar\nGET /status")

    flecha(s, 6.20, 2.53, 6.85, 2.53, color=NAVY)
    rotulo(6.205, 2.12, 0.64, "chord de\ntareas")

    # Redis -> worker: diagonal limpia, sin codo, con el rotulo fuera de la traza
    flecha(s, 7.40, 2.80, 5.60, 3.72, color=NAVY)
    rotulo(7.30, 2.88, 1.60, "el worker consume el lote")

    # fila 2: worker <-> base de conocimiento y repositorio
    flecha(s, 3.85, 4.17, 3.20, 4.17, color=VERDE)
    rotulo(3.205, 3.86, 0.64, "norma por\nmetadato")

    flecha(s, 6.20, 4.17, 6.85, 4.17, color=VERDE)
    rotulo(6.205, 3.86, 0.64, "copia PDF\n+ reporte")
    return s


def slide_A4(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Las compuertas de seguridad Pre-LLM",
           "Si un documento no supera las compuertas, el modelo NI SE LLAMA: no puede alucinar "
           "sobre lo que nunca leyó, y el lote no gasta la cuota en basura.")

    b = caja(s, X0, 1.42, ANCHO, 0.34, relleno=VERDE_SUAVE, borde=VERDE, radio=0.14)
    escribir(b, [("ETAPA 1 — 100 % determinista · se ejecuta en milisegundos · sin modelo de "
                  "lenguaje", 8.5, True, VERDE, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    compuertas = [
        ("1", "Rechazo léxico", "¿Tiene al menos dos términos del vocabulario académico?",
         ROJO, ("PLANTILLA NO RECONOCIDA", "el documento no es académico")),
        ("2", "Enrutado al indicador", "Palabras clave del encabezado; respaldo por similitud.",
         NAVY, ("No rechaza", "elige la norma del indicador")),
        ("3", "Plantilla oficial", "¿Aparecen los MARCADORES obligatorios del indicador?",
         ROJO, ("PLANTILLA NO RECONOCIDA", "→ carpeta 12")),
        ("4", "Pertinencia de carrera", "¿El campo CARRERA/ASIGNATURA es de Software?",
         ROJO, ("NO CUMPLE · 0 %", "→ carpeta 11")),
        ("5", "Campos obligatorios", "¿La plantilla oficial está mayoritariamente en blanco?",
         ROJO, ("NO CUMPLE", "→ carpeta 11")),
    ]
    w, gap = 1.66, 0.155
    x = X0
    for num, nombre, pregunta, color, salida in compuertas:
        c = caja(s, x, 1.95, w, 1.10, relleno=BLANCO, borde=BORDE, radio=0.08)
        caja(s, x, 1.95, w, 0.07, relleno=color, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(c, [(num + " · " + nombre, 9, True, TINTA, 0),
                     (pregunta, 7.5, False, GRIS, 2)], anchor=MSO_ANCHOR.MIDDLE)
        flecha(s, x + w / 2, 3.10, x + w / 2, 3.42, color=color, grosor=1.1)
        suave = ROJO_SUAVE if color is ROJO else NAVY_SUAVE
        d = caja(s, x, 3.45, w, 0.72, relleno=suave, borde=color, radio=0.08)
        veredicto, destino = salida
        escribir(d, [(veredicto, 8, True, color, 0),
                     (destino, 7, False, color, 2)],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if x + w + gap < X1:
            flecha(s, x + w, 2.50, x + w + gap, 2.50, color=GRIS, grosor=1.0)
        x += w + gap

    f = caja(s, X0, 4.32, ANCHO, 0.50, relleno=VERDE, borde=None, radio=0.12)
    escribir(f, [("Sólo lo que supera las cinco compuertas llega a la ETAPA 2 · Juicio "
                  "cognitivo del LLM   →   0 % de falsos positivos medidos en el Capítulo IV",
                  9.5, True, BLANCO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# --------------------------------------------------------------------------- #
# BLOQUE B — Delimitacion de indicadores
# --------------------------------------------------------------------------- #
def slide_B1(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "¿Por qué cinco indicadores de diez?",
           "Un indicador sólo es evaluable por el sistema si cumple las TRES condiciones a la vez.")

    condiciones = [
        ("① Materialización documental",
         "El indicador se concreta en un documento formal, textual y autocontenido; no en una "
         "actividad, un proceso de aula ni un conjunto disperso de registros."),
        ("② Verificabilidad por lectura",
         "Sus elementos fundamentales se comprueban leyendo el contenido, sin observar el "
         "proceso real ni triangular fuentes externas al documento."),
        ("③ Naturaleza cualitativa-declarativa",
         "El juicio resulta de contrastar afirmaciones textuales contra un estándar, no de un "
         "cálculo numérico sobre datos estructurados."),
    ]
    y = 1.45
    for nombre, desc in condiciones:
        c = caja(s, X0, y, 3.35, 0.98, relleno=BLANCO, borde=BORDE, radio=0.08)
        caja(s, X0, y, 0.07, 0.98, relleno=NAVY, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(c, [(nombre, 9.5, True, NAVY, 0), (desc, 7.5, False, TINTA, 2)],
                 anchor=MSO_ANCHOR.MIDDLE)
        c.text_frame.margin_left = Inches(0.16)
        y += 1.10

    niveles = [
        (4.35, 5.11, "10 indicadores evaluados", "Criterio Currículo (1–7) y Criterio Docencia (8–10)", GRIS, GRIS_SUAVE),
        (4.65, 4.51, "quedan 8", "superan la materialización documental", NAVY, NAVY_SUAVE),
        (4.95, 3.91, "quedan 7", "superan la verificabilidad por lectura", NAVY, NAVY_SUAVE),
        (5.20, 3.41, "5 INDICADORES EN ALCANCE", "1 · 2 · 3 · 4 · 6 — validados en el Cap. IV", VERDE, VERDE_SUAVE),
    ]
    caidas = [
        "✕  caen 5 y 7 — evalúan la ejecución de un proceso; su evidencia es dispersa",
        "✕  cae 10 — sólo 1 de sus 5 elementos es documental; el resto es procesual",
        "✕  caen 8 y 9 — son cuantitativos: se resuelven por fórmula, no por lectura",
    ]
    y = 1.45
    for i, (x, w, tit, sub, color, fondo) in enumerate(niveles):
        alto = 0.60 if i == 3 else 0.50
        c = caja(s, x, y, w, alto, relleno=fondo, borde=color, radio=0.10)
        escribir(c, [(tit, 10 if i == 3 else 9.5, True, color, 0),
                     (sub, 7.5, False, GRIS if i != 3 else VERDE, 1)],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        y += alto
        if i < 3:
            texto(s, 4.45, y + 0.02, 5.01, 0.28, [(caidas[i], 8, True, ROJO, 0)],
                  align=PP_ALIGN.CENTER)
            y += 0.30
    return s


def slide_B2(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Dentro del alcance: cinco indicadores",
           "Todos del Criterio Currículo, todos cualitativos y materializados en un documento formal.")

    cols = [(X0, 0.45), (1.09, 1.78), (2.95, 2.42), (5.45, 4.01)]
    cab = ["", "INDICADOR", "DOCUMENTO QUE LO MATERIALIZA", "QUÉ VERIFICA EL SISTEMA"]
    for (x, w), t in zip(cols, cab):
        if t:
            texto(s, x, 1.42, w, 0.24, [(t, 6.5, True, GRIS, 0)])

    filas = [
        ("1", "Perfil de egreso", "Perfil del egresado, en prosa, dentro del proyecto curricular",
         "Presencia y coherencia de los resultados de aprendizaje, los dominios y los saberes declarados. 5 elementos.", NAVY),
        ("2", "Proyecto curricular", "Formulario de rediseño SENESCYT/CES (≈113 páginas)",
         "Coherencia con el modelo educativo, pertinencia de la carrera y requisitos declarados. 6 elementos.", NAVY),
        ("3", "Malla curricular", "Diagrama apaisado de una página",
         "Distribución por PAO, asignaturas, prerrequisitos y créditos, con el invariante HPAO = 48 × créditos. 4 elementos.", NAVY),
        ("4", "Syllabus", "Plantilla oficial SGC.DI.321 (6 páginas)",
         "Los seis elementos del sílabo. Escenario idóneo de validación: 181 de los 214 documentos del corpus etiquetado.", VERDE),
        ("6", "Escenarios de prácticas", "Guía de uso de laboratorio",
         "Planificación de la práctica, instrumento que la guía y correspondencia práctica–resultados de aprendizaje. 4 elementos.", NAVY),
    ]
    y = 1.70
    for num, nombre, doc, verifica, color in filas:
        fondo = VERDE_SUAVE if color is VERDE else BLANCO
        caja(s, X0, y, ANCHO, 0.60, relleno=fondo, borde=BORDE, radio=0.05)
        chip(s, X0 + 0.03, y + 0.11, 0.39, 0.38, num, color, pt=11)
        escribir(texto(s, cols[1][0], y + 0.08, cols[1][1], 0.46,
                       [(nombre, 9, True, TINTA, 0)], anchor=MSO_ANCHOR.MIDDLE), [])
        texto(s, cols[2][0], y + 0.08, cols[2][1], 0.46, [(doc, 7.5, False, GRIS, 0)],
              anchor=MSO_ANCHOR.MIDDLE)
        texto(s, cols[3][0], y + 0.08, cols[3][1], 0.46, [(verifica, 7.5, False, TINTA, 0)],
              anchor=MSO_ANCHOR.MIDDLE)
        y += 0.66

    texto(s, X0, y + 0.02, ANCHO, 0.26,
          [("El indicador 6 entra al alcance a través de la guía de laboratorio: es el "
            "instrumento documental de la práctica, y el propio sílabo declara la "
            "correspondencia entre práctica y resultado de aprendizaje.", 7.5, False, GRIS, 0)])
    return s


def slide_B3(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Fuera del alcance: por qué se rechazan",
           "Cinco indicadores quedan fuera. No por falta de tiempo, sino por tres causas "
           "estructurales distintas.")

    tarjetas = [
        (X0, ROJO, ROJO_SUAVE, "5 · 7", "No existe el documento",
         [("Los indicadores 5 (metodologías y recursos) y 7 (TAC) no evalúan un documento: "
           "evalúan la EJECUCIÓN del proceso formativo en el aula.", 7.5, False, TINTA),
          ("Su evidencia es dispersa y heterogénea: portafolio docente, registros de "
           "asistencia y calificaciones, entornos virtuales, actas de capacitación.", 7.5, False, TINTA),
          ("No hay documento autocontenido que leer.", 8, True, ROJO),
          ("Incumplen la Condición 1.", 7.5, True, GRIS)]),
        (3.60, ROJO, ROJO_SUAVE, "8 · 9", "No se leen: se calculan",
         [("Carecen de elementos fundamentales. Su valor sale de una fórmula sobre datos "
           "estructurados del SIIES y del distributivo docente:", 7.5, False, TINTA),
          ("APA = 100 × (TAAF / TA)", 9.5, True, ROJO),
          ("TPP = 100 × (PP / TPA)", 9.5, True, ROJO),
          ("Es cómputo aritmético, no comprensión documental.", 8, True, ROJO),
          ("Incumplen la Condición 3.", 7.5, True, GRIS)]),
        (6.66, AMBAR, AMBAR_SUAVE, "10", "Sólo 1 de sus 5 elementos es documental",
         [("Únicamente la existencia declarada del sistema de evaluación docente —políticas, "
           "instrumentos y procedimientos— es verificable en documento.", 7.5, False, TINTA),
          ("Los elementos 2 a 5 son procesuales: aplicación periódica, participación de "
           "actores, retroalimentación y uso de los resultados.", 7.5, False, TINTA),
          ("Parcialmente alcanzable en teoría; NO instrumentado en esta versión.", 8, True, AMBAR),
          ("Declarado trabajo futuro.", 7.5, True, GRIS)]),
    ]
    for x, color, fondo, nums, titulo_t, cuerpo in tarjetas:
        c = caja(s, x, 1.50, 2.80, 2.52, relleno=BLANCO, borde=BORDE, radio=0.06)
        caja(s, x, 1.50, 2.80, 0.09, relleno=color, borde=None, forma=MSO_SHAPE.RECTANGLE)
        chip(s, x + 0.14, 1.70, 0.62, 0.26, "IND. " + nums, color, pt=7.5, radio=0.4)
        texto(s, x + 0.14, 2.02, 2.52, 0.40, [(titulo_t, 10.5, True, TINTA, 0)])
        lineas = [(t, pt, b, col, 4) for t, pt, b, col in cuerpo]
        texto(s, x + 0.14, 2.46, 2.52, 1.50, lineas)

    q = caja(s, X0, 4.16, ANCHO, 0.66, relleno=NAVY, borde=None, radio=0.10)
    escribir(q, [("«Esta delimitación no responde a una restricción de tiempo, sino a la "
                  "naturaleza estructural de cada indicador frente al paradigma de comprensión "
                  "documental del sistema.»", 9, True, BLANCO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# --------------------------------------------------------------------------- #
# BLOQUE C — BPMN
# --------------------------------------------------------------------------- #
def slide_C1(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Proceso de auditoría documental (BPMN)",
           "Carril superior: lo que hace la persona. Carril inferior: lo que ejecuta el sistema "
           "sin intervención humana.")

    # carriles
    caja(s, X0, 1.35, ANCHO, 0.95, relleno=None, borde=BORDE, radio=0.02,
         forma=MSO_SHAPE.RECTANGLE)
    caja(s, X0, 2.30, ANCHO, 2.60, relleno=None, borde=BORDE, radio=0.02,
         forma=MSO_SHAPE.RECTANGLE)
    l1 = caja(s, X0, 1.35, 0.40, 0.95, relleno=NAVY, borde=None, forma=MSO_SHAPE.RECTANGLE)
    escribir(l1, [("AUDITOR", 7.5, True, BLANCO, 0)], align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    vertical(l1)
    l2 = caja(s, X0, 2.30, 0.40, 2.60, relleno=VERDE, borde=None, forma=MSO_SHAPE.RECTANGLE)
    escribir(l2, [("SISTEMA AUTOMATIZADO (IPA)", 7.5, True, BLANCO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    vertical(l2)

    def tarea(x, y, w, h, t, color=NAVY, fondo=BLANCO, pt=7.5):
        c = caja(s, x, y, w, h, relleno=fondo, borde=color, radio=0.10)
        escribir(c, [(t, pt, False, TINTA, 0)], align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
        _margenes(c.text_frame, 0.03, 0.03, 0.02, 0.02)
        return c

    # carril del auditor
    ini = caja(s, 0.99, 1.64, 0.36, 0.36, relleno=BLANCO, borde=VERDE,
               forma=MSO_SHAPE.OVAL, grosor=1.5)
    tarea(1.50, 1.55, 1.45, 0.55, "Cargar los PDF del período\nen la interfaz web")
    flecha(s, 1.35, 1.82, 1.50, 1.82, color=GRIS)
    rev = tarea(6.97, 1.55, 1.45, 0.55, "Revisar el panel y\ndescargar los reportes")
    fin = caja(s, 8.60, 1.64, 0.36, 0.36, relleno=BLANCO, borde=NAVY,
               forma=MSO_SHAPE.OVAL, grosor=2.0)
    flecha(s, 8.42, 1.82, 8.60, 1.82, color=GRIS)

    # carril del sistema
    y, h = 2.70, 0.62
    w, gap = 1.14, 0.14
    xs = {}
    x = 0.99
    tarea(x, y, w, h, "Extraer el texto\ndel PDF (OCR)", color=VERDE)
    xs["T1"] = (x, x + w)
    x += w + gap
    gx = x
    g = caja(s, gx, 2.65, 0.72, 0.72, relleno=BLANCO, borde=AMBAR,
             forma=MSO_SHAPE.DIAMOND, grosor=1.5)
    escribir(g, [("X", 11, True, AMBAR, 0)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    texto(s, gx - 0.55, 2.40, 1.82, 0.22,
          [("¿supera las 5 compuertas Pre-LLM?", 6.5, True, AMBAR, 0)], align=PP_ALIGN.CENTER)
    x += 0.72 + gap
    for clave, t in [("T2", "Recuperar la norma\ndel indicador (RAG)"),
                     ("T3", "Emitir el dictamen\n(LLM · checklist)"),
                     ("T4", "Calcular el veredicto\ny el porcentaje"),
                     ("T5", "Enrutar el PDF a la\ncarpeta del indicador"),
                     ("T6", "Generar el reporte\nPDF y el ejecutivo")]:
        tarea(x, y, w, h, t, color=VERDE)
        xs[clave] = (x, x + w)
        x += w + gap

    flecha(s, xs["T1"][1], 3.01, gx, 3.01, color=GRIS)
    flecha(s, gx + 0.72, 3.01, xs["T2"][0], 3.01, color=GRIS)
    texto(s, gx + 0.74, 2.76, 0.30, 0.20, [("Sí", 6.5, True, VERDE, 0)])
    for a, b in [("T2", "T3"), ("T3", "T4"), ("T4", "T5"), ("T5", "T6")]:
        flecha(s, xs[a][1], 3.01, xs[b][0], 3.01, color=GRIS)

    flecha(s, gx + 0.36, 3.37, gx + 0.36, 3.95, color=ROJO)
    texto(s, gx + 0.40, 3.50, 0.32, 0.20, [("No", 6.5, True, ROJO, 0)])
    r = caja(s, 1.90, 3.95, 4.50, 0.60, relleno=ROJO_SUAVE, borde=ROJO, radio=0.10)
    escribir(r, [("Rechazo sin invocar al modelo: PLANTILLA NO RECONOCIDA → carpeta 12, "
                  "o NO CUMPLE → carpeta 11, con reporte del motivo", 7.5, False, ROJO, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    flecha(s, 6.40, 4.25, xs["T5"][0] + 0.57, 3.32, color=ROJO, codo=True)

    flecha(s, 1.50 + 0.72, 2.10, 0.99 + 0.57, 2.70, color=GRIS, codo=True)
    flecha(s, xs["T6"][0] + 0.57, 2.70, 6.97 + 0.72, 2.10, color=GRIS, codo=True)
    return s


def slide_C2(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "AS-IS / TO-BE: manual vs. automatizado",
           "La fase 3 de la metodología IPA: qué cambia exactamente cuando se automatiza.")

    def banda(y, color, fondo, etiqueta, pasos, metricas):
        caja(s, X0, y, ANCHO, 1.52, relleno=fondo, borde=color, radio=0.06)
        e = caja(s, X0, y, 1.15, 1.52, relleno=color, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(e, [(etiqueta, 10, True, BLANCO, 0)], align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
        w, gap = 1.44, 0.13
        x = 1.85
        for i, p in enumerate(pasos):
            c = caja(s, x, y + 0.18, w, 0.62, relleno=BLANCO, borde=color, radio=0.10)
            escribir(c, [(p, 7, False, TINTA, 0)], align=PP_ALIGN.CENTER,
                     anchor=MSO_ANCHOR.MIDDLE)
            _margenes(c.text_frame, 0.03, 0.03, 0.02, 0.02)
            if i < len(pasos) - 1:
                flecha(s, x + w, y + 0.49, x + w + gap, y + 0.49, color=color, grosor=1.0)
            x += w + gap
        texto(s, 1.85, y + 0.92, 7.45, 0.50, [(metricas, 8, True, color, 0)])

    banda(1.42, ROJO, ROJO_SUAVE, "AS-IS\nManual",
          ["Buscar el archivo entre carpetas dispersas",
           "Abrir y leer el PDF completo",
           "Contrastar a mano contra el modelo CACES",
           "Renombrar y archivar el documento",
           "Anotar el resultado en una hoja"],
          "Más de 30 minutos por archivo  ·  hasta 40 % de duplicidad en los registros  ·  "
          "tiempo académico desviado a control documental  ·  criterio no reproducible entre revisores")

    banda(3.22, VERDE, VERDE_SUAVE, "TO-BE\nIPA",
          ["Arrastrar el lote de PDF a la interfaz",
           "Compuertas deterministas Pre-LLM",
           "Dictamen del LLM contra la norma (RAG)",
           "Triage automático a la carpeta del indicador",
           "Reporte individual y ejecutivo del lote"],
          "2,76 documentos por minuto  ·  20 documentos concurrentes  ·  0 % de falsos positivos  ·  "
          "checklist con cita literal por elemento: el mismo criterio para todos los documentos")
    return s


# --------------------------------------------------------------------------- #
# BLOQUE D — Scrum e IPA
# --------------------------------------------------------------------------- #
def slide_D1(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Scrum aplicado: ciclo y cronograma",
           "Cinco sprints de dos semanas, de abril a julio de 2026, con un incremento "
           "ejecutable al cierre de cada uno.")

    texto(s, X0, 1.38, 3.9, 0.26, [("CICLO DE TRABAJO", 7.5, True, GRIS, 0)])
    etapas = [
        ("Product Backlog", "Historias priorizadas con MoSCoW"),
        ("Sprint Planning", "Selección del alcance del sprint"),
        ("Sprint · 2 semanas", "Desarrollo e integración continua"),
        ("Incremento ejecutable", "Software funcionando y demostrable"),
        ("Review y Retrospectiva", "Ajuste del backlog con el Product Owner"),
    ]
    y = 1.66
    for i, (nombre, desc) in enumerate(etapas):
        c = caja(s, 1.15, y, 3.29, 0.52, relleno=BLANCO, borde=BORDE, radio=0.10)
        caja(s, 1.15, y, 0.06, 0.52, relleno=NAVY, borde=None, forma=MSO_SHAPE.RECTANGLE)
        escribir(c, [(nombre, 9, True, TINTA, 0), (desc, 7, False, GRIS, 1)],
                 anchor=MSO_ANCHOR.MIDDLE)
        c.text_frame.margin_left = Inches(0.14)
        if i < len(etapas) - 1:
            flecha(s, 2.80, y + 0.52, 2.80, y + 0.62, color=GRIS, grosor=1.0)
        y += 0.62

    # camino de realimentacion: sale del ultimo bloque, rodea por la izquierda y vuelve al primero
    ultimo = y - 0.62 + 0.26
    flecha(s, 1.15, ultimo, 0.90, ultimo, color=NAVY, grosor=1.25, punta=False)
    flecha(s, 0.90, ultimo, 0.90, 1.92, color=NAVY, grosor=1.25, punta=False)
    flecha(s, 0.90, 1.92, 1.15, 1.92, color=NAVY, grosor=1.25)
    texto(s, 0.90, y + 0.02, 4.00, 0.24,
          [("La retrospectiva realimenta el backlog del sprint siguiente.", 7, True, NAVY, 0)])

    texto(s, 4.85, 1.38, 4.61, 0.26,
          [("CRONOGRAMA · ABRIL – JULIO DE 2026", 7.5, True, GRIS, 0)])

    hitos = [
        (VERDE, "SPRINT 1 · 2 semanas", "Cimiento cognitivo y RAG: embeddings e ingesta inicial"),
        (NAVY, "SPRINT 2 · 2 semanas", "Inferencia y prompts de auditoría"),
        (VERDE, "SPRINT 3 · 2 semanas", "RPA y organización de archivos: triage de carpetas"),
        (NAVY, "SPRINT 4 · 2 semanas", "Explicabilidad: checklist y justificaciones"),
        (VERDE, "SPRINT 5 · 2 semanas", "Procesamiento por lotes y reportes"),
        (GRIS, "CIERRE", "Pruebas integrales, validación y documentación"),
    ]
    caja(s, 5.11, 1.90, 0.03, 2.50, relleno=GRIS, borde=None, forma=MSO_SHAPE.RECTANGLE)
    for i, (color, cod, nombre) in enumerate(hitos):
        cy = 1.90 + i * 0.50
        caja(s, 5.02, cy - 0.10, 0.21, 0.21, relleno=color, borde=None, forma=MSO_SHAPE.OVAL)
        texto(s, 5.45, cy - 0.22, 4.01, 0.44,
              [(cod, 7.5, True, color, 0), (nombre, 8.5, False, TINTA, 1)],
              anchor=MSO_ANCHOR.MIDDLE)
    return s


def slide_D2(prs, layout):
    """Cadena de fases IPA en chevrones, con el artefacto colgando de cada una y el
    bucle de control que devuelve al entendimiento. Deliberadamente distinta de la
    diapositiva anterior (que ya describe las fases en tarjetas)."""
    s = nueva(prs, layout)
    titulo(s, "Qué dejó cada fase de la metodología IPA",
           "La diapositiva anterior describe las seis fases; ésta muestra el entregable "
           "verificable que produjo cada una en este proyecto.")

    fases = [
        ("01", "Entendimiento", "Diagrama AS-IS del proceso documental de la carrera"),
        ("02", "Viabilidad y priorización", "Delimitación de los 5 indicadores evaluables (Tablas 8 y 9)"),
        ("03", "Diseño TO-BE", "BPMN del proceso automatizado y arquitectura N-capas"),
        ("04", "Desarrollo", "Extractor documental OCR y normativa CACES vectorizada"),
        ("05", "Orquestación", "FastAPI + Celery + Redis: un chord por lote"),
        ("06", "Control y pruebas", "Protocolo experimental del Capítulo IV"),
    ]
    paso, w = 1.474, 1.54
    centros = []
    for i, (num, nombre, artefacto) in enumerate(fases):
        x = X0 + i * paso
        color = VERDE if i % 2 == 0 else NAVY
        cx = x + 0.07 + 0.70  # centro del cuerpo del chevron

        # La geometria del chevron reserva la punta dentro de su rectangulo de texto,
        # asi que el rotulo va en una caja de texto encima, no dentro de la forma.
        ch = caja(s, x, 1.52, w, 0.74, relleno=color, borde=None, forma=MSO_SHAPE.CHEVRON)
        try:
            ch.adjustments[0] = 0.25
        except Exception:
            pass
        claro = RGBColor(0xB8, 0xD8, 0xCC) if color is VERDE else RGBColor(0xB8, 0xC2, 0xE8)
        texto(s, x + 0.20, 1.55, w - 0.40, 0.68,
              [(num, 7.5, True, claro, 0), (nombre, 8.5, True, BLANCO, 0)],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

        flecha(s, cx, 2.30, cx, 2.52, color=color, grosor=1.25)
        a = caja(s, cx - 0.70, 2.55, 1.40, 0.98,
                 relleno=VERDE_SUAVE if color is VERDE else NAVY_SUAVE,
                 borde=color, radio=0.10)
        escribir(a, [(artefacto, 7.5, True, color, 0)],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        _margenes(a.text_frame, 0.05, 0.05, 0.03, 0.03)
        centros.append(cx)

    texto(s, X0, 2.30, 2.20, 0.20,
          [("ARTEFACTO PRODUCIDO", 6.5, True, GRIS, 0)])

    # bucle de control: la fase 06 realimenta a la 01
    flecha(s, centros[-1], 3.53, centros[-1], 3.78, color=GRIS, grosor=1.25, punta=False)
    flecha(s, centros[-1], 3.78, centros[0], 3.78, color=GRIS, grosor=1.25, punta=False)
    flecha(s, centros[0], 3.78, centros[0], 3.53, color=GRIS, grosor=1.25)
    texto(s, X0, 3.84, ANCHO, 0.24,
          [("El control realimenta al entendimiento: el ciclo IPA se repite en cada período "
            "de evaluación.", 8, True, GRIS, 0)], align=PP_ALIGN.CENTER)

    f = caja(s, X0, 4.20, ANCHO, 0.52, relleno=VERDE_SUAVE, borde=VERDE, radio=0.12)
    escribir(f, [("Ninguna fase quedó en el papel: cada una se sostiene con un entregable "
                  "que el tribunal puede revisar.", 9.5, True, VERDE, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


def slide_D3(prs, layout):
    s = nueva(prs, layout)
    titulo(s, "Scrum e IPA: dos ejes, no dos rivales",
           "Se aplican a la vez porque responden preguntas distintas del mismo proyecto.")

    a = caja(s, X0, 1.45, 4.35, 1.30, relleno=BLANCO, borde=BORDE, radio=0.08)
    caja(s, X0, 1.45, 0.07, 1.30, relleno=NAVY, borde=None, forma=MSO_SHAPE.RECTANGLE)
    escribir(a, [("SCRUM responde: ¿CÓMO se construyó?", 11, True, NAVY, 0),
                 ("Gobierna el tiempo y la gestión: roles, backlog priorizado con MoSCoW, "
                  "sprints de dos semanas, incremento ejecutable y retrospectiva. Mitiga la "
                  "incertidumbre técnica del comportamiento empírico del modelo.",
                  8, False, TINTA, 4)], anchor=MSO_ANCHOR.MIDDLE)
    a.text_frame.margin_left = Inches(0.18)

    b = caja(s, 5.11, 1.45, 4.35, 1.30, relleno=BLANCO, borde=BORDE, radio=0.08)
    caja(s, 5.11, 1.45, 0.07, 1.30, relleno=VERDE, borde=None, forma=MSO_SHAPE.RECTANGLE)
    escribir(b, [("IPA responde: ¿QUÉ se automatizó?", 11, True, VERDE, 0),
                 ("Gobierna el alcance de la automatización: analiza el proceso manual, decide "
                  "qué tarea es automatizable y con qué tecnología, y delimita los indicadores "
                  "que el sistema puede dictaminar.", 8, False, TINTA, 4)],
             anchor=MSO_ANCHOR.MIDDLE)
    b.text_frame.margin_left = Inches(0.18)

    texto(s, X0, 2.90, ANCHO, 0.24,
          [("EN QUÉ SPRINT SE EJECUTÓ CADA FASE DE LA METODOLOGÍA IPA", 7.5, True, GRIS, 0)])

    columnas = [
        ("SPRINT 1", ["01 Entendimiento", "02 Viabilidad", "04 Desarrollo (RAG)"]),
        ("SPRINT 2", ["04 Desarrollo (prompts e inferencia)"]),
        ("SPRINT 3", ["03 Diseño TO-BE (triage)", "04 Desarrollo (RPA)"]),
        ("SPRINT 4", ["04 Desarrollo (explicabilidad)"]),
        ("SPRINT 5", ["05 Orquestación", "06 Control y pruebas"]),
    ]
    w, gap = 1.64, 0.17
    x = X0
    for cod, fases in columnas:
        c = caja(s, x, 3.18, w, 1.20, relleno=GRIS_SUAVE, borde=BORDE, radio=0.08)
        chip(s, x, 3.18, w, 0.28, cod, NAVY, pt=7.5, radio=0.14)
        lineas = [("• " + f, 7, False, TINTA, 3) for f in fases]
        texto(s, x + 0.08, 3.52, w - 0.16, 0.80, lineas)
        x += w + gap

    f = caja(s, X0, 4.50, ANCHO, 0.40, relleno=VERDE_SUAVE, borde=VERDE, radio=0.10)
    escribir(f, [("No compiten: Scrum gobierna el tiempo del desarrollo; IPA gobierna el "
                  "alcance de lo que se automatiza.", 9, True, VERDE, 0)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# --------------------------------------------------------------------------- #
# Renombrado de "capas" en las diapositivas existentes
# --------------------------------------------------------------------------- #
SUSTITUCIONES = {
    19: [("Diseño de la arquitectura de 3 capas (FastAPI/Celery). Interfaz web con 4 estados "
          "UI: bienvenida, carga, encolado y reporte.",
          "Diseño de la arquitectura N-capas y del pipeline de auditoría en 3 etapas "
          "(FastAPI/Celery). Interfaz web con 4 estados UI: bienvenida, carga, encolado y reporte.")],
    22: [("1. FIABILIDAD ESTRUCTURAL (CAPA 1)",
          "1. FIABILIDAD ESTRUCTURAL (PRE-LLM)")],
    23: [("2. ADECUACIÓN FUNCIONAL GLOBAL (CAPA 2)",
          "2. ADECUACIÓN FUNCIONAL (JUICIO DEL LLM)")],
    28: [("Eficacia de las 3 Capas", "Eficacia de las compuertas de seguridad"),
         ("La separación de la lógica en compuertas deterministas (Capa 1) y razonamiento del "
          "LLM (Capa 2) mitiga errores de forma robusta.",
          "La separación entre las compuertas deterministas Pre-LLM y el juicio del modelo "
          "mitiga errores de forma robusta.")],
}


def _runs(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from _runs(sh.shapes)
            continue
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    yield r


def aplicar_sustituciones(prs):
    hechas = 0
    for idx, pares in SUSTITUCIONES.items():
        for r in _runs(prs.slides[idx].shapes):
            for viejo, nuevo in pares:
                if r.text.strip() == viejo.strip():
                    r.text = nuevo
                    hechas += 1
    return hechas


# --------------------------------------------------------------------------- #
# Principal
# --------------------------------------------------------------------------- #
def main():
    shutil.copyfile(ORIGEN, DESTINO)
    prs = Presentation(str(DESTINO))
    assert len(prs.slides._sldIdLst) == 31, "El original debería tener 31 diapositivas"

    n = aplicar_sustituciones(prs)
    print(f"Sustituciones de texto aplicadas: {n} (esperadas 5)")

    layout = prs.slides[22].slide_layout  # el TITLE_ONLY del ESPE realmente usado

    # slide_C2 (AS-IS/TO-BE) y slide_D3 (Scrum x IPA) quedan definidas pero fuera del
    # mazo por decisión del usuario: 38 diapositivas es la duración que quiere exponer.
    constructores = [slide_A1, slide_A2, slide_A3, slide_A4,
                     slide_B1, slide_B2, slide_B3,
                     slide_C1,
                     slide_D1, slide_D2]
    for f in constructores:
        f(prs, layout)
    print(f"Diapositivas nuevas construidas: {len(constructores)}")

    # eliminar 12 (en blanco), 19 (Gantt rasterizado) y 21 (BPMN ilegible)
    for idx in sorted([11, 18, 20], reverse=True):
        borrar_slide(prs, idx)

    # tras borrar: 28 originales (0..27) + 10 nuevas (28..37)
    A1, A2, A3, A4, B1, B2, B3, C1, D1, D2 = range(28, 38)
    orden = (
        list(range(0, 15))          # portada .. diagrama N-capas
        + [A1, A2, A3, A4]
        + [15, 16, D1, 17, D2]      # Cap.3, Scrum, ciclo+cronograma, IPA, IPA-artefactos
        + [B1, B2, B3, C1]
        + list(range(18, 28))       # Cap.4 y Cap.5 hasta GRACIAS
    )
    assert sorted(orden) == list(range(38)), "El orden debe ser una permutación completa"
    reordenar(prs, orden)

    prs.save(str(DESTINO))
    print(f"Guardado: {DESTINO}")
    print(f"Total de diapositivas: {len(Presentation(str(DESTINO)).slides._sldIdLst)}")


if __name__ == "__main__":
    main()
