# -*- coding: utf-8 -*-
"""Por cada sílabo, separa lo que FALTA DE LA PLANTILLA (AUSENTE = sección/tabla/campo que
ni siquiera aparece) de los campos meramente VACÍOS (presentes pero en blanco)."""
import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

import completitud as sil
_base = sil._abrir_base()
sil._abrir_base = lambda: _base
from plantilla_silabo import PLANTILLA_SILABO

TIPO = {n: t for n, _s, t, _a in PLANTILLA_SILABO}

filas = []
for ruta in sorted(glob.glob(sil.SILABOS)):
    if "_Reporte" in ruta:
        continue
    nombre = os.path.basename(ruta)
    _meta, estado, _f = sil.evaluar(ruta)
    if estado is None:
        continue
    ausentes = [n for n, e in estado.items() if e == "AUSENTE"]
    vacias = [n for n, e in estado.items() if e == "VACÍA"]   # sección presente sin contenido
    vacios = [n for n, e in estado.items() if e == "VACÍO"]   # campo en blanco
    if ausentes or vacias:
        filas.append((nombre[:52], ausentes, vacias, vacios))

filas.sort(key=lambda f: -(len(f[1]) + len(f[2])))
print(f"{'SÍLABO':54} AUSENTE(no cumple plantilla) | VACÍA(sección sin contenido)")
print("=" * 110)
for nombre, ausentes, vacias, vacios in filas:
    print(f"\n■ {nombre}")
    if ausentes:
        print(f"   AUSENTES ({len(ausentes)}): {', '.join(f'{n} [{TIPO[n]}]' for n in ausentes)}")
    if vacias:
        print(f"   VACÍAS   ({len(vacias)}): {', '.join(vacias)}")
    if vacios:
        print(f"   (vacíos de campo, no plantilla): {', '.join(vacios)}")
