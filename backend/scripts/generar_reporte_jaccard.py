# -*- coding: utf-8 -*-
"""
Informe HTML (+ PDF) autocontenido con la evaluación de las evidencias de los CINCO
indicadores instrumentados: 1 perfil, 2 proyecto, 3 malla, 4 sílabo, 6 guía.

Para los indicadores de FORMULARIO (4 sílabo, 6 guía, 3 malla) separa DOS medidas:

  1. CUMPLIMIENTO DE PLANTILLA (Jaccard principal): ¿están presentes los elementos que exige
     la plantilla? Sólo un elemento AUSENTE (que ni siquiera aparece) cuenta como falta.
     J_plantilla = |presentes| / |total|.
  2. VACÍOS (cálculo aparte): de los elementos PRESENTES, cuántos están sin contenido
     (sección vacía o campo en blanco). No es incumplir la plantilla, es no rellenarla.

Los indicadores 1 y 2 NO son formularios de casillas y su ALCANCE es distinto: parte de sus
elementos fundamentales se evidencian en fuentes EXTERNAS (documentos que el PDF auditado no
es) y quedan FUERA del cociente, nombrando la fuente ausente. Ver `plantilla_perfil.py` y
`plantilla_proyecto.py`. El informe lo dice en su cara: presentar los cinco números como
comparables sin esa advertencia induciría a error.

Además del J contra el ESQUEMA, para los indicadores 1 y 2 se incluye el modo `--base`: el
Jaccard de cada documento contra el DOCUMENTO BASE APROBADO de su carpeta.

Reutiliza las funciones `evaluar` de los cinco evaluadores (datos en vivo). Salidas:
    backend/data/resultados_evaluacion/reporte_jaccard.html
    backend/data/resultados_evaluacion/reporte_jaccard.pdf   (Chrome headless)
El sílabo abre ChromaDB (se cachea una sola vez). Perfil y proyecto no: van sin cuota.
"""
import glob
import html
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

# Los evaluadores re-envuelven sys.stdout al importarse; se mantiene vivo cada wrapper
# para que el recolector no cierre el buffer compartido a mitad de corrida.
_keepalive = [sys.stdout]
import completitud as sil  # noqa: E402
_keepalive.append(sys.stdout)
_base = sil._abrir_base()
sil._abrir_base = lambda: _base
import completitud_guia as gui  # noqa: E402
_keepalive.append(sys.stdout)
import completitud_malla as mal  # noqa: E402
_keepalive.append(sys.stdout)
import completitud_perfil as per  # noqa: E402
_keepalive.append(sys.stdout)
import completitud_proyecto as pro  # noqa: E402
_keepalive.append(sys.stdout)
from plantilla_silabo import PLANTILLA_SILABO  # noqa: E402
from plantilla_guia import PLANTILLA_GUIA  # noqa: E402
from plantilla_malla import ORDINALES_PAO, CAMPOS_ASIGNATURA  # noqa: E402
import plantilla_perfil as pp  # noqa: E402
import plantilla_proyecto as px  # noqa: E402

AUSENTE = ("AUSENTE",)
VACIO = ("VACÍO", "VACÍA", "VACIO")


def clasificar(estado):
    """3 estados: 'aus' (ausente, NO cumple plantilla) · 'vac' (presente pero vacío) · 'ok'."""
    if estado in AUSENTE:
        return "aus"
    if estado in VACIO:
        return "vac"
    return "ok"


def _metricas(elementos):
    """A partir de [{clase}] calcula las dos medidas por evidencia."""
    total = len(elementos)
    aus = sum(1 for e in elementos if e["clase"] == "aus")
    vac = sum(1 for e in elementos if e["clase"] == "vac")
    presentes = total - aus
    return {
        "total": total, "ausentes": aus, "vacios": vac, "presentes": presentes,
        "j_plantilla": presentes / total if total else 1.0,
        "j_contenido": (presentes - vac) / presentes if presentes else 1.0,
    }


# ---------------------------------------------------------------------------
# Recolección
# ---------------------------------------------------------------------------
def _evidencia_form(nombre, estado, plantilla):
    elementos = []
    for n, seccion, tipo, _a in plantilla:
        raw = str(estado.get(n, "AUSENTE"))
        elementos.append({"seccion": seccion, "nombre": n, "tipo": tipo,
                          "estado": raw, "clase": clasificar(raw)})
    ev = {"nombre": nombre, "sin_plantilla": False, "elementos": elementos}
    ev.update(_metricas(elementos))
    return ev


def datos_silabo():
    evs = []
    for ruta in sorted(glob.glob(sil.SILABOS)):
        if "_Reporte" in ruta:
            continue
        nombre = os.path.basename(ruta)
        _meta, estado, _f = sil.evaluar(ruta)
        if estado is None:
            evs.append({"nombre": nombre, "sin_plantilla": True})
        else:
            evs.append(_evidencia_form(nombre, estado, PLANTILLA_SILABO))
    return evs


def datos_guia():
    evs = []
    for ruta in sorted(glob.glob(gui.GUIAS)):
        if "_Reporte" in ruta:
            continue
        nombre = os.path.basename(ruta)
        estado = gui.evaluar(ruta)
        if estado is None:
            evs.append({"nombre": nombre, "sin_plantilla": True})
        else:
            evs.append(_evidencia_form(nombre, estado, PLANTILLA_GUIA))
    return evs


def datos_malla():
    """Cada malla FUENTE (el corpus ya excluye las copias que el sistema auto-genera).

    Para la malla, un elemento 'ausente' es un PAO que falta (estructura no presente); un
    campo de asignatura en 'VACIO' es 'presente pero vacío'. El código nunca es ausente (es
    el ancla). Devuelve (evaluadas, rechazadas)."""
    evaluadas, rechazadas = [], []
    for ruta in mal._rutas_corpus():
        nombre = os.path.basename(ruta)
        filas, _niveles, presentes = mal.evaluar(ruta)
        if filas is None:
            rechazadas.append(nombre)
            continue
        elementos = []
        for f in filas:
            for c in CAMPOS_ASIGNATURA:
                raw = str(f.get(c))
                elementos.append({"codigo": f["codigo"], "campo": c, "estado": raw,
                                  "clase": "vac" if raw == mal.VALOR_VACIO else "ok"})
        for i, ordinal in enumerate(ORDINALES_PAO, start=1):
            pres = i in presentes
            elementos.append({"codigo": None, "campo": f"{ordinal} PAO",
                              "estado": "presente" if pres else "AUSENTE",
                              "clase": "ok" if pres else "aus"})
        ev = {"nombre": nombre, "sin_plantilla": False, "filas": filas,
              "presentes_pao": presentes, "anomalias": mal._anomalias_hpao(filas),
              "elementos": elementos}
        ev.update(_metricas(elementos))
        evaluadas.append(ev)
    return evaluadas, rechazadas


def datos_perfil():
    """Indicador 1. Dos salidas: J contra el ESQUEMA y J contra el DOCUMENTO BASE APROBADO.

    El cociente es sobre 3 elementos (E1, E2, E4), NO sobre los 5 de la norma: E3 y E5 se
    evidencian en fuentes externas (b/d/e/f) y quedan fuera a propósito, nombrando la fuente.
    Ver la NOTA DE ALCANCE en `plantilla_perfil.py`. Cada PDF se extrae UNA vez y se cachea:
    la tabla contra el base reutiliza el mismo resultado.
    """
    A = pp.universo()
    evs, cache = [], {}
    for ruta in per._rutas_corpus():
        reconocida, detectados, evidencias, longitud = per.evaluar(ruta)
        cache[ruta] = (detectados, evidencias)
        B = per._puntuables(detectados)
        elementos = [
            {"seccion": f"Elementos evidenciables en el perfil · el cociente es sobre {len(A)}",
             "nombre": e.etiqueta, "tipo": "sem",
             "estado": "con evidencia léxica" if e.etiqueta in B else "SIN EVIDENCIA",
             "clase": "ok" if e.etiqueta in B else "aus",
             "pistas": evidencias[e.etiqueta]}
            for e in pp.ELEMENTOS_EVALUABLES]
        # E3/E5: NO son un 'ausente'. No se evidencian aquí y no puntúan; se nombra su fuente.
        fuera = [{"nombre": e.etiqueta, "fuente": e.fuente,
                  "rastro": e.etiqueta in detectados, "pistas": evidencias[e.etiqueta]}
                 for e in pp.ELEMENTOS_FUENTE_EXTERNA]
        ev = {"nombre": os.path.basename(ruta), "sin_plantilla": False, "ruta": ruta,
              "reconocida": reconocida, "chars": longitud, "elementos": elementos,
              "fuera": fuera}
        ev.update(_metricas(elementos))
        ev["j_plantilla"] = per._jaccard(A, B)[0]      # None ⇒ INDEFINIDO, nunca 1,0 maquillado
        evs.append(ev)

    ruta_base = next((r for r in cache
                      if per.BASE_APROBADO.lower() in os.path.basename(r).lower()), None)
    base = []
    if ruta_base:
        A_base = per._puntuables(cache[ruta_base][0])
        for ruta, (detectados, _e) in cache.items():
            if ruta == ruta_base:
                continue
            B = per._puntuables(detectados)
            j, inter, union = per._jaccard(A_base, B)
            base.append({"nombre": os.path.basename(ruta), "j": j, "inter": len(inter),
                         "union": len(union),
                         "dif": sorted(d.split(" · ")[0] for d in (A_base ^ B))})
    return evs, {"nombre": os.path.basename(ruta_base) if ruta_base else None,
                 "universo": sorted(per._puntuables(cache[ruta_base][0])) if ruta_base else [],
                 "filas": base}


def datos_proyecto():
    """Indicador 2. J contra el ESQUEMA (3 marcadores + 7 anclas = 10 etiquetas) y J de
    SECCIONES contra el ejemplar aprobado.

    El cociente cubre 3 de los 6 elementos de la norma: E2, E4 y E6 se evidencian en las
    fuentes b), d) y e)/f) y quedan fuera, nombrando la fuente (`plantilla_proyecto.py`).
    Sólo UN documento del corpus es un proyecto de rediseño auténtico; los otros dos (modelo
    educativo y reglamento de examen) no lo son y se rechazan: eso es un ACIERTO.
    """
    A = px.universo()
    evs, secs = [], {}
    for ruta in pro._rutas_corpus():
        _texto, secciones, B, recorte = pro.evaluar(ruta)
        secs[ruta] = set(secciones)
        elementos = [
            {"seccion": "Marcadores · identifican el formulario de rediseño",
             "nombre": " | ".join(g), "tipo": "marc",
             "estado": "presente" if px.etiqueta_marcador(g) in B else "AUSENTE",
             "clase": "ok" if px.etiqueta_marcador(g) in B else "aus", "pistas": []}
            for g in px.MARCADORES]
        elementos += [
            {"seccion": "Anclas de sección · las exigen los elementos 1, 3 y 5",
             "nombre": f"{a} (elem. "
                       f"{','.join(str(n) for n in px.ELEMENTO_DE_ANCLA.get(a, []))})",
             "tipo": "ancla",
             "estado": (f"{len(secciones[a])} ch" if a in secciones else "AUSENTE"),
             "clase": "ok" if px.etiqueta_ancla(a) in B else "aus", "pistas": []}
            for a in px.ANCLAS]
        fuera = [{"nombre": f"E{e.numero} · {e.descripcion}", "fuente": e.fuente,
                  "rastro": False, "pistas": []} for e in px.ELEMENTOS_FUENTE_EXTERNA]
        union = A | B
        ev = {"nombre": os.path.basename(ruta), "sin_plantilla": False, "ruta": ruta,
              "reconocida": all(px.etiqueta_marcador(g) in B for g in px.MARCADORES),
              "chars": recorte["original"], "elementos": elementos, "fuera": fuera,
              "parciales": [f"E{e.numero} · {e.fuente_parcial}"
                            for e in px.ELEMENTOS if e.fuente_parcial]}
        ev.update(_metricas(elementos))
        ev["j_plantilla"] = (len(A & B) / len(union)) if union else None
        evs.append(ev)

    ruta_base = next((r for r in secs if os.path.basename(r) == pro.DOCUMENTO_BASE), None)
    base = []
    if ruta_base:
        A_base = secs[ruta_base]
        for ruta, B in secs.items():
            union = A_base | B
            base.append({"nombre": os.path.basename(ruta),
                         "j": (len(A_base & B) / len(union)) if union else None,
                         "inter": len(A_base & B), "union": len(union),
                         "dif": sorted(A_base - B), "es_base": ruta == ruta_base})
    return evs, {"nombre": pro.DOCUMENTO_BASE if ruta_base else None,
                 "universo": sorted(secs[ruta_base]) if ruta_base else [],
                 "filas": base}


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def esc(t):
    return html.escape(str(t))


def chip_jaccard(j, etiqueta="plantilla"):
    """J = None ⇒ A ∪ B vacío ⇒ INDEFINIDO. Nunca se maquilla como 1,0 (mismo criterio que
    `jaccard.py` y `completitud_malla.py`): 0/0 no premia detectar algo, premia que no
    hubiera nada que detectar."""
    if j is None:
        return ('<span class="jac jac-indef"><span class="jac-bar"></span>'
                '<span class="jac-num jac-indef-n" title="A ∪ B vacío: no había nada que '
                'comparar">INDEF.</span></span>')
    clase = "ok" if j >= 0.999 else ("warn" if j >= 0.85 else "bad")
    return (f'<span class="jac jac-{clase}"><span class="jac-bar">'
            f'<span style="width:{j*100:.1f}%"></span></span>'
            f'<span class="jac-num">{j:.3f}</span></span>')


def badge_vacios(n):
    if n == 0:
        return '<span class="vb vb-0">sin vacíos</span>'
    return f'<span class="vb vb-n">{n} vacío(s)</span>'


DOTS = {"ok": '<span class="dot dot-ok"></span>',
        "vac": '<span class="dot dot-vac"></span>',
        "aus": '<span class="dot dot-aus"></span>'}
ETIQ = {"ok": "", "vac": "presente · vacío", "aus": "AUSENTE · no está en el documento"}


def render_lista_elementos(elementos):
    filas, seccion = [], None
    for e in elementos:
        if e["seccion"] != seccion:
            seccion = e["seccion"]
            filas.append(f'<div class="grp">{esc(seccion)}</div>')
        clase = e["clase"]
        estado = e["estado"]
        if clase == "ok":
            val = estado if estado in VACIO + AUSENTE else esc(estado)
        elif clase == "vac":
            val = "vacío" if estado in ("VACÍO", "VACIO") else "vacía"
        else:
            val = "no está"
        filas.append(
            f'<div class="el el-{clase}">{DOTS[clase]}'
            f'<span class="el-n">{esc(e["nombre"])}</span>'
            f'<span class="el-v">{val}</span></div>')
    return "".join(filas)


def render_evidencia(ev):
    if ev.get("sin_plantilla"):
        return (f'<div class="ev ev-off"><div class="ev-h">'
                f'<span class="ev-n">{esc(ev["nombre"])}</span>'
                f'<span class="tag tag-off">no usa la plantilla oficial</span></div></div>')
    aus = ev["ausentes"]
    meta = (f'<span class="ev-meta">{ev["presentes"]}/{ev["total"]} presentes'
            + (f' · <b class="bad-t">{aus} ausente(s)</b>' if aus else '') + '</span>')
    return (
        f'<details class="ev">'
        f'<summary class="ev-h">'
        f'<span class="ev-n">{esc(ev["nombre"])}</span>{meta}'
        f'{badge_vacios(ev["vacios"])}{chip_jaccard(ev["j_plantilla"])}'
        f'<span class="caret" aria-hidden="true"></span></summary>'
        f'<div class="ev-body">{render_lista_elementos(ev["elementos"])}</div>'
        f'</details>')


def render_malla_evidencia(info):
    filas = info["filas"]
    presentes = info["presentes_pao"]
    filas_html = []
    for f in filas:
        campos = "".join(
            f'<td class="{"c-vac" if f.get(c) == mal.VALOR_VACIO else "c-ok"}">'
            f'{DOTS["vac"] if f.get(c) == mal.VALOR_VACIO else DOTS["ok"]}'
            f'<span>{esc(f.get(c) if f.get(c) != mal.VALOR_VACIO else "vacío")}</span></td>'
            for c in CAMPOS_ASIGNATURA)
        filas_html.append(f'<tr><td class="cod">{esc(f["codigo"])}</td>{campos}</tr>')
    pao = "".join(
        f'<span class="pao pao-{"ok" if (i+1) in presentes else "aus"}">'
        f'{DOTS["ok"] if (i+1) in presentes else DOTS["aus"]}{esc(ordinal)}</span>'
        for i, ordinal in enumerate(ORDINALES_PAO))
    return (
        f'<details class="ev">'
        f'<summary class="ev-h">'
        f'<span class="ev-n">{esc(info["nombre"])}</span>'
        f'<span class="ev-meta">{len(filas)} asignaturas · '
        f'{len(presentes)}/8 PAO</span>'
        f'{badge_vacios(info["vacios"])}{chip_jaccard(info["j_plantilla"])}'
        f'<span class="caret" aria-hidden="true"></span></summary>'
        f'<div class="ev-body">'
        f'<div class="paos">{pao}</div>'
        f'<div class="tbl-wrap"><table class="tbl">'
        f'<thead><tr><th>Código</th><th>Nombre</th><th>Prerrequisito</th>'
        f'<th>HPAO</th><th>Créditos</th></tr></thead>'
        f'<tbody>{"".join(filas_html)}</tbody></table></div></div></details>')


def render_lista_semantica(elementos):
    """Como `render_lista_elementos`, pero muestra las PISTAS que dispararon el proxy: si la
    evidencia no convence a un lector humano, es un falso positivo y debe poder verse."""
    filas, seccion = [], None
    for e in elementos:
        if e["seccion"] != seccion:
            seccion = e["seccion"]
            filas.append(f'<div class="grp">{esc(seccion)}</div>')
        pistas = "".join(f'<div class="pista">· {esc(p)}</div>' for p in e.get("pistas") or [])
        filas.append(
            f'<div class="el el-{e["clase"]}">{DOTS[e["clase"]]}'
            f'<span class="el-n">{esc(e["nombre"])}</span>'
            f'<span class="el-v">{esc(e["estado"])}</span></div>'
            + (f'<div class="pistas">{pistas}</div>' if pistas else ""))
    return "".join(filas)


def render_fuera(fuera, parciales=()):
    """Los elementos que exigen FUENTE EXTERNA. No son 'ausentes' ni incumplimientos: este
    documento no es donde se evidencian. Se nombra la fuente que falta, que es lo honesto."""
    if not fuera:
        return ""
    items = []
    for f in fuera:
        rastro = ""
        if f.get("rastro"):
            pistas = "".join(f'<div class="pista">· {esc(p)}</div>'
                             for p in f.get("pistas") or [])
            rastro = ('<div class="fx-r">rastro léxico presente · señal informativa, NO '
                      'acredita nada (un rastro léxico no es un acta ni una política)'
                      f'{pistas}</div>')
        items.append(f'<div class="fx-el"><span class="fx-n">{esc(f["nombre"])}</span>'
                     f'<div class="fx-src">no evaluable sobre este documento · requiere '
                     f'fuente {esc(f["fuente"])}</div>{rastro}</div>')
    par = "".join(f'<div class="fx-p">~ {esc(p)}</div>' for p in parciales)
    return (f'<div class="fx"><div class="fx-h">Fuera del cociente · {len(fuera)} elemento(s) '
            f'que se evidencian en otra fuente</div>{"".join(items)}'
            + (f'<div class="fx-ph">Entra en el cociente, pero su juicio completo exige '
               f'además otra fuente:</div>{par}' if par else "")
            + '<div class="fx-f">No es que la carrera incumpla: es que la fuente que lo '
              'evidencia no es este PDF y no se aportó. Contarlos como incumplidos sería '
              'decir "eres mediocre" cuando lo cierto es "no me diste el acta".</div></div>')


def render_evidencia_semantica(ev):
    """Tarjeta de un documento de los indicadores 1 / 2 (prosa y estructura, no casillas)."""
    aus = ev["ausentes"]
    plant = ('<span class="tag tag-ok">plantilla reconocida</span>' if ev["reconocida"]
             else '<span class="tag tag-off">plantilla NO reconocida</span>')
    meta = (f'<span class="ev-meta">{ev["presentes"]}/{ev["total"]} con evidencia'
            + (f' · <b class="bad-t">{aus} sin</b>' if aus else '') + '</span>')
    return (
        f'<details class="ev">'
        f'<summary class="ev-h"><span class="ev-n">{esc(ev["nombre"])}</span>{meta}'
        f'{plant}{chip_jaccard(ev["j_plantilla"])}'
        f'<span class="caret" aria-hidden="true"></span></summary>'
        f'<div class="ev-body">{render_lista_semantica(ev["elementos"])}'
        f'{render_fuera(ev["fuera"], ev.get("parciales", ()))}</div></details>')


def render_tabla_base(base, titulo, explicacion, col_dif):
    """Modo `--base`: Jaccard contra el DOCUMENTO BASE APROBADO de la carpeta."""
    if not base.get("nombre"):
        return ""
    filas = []
    for f in base["filas"]:
        dif = ", ".join(f["dif"]) if f["dif"] else "—"
        marca = (' <span class="tag tag-base">referencia</span>' if f.get("es_base") else "")
        filas.append(
            f'<tr><td class="cod-b">{esc(f["nombre"])}{marca}</td>'
            f'<td class="num">{f["inter"]}</td><td class="num">{f["union"]}</td>'
            f'<td class="num">{chip_jaccard(f["j"])}</td>'
            f'<td class="dif">{esc(dif)}</td></tr>')
    return (
        f'<details class="inv base" open><summary>{esc(titulo)}</summary>'
        f'<div class="inv-body base-body">'
        f'<p class="nota nota-base">{explicacion}</p>'
        f'<div class="base-uni"><b>Base aprobado:</b> <code>{esc(base["nombre"])}</code> · '
        f'A = {len(base["universo"])} · {esc(", ".join(base["universo"]) or "(vacío)")}</div>'
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Documento</th>'
        f'<th>|A∩B|</th><th>|A∪B|</th><th>Jaccard</th><th>{esc(col_dif)}</th></tr></thead>'
        f'<tbody>{"".join(filas)}</tbody></table></div></div></details>')


def inventario_html(pares):
    bloques = []
    for seccion, nombres in pares:
        items = "".join(f'<li>{esc(n)}</li>' for n in nombres)
        bloques.append(f'<div class="inv-grp"><h4>{esc(seccion)}</h4>'
                       f'<ol class="inv-list">{items}</ol></div>')
    return "".join(bloques)


def inventario_de(plantilla):
    orden, grupos = [], {}
    for n, seccion, _t, _a in plantilla:
        if seccion not in grupos:
            grupos[seccion] = []
            orden.append(seccion)
        grupos[seccion].append(n)
    return [(s, grupos[s]) for s in orden]


def seccion_indicador(idc, titulo, subtitulo, cumplen, total_ev, jp_medio,
                      total_vacios, inventario, cuerpo, nota="", lbl_jp="cumplimiento de plantilla",
                      lbl_cumplen="cumplen la plantilla",
                      lbl_vacios="elementos vacíos (aparte)", alcance="", extra=""):
    stat = (f'<div class="stat"><span class="stat-num">{jp_medio:.3f}</span>'
            f'<span class="stat-lbl">{esc(lbl_jp)}</span></div>'
            f'<div class="stat"><span class="stat-num">{cumplen}<span class="stat-of">/{total_ev}</span></span>'
            f'<span class="stat-lbl">{esc(lbl_cumplen)}</span></div>'
            f'<div class="stat"><span class="stat-num stat-vac">{total_vacios}</span>'
            f'<span class="stat-lbl">{esc(lbl_vacios)}</span></div>')
    nota_html = f'<p class="nota">{nota}</p>' if nota else ""
    # El aviso de ALCANCE va ANTES del inventario a propósito: quien lea el número tiene que
    # tropezarse con lo que el número NO cubre antes de citarlo.
    alcance_html = f'<div class="alc">{alcance}</div>' if alcance else ""
    return (
        f'<section class="ind" id="{idc}">'
        f'<div class="ind-head"><div class="ind-title">'
        f'<span class="eyebrow">{esc(subtitulo)}</span><h2>{esc(titulo)}</h2></div>'
        f'<div class="ind-stats">{stat}</div></div>{nota_html}{alcance_html}'
        f'<details class="inv" open><summary>Inventario · el universo que se compara</summary>'
        f'<div class="inv-body">{inventario}</div></details>'
        f'<div class="evs">{cuerpo}</div>{extra}</section>')


CSS = """
<style>
:root{
  --ground:#f6f4ef; --surface:#fffdf9; --surface-2:#f0ece3; --ink:#1b1e1c; --muted:#696e69;
  --faint:#9a9e97; --line:#e4e0d7; --line-2:#d4cfc3; --accent:#0f6b64; --accent-soft:#dfece9;
  --ok:#2f8a57; --vac:#b0761a; --vac-soft:#f3e9d3; --bad:#bc4530; --bad-soft:#f3ddd6;
  --shadow:0 1px 2px rgba(20,25,22,.05),0 10px 30px -16px rgba(20,25,22,.18);
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"Cascadia Code","SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root{
  --ground:#141614; --surface:#1c201d; --surface-2:#242926; --ink:#ecebe4; --muted:#9ba09a;
  --faint:#6c716b; --line:#2b302c; --line-2:#39403a; --accent:#46bdb1; --accent-soft:#153230;
  --ok:#5cc088; --vac:#d7a441; --vac-soft:#2b2416; --bad:#e17c65; --bad-soft:#2e1c18;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 34px -18px rgba(0,0,0,.6);
}}
:root[data-theme="light"]{
  --ground:#f6f4ef; --surface:#fffdf9; --surface-2:#f0ece3; --ink:#1b1e1c; --muted:#696e69;
  --faint:#9a9e97; --line:#e4e0d7; --line-2:#d4cfc3; --accent:#0f6b64; --accent-soft:#dfece9;
  --ok:#2f8a57; --vac:#b0761a; --vac-soft:#f3e9d3; --bad:#bc4530; --bad-soft:#f3ddd6;
  --shadow:0 1px 2px rgba(20,25,22,.05),0 10px 30px -16px rgba(20,25,22,.18);
}
:root[data-theme="dark"]{
  --ground:#141614; --surface:#1c201d; --surface-2:#242926; --ink:#ecebe4; --muted:#9ba09a;
  --faint:#6c716b; --line:#2b302c; --line-2:#39403a; --accent:#46bdb1; --accent-soft:#153230;
  --ok:#5cc088; --vac:#d7a441; --vac-soft:#2b2416; --bad:#e17c65; --bad-soft:#2e1c18;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 34px -18px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);line-height:1.5;
  -webkit-font-smoothing:antialiased;margin:0}
.wrap{max-width:1080px;margin:0 auto;padding:clamp(20px,5vw,56px) clamp(16px,4vw,40px) 80px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);font-weight:600}
h1{font-size:clamp(26px,4.5vw,40px);font-weight:680;letter-spacing:-.02em;line-height:1.08;
  margin:.35em 0 .2em;text-wrap:balance}
.lede{color:var(--muted);max-width:64ch;font-size:15.5px}
.two-metrics{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.two-metrics .m{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:10px 14px;font-size:13px;max-width:33ch}
.two-metrics .m b{display:block;font-size:12.5px;margin-bottom:2px}
.m-1 b{color:var(--accent)} .m-2 b{color:var(--vac)} .m-3 b{color:var(--bad)}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;font-size:12.5px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:9px;height:9px;border-radius:50%;flex:none;display:inline-block}
.dot-ok{background:var(--ok)} .dot-vac{background:var(--vac)} .dot-aus{background:var(--bad)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:34px 0 8px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px;
  box-shadow:var(--shadow)}
.card .k{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.card .big{font-family:var(--mono);font-size:34px;font-weight:600;letter-spacing:-.02em;
  font-variant-numeric:tabular-nums;margin:6px 0 2px;color:var(--accent)}
.card .sub{font-size:13px;color:var(--muted)}
.card .sub2{font-size:12px;color:var(--vac);margin-top:3px}
.card .barrow{display:flex;gap:3px;margin-top:12px}
.card .barrow i{height:6px;border-radius:2px;flex:1}
.ind{margin-top:44px;border-top:1px solid var(--line-2);padding-top:26px}
.ind-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap}
.ind-title h2{font-size:23px;font-weight:660;letter-spacing:-.01em;margin:.2em 0 0}
.ind-stats{display:flex;gap:22px;flex-wrap:wrap}
.stat{text-align:right}
.stat-num{display:block;font-family:var(--mono);font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.stat-vac{color:var(--vac)}
.stat-of{color:var(--faint);font-size:14px}
.stat-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.nota{background:var(--surface-2);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;
  padding:10px 14px;font-size:13.5px;color:var(--muted);margin:18px 0 0}
.nota code{font-family:var(--mono);font-size:12px}
.inv{margin:20px 0 8px;background:var(--surface);border:1px solid var(--line);border-radius:12px}
.inv>summary{cursor:pointer;padding:13px 18px;font-weight:600;font-size:13.5px;list-style:none;
  display:flex;align-items:center;gap:8px}
.inv>summary::-webkit-details-marker{display:none}
.inv>summary::before{content:"›";font-family:var(--mono);color:var(--accent);font-size:18px;transition:transform .18s}
.inv[open]>summary::before{transform:rotate(90deg)}
.inv-body{padding:2px 18px 18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px 26px}
.inv-grp h4{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin:8px 0 6px;font-weight:650}
.inv-list{margin:0;padding-left:22px;font-size:13px;color:var(--muted)}
.inv-list li{margin:2px 0}
.evs{display:flex;flex-direction:column;gap:7px;margin-top:14px}
.ev{background:var(--surface);border:1px solid var(--line);border-radius:11px;overflow:hidden}
.ev[open]{box-shadow:var(--shadow);border-color:var(--line-2)}
.ev-h{cursor:pointer;display:flex;align-items:center;gap:11px;padding:12px 16px;list-style:none;font-size:13.5px}
.ev-h::-webkit-details-marker{display:none}
.ev-n{font-weight:560;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ev-meta{color:var(--faint);font-size:12px;font-family:var(--mono);white-space:nowrap;flex:none}
.bad-t{color:var(--bad)}
.caret{width:8px;height:8px;border-right:2px solid var(--faint);border-bottom:2px solid var(--faint);
  transform:rotate(45deg);transition:transform .18s;flex:none}
.ev[open] .caret{transform:rotate(-135deg)}
.ev-off{opacity:.72}.ev-off .ev-h{cursor:default}
.tag{font-size:11px;font-family:var(--mono);padding:2px 8px;border-radius:20px;flex:none}
.tag-off{background:var(--vac-soft);color:var(--vac)}
.vb{font-size:11px;font-family:var(--mono);padding:2px 9px;border-radius:20px;flex:none;white-space:nowrap}
.vb-0{background:var(--surface-2);color:var(--faint)}
.vb-n{background:var(--vac-soft);color:var(--vac)}
.jac{display:inline-flex;align-items:center;gap:8px;flex:none}
.jac-bar{width:52px;height:6px;border-radius:4px;background:var(--surface-2);overflow:hidden;border:1px solid var(--line)}
.jac-bar>span{display:block;height:100%;background:var(--accent)}
.jac-bad .jac-bar>span{background:var(--bad)}.jac-warn .jac-bar>span{background:var(--vac)}.jac-ok .jac-bar>span{background:var(--ok)}
.jac-num{font-family:var(--mono);font-size:13px;font-weight:600;font-variant-numeric:tabular-nums;width:3.4ch;text-align:right}
.jac-ok .jac-num{color:var(--ok)}.jac-warn .jac-num{color:var(--vac)}.jac-bad .jac-num{color:var(--bad)}
.ev-body{padding:4px 16px 16px;border-top:1px solid var(--line)}
.grp{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);margin:14px 0 4px;font-weight:600}
.el{display:flex;align-items:baseline;gap:9px;padding:3px 0;font-size:13px;border-bottom:1px dotted var(--line)}
.el-n{flex:1 1 auto}
.el-v{color:var(--muted);font-family:var(--mono);font-size:11.5px;max-width:46%;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;text-align:right}
.el-vac .el-v{color:var(--vac)}
.el-aus .el-n{color:var(--bad);font-weight:560}.el-aus .el-v{color:var(--bad)}
.paos{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0 6px}
.pao{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-family:var(--mono);
  padding:3px 9px;border-radius:20px;background:var(--surface-2);border:1px solid var(--line)}
.pao-aus{background:var(--bad-soft);color:var(--bad)}
.tbl-wrap{overflow-x:auto;margin-top:8px;border:1px solid var(--line);border-radius:9px}
.tbl{border-collapse:collapse;width:100%;font-size:12px;min-width:640px}
.tbl th{text-align:left;font-family:var(--mono);font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--muted);padding:8px 10px;border-bottom:1px solid var(--line-2);background:var(--surface-2)}
.tbl td{padding:6px 10px;border-bottom:1px dotted var(--line);vertical-align:top}
.tbl td.cod{font-family:var(--mono);font-weight:600;color:var(--accent);white-space:nowrap}
.tbl td.c-ok,.tbl td.c-vac{white-space:nowrap;max-width:220px;overflow:hidden;text-overflow:ellipsis}
.tbl td.c-vac{color:var(--vac)}
.tbl tr:hover td{background:var(--accent-soft)}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--line-2);font-size:12px;color:var(--faint);font-family:var(--mono)}
@media (max-width:560px){.ind-head{align-items:flex-start}.ind-stats{gap:14px}.el-v{max-width:36%}.ev-meta{display:none}}

/* --- Indicadores 1 y 2: proxy semántico, alcance y fuentes externas --- */
.tag-ok{background:var(--accent-soft);color:var(--accent)}
.tag-base{background:var(--accent-soft);color:var(--accent)}
.jac-indef .jac-bar{background:repeating-linear-gradient(45deg,var(--surface-2),var(--surface-2) 3px,var(--line) 3px,var(--line) 6px)}
.jac-indef-n{color:var(--faint);font-size:10px;width:auto}
.pistas{margin:0 0 6px 18px}
.pista{font-family:var(--mono);font-size:11px;color:var(--faint);padding:1px 0;
  overflow-wrap:anywhere}
.alc{background:var(--vac-soft);border:1px solid var(--vac);border-left-width:3px;
  border-radius:0 8px 8px 0;padding:12px 15px;font-size:13px;color:var(--ink);margin:16px 0 0}
.alc b{color:var(--vac)}
.alc ul{margin:7px 0 0;padding-left:20px}
.alc li{margin:3px 0;color:var(--muted)}
.fx{margin:16px 0 4px;background:var(--surface-2);border:1px dashed var(--line-2);
  border-radius:10px;padding:12px 14px}
.fx-h{font-family:var(--mono);font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);font-weight:600;margin-bottom:8px}
.fx-el{padding:6px 0;border-bottom:1px dotted var(--line)}
.fx-el:last-of-type{border-bottom:0}
.fx-n{font-size:13px;font-weight:560}
.fx-src{font-size:11.5px;color:var(--muted);font-family:var(--mono);margin-top:2px;
  overflow-wrap:anywhere}
.fx-r{font-size:11.5px;color:var(--vac);margin-top:3px}
.fx-ph{font-size:11.5px;color:var(--muted);margin-top:9px;font-weight:600}
.fx-p{font-size:11.5px;color:var(--muted);font-family:var(--mono);margin-top:3px;
  overflow-wrap:anywhere}
.fx-f{font-size:12px;color:var(--muted);margin-top:9px;padding-top:8px;
  border-top:1px solid var(--line);font-style:italic}
.base-body{display:block}
.nota-base{margin:0 0 12px}
.base-uni{font-size:12px;color:var(--muted);margin-bottom:10px;overflow-wrap:anywhere}
.base-uni code{font-family:var(--mono);font-size:11.5px;color:var(--accent)}
.tbl td.cod-b{font-weight:560;max-width:280px;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.tbl td.num{text-align:center;font-family:var(--mono);font-variant-numeric:tabular-nums}
.tbl td.dif{color:var(--muted);font-size:11.5px;max-width:240px}
.asim{background:var(--bad-soft);border:1px solid var(--bad);border-left-width:3px;
  border-radius:0 8px 8px 0;padding:12px 15px;font-size:13px;margin:18px 0 0;color:var(--ink)}
.asim b{color:var(--bad)}

/* --- Impresión / PDF ---------------------------------------------------
   El informe se imprime con Chrome headless. Sin esto el PDF saldría con el tema OSCURO
   (el HTML tiene prefers-color-scheme) y cortando tarjetas por la mitad. Se fuerza el tema
   claro, se abren los <details> (en papel no hay nada que desplegar: lo colapsado
   sencillamente no existiría) y se evita partir una tarjeta entre páginas. */
@media print{
  /* Los tres selectores, no sólo `:root`: `:root[data-theme="dark"]` tiene MÁS
     especificidad y ganaría, dejando el PDF en negro si alguien fija el tema a mano. */
  :root,:root[data-theme="dark"],:root[data-theme="light"]{
    --ground:#fff; --surface:#fff; --surface-2:#f4f2ec; --ink:#111; --muted:#4a4f4a;
    --faint:#6e736d; --line:#ddd8cd; --line-2:#c3bdb0; --accent:#0b544e; --accent-soft:#e8f1ef;
    --ok:#20623d; --vac:#8a5a11; --vac-soft:#f7efdc; --bad:#93321f; --bad-soft:#f7e2db;
    --shadow:none;
  }
  @page{size:A4;margin:14mm 12mm}
  /* Sin esto Chrome descarta TODO fondo al imprimir y los puntos de estado (que son
     `background`) saldrían invisibles: la leyenda quedaría sin significado. */
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  body{background:#fff}
  .wrap{max-width:none;padding:0}
  .card,.ev,.inv,.nota,.alc,.asim,.fx,.two-metrics .m{box-shadow:none}
  /* En papel no se despliega nada: todo el detalle tiene que estar visible. */
  details>.ev-body,details>.inv-body{display:block!important}
  .caret,.inv>summary::before{display:none}
  .ev,.card,.fx,.inv-grp,.alc,.asim,.two-metrics .m,.el,.fx-el,.tbl tr{break-inside:avoid}
  .ind{break-before:page;border-top:0}
  .ind-head,.stat{break-inside:avoid}
  h1,h2,.grp{break-after:avoid}
  .ev-h{background:var(--surface-2)}
  .ev-n{white-space:normal;overflow:visible}
  .tbl-wrap{overflow:visible}
  .tbl{min-width:0;font-size:10px}
  .tbl td.c-ok,.tbl td.c-vac,.tbl td.cod-b{white-space:normal;max-width:none}
  .el-v{max-width:40%;white-space:normal;overflow:visible}
  .tbl tr:hover td{background:transparent}
  a{text-decoration:none;color:inherit}
}
</style>
"""


def barrow(evs):
    seg = []
    for ev in evs:
        j = None if ev.get("sin_plantilla") else ev["j_plantilla"]
        if j is None:      # sin plantilla o A ∪ B vacío (INDEFINIDO): ni verde ni rojo
            seg.append('<i style="background:var(--vac-soft)"></i>')
            continue
        col = "var(--ok)" if j >= 0.999 else ("var(--vac)" if j >= 0.85 else "var(--bad)")
        seg.append(f'<i style="background:{col}"></i>')
    return "".join(seg)


# ---------------------------------------------------------------------------
# PDF (Chrome headless: no hay weasyprint/reportlab/playwright en el venv)
# ---------------------------------------------------------------------------
DESCARGAS = os.path.join(os.path.expanduser("~"), "Downloads")
NAVEGADORES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


def exportar_pdf(ruta_html):
    """Imprime el HTML a PDF con Chrome/Edge headless. Devuelve la ruta o None.

    Detalles que importan y que no son evidentes:
      - `--user-data-dir` temporal: sin él, Chrome ve la sesión del usuario ya abierta,
        delega en ella y sale SIN imprimir nada (el `--version` de esta máquina hace justo
        eso: "Abriendo en una sesión existente del navegador").
      - `--no-pdf-header-footer` no existe en todas las versiones; si la corrida falla se
        reintenta sin él antes de darse por vencida.
      - El CSS `@media print` fuerza el tema claro: sin eso el PDF sale en negro, porque el
        HTML tiene `prefers-color-scheme` y la máquina puede estar en modo oscuro.
    """
    navegador = next((n for n in NAVEGADORES if os.path.exists(n)), None)
    if not navegador:
        print("PDF omitido: no encuentro Chrome ni Edge.")
        return None

    pdf = os.path.splitext(ruta_html)[0] + ".pdf"
    if os.path.exists(pdf):
        os.remove(pdf)
    perfil_tmp = os.path.join(os.environ.get("TEMP", "."), f"chrome_pdf_{os.getpid()}")

    # Se imprime desde una COPIA con todos los <details> abiertos. Un `display:block` en
    # `@media print` NO basta: Chrome oculta el contenido de un <details> cerrado con
    # `content-visibility` desde su shadow DOM, así que el PDF salía con las fichas
    # colapsadas (17 páginas de titulares y ni un elemento). En papel no hay nada que
    # desplegar: o el detalle está impreso, o no existe. El HTML interactivo se queda como
    # está (colapsado), que es como se navega bien en pantalla.
    with open(ruta_html, encoding="utf-8") as f:
        html_print = f.read()
    html_print = html_print.replace("<details class=", "<details open class=")
    ruta_print = os.path.splitext(ruta_html)[0] + "_print.html"
    with open(ruta_print, "w", encoding="utf-8") as f:
        f.write(html_print)
    url = "file:///" + ruta_print.replace("\\", "/")
    comun = ["--headless=new", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=20000",
             f"--user-data-dir={perfil_tmp}"]

    for extra in (["--no-pdf-header-footer"], []):
        cmd = [navegador] + comun + extra + [f"--print-to-pdf={pdf}", url]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            print("PDF: Chrome no respondió en 180 s.")
            continue
        time.sleep(1)
        if os.path.exists(pdf) and os.path.getsize(pdf) > 0:
            print(f"PDF:     {pdf}  ({os.path.getsize(pdf):,} bytes)"
                  + ("" if extra else "  [sin --no-pdf-header-footer]"))
            shutil.rmtree(perfil_tmp, ignore_errors=True)
            os.remove(ruta_print)
            return pdf
        print(f"PDF: intento fallido (código {proc.returncode}). "
              f"{(proc.stderr or '').strip()[:200]}")
    shutil.rmtree(perfil_tmp, ignore_errors=True)
    if os.path.exists(ruta_print):
        os.remove(ruta_print)
    print("PDF: no se pudo generar. El HTML sí está escrito.")
    return None


def main():
    print("Recolectando sílabos…")
    silabos = datos_silabo()
    print("Recolectando guías…")
    guias = datos_guia()
    print("Recolectando mallas…")
    mallas, malla_rechazadas = datos_malla()
    print("Recolectando perfiles de egreso (Ind. 1)…")
    perfiles, perfil_base = datos_perfil()
    print("Recolectando proyectos curriculares (Ind. 2)…")
    proyectos, proyecto_base = datos_proyecto()

    def conp(evs):
        return [e for e in evs if not e.get("sin_plantilla")]

    def jp_medio(evs):
        v = [e["j_plantilla"] for e in conp(evs) if e["j_plantilla"] is not None]
        return sum(v) / len(v) if v else 1.0

    def cumplen(evs):  # sin ningún AUSENTE
        return sum(1 for e in conp(evs) if e["ausentes"] == 0)

    def vacios_tot(evs):
        return sum(e["vacios"] for e in conp(evs))

    sjp, gjp = jp_medio(silabos), jp_medio(guias)
    mjp = jp_medio(mallas)
    pjp, xjp = jp_medio(perfiles), jp_medio(proyectos)

    n_ext_perfil = len(pp.ELEMENTOS_FUENTE_EXTERNA)
    n_ext_proyecto = len(px.ELEMENTOS_FUENTE_EXTERNA)
    cards = f"""
    <div class="cards">
      <div class="card"><div class="k">Ind. 1 · Perfil de egreso</div>
        <div class="big">{pjp:.3f}</div>
        <div class="sub">{cumplen(perfiles)}/{len(perfiles)} con evidencia completa ·
          {len(pp.ELEMENTOS_EVALUABLES)} de {pp.TOTAL_ELEMENTOS} elementos en el cociente</div>
        <div class="sub2">{n_ext_perfil} elementos fuera: exigen fuente externa</div>
        <div class="barrow">{barrow(perfiles)}</div></div>
      <div class="card"><div class="k">Ind. 2 · Proyecto curricular</div>
        <div class="big">{xjp:.3f}</div>
        <div class="sub">{cumplen(proyectos)}/{len(proyectos)} con el esquema completo ·
          10 etiquetas ({len(px.ELEMENTOS_EVALUABLES)} de {px.TOTAL_ELEMENTOS} elementos)</div>
        <div class="sub2">{n_ext_proyecto} elementos fuera: exigen fuente externa</div>
        <div class="barrow">{barrow(proyectos)}</div></div>
      <div class="card"><div class="k">Ind. 4 · Sílabo</div>
        <div class="big">{sjp:.3f}</div>
        <div class="sub">{cumplen(silabos)}/{len(conp(silabos))} cumplen la plantilla · 39 elementos</div>
        <div class="sub2">{vacios_tot(silabos)} elementos vacíos (cálculo aparte)</div>
        <div class="barrow">{barrow(silabos)}</div></div>
      <div class="card"><div class="k">Ind. 3 · Malla</div>
        <div class="big">{mjp:.3f}</div>
        <div class="sub">{cumplen(mallas)}/{len(mallas)} cumplen la plantilla · 184 elementos</div>
        <div class="sub2">{vacios_tot(mallas)} campos vacíos (cálculo aparte)</div>
        <div class="barrow">{barrow(mallas)}</div></div>
      <div class="card"><div class="k">Ind. 6 · Guía</div>
        <div class="big">{gjp:.3f}</div>
        <div class="sub">{cumplen(guias)}/{len(conp(guias))} cumplen la plantilla · 27 elementos</div>
        <div class="sub2">{vacios_tot(guias)} elementos vacíos (cálculo aparte)</div>
        <div class="barrow">{barrow(guias)}</div></div>
    </div>
    <div class="asim">
      <b>Los cinco números NO son igual de fiables.</b> La base de oro de los indicadores
      <b>1 y 2</b> acaba de corregirse contra el modelo CACES oficial (el estándar estaba
      truncado; el Indicador 2 tenía 5 elementos donde la norma tiene 6). Los indicadores
      <b>3, 4 y 6 nunca se han auditado contra la norma</b>: sus plantillas se derivaron de los
      formularios reales, no de una lectura del modelo oficial. Que aparezcan juntos aquí no
      los iguala: los dos primeros están verificados contra la norma y los otros tres están
      pendientes de esa auditoría. Cualquier número de <code>docs/</code> anterior a esta
      corrección, sobre los indicadores 1 y 2, está viciado.
    </div>"""

    # --- Indicador 1 · Perfil de egreso ---------------------------------------------------
    saturados = sum(1 for e in perfiles if e["j_plantilla"] == 1.0)
    sec_per = seccion_indicador(
        "perfil", "Perfil de egreso", "Indicador 1 · proxy léxico · sin LLM, sin cuota",
        cumplen(perfiles), len(perfiles), pjp, n_ext_perfil,
        inventario_html([
            (f"Evidenciables en el perfil · cociente sobre {len(pp.ELEMENTOS_EVALUABLES)}",
             [e.etiqueta for e in pp.ELEMENTOS_EVALUABLES]),
            ("Fuera del cociente · viven en otra fuente",
             [f"{e.etiqueta} → fuente {e.fuente.split(';')[0]}"
              for e in pp.ELEMENTOS_FUENTE_EXTERNA]),
            ("Marcadores de plantilla (basta uno)", list(pp.MARCADORES_PERFIL)),
        ]),
        "".join(render_evidencia_semantica(e) for e in perfiles),
        lbl_jp="cobertura de evidencia media", lbl_cumplen="con los 3 elementos evidenciados",
        lbl_vacios="fuera del cociente (fuente externa)",
        nota=("El perfil de egreso <b>no es un formulario</b>: es prosa. Sus 5 elementos son "
              "<code>[SEMÁNTICO]</code> y esto <b>no los verifica</b>: rastrea la huella léxica "
              "que deja un documento cuando habla de ellos. La métrica es <b>asimétrica</b>: "
              "J bajo es indicio razonable de que el documento ni aborda el elemento; "
              "<b>J alto NO acredita cumplimiento</b>. El juez real es el LLM, que además debe "
              "citar el documento."),
        alcance=(
            f"<b>Alcance distinto al de los indicadores 3, 4 y 6 — léelo antes de comparar.</b>"
            f"<ul>"
            f"<li>El cociente es sobre <b>{len(pp.ELEMENTOS_EVALUABLES)} elementos "
            f"(E1, E2, E4)</b>, no sobre los {pp.TOTAL_ELEMENTOS} de la norma. <b>E3</b> "
            f"(aporte de expertos externos, empleadores y graduados) y <b>E5</b> (seguimiento "
            f"y mejora continua) se evidencian en <b>fuentes b), d), e) y f)</b> — actas, "
            f"encuestas, políticas —, que no son este PDF. Dejarlos dentro daría a todo perfil "
            f"del mundo un techo de 3/5 y mediría «documentos que no me diste», no la calidad "
            f"del perfil. Quedan fuera <b>nombrando su fuente</b>, nunca como incumplidos en "
            f"silencio.</li>"
            f"<li><b>El J satura en 1,000:</b> {saturados} de {len(perfiles)} documentos lo "
            f"alcanzan. Este número <b>discrimina la basura de control</b> (el "
            f"<code>ejemplo_malo</code>, 221 caracteres, sale 0,000) <b>pero no la calidad</b>: "
            f"no separa un perfil bueno de uno mediocre. Como métrica de calidad no sirve; "
            f"como filtro de entrada, sí.</li>"
            f"<li>Un <code>A ∪ B</code> vacío se reporta <b>INDEFINIDO</b>, jamás como un 1,0 "
            f"maquillado: 0/0 no premia detectar algo, premia que no hubiera nada que "
            f"detectar.</li></ul>"),
        extra=render_tabla_base(
            perfil_base, "Modo --base · Jaccard contra el documento base aprobado",
            "A = elementos evaluables <b>con evidencia en el base</b>; B = los del candidato. "
            "Aquí el Jaccard es <b>simétrico</b> y no se reduce a un porcentaje. Ojo: el base "
            "es la <b>referencia de esta carrera, no el ideal de la norma</b>. Parecerse a él "
            "no acredita el Indicador 1: acredita parecerse a él. Si el base no declara un "
            "elemento, este modo no lo penaliza en nadie. E3 y E5 no entran: no son evaluables "
            "sobre un perfil.", "diferencias con el base"))

    # --- Indicador 2 · Proyecto curricular ------------------------------------------------
    autenticos = sum(1 for e in proyectos if e["reconocida"])
    sec_pro = seccion_indicador(
        "proyecto", "Proyecto curricular", "Indicador 2 · formulario de rediseño SENESCYT/CES",
        cumplen(proyectos), len(proyectos), xjp, n_ext_proyecto,
        inventario_html([
            ("Marcadores · identifican el formulario", [" | ".join(g) for g in px.MARCADORES]),
            ("Anclas de sección · elementos 1, 3 y 5",
             [f"{a} (elem. {','.join(str(n) for n in px.ELEMENTO_DE_ANCLA.get(a, []))})"
              for a in px.ANCLAS]),
            ("Fuera del cociente · viven en otra fuente",
             [f"E{e.numero} · {e.descripcion}" for e in px.ELEMENTOS_FUENTE_EXTERNA]),
        ]),
        "".join(render_evidencia_semantica(e) for e in proyectos),
        lbl_jp="completitud media del esquema", lbl_cumplen="con las 10 etiquetas",
        lbl_vacios="fuera del cociente (fuente externa)",
        nota=("El documento es el formulario de rediseño de carrera (~113 páginas). Su "
              "plantilla no son casillas etiqueta→valor (la base de oro deja "
              "<code>CAMPOS:</code> vacío), sino <b>3 marcadores + 7 anclas de sección = 10 "
              "etiquetas</b>. Que una sección <b>exista</b> no dice que su contenido sea "
              "coherente: eso lo juzga el LLM, no esto."),
        alcance=(
            f"<b>Alcance distinto al de los indicadores 3, 4 y 6 — léelo antes de comparar.</b>"
            f"<ul>"
            f"<li>El cociente cubre <b>{len(px.ELEMENTOS_EVALUABLES)} de los "
            f"{px.TOTAL_ELEMENTOS} elementos</b> de la norma. <b>E2</b> (políticas de "
            f"actualización del currículo), <b>E4</b> (aporte de académicos nacionales e "
            f"internacionales) y <b>E6</b> (seguimiento y evaluación del proyecto) se "
            f"evidencian en las <b>fuentes b), d), e) y f)</b> — documentos aparte que aquí no "
            f"se aportan. Fuera del cociente, con su fuente nombrada. Inventarles un ancla "
            f"(buscar «mejora continua» en el formulario para dar E2 por bueno) sería "
            f"exactamente el falso positivo que la norma prohíbe.</li>"
            f"<li><b>El J satura en 1,000</b> para el único proyecto auténtico del corpus. "
            f"Discrimina lo que no es un proyecto de rediseño; no mide la calidad del "
            f"proyecto.</li>"
            f"<li><b>Sólo {autenticos} de los {len(proyectos)} documentos es un proyecto de "
            f"rediseño auténtico.</b> Los otros dos —el modelo educativo institucional y un "
            f"reglamento de examen de fin de carrera— <b>no son proyectos curriculares</b>: "
            f"están en el corpus para comprobar que se rechazan, y su J bajo es un "
            f"<b>ACIERTO del sistema</b> (los descarta por marcadores antes de gastar una sola "
            f"llamada al LLM), no un fallo. Con n = 1 proyecto real <b>no hay estadística que "
            f"declarar</b>: hay una comprobación de que el esquema se satisface.</li></ul>"),
        extra=render_tabla_base(
            proyecto_base, "Modo --base · Jaccard de secciones contra el ejemplar aprobado",
            "A = secciones del ejemplar aprobado; B = las del documento evaluado. Se comparan "
            "<b>todas las secciones detectadas</b> (útiles y descartadas): aquí se mide el "
            "<b>parecido estructural</b> con el ejemplar, no la completitud del indicador. El "
            "base contra sí mismo da 1,000 <b>por construcción</b> — es la referencia, no una "
            "medida de acierto. Lo informativo es lo lejos que quedan los documentos que no "
            "son un proyecto de rediseño.", "secciones del base que le faltan"))

    sec_sil = seccion_indicador(
        "silabo", "Sílabo", "Indicador 4 · plantilla SGC.DI.321",
        cumplen(silabos), len(conp(silabos)), sjp, vacios_tot(silabos),
        inventario_html(inventario_de(PLANTILLA_SILABO)),
        "".join(render_evidencia(e) for e in silabos),
        nota=("<b>Cumplimiento de plantilla</b> = elementos presentes / 39. Sólo 4 sílabos "
              "tienen elementos <b>AUSENTES</b> (secciones que no están): 21495 (4), 21521 (3), "
              "22670 (1), 21413 (1). El <code>silabus_trampa</code> cumple la plantilla al 100% "
              "(todas las secciones presentes) pero sale con muchos <b>vacíos</b> — por eso las "
              "dos medidas van separadas. 2 documentos no usan la plantilla SGC.DI.321."))

    rechazadas_html = "".join(
        f'<div class="ev ev-off"><div class="ev-h"><span class="ev-n">{esc(n)}</span>'
        f'<span class="tag tag-off">rechazada por el filtro es_malla</span></div></div>'
        for n in malla_rechazadas)
    sec_mal = seccion_indicador(
        "malla", "Malla curricular", "Indicador 3 · reconstrucción por coordenadas",
        cumplen(mallas), len(mallas), mjp, vacios_tot(mallas),
        inventario_html([
            ("Por asignatura (4 campos)", CAMPOS_ASIGNATURA),
            ("Estructura del pénsum", [f"{o} PAO" for o in ORDINALES_PAO]),
            ("Identificador / invariante", ["código de asignatura (ancla · sin NRC)",
                                            "HPAO = 48 × créditos (anomalía aparte)"]),
        ]),
        "".join(render_malla_evidencia(m) for m in mallas) + rechazadas_html,
        nota=("Cumplir la plantilla en la malla = las asignaturas presentes y los 8 PAO "
              "detectados; un campo en <code>VACIO</code> cuenta como vacío (aparte). Corpus "
              f"FUENTE ({len(mallas)} mallas + {len(malla_rechazadas)} rechazada por "
              "<code>es_malla</code>); NO las copias con timestamp que el sistema auto-genera."))

    sec_gui = seccion_indicador(
        "guia", "Guía de laboratorio", "Indicador 6 · GUIA DE USO DE LABORATORIO",
        cumplen(guias), len(conp(guias)), gjp, vacios_tot(guias),
        inventario_html(inventario_de(PLANTILLA_GUIA)),
        "".join(render_evidencia(e) for e in guias),
        nota=("Las 10 guías <b>cumplen la plantilla</b> (todos los elementos presentes). Los "
              "vacíos de 4 de ellas (Fecha, Departamento, Laboratorio de la práctica) son "
              "llenado en blanco, no ausencia de plantilla — por eso van en el cálculo aparte."))

    total_ev = (len(conp(silabos)) + len(mallas) + len(conp(guias)) + len(perfiles)
                + len(proyectos))
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cuerpo = f"""
    <div class="wrap">
      <header>
        <span class="eyebrow">Auditor IA · CACES 2024 · Objetivo 3</span>
        <h1>Cumplimiento de plantilla y vacíos por evidencia</h1>
        <p class="lede">Cinco indicadores instrumentados. Dos medidas distintas por cada
          evidencia de formulario (3, 4 y 6); cobertura de evidencia con alcance declarado en
          los indicadores semánticos (1 y 2). Despliega cualquiera para ver la lista completa
          de elementos comparados y su estado.</p>
        <div class="two-metrics">
          <div class="m m-1"><b>1 · Cumplimiento de plantilla (Jaccard)</b>
            ¿están presentes los elementos que exige la plantilla? Sólo un elemento AUSENTE
            resta. J = presentes / total.</div>
          <div class="m m-2"><b>2 · Vacíos (cálculo aparte)</b>
            de los presentes, cuántos están sin contenido. No es incumplir la plantilla, es no
            rellenarla.</div>
          <div class="m m-3"><b>Indicadores 1 y 2 · otro alcance</b>
            no son formularios: los elementos que exigen una fuente externa quedan FUERA del
            cociente, con su fuente nombrada. Su J satura en 1,000.</div>
        </div>
        <div class="legend">
          <span>{DOTS["ok"]} presente y con contenido</span>
          <span>{DOTS["vac"]} presente pero vacío</span>
          <span>{DOTS["aus"]} ausente (no cumple plantilla)</span>
        </div>
      </header>
      {cards}
      {sec_per}
      {sec_pro}
      {sec_sil}
      {sec_mal}
      {sec_gui}
      <footer>{total_ev} evidencias · {fecha} · generado desde los evaluadores deterministas
        (completitud.py · completitud_malla.py · completitud_guia.py · completitud_perfil.py ·
        completitud_proyecto.py) · sin LLM y sin cuota.<br>
        n por indicador: perfil {len(perfiles)} · proyecto {len(proyectos)}
        (sólo {autenticos} es un proyecto de rediseño auténtico) · sílabo
        {len(conp(silabos))} · malla {len(mallas)} · guía {len(conp(guias))}. Muestras
        pequeñas: son comprobaciones deterministas y reproducibles, no una estimación
        estadística con intervalo de confianza.</footer>
    </div>"""

    carpeta = os.path.join(os.path.dirname(AQUI), "data", "resultados_evaluacion")
    os.makedirs(carpeta, exist_ok=True)
    salida = os.path.join(carpeta, "reporte_jaccard.html")
    with open(salida, "w", encoding="utf-8") as f:
        f.write(CSS + cuerpo)
    print(f"\nEscrito: {salida}")
    print(f"Sílabo cumplen plantilla: {cumplen(silabos)}/{len(conp(silabos))} | "
          f"Guía: {cumplen(guias)}/{len(conp(guias))} | Malla: {cumplen(mallas)}/{len(mallas)} | "
          f"Perfil: {cumplen(perfiles)}/{len(perfiles)} | "
          f"Proyecto: {cumplen(proyectos)}/{len(proyectos)}")

    print("\nIndicador 1 · Perfil de egreso (J contra el esquema, cociente sobre "
          f"{len(pp.ELEMENTOS_EVALUABLES)}):")
    for e in perfiles:
        j = "INDEF." if e["j_plantilla"] is None else f"{e['j_plantilla']:.3f}"
        print(f"  {e['nombre'][:52]:52} {j:>7}  ({e['presentes']}/{e['total']} elem, "
              f"{e['chars']} ch, plantilla {'ok' if e['reconocida'] else 'NO'})")
    print("Indicador 2 · Proyecto curricular (J contra el esquema, 10 etiquetas):")
    for e in proyectos:
        j = "INDEF." if e["j_plantilla"] is None else f"{e['j_plantilla']:.3f}"
        print(f"  {e['nombre'][:52]:52} {j:>7}  ({e['presentes']}/{e['total']} etiq, "
              f"{e['chars']} ch, plantilla {'ok' if e['reconocida'] else 'NO'})")

    pdf = exportar_pdf(salida)
    for destino in (salida, pdf):
        if destino and os.path.exists(destino):
            copia = os.path.join(DESCARGAS, "reporte_jaccard_5_indicadores"
                                 + os.path.splitext(destino)[1])
            shutil.copyfile(destino, copia)   # nombre NUEVO: no pisa el reporte_jaccard.html
            print(f"Copiado a: {copia}  ({os.path.getsize(copia):,} bytes)")


if __name__ == "__main__":
    main()
