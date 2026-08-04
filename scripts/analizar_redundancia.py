# -*- coding: utf-8 -*-
"""
Script para analizar redundancia, frases repetitivas y longitud de secciones en la tesis.
"""
import re
from pathlib import Path
from collections import Counter

FILE_PATH = Path("docs/conocimiento/tesis-escritura/texto/00_manuscrito/TESIS V1.0 FLORES_MORALES oficial (2).txt")

def segmentar_secciones(texto):
    lineas = texto.splitlines()
    secciones = []
    seccion_actual = {"titulo": "Preliminares", "linea_inicio": 1, "texto": []}
    
    for i, linea in enumerate(lineas, 1):
        if linea.strip().startswith("#"):
            if seccion_actual["texto"]:
                seccion_actual["texto"] = "\n".join(seccion_actual["texto"])
                secciones.append(seccion_actual)
            seccion_actual = {"titulo": linea.strip(), "linea_inicio": i, "texto": []}
        else:
            seccion_actual["texto"].append(linea)
            
    if seccion_actual["texto"]:
        seccion_actual["texto"] = "\n".join(seccion_actual["texto"])
        secciones.append(seccion_actual)
        
    return secciones

def buscar_frases_repetidas(texto):
    # Frases de relleno académico común
    patrones_relleno = {
        "con el propósito de": r"\bcon el propósito de\b",
        "con el fin de": r"\bcon el fin de\b",
        "es indispensable mencionar": r"\bes indispensable mencionar\b",
        "cabe destacar": r"\bcabe destacar\b",
        "cabe recalcar": r"\bcabe recalcar\b",
        "es importante señalar": r"\bes importante señalar\b",
        "se puede evidenciar": r"\bse puede evidenciar\b",
        "en el contexto de": r"\ben el contexto de\b",
        "debido a que": r"\bdebido a que\b",
        "en la práctica": r"\ben la práctica\b",
        "de esta manera": r"\bde esta manera\b",
        "de igual manera": r"\bde igual manera\b",
        "por lo cual": r"\bpor lo cual\b",
        "por esta razón": r"\bpor esta razón\b",
        "en este sentido": r"\ben este sentido\b",
        "a través de": r"\ba través de\b",
        "con respecto a": r"\bcon respecto a\b",
        "de forma autónoma": r"\bde forma autónoma\b",
        "en este apartado": r"\ben este apartado\b",
        "en la actualidad": r"\ben la actualidad\b",
    }
    
    resultados = {}
    for nombre, patron in patrones_relleno.items():
        coincidencias = len(re.findall(patron, texto, re.IGNORECASE))
        if coincidencias > 0:
            resultados[nombre] = coincidencias
    return resultados

def buscar_parrafos_duplicados_o_similares(secciones):
    parrafos_todos = []
    for sec in secciones:
        parrafos = [p.strip() for p in sec["texto"].split("\n\n") if len(p.strip()) > 30]
        for p in parrafos:
            parrafos_todos.append((sec["titulo"], sec["linea_inicio"], p))
            
    # Comparar similitud aproximada de n-gramas o duplicaciones textuales
    duplicados = []
    for i in range(len(parrafos_todos)):
        for j in range(i + 1, len(parrafos_todos)):
            t1, l1, p1 = parrafos_todos[i]
            t2, l2, p2 = parrafos_todos[j]
            
            # Si son idénticos o casi idénticos en longitud y comparten muchas palabras
            w1 = set(p1.lower().split())
            w2 = set(p2.lower().split())
            interseccion = w1.intersection(w2)
            union = w1.union(w2)
            jaccard = len(interseccion) / len(union) if union else 0
            
            if jaccard > 0.6:  # Alta similitud semántica/textual
                duplicados.append({
                    "sec1": t1, "linea1": l1,
                    "sec2": t2, "linea2": l2,
                    "jaccard": jaccard,
                    "p1": p1[:150] + "...",
                    "p2": p2[:150] + "..."
                })
    return duplicados

def main():
    if not FILE_PATH.exists():
        print(f"Error: {FILE_PATH} no existe.")
        return
        
    texto = FILE_PATH.read_text(encoding="utf-8")
    secciones = segmentar_secciones(texto)
    
    out_lines = []
    out_lines.append("# REPORTE DE ANALISIS DE REDUNDANCIA Y ESTRUCTURA\n")
    out_lines.append(f"Archivo: {FILE_PATH.name}")
    out_lines.append(f"Total caracteres: {len(texto)}")
    out_lines.append(f"Total palabras aprox: {len(texto.split())}")
    out_lines.append(f"Total secciones detectadas: {len(secciones)}\n")
    
    out_lines.append("## 1. Conteo de Palabras por Secciones Mayores")
    for sec in secciones:
        palabras = len(sec["texto"].split())
        if palabras > 100:
            out_lines.append(f"- **{sec['titulo']}** (Línea {sec['linea_inicio']}): {palabras} palabras")
            
    out_lines.append("\n## 2. Uso excesivo de conectores y frases de relleno (Frecuencia)")
    frases_rep = buscar_frases_repetidas(texto)
    for frase, count in sorted(frases_rep.items(), key=lambda x: x[1], reverse=True):
        out_lines.append(f"- `{frase}`: {count} veces")
        
    out_lines.append("\n## 3. Párrafos duplicados o altamente similares (Similitud Jaccard > 0.6)")
    duplicados = buscar_parrafos_duplicados_o_similares(secciones)
    if not duplicados:
        out_lines.append("No se encontraron párrafos con coincidencia exacta mayor a 0.6.")
    else:
        for dup in duplicados:
            out_lines.append(f"- **Coincidencia ({dup['jaccard']:.2f})** entre:")
            out_lines.append(f"  - *{dup['sec1']}* (cerca de Línea {dup['linea1']}): \"{dup['p1']}\"")
            out_lines.append(f"  - *{dup['sec2']}* (cerca de Línea {dup['linea2']}): \"{dup['p2']}\"")
            out_lines.append("")
            
    output_path = Path("docs/conocimiento/reporte_redundancia.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Reporte escrito en: {output_path}")

if __name__ == "__main__":
    main()
