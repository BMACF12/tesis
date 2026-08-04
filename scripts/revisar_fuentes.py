"""Inventario y control de duplicados de las fuentes bibliográficas.

Responde de forma determinista a tres preguntas que el agente `curador-fuentes` no
debe contestar a ojo:

  1. ¿Qué hay en `Documentos para la tesis/`? (hash, DOI, año, tipo, nº de referencia)
  2. ¿Se repite algo? (duplicado exacto por MD5, o mismo trabajo por DOI/título)
  3. ¿Está citado en el manuscrito, y qué números de referencia quedan libres?

Depende del cache de texto que genera `extraer_texto_tesis.py`; si falta, avisa.

Uso:
    venv/Scripts/python.exe scripts/revisar_fuentes.py            # informe completo
    venv/Scripts/python.exe scripts/revisar_fuentes.py --duplicados   # sólo repeticiones
    venv/Scripts/python.exe scripts/revisar_fuentes.py --json     # para procesar
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# La consola de Windows es cp1252 y revienta con los acentos y los símbolos del informe.
for flujo in (sys.stdout, sys.stderr):
    flujo.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "Documentos para la tesis"
CACHE = RAIZ / "docs" / "conocimiento" / "tesis-escritura" / "texto"


def ruta_manuscrito() -> Path | None:
    """El .docx vive en 00_manuscrito/ y puede cambiar de nombre al subir de versión."""
    return next(iter(sorted(CACHE.rglob("TESIS*.txt"))), None)

EXTENSIONES = {".pdf", ".htm", ".html", ".docx"}
RE_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.I)
RE_NUM = re.compile(r"\[(\d{1,3})\]")  # la etiqueta de estante va al final del nombre
RE_ANIO = re.compile(r"\b(19[89]\d|20[0-3]\d)\b")

# Un texto extraído por debajo de esto es un escaneo sin capa de texto o un PDF protegido.
MINIMO_LEGIBLE = 2000


def md5(ruta: Path) -> str:
    h = hashlib.md5()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def ruta_cache(ruta: Path) -> Path:
    rel = ruta.relative_to(ORIGEN)
    return CACHE / rel.parent / (rel.stem + ".txt")


def limpiar_doi(doi: str) -> str:
    """Los DOI extraídos de un PDF arrastran puntuación de la maquetación."""
    return doi.rstrip(".,;)»").lower()


def titulo_probable(texto: str) -> str:
    """Primera línea larga y sin pinta de cabecera de revista."""
    for linea in texto.splitlines():
        linea = linea.strip()
        if len(linea) < 25 or len(linea) > 250:
            continue
        if re.search(r"^\s*(https?://|doi:|www\.|\d+\s*$)", linea, re.I):
            continue
        return linea
    return "(no determinado)"


def inventariar(incluir_descartadas: bool = False) -> list[dict]:
    fuentes = []
    todas = sorted(r for r in ORIGEN.rglob("*") if r.suffix.lower() in EXTENSIONES)
    # Lo ya descartado volvería a salir como duplicado en cada pasada; su registro
    # está en 03_descartadas/MOTIVOS.md.
    if not incluir_descartadas:
        todas = [r for r in todas if "03_descartadas" not in r.parts]
    for ruta in todas:
        cache = ruta_cache(ruta)
        texto = cache.read_text(encoding="utf-8", errors="ignore") if cache.exists() else ""
        dois = sorted({limpiar_doi(d) for d in RE_DOI.findall(texto[:8000])})
        etiquetas = RE_NUM.findall(ruta.stem)
        m = etiquetas[-1] if etiquetas else None
        cabecera = texto[:4000]
        fuentes.append(
            {
                "ruta": str(ruta.relative_to(ORIGEN)).replace("\\", "/"),
                "carpeta": str(ruta.parent.relative_to(ORIGEN)).replace("\\", "/") or ".",
                "num_ref": int(m) if m else None,
                "md5": md5(ruta),
                "doi": dois[0] if dois else None,
                "dois_citados": dois[1:5],
                "anios": sorted(set(RE_ANIO.findall(cabecera)))[-3:],
                "caracteres": len(texto),
                "legible": len(texto) >= MINIMO_LEGIBLE,
                "sin_cache": not cache.exists(),
                "titulo": titulo_probable(texto) if texto else "(sin texto extraído)",
            }
        )
    return fuentes


def agrupar_duplicados(fuentes: list[dict]) -> dict[str, list[list[dict]]]:
    """Duplicados exactos (mismo MD5) y del mismo trabajo (mismo DOI, distinto archivo)."""
    por_md5, por_doi = defaultdict(list), defaultdict(list)
    for f in fuentes:
        por_md5[f["md5"]].append(f)
        if f["doi"]:
            por_doi[f["doi"]].append(f)

    exactos = [g for g in por_md5.values() if len(g) > 1]
    ya_visto = {f["md5"] for g in exactos for f in g}

    # Mismo trabajo pero archivos distintos: es el caso interesante (PDF vs HTML, v1 vs v2).
    mismo_trabajo = [g for g in por_doi.values() if len({f["md5"] for f in g}) > 1]

    # Respaldo para los que no tienen DOI legible: mismo nombre de archivo sin el prefijo [nn].
    por_nombre = defaultdict(list)
    for f in fuentes:
        base = re.sub(r"\s*\[\d{1,3}\]\s*$", "", Path(f["ruta"]).stem).strip().lower()
        por_nombre[base].append(f)
    vistos_doi = {f["md5"] for g in mismo_trabajo for f in g}
    por_nombre_dup = [
        g
        for g in por_nombre.values()
        if len({f["md5"] for f in g}) > 1 and not {f["md5"] for f in g} & (ya_visto | vistos_doi)
    ]

    return {"exactos": exactos, "mismo_trabajo": mismo_trabajo + por_nombre_dup}


def citas_del_manuscrito() -> set[int]:
    tesis = ruta_manuscrito()
    if tesis is None:
        return set()
    return {int(n) for n in re.findall(r"\[(\d{1,3})\]", tesis.read_text(encoding="utf-8", errors="ignore"))}


def informe(fuentes: list[dict], dups: dict, solo_dups: bool) -> None:
    citadas = citas_del_manuscrito()

    if not solo_dups:
        print(f"INVENTARIO — {len(fuentes)} archivos en 'Documentos para la tesis/'\n")
        for f in sorted(fuentes, key=lambda x: (x["num_ref"] is None, x["num_ref"] or 0, x["ruta"])):
            etiqueta = f"[{f['num_ref']}]" if f["num_ref"] else "[ - ]"
            banderas = []
            if not f["legible"]:
                banderas.append("ILEGIBLE (escaneo/protegido)")
            if f["sin_cache"]:
                banderas.append("SIN CACHE (corre extraer_texto_tesis.py)")
            if f["num_ref"] and f["num_ref"] not in citadas:
                banderas.append("NO CITADO en el manuscrito")
            print(f"{etiqueta:>6}  {f['ruta']}")
            print(f"         {f['titulo'][:110]}")
            print(
                f"         doi={f['doi'] or '—'}  años={','.join(f['anios']) or '—'}  {f['caracteres']:,} car."
                + (f"  ⚠ {' · '.join(banderas)}" if banderas else "")
            )
            print()

    print("=" * 78)
    print("DUPLICADOS\n")
    if not dups["exactos"] and not dups["mismo_trabajo"]:
        print("  Ninguno.\n")
    for grupo in dups["exactos"]:
        print(f"  IDÉNTICOS (mismo MD5 {grupo[0]['md5'][:8]}):")
        for f in grupo:
            print(f"    - {f['ruta']}")
        print()
    for grupo in dups["mismo_trabajo"]:
        clave = f"doi {grupo[0]['doi']}" if grupo[0]["doi"] else "mismo nombre, sin DOI legible"
        print(f"  MISMO TRABAJO ({clave}), archivos distintos:")
        for f in grupo:
            print(f"    - {f['ruta']}  ({f['caracteres']:,} car.)")
        mejor = max(grupo, key=lambda x: x["caracteres"])
        print(f"    -> conserva el más completo: {mejor['ruta']}")
        print()

    print("=" * 78)
    print("NUMERACIÓN\n")
    asignados = sorted(f["num_ref"] for f in fuentes if f["num_ref"])
    repetidos = sorted({n for n in asignados if asignados.count(n) > 1})
    print(f"  Números en los archivos : {asignados or '—'}")
    if repetidos:
        print(f"  ⚠ Número REPETIDO en dos archivos distintos: {repetidos}")
    print(f"  Citados en el manuscrito: {sorted(citadas) or '—'}")
    huerfanas = sorted(citadas - set(asignados))
    print(f"  Citados sin archivo aquí : {huerfanas or '—'}")

    # Un salto en la secuencia delata una cita mal tecleada, no una referencia real.
    todos = sorted(citadas | set(asignados))
    huecos = [n for n in range(1, max(todos, default=0)) if n not in todos]
    if huecos:
        print(f"  ⚠ HUECOS en la secuencia : {huecos[:1]}..{huecos[-1:]} ({len(huecos)} números)")
        print("    Un número muy por encima del resto suele ser una cita mal tecleada; revísalo")
        print("    antes de dar por bueno el 'siguiente libre'.")
        contiguo = next((n for n in range(1, max(todos) + 2) if n not in todos), 1)
        print(f"  Siguiente libre contiguo : [{contiguo}]")
    else:
        print(f"  Siguiente número libre   : [{max(todos, default=0) + 1}]")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--duplicados", action="store_true", help="omitir el inventario detallado")
    ap.add_argument("--json", action="store_true", help="volcar el inventario en JSON")
    ap.add_argument("--con-descartadas", action="store_true", help="incluir también 03_descartadas/")
    args = ap.parse_args()

    if not ORIGEN.is_dir():
        print(f"ERROR: no existe {ORIGEN}", file=sys.stderr)
        return 1
    if not CACHE.is_dir():
        print("AVISO: no hay cache de texto. Corre antes scripts/extraer_texto_tesis.py\n", file=sys.stderr)

    fuentes = inventariar(args.con_descartadas)
    dups = agrupar_duplicados(fuentes)
    if args.json:
        print(json.dumps({"fuentes": fuentes, "duplicados": dups}, ensure_ascii=False, indent=2))
    else:
        informe(fuentes, dups, args.duplicados)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
