# -*- coding: utf-8 -*-
"""
Informe HTML autocontenido con la evaluación de las evidencias de los tres indicadores
instrumentados (4 sílabo, 6 guía, 3 malla). Separa DOS medidas distintas por evidencia:

  1. CUMPLIMIENTO DE PLANTILLA (Jaccard principal): ¿están presentes los elementos que exige
     la plantilla? Sólo un elemento AUSENTE (que ni siquiera aparece) cuenta como falta.
     J_plantilla = |presentes| / |total|.
  2. VACÍOS (cálculo aparte): de los elementos PRESENTES, cuántos están sin contenido
     (sección vacía o campo en blanco). No es incumplir la plantilla, es no rellenarla.

Reutiliza las funciones `evaluar` de los tres evaluadores (datos en vivo). Salida:
    backend/data/resultados_evaluacion/reporte_jaccard.html
El sílabo abre ChromaDB (se cachea una sola vez).
"""
import glob
import html
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

# Los tres evaluadores re-envuelven sys.stdout al importarse; se mantiene vivo cada wrapper
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
from plantilla_silabo import PLANTILLA_SILABO  # noqa: E402
from plantilla_guia import PLANTILLA_GUIA  # noqa: E402
from plantilla_malla import ORDINALES_PAO, CAMPOS_ASIGNATURA  # noqa: E402

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


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def esc(t):
    return html.escape(str(t))


def chip_jaccard(j, etiqueta="plantilla"):
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
                      total_vacios, inventario, cuerpo, nota=""):
    stat = (f'<div class="stat"><span class="stat-num">{jp_medio:.3f}</span>'
            f'<span class="stat-lbl">cumplimiento de plantilla</span></div>'
            f'<div class="stat"><span class="stat-num">{cumplen}<span class="stat-of">/{total_ev}</span></span>'
            f'<span class="stat-lbl">cumplen la plantilla</span></div>'
            f'<div class="stat"><span class="stat-num stat-vac">{total_vacios}</span>'
            f'<span class="stat-lbl">elementos vacíos (aparte)</span></div>')
    nota_html = f'<p class="nota">{nota}</p>' if nota else ""
    return (
        f'<section class="ind" id="{idc}">'
        f'<div class="ind-head"><div class="ind-title">'
        f'<span class="eyebrow">{esc(subtitulo)}</span><h2>{esc(titulo)}</h2></div>'
        f'<div class="ind-stats">{stat}</div></div>{nota_html}'
        f'<details class="inv" open><summary>Inventario · el universo que se compara</summary>'
        f'<div class="inv-body">{inventario}</div></details>'
        f'<div class="evs">{cuerpo}</div></section>')


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
.m-1 b{color:var(--accent)} .m-2 b{color:var(--vac)}
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
</style>
"""


def barrow(evs):
    seg = []
    for ev in evs:
        if ev.get("sin_plantilla"):
            seg.append('<i style="background:var(--vac-soft)"></i>')
        else:
            j = ev["j_plantilla"]
            col = "var(--ok)" if j >= 0.999 else ("var(--vac)" if j >= 0.85 else "var(--bad)")
            seg.append(f'<i style="background:{col}"></i>')
    return "".join(seg)


def main():
    print("Recolectando sílabos…")
    silabos = datos_silabo()
    print("Recolectando guías…")
    guias = datos_guia()
    print("Recolectando mallas…")
    mallas, malla_rechazadas = datos_malla()

    def conp(evs):
        return [e for e in evs if not e.get("sin_plantilla")]

    def jp_medio(evs):
        v = [e["j_plantilla"] for e in conp(evs)]
        return sum(v) / len(v) if v else 1.0

    def cumplen(evs):  # sin ningún AUSENTE
        return sum(1 for e in conp(evs) if e["ausentes"] == 0)

    def vacios_tot(evs):
        return sum(e["vacios"] for e in conp(evs))

    sjp, gjp = jp_medio(silabos), jp_medio(guias)
    mjp = jp_medio(mallas)

    cards = f"""
    <div class="cards">
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
    </div>"""

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

    total_ev = len(conp(silabos)) + len(mallas) + len(conp(guias))
    cuerpo = f"""
    <div class="wrap">
      <header>
        <span class="eyebrow">Auditor IA · CACES 2024 · Objetivo 3</span>
        <h1>Cumplimiento de plantilla y vacíos por evidencia</h1>
        <p class="lede">Dos medidas distintas por cada evidencia. Despliega cualquiera para ver
          la lista completa de elementos comparados y su estado.</p>
        <div class="two-metrics">
          <div class="m m-1"><b>1 · Cumplimiento de plantilla (Jaccard)</b>
            ¿están presentes los elementos que exige la plantilla? Sólo un elemento AUSENTE
            resta. J = presentes / total.</div>
          <div class="m m-2"><b>2 · Vacíos (cálculo aparte)</b>
            de los presentes, cuántos están sin contenido. No es incumplir la plantilla, es no
            rellenarla.</div>
        </div>
        <div class="legend">
          <span>{DOTS["ok"]} presente y con contenido</span>
          <span>{DOTS["vac"]} presente pero vacío</span>
          <span>{DOTS["aus"]} ausente (no cumple plantilla)</span>
        </div>
      </header>
      {cards}
      {sec_sil}
      {sec_mal}
      {sec_gui}
      <footer>{total_ev} evidencias con plantilla · generado desde los evaluadores deterministas
        (completitud.py · completitud_malla.py · completitud_guia.py) · sin LLM.</footer>
    </div>"""

    salida = os.path.join(os.path.dirname(AQUI), "data", "resultados_evaluacion",
                          "reporte_jaccard.html")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(CSS + cuerpo)
    print(f"\nEscrito: {salida}")
    print(f"Sílabo cumplen plantilla: {cumplen(silabos)}/{len(conp(silabos))} | "
          f"Guía: {cumplen(guias)}/{len(conp(guias))} | Malla: {cumplen(mallas)}/{len(mallas)}")


if __name__ == "__main__":
    main()
