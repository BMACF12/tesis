"""
Banco de pruebas de la capa determinista: extracción, enrutado, plantilla, pertinencia y
campos sin llenar. NO llama al LLM, así que no consume cuota de Groq.

Lo único que no se puede comprobar aquí es el juicio del checklist, que es lo único que
queda en manos del modelo.

Uso:
    python scripts/banco_pruebas.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extraccion import extraer_documento  # noqa: E402
from services.tareas_ia import (  # noqa: E402
    PALABRAS_ACADEMICAS, _abrir_base, _campos_sin_llenar, _pertinencia,
    _plantilla_valida, _recuperar_norma,
)

IND = r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS"
GUI = r"C:\Users\User\Downloads\GUIAS\GUIAS"
AUD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Auditoria_CACES")

# (etiqueta, patrón glob, indicador esperado, plantilla esperada, pertinencia esperada)
#   pertinencia: True / False / None (indeterminada). El rechazo léxico se anota como
#   indicador None y plantilla False: el documento ni siquiera llega al LLM.
CASOS = [
    ("sílabo Software 21278", rf"{IND}\INDICADOR 4 Syllabus\Silabo_NRC-21278_*.pdf", 4, True, True),
    ("sílabo Software 21306", rf"{IND}\INDICADOR 4 Syllabus\Silabo_NCR-21306_*.pdf", 4, True, True),
    ("sílabo Contabilidad 22639", rf"{IND}\INDICADOR 4 Syllabus\Silabo_NRC-22639_*.pdf", 4, True, False),
    # Limitación conocida: "APLICACIONES MOVILES" consta también en la malla de Software,
    # y el sílabo de la ESPE no declara ningún campo con la carrera. Indistinguible.
    ("sílabo Redes/Telecom 22745", rf"{IND}\INDICADOR 4 Syllabus\Silabo_NRC_22745_*.pdf", 4, True, True),
    ("sílabo Psicología", rf"{IND}\INDICADOR 4 Syllabus\SYLLABUS EN PSICOLOG*.pdf", 4, False, None),
    ("sílabo trampa (vacío)", rf"{IND}\INDICADOR 4 Syllabus\silabus_trampa_*.pdf", 4, True, None),
    ("no-sílabo (receta)", rf"{IND}\INDICADOR 4 Syllabus\sylabus-nosylabus.pdf", 3, False, None),
    ("malla Software", rf"{IND}\INDICADOR 3 Malla curricular\malla isoj*.pdf", 3, True, True),
    ("malla Educación Inicial", rf"{IND}\INDICADOR 3 Malla curricular\MALLA-EDUCACION-INICIAL*.pdf", 3, True, False),
    ("guía 2.3 (completa)", rf"{GUI}\2.3 Guia Laboratorio*.pdf", 6, True, True),
    ("guía 3.3 (campos vacíos)", rf"{GUI}\3.3 Guia Laboratorio*.pdf", 6, True, True),
    ("perfil de egreso Software", os.path.join(AUD, "Indicador_1_Perfil_de_egreso", "PERFILEGRESO_SW*.pdf"), 1, True, True),
    ("factura (no académico)", os.path.join(AUD, "11_Documentos_Rechazados", "Factura*.pdf"), None, False, None),
    ("receta de comida", os.path.join(AUD, "11_Documentos_Rechazados", "Receta*.pdf"), None, False, None),
]


def resolver_ruta(patron):
    import glob
    candidatos = [p for p in glob.glob(patron) if "_Reporte" not in p]
    return sorted(candidatos)[0] if candidatos else None


def main():
    vector_db = _abrir_base()
    fallos = 0

    print(f"{'caso':28}{'ind':>5}{'plant':>7}{'pert':>7}{'vacíos':>9}  detalle")
    print("-" * 108)

    for etiqueta, ruta, ind_esperado, plant_esperada, pert_esperada in CASOS:
        ruta = resolver_ruta(ruta)
        if not ruta:
            print(f"{etiqueta:28}{'':>5}  ARCHIVO NO ENCONTRADO")
            fallos += 1
            continue

        try:
            documento = extraer_documento(ruta)
        except Exception as error:
            print(f"{etiqueta:28}  ERROR DE EXTRACCIÓN: {type(error).__name__}")
            fallos += 1
            continue

        texto, cajas = documento["texto"], documento["cajas"]
        academico = sum(1 for p in PALABRAS_ACADEMICAS if p in texto.lower()) >= 2
        if not academico:
            observado = (None, False, None, [], 0, "rechazo léxico")
        else:
            norma, meta = _recuperar_norma(vector_db, texto)
            plantilla, faltan = _plantilla_valida(texto, meta.get("marcadores", ""))
            if not plantilla:
                # El pipeline corta aquí: no se evalúa pertinencia ni campos.
                observado = (meta.get("indicador"), False, None, [], 0, f"faltan {faltan}")
            else:
                pertenece, motivo = _pertinencia(texto, cajas)
                vacios, localizados = _campos_sin_llenar(cajas, meta.get("campos", ""))
                observado = (meta.get("indicador"), True, pertenece, vacios, localizados, motivo[:44])

        ind, plantilla, pertenece, vacios, localizados, detalle = observado
        ok = (ind == ind_esperado and plantilla == plant_esperada and pertenece == pert_esperada)
        fallos += 0 if ok else 1
        marca = " " if ok else "!"
        campos = f"{len(vacios)}/{localizados}" if localizados else "-"
        print(f"{marca}{etiqueta:27}{str(ind):>5}{str(plantilla):>7}{str(pertenece):>7}{campos:>9}  {detalle}")
        if vacios:
            print(f"{'':28}{'':>5}{'':>7}{'':>7}{'':>9}  sin llenar: {', '.join(vacios)}")

    print("-" * 108)
    print(f"{len(CASOS) - fallos}/{len(CASOS)} casos con enrutado, plantilla y pertinencia correctos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
