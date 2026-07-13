"""
Evaluación de la Compuerta 5 (detección de campos sin llenar) con el índice de Jaccard.

Es la única compuerta cuya salida es un CONJUNTO de tamaño variable —el subconjunto de
campos que el documento deja en blanco—, y por tanto la única donde Jaccard tiene sentido.
Las demás devuelven una etiqueta única, y allí Jaccard sólo puede valer 0 o 1: degenera en
la exactitud sin aportar nada.

TRES MODOS DE USO
-----------------

1) VER  — qué lee el sistema en cada campo de un documento. Con esto compruebas contra el
   PDF si acierta. No necesitas etiquetar nada.

       python scripts/evaluar_campos.py ver 21278

2) UNO  — evalúa un documento con Jaccard. Tú le dices qué campos están vacíos DE VERDAD
   (los que leíste en el PDF) y él calcula el índice y lo interpreta.

       python scripts/evaluar_campos.py uno 3.3 --vacios "FECHA,DEPARTAMENTO"
       python scripts/evaluar_campos.py uno 21278 --vacios ""     # ninguno vacío

3) TODO — evalúa el corpus entero contra `data/verdad_campos.csv`, que generas con
   `--plantilla` y corriges a mano.

       python scripts/evaluar_campos.py --plantilla
       python scripts/evaluar_campos.py todo
"""
import csv
import glob
import io
import os
import sys

# La consola de Windows usa cp1252 y aborta ante las tildes de los nombres de fichero.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extraccion import extraer_documento, resolver_campos  # noqa: E402
from services.tareas_ia import (  # noqa: E402
    _abrir_base, _campos_sin_llenar, _plantilla_valida, _recuperar_norma,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERDAD = os.path.join(BASE_DIR, "data", "verdad_campos.csv")

# Sólo los indicadores 4 (sílabo) y 6 (guía) declaran campos etiquetados.
CORPUS = [
    r"C:\Users\User\Downloads\INDICADORES PRUEBAS\INDICADORES PRUEBAS\INDICADOR 4 Syllabus\*.pdf",
    r"C:\Users\User\Downloads\GUIAS\GUIAS\*.pdf",
    os.path.join(BASE_DIR, "Auditoria_CACES", "**", "*.pdf"),
]


def documentos():
    vistos = set()
    for patron in CORPUS:
        for ruta in sorted(glob.glob(patron, recursive=True)):
            nombre = os.path.basename(ruta)
            if "_Reporte" in nombre or nombre in vistos:
                continue
            vistos.add(nombre)
            yield ruta


def buscar(texto: str):
    """
    Localiza un documento por un fragmento de su nombre (p. ej. '21278' o '3.3 Guia').

    El corpus contiene copias del mismo PDF en varias carpetas (el archivo original y las
    que el orquestador dejó en Auditoria_CACES). Si todas tienen el mismo contenido, se
    toma la primera: son el mismo documento.
    """
    coincidencias = [r for r in documentos() if texto.lower() in os.path.basename(r).lower()]
    if not coincidencias:
        print(f"No se encontró ningún documento que contenga '{texto}'.")
        print("\nDocumentos disponibles:")
        for r in list(documentos())[:40]:
            print("   ", os.path.basename(r)[:72])
        raise SystemExit(1)

    if len(coincidencias) > 1:
        tamanos = {os.path.getsize(r) for r in coincidencias}
        if len(tamanos) > 1:
            print(f"'{texto}' coincide con varios documentos DISTINTOS. Sé más específico:")
            for r in coincidencias[:12]:
                print(f"    {os.path.basename(r)[:64]}  ({os.path.getsize(r)} bytes)")
            raise SystemExit(1)
        print(f"(aviso: '{texto}' aparece en {len(coincidencias)} rutas con el mismo "
              "contenido; se usa la primera)")
    return coincidencias[0]


def analizar(ruta):
    """Devuelve (declarados, valores leídos, conjunto de vacíos según el sistema)."""
    documento = extraer_documento(ruta)
    _norma, meta = _recuperar_norma(_abrir_base(), documento["texto"])
    valida, faltan = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
    if not valida:
        print(f"El documento no usa la plantilla oficial del indicador {meta.get('indicador')}.")
        print(f"Faltan los marcadores: {'; '.join(faltan)}")
        print("La Compuerta 5 no llega a ejecutarse sobre él.")
        raise SystemExit(1)
    if not meta.get("campos", "").strip():
        print(f"El indicador {meta.get('indicador')} ({meta.get('nombre')}) no declara campos "
              "etiquetados: no hay nada que evaluar en esta compuerta.")
        raise SystemExit(1)

    declarados = [c.strip() for c in meta["campos"].split(";") if c.strip()]
    valores = resolver_campos(documento["cajas"], declarados)
    vacios, _localizados = _campos_sin_llenar(documento["cajas"], meta["campos"])
    return meta, declarados, valores, set(vacios)


# ---------------------------------------------------------------------------
# Modo VER
# ---------------------------------------------------------------------------
def modo_ver(texto):
    ruta = buscar(texto)
    meta, declarados, valores, vacios = analizar(ruta)

    print("=" * 84)
    print(f"QUÉ LEE EL SISTEMA EN CADA CAMPO")
    print("=" * 84)
    print(f"Documento : {os.path.basename(ruta)[:70]}")
    print(f"Indicador : {meta['indicador']} — {meta['nombre']}")
    print()
    print(f"{'#':>3}  {'campo':40} {'valor leído del PDF':34} veredicto")
    print("-" * 84)
    for i, campo in enumerate(declarados, 1):
        valor = valores.get(campo)
        leido = str(valor)[:32] if valor else ""
        estado = "VACÍO" if campo in vacios else "lleno"
        print(f"{i:>3}  {campo[:40]:40} {leido:34} {estado}")
    print("-" * 84)
    print()
    print(f"El sistema declara VACÍOS estos {len(vacios)} campos: "
          f"{', '.join(sorted(vacios)) if vacios else '(ninguno)'}")
    print()
    print("AHORA ABRE EL PDF Y COMPRUÉBALO. Si el sistema acierta en todos, su lista de")
    print("campos vacíos es correcta. Si no, apunta la lista CORRECTA y ejecuta:")
    lista = ",".join(sorted(vacios))
    print(f'   python scripts/evaluar_campos.py uno {texto} --vacios "{lista}"')


# ---------------------------------------------------------------------------
# Modo UNO: Jaccard sobre un documento, explicado
# ---------------------------------------------------------------------------
def modo_uno(texto, vacios_reales):
    ruta = buscar(texto)
    meta, declarados, valores, prediccion = analizar(ruta)

    # Se admiten nombres abreviados: basta con que sean inequívocos.
    verdad = set()
    for pedido in vacios_reales:
        candidatos = [c for c in declarados if pedido.lower() in c.lower()]
        if len(candidatos) == 1:
            verdad.add(candidatos[0])
        elif not candidatos:
            print(f"Aviso: '{pedido}' no es un campo de este indicador. Se ignora.")
        else:
            print(f"Aviso: '{pedido}' es ambiguo ({candidatos}). Escríbelo completo.")
            raise SystemExit(1)

    interseccion = verdad & prediccion
    union = verdad | prediccion
    falsos_positivos = prediccion - verdad
    falsos_negativos = verdad - prediccion
    aciertos_llenos = len(declarados) - len(union)

    print("=" * 84)
    print("COMPUERTA 5 — ÍNDICE DE JACCARD SOBRE UN DOCUMENTO")
    print("=" * 84)
    print(f"Documento : {os.path.basename(ruta)[:70]}")
    print(f"Indicador : {meta['indicador']} — {meta['nombre']}   ({len(declarados)} campos)")
    print()
    print("LOS DOS CONJUNTOS QUE SE COMPARAN")
    print(f"  A (auditor: lo que TÚ leíste en el PDF) : "
          f"{', '.join(sorted(verdad)) if verdad else '(ninguno)'}")
    print(f"  B (sistema: lo que detectó el programa) : "
          f"{', '.join(sorted(prediccion)) if prediccion else '(ninguno)'}")
    print()
    print("CÁLCULO")
    print(f"  A ∩ B  (en ambas listas)      = {sorted(interseccion) or '{}'}   -> {len(interseccion)}")
    print(f"  A ∪ B  (en cualquiera)        = {sorted(union) or '{}'}   -> {len(union)}")
    print()

    if not union:
        print("  Jaccard = 0 / 0 = INDEFINIDO")
        print()
        print("  QUÉ SIGNIFICA: ninguna de las dos listas tiene nada. No hay campos vacíos")
        print("  en el PDF y el sistema tampoco reportó ninguno. Jaccard NO PUEDE MEDIR ESTO:")
        print("  sólo sabe comparar listas de campos vacíos, y aquí no hay ninguna.")
        print()
        print("  La convención de la literatura multietiqueta es contarlo como 1,0. Pero ese")
        print("  1,0 no premia haber detectado algo: premia que no hubiera nada que detectar.")
        print("  Un sistema que NUNCA reportara campos vacíos sacaría 1,0 en todos los")
        print("  documentos correctos. Por eso Jaccard no puede reportarse solo.")
        print()
        print("  MÉTRICA HONESTA PARA ESTE DOCUMENTO:")
        print(f"     exact-match : SÍ — la lista del sistema coincide con la tuya")
        print(f"     aciertos    : {aciertos_llenos}/{len(declarados)} campos llenos correctamente identificados")
    else:
        j = len(interseccion) / len(union)
        print(f"  Jaccard = |A ∩ B| / |A ∪ B| = {len(interseccion)} / {len(union)} = {j:.3f}")
        print()
        if j == 1.0:
            print("  QUÉ SIGNIFICA: coincidencia perfecta. El sistema detectó exactamente los")
            print("  campos vacíos que hay, ni uno más ni uno menos.")
        elif j == 0.0:
            print("  QUÉ SIGNIFICA: las dos listas no comparten NADA. El sistema falló por")
            print("  completo en este documento.")
        else:
            print(f"  QUÉ SIGNIFICA: las listas se solapan en {len(interseccion)} de {len(union)} campos.")
            print("  Jaccard baja tanto por reportar campos que no están vacíos como por no")
            print("  detectar los que sí lo están. NO distingue entre los dos errores: para")
            print("  eso están la precisión y el recall de abajo.")

    print()
    print("DESGLOSE DEL ERROR (lo que Jaccard funde en un solo número)")
    if falsos_positivos:
        print(f"  FALSOS POSITIVOS ({len(falsos_positivos)}) — el sistema los cree vacíos y están llenos:")
        for campo in sorted(falsos_positivos):
            print(f"      '{campo}'   (el sistema leyó: {str(valores.get(campo))[:40]!r})")
        print("      Coste: el responsable pierde tiempo buscando algo que ya está.")
    else:
        print("  FALSOS POSITIVOS: ninguno.")
    if falsos_negativos:
        print(f"  FALSOS NEGATIVOS ({len(falsos_negativos)}) — están vacíos y el sistema no los detecta:")
        for campo in sorted(falsos_negativos):
            print(f"      '{campo}'   (el sistema creyó leer: {str(valores.get(campo))[:40]!r})")
        print("      Coste: evidencia incompleta pasa a la acreditación sin aviso.")
    else:
        print("  FALSOS NEGATIVOS: ninguno.")

    if union:
        precision = len(interseccion) / len(prediccion) if prediccion else 0.0
        recall = len(interseccion) / len(verdad) if verdad else 0.0
        print()
        print(f"  Precisión = {len(interseccion)}/{len(prediccion) or 0} = {precision:.3f}"
              "   (de los que declaro vacíos, cuántos lo están)")
        print(f"  Recall    = {len(interseccion)}/{len(verdad) or 0} = {recall:.3f}"
              "   (de los vacíos reales, cuántos detecto)")


# ---------------------------------------------------------------------------
# Modo TODO: corpus completo contra el CSV etiquetado
# ---------------------------------------------------------------------------
def generar_plantilla():
    vector_db = _abrir_base()
    filas = []
    for ruta in documentos():
        try:
            documento = extraer_documento(ruta)
            _n, meta = _recuperar_norma(vector_db, documento["texto"])
            valida, _f = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
            if not valida or not meta.get("campos", "").strip():
                continue
            declarados = [c.strip() for c in meta["campos"].split(";") if c.strip()]
            vacios, _l = _campos_sin_llenar(documento["cajas"], meta["campos"])
        except Exception as error:
            print(f"  omitido ({type(error).__name__}): {os.path.basename(ruta)[:50]}")
            continue
        for campo in declarados:
            filas.append({"documento": os.path.basename(ruta), "campo": campo,
                          "vacio_real": "1" if campo in vacios else "0",
                          "prediccion_sistema": "1" if campo in vacios else "0"})

    os.makedirs(os.path.dirname(VERDAD), exist_ok=True)
    with open(VERDAD, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(
            f, fieldnames=["documento", "campo", "vacio_real", "prediccion_sistema"])
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"\nPlantilla escrita en {VERDAD}")
    print(f"{len(filas)} pares (documento, campo) sobre "
          f"{len({f['documento'] for f in filas})} documentos.")
    print("\nCorrige la columna 'vacio_real' (1 = en blanco en el PDF, 0 = tiene contenido).")
    print("Viene pre-rellenada con la predicción del sistema: REVÍSALA CONTRA EL PDF, o")
    print("estarás midiendo el sistema contra sí mismo y todo dará 1,000.")


def modo_todo():
    if not os.path.exists(VERDAD):
        print(f"No existe {VERDAD}. Genéralo antes con:")
        print("   python scripts/evaluar_campos.py --plantilla")
        raise SystemExit(1)

    verdad = {}
    with open(VERDAD, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            verdad.setdefault(fila["documento"], set())
            if fila["vacio_real"].strip() == "1":
                verdad[fila["documento"]].add(fila["campo"])

    vector_db = _abrir_base()
    tp = fp = fn = tn = exactos = 0
    jaccards, jaccards_reales, desacuerdos = [], [], []
    evaluados = 0

    for ruta in documentos():
        nombre = os.path.basename(ruta)
        if nombre not in verdad:
            continue
        try:
            documento = extraer_documento(ruta)
            _n, meta = _recuperar_norma(vector_db, documento["texto"])
            valida, _f = _plantilla_valida(documento["texto"], meta.get("marcadores", ""))
            if not valida or not meta.get("campos", "").strip():
                continue
            declarados = [c.strip() for c in meta["campos"].split(";") if c.strip()]
            vacios, _l = _campos_sin_llenar(documento["cajas"], meta["campos"])
        except Exception:
            continue

        A, B = verdad[nombre], set(vacios)
        evaluados += 1
        tp += len(A & B); fp += len(B - A); fn += len(A - B)
        tn += len(declarados) - len(A | B)
        jaccards.append(1.0 if not (A | B) else len(A & B) / len(A | B))
        if A:
            jaccards_reales.append(len(A & B) / len(A | B))
        if A == B:
            exactos += 1
        else:
            desacuerdos.append((nombre, sorted(B - A), sorted(A - B)))

    if not evaluados:
        print("No hay documentos evaluables."); raise SystemExit(1)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    pares = tp + fp + fn + tn
    sin_vacios = evaluados - len(jaccards_reales)

    print("=" * 78)
    print("COMPUERTA 5 — CORPUS COMPLETO")
    print("=" * 78)
    print(f"Documentos: {evaluados}   |   pares (documento, campo): {pares}")
    print()
    print("                     auditor: VACÍO   auditor: LLENO")
    print(f"  sistema: VACÍO   {tp:>14}   {fp:>14}")
    print(f"  sistema: LLENO   {fn:>14}   {tn:>14}")
    print()
    print("MICRO (unidad = par documento-campo)")
    print(f"  Precisión    : {precision:.3f}   (de los que declaro vacíos, cuántos lo están)")
    print(f"  Recall       : {recall:.3f}   (de los vacíos reales, cuántos detecto)")
    print(f"  F1           : {f1:.3f}")
    print(f"  Hamming loss : {(fp + fn) / pares:.4f}   (fracción de etiquetas erróneas)")
    print()
    print("A NIVEL DE DOCUMENTO")
    print(f"  Exact-match             : {exactos}/{evaluados} = {exactos / evaluados:.3f}")
    print(f"  Jaccard medio (0/0 = 1) : {sum(jaccards) / evaluados:.3f}")
    if jaccards_reales:
        print(f"  Jaccard SÓLO donde hay campos vacíos (n={len(jaccards_reales)}) : "
              f"{sum(jaccards_reales) / len(jaccards_reales):.3f}")
    print()
    print(f"AVISO: en {sin_vacios} de {evaluados} documentos el auditor no halló ningún campo")
    print("vacío. Ahí Jaccard es 0/0 y la convención lo cuenta como 1, inflando la media.")
    print("Compara las dos cifras de Jaccard: si difieren mucho, la primera está mintiendo.")

    if desacuerdos:
        print()
        print("DESACUERDOS")
        for nombre, fpos, fneg in desacuerdos:
            print(f"  {nombre[:56]}")
            for c in fpos:
                print(f"      FALSO POSITIVO  '{c}' — el sistema lo cree vacío y está lleno")
            for c in fneg:
                print(f"      FALSO NEGATIVO  '{c}' — está vacío y el sistema no lo detecta")


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    if not argumentos:
        print(__doc__)
    elif argumentos[0] == "--plantilla":
        generar_plantilla()
    elif argumentos[0] == "ver" and len(argumentos) >= 2:
        modo_ver(argumentos[1])
    elif argumentos[0] == "uno" and len(argumentos) >= 2:
        vacios = []
        if "--vacios" in argumentos:
            crudo = argumentos[argumentos.index("--vacios") + 1]
            vacios = [c.strip() for c in crudo.split(",") if c.strip()]
        modo_uno(argumentos[1], vacios)
    elif argumentos[0] == "todo":
        modo_todo()
    else:
        print(__doc__)
