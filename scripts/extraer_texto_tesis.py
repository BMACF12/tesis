"""Extrae a texto plano el material de `Documentos para la tesis/`.

Sirve al agente `tesis-escritura`: el avance de la tesis viene en .docx (que las
herramientas de lectura no abren) y la bibliografía en PDF (que sí se abren, pero
uno a uno). Este script vuelca todo a .txt en un cache para poder hacer Grep sobre
el corpus completo: buscar una cita, un concepto o comprobar si algo ya está escrito.

Sin dependencias nuevas: .docx se lee como ZIP + XML, .pdf con pdfminer.six (ya
instalado), .htm/.html con BeautifulSoup (ya instalado).

Uso:
    venv/Scripts/python.exe scripts/extraer_texto_tesis.py            # todo lo que falte
    venv/Scripts/python.exe scripts/extraer_texto_tesis.py --forzar   # re-extraer todo
    venv/Scripts/python.exe scripts/extraer_texto_tesis.py --solo docx
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "Documentos para la tesis"
CACHE = RAIZ / "docs" / "conocimiento" / "tesis-escritura" / "texto"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _texto_parrafo(p: ElementTree.Element) -> str:
    """Texto de un <w:p>, respetando tabuladores y saltos de línea."""
    partes: list[str] = []
    for nodo in p.iter():
        if nodo.tag == f"{W}t":
            partes.append(nodo.text or "")
        elif nodo.tag == f"{W}tab":
            partes.append("\t")
        elif nodo.tag in (f"{W}br", f"{W}cr"):
            partes.append("\n")
    return "".join(partes)


def _estilo(p: ElementTree.Element) -> str:
    nodo = p.find(f"{W}pPr/{W}pStyle")
    return (nodo.get(f"{W}val") or "") if nodo is not None else ""


def extraer_docx(ruta: Path) -> str:
    """docx -> markdown ligero. Los Heading N se marcan con '#' para ver la estructura."""
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml")
    cuerpo = ElementTree.fromstring(xml).find(f"{W}body")
    if cuerpo is None:
        return ""

    lineas: list[str] = []
    for hijo in cuerpo:
        if hijo.tag == f"{W}p":
            txt = _texto_parrafo(hijo).strip()
            if not txt:
                continue
            m = re.match(r"(?:Heading|Ttulo|Título)(\d)", _estilo(hijo))
            lineas.append(f"{'#' * min(int(m.group(1)), 6)} {txt}" if m else txt)
        elif hijo.tag == f"{W}tbl":
            # Las tablas se aplanan a filas separadas por ' | ' (suficiente para buscar).
            lineas.append("")
            for fila in hijo.findall(f"{W}tr"):
                celdas = [
                    " ".join(_texto_parrafo(p).strip() for p in celda.findall(f"{W}p")).strip()
                    for celda in fila.findall(f"{W}tc")
                ]
                lineas.append("| " + " | ".join(celdas) + " |")
            lineas.append("")
    return "\n\n".join(lineas)


def extraer_pdf(ruta: Path) -> str:
    from pdfminer.high_level import extract_text

    return extract_text(str(ruta)) or ""


def extraer_html(ruta: Path) -> str:
    from bs4 import BeautifulSoup

    sopa = BeautifulSoup(ruta.read_bytes(), "html.parser")
    for basura in sopa(["script", "style"]):
        basura.decompose()
    return re.sub(r"\n{3,}", "\n\n", sopa.get_text("\n"))


EXTRACTORES = {".docx": extraer_docx, ".pdf": extraer_pdf, ".htm": extraer_html, ".html": extraer_html}


def destino(ruta: Path) -> Path:
    """Espeja la ruta relativa dentro del cache, con extensión .txt."""
    rel = ruta.relative_to(ORIGEN)
    return CACHE / rel.parent / (rel.stem + ".txt")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--forzar", action="store_true", help="re-extraer aunque el .txt ya exista")
    ap.add_argument("--solo", help="filtrar por extensión (docx, pdf, htm) o por subcadena del nombre")
    args = ap.parse_args()

    if not ORIGEN.is_dir():
        print(f"ERROR: no existe {ORIGEN}", file=sys.stderr)
        return 1

    fuentes = sorted(r for r in ORIGEN.rglob("*") if r.suffix.lower() in EXTRACTORES)
    if args.solo:
        f = args.solo.lower().lstrip(".")
        fuentes = [r for r in fuentes if r.suffix.lower().lstrip(".") == f or f in r.name.lower()]

    for ruta in fuentes:
        sal = destino(ruta)
        if sal.exists() and not args.forzar and sal.stat().st_mtime >= ruta.stat().st_mtime:
            print(f"= {sal.relative_to(CACHE)}")
            continue
        try:
            texto = EXTRACTORES[ruta.suffix.lower()](ruta)
        except Exception as e:  # un PDF corrupto no debe tumbar el lote
            print(f"! {ruta.name}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        sal.parent.mkdir(parents=True, exist_ok=True)
        sal.write_text(texto, encoding="utf-8")
        print(f"+ {sal.relative_to(CACHE)}  ({len(texto):,} car.)")

    print(f"\nCache: {CACHE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
