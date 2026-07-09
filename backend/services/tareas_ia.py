"""
Auditoría de un documento contra la normativa CACES, en tres capas.

1. HECHOS (determinista, sin LLM). Extracción por coordenadas, verificación de la
   plantilla, pertinencia a la carrera y campos sin llenar. Todo esto son datos, no
   juicios: pedírselos al LLM producía alucinaciones (campos llenos declarados vacíos,
   pertenencias inventadas) porque el extractor le entregaba una tabla desordenada.

2. JUICIO (LLM). Recibe la norma recuperada de ChromaDB, los hechos ya verificados y el
   documento. Devuelve sólo el checklist y el diagnóstico. Nada más.

3. VEREDICTO (determinista). Se deriva de la plantilla, la pertinencia, los campos vacíos
   y el porcentaje del checklist.

Si la plantilla no es válida o el documento no pertenece a la carrera, no se llama al LLM.
"""
import os
import re
from typing import List, Optional

from celery import Celery
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from services.extraccion import comparable, extraer_documento, normalizar, resolver_campos
from services.orchestrator_service import enrutar_documento

load_dotenv()

URL_REDIS = "redis://localhost:6379/0"
celery_app = Celery("orquestador", broker=URL_REDIS, backend=URL_REDIS)


# ---------------------------------------------------------------------------
# Esquema de salida: el LLM sólo emite juicios, nunca hechos
# ---------------------------------------------------------------------------
class ElementoChecklist(BaseModel):
    numero_elemento: int = Field(description="Número del elemento fundamental según la norma")
    descripcion: str = Field(description="Texto del elemento fundamental según la norma")
    cumple: bool = Field(description="True si el documento cumple el elemento")
    justificacion: str = Field(
        description="Cita textual EXACTA del documento que lo demuestra. Si no puedes citar, "
                    "el elemento no cumple. NO inventes explicaciones.")


class DictamenAuditoria(BaseModel):
    checklist: List[ElementoChecklist] = Field(
        description="Un ítem por cada elemento fundamental de la norma, en su orden")
    analisis_libre: str = Field(
        description="Diagnóstico de ESTE documento en 3 a 5 frases: nómbralo, di qué elementos "
                    "fallaron y por qué, y qué debe corregir el responsable. Nada genérico.")


# ---------------------------------------------------------------------------
# Enrutado al indicador
# ---------------------------------------------------------------------------
# El orden no es arbitrario:
#  - El sílabo va primero: menciona "malla curricular" y "perfil de egreso" en su interior.
#  - El proyecto curricular va antes que la malla y que el perfil: los cita a ambos en sus
#    primeras páginas, mientras que ninguno de ellos lo cita a él.
#  - No se usa "LABORATORIO" a secas: aparece en documentos de otros indicadores.
MAPEO_INDICADORES = (
    (("PROGRAMA DE ASIGNATURA", "SÍLABO", "SILABO", "SYLLABUS"), 4),
    (("GUIA DE USO DE LABORATORIO", "GUÍA DE USO DE LABORATORIO", "GUÍA DE LABORATORIO",
      "GUÍA DE PRÁCTICA", "PRÁCTICAS FORMATIVAS", "ESCENARIOS DE APRENDIZAJE"), 6),
    (("PROYECTO CURRICULAR", "DISEÑO CURRICULAR", "MACRO CURRÍCULO", "MODELO EDUCATIVO"), 2),
    (("PERFIL DE EGRESO", "PERFIL EGRESO", "PERFIL PROFESIONAL"), 1),
    (("MALLA CURRICULAR", "HPAO"), 3),
)

PALABRAS_ACADEMICAS = (
    "universidad", "instituto", "sílabo", "syllabus", "caces", "asignatura", "evaluación",
    "carrera", "educación", "estudiante", "aprendizaje", "perfil", "malla", "facultad",
    "currículo", "proyecto", "profesional", "metodología", "recursos", "portafolio",
    "prácticas", "laboratorio", "escenario", "tecnología", "virtual", "afinidad",
    "posgrado", "titular", "nombramiento", "concurso", "desempeño", "docente", "académico",
)


def _detectar_indicador(texto: str) -> Optional[int]:
    muestra = texto[:1500].upper()
    for claves, numero in MAPEO_INDICADORES:
        if any(clave in muestra for clave in claves):
            return numero
    return None


# ---------------------------------------------------------------------------
# Pertinencia: ¿el documento es de la carrera de Software?
# ---------------------------------------------------------------------------
_VACIAS = {"de", "del", "la", "el", "los", "las", "en", "y", "e", "para", "con", "por", "al"}
# "Resultado de Aprendizaje de la Carrera:" no declara ninguna carrera; se excluye.
_CARRERA_EN_TEXTO = re.compile(r"(?<!de la )carrera\s*:\s*([^|\n]{3,60})", re.IGNORECASE)


def _fichas(nombre: str) -> list:
    return [p for p in normalizar(nombre).replace(".", " ").replace(",", " ").split()
            if len(p) >= 3 and p not in _VACIAS]


def _cargar_asignaturas() -> list:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta = os.path.join(base_dir, "data", "asignaturas_malla.txt")
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


ASIGNATURAS_MALLA = _cargar_asignaturas()


def _asignatura_en_malla(nombre: str) -> Optional[str]:
    """
    El sílabo abrevia y trunca: "APL. BASADAS EN EL CONOCIMIENT" es "Aplicaciones Basadas
    en el Conocimiento". Se comparan las palabras significativas admitiendo que cada una
    del sílabo sea el principio de la de la malla.
    """
    fichas = _fichas(nombre)
    if len(fichas) < 2:
        return None
    for asignatura in ASIGNATURAS_MALLA:
        candidatas = _fichas(asignatura)
        if all(any(c.startswith(f) for c in candidatas) for f in fichas):
            return asignatura
    return None


def _pertinencia(texto: str, cajas: list):
    """Devuelve (pertenece: True/False/None, motivo citado). None = indeterminado."""
    campos = resolver_campos(cajas, ["CARRERA", "Nombre Asignatura", "ASIGNATURA"]) if cajas else {}

    carrera = campos.get("CARRERA")
    if not carrera:
        encontrado = _CARRERA_EN_TEXTO.search(texto)
        carrera = encontrado.group(1).strip() if encontrado else None
    if carrera:
        es_sw = "software" in normalizar(carrera)
        return es_sw, f"CARRERA: {carrera}"

    asignatura = campos.get("Nombre Asignatura") or campos.get("ASIGNATURA")
    if asignatura:
        coincide = _asignatura_en_malla(asignatura)
        if coincide:
            return True, f"Nombre Asignatura: {asignatura} (consta en la malla como «{coincide}»)"
        return False, f"Nombre Asignatura: {asignatura} (no consta en la malla de Software)"

    normalizado = normalizar(texto)
    if "carrera de software" in normalizado or "ingenieria de software" in normalizado:
        return True, "El documento menciona la carrera de Ingeniería de Software"
    return None, "No se pudo determinar la carrera a partir del documento"


# ---------------------------------------------------------------------------
# Plantilla y campos sin llenar
# ---------------------------------------------------------------------------
def _plantilla_valida(texto: str, marcadores: str):
    """
    MARCADORES separados por ';' son obligatorios; por '|' son alternativos.

    La comparación se hace sobre la forma canónica (sin tildes, sin guiones, sin el
    separador de celdas): un marcador partido entre dos cajas del PDF no debe hacer que
    un documento válido se declare plantilla no reconocida.
    """
    if not marcadores.strip():
        return True, []
    documento = comparable(texto)
    faltan = []
    for grupo in marcadores.split(";"):
        alternativas = [a.strip() for a in grupo.split("|") if a.strip()]
        if alternativas and not any(comparable(a) in documento for a in alternativas):
            faltan.append(" o ".join(alternativas))
    return (not faltan), faltan


def _campos_sin_llenar(cajas: list, campos: str):
    """
    Devuelve (vacíos, localizados). Un campo cuya etiqueta no aparece en el documento no
    se cuenta: no se puede afirmar nada de él. Un valor "No aplica" o "NA" está lleno.
    """
    nombres = [c.strip() for c in campos.split(";") if c.strip()]
    if not nombres or not cajas:
        return [], 0
    resueltos = resolver_campos(cajas, nombres)
    vacios = [nombre for nombre, valor in resueltos.items() if not valor]
    return vacios, len(resueltos)


# ---------------------------------------------------------------------------
# Recuperación de contexto (RAG)
# ---------------------------------------------------------------------------
def _abrir_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return Chroma(
        persist_directory=os.path.join(base_dir, "chroma_data"),
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
    )


def _recuperar_norma(vector_db, texto: str):
    """
    Devuelve (criterio, metadatos). Si el enrutador identifica el indicador se lee por
    metadatos: es exacto y no gasta una llamada de embeddings. El respaldo por similitud
    filtra tipo="norma" para no devolver nunca el documento maestro, que comparte colección.
    """
    numero = _detectar_indicador(texto)
    if numero is not None:
        encontrado = vector_db.get(where={"indicador": numero})
        if encontrado["documents"]:
            meta = dict(encontrado["metadatas"][0])
            meta["enrutado_por"] = "palabras_clave"
            return encontrado["documents"][0], meta

    resultados = vector_db.similarity_search(texto[:1000], k=1, filter={"tipo": "norma"})
    if not resultados:
        raise ValueError("No se encontró un indicador correspondiente en la base de oro.")
    meta = dict(resultados[0].metadata)
    meta["enrutado_por"] = "similitud"
    return resultados[0].page_content, meta


def _recuperar_reglas(vector_db) -> str:
    documentos = vector_db.get(where={"tipo": "reglas"})["documents"]
    return documentos[0] if documentos else ""


def _recuperar_maestro(vector_db) -> str:
    """
    Contexto de la carrera. Se recorta la lista completa de asignaturas: ya se verifica de
    forma determinista en `_asignatura_en_malla` y el modelo no necesita leerla.
    """
    documentos = vector_db.get(where={"tipo": "documento_maestro"})["documents"]
    if not documentos:
        return "No se encontró el documento maestro."
    texto = documentos[0]
    corte = texto.find("Asignaturas de la malla curricular vigente")
    return (texto[:corte] if corte != -1 else texto).strip()


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
PLANTILLA_AUDITOR = PromptTemplate(
    input_variables=["reglas", "norma", "maestro", "hechos", "documento"],
    template="""Eres un auditor académico riguroso del CACES (Ecuador). Evalúas un documento contra la norma de su indicador.

{reglas}

NORMA DEL INDICADOR:
{norma}

CONTEXTO DE LA CARRERA (Ingeniería de Software):
{maestro}

{hechos}

DOCUMENTO A EVALUAR:
{documento}""",
)


def _hoja_de_hechos(pertenece, motivo, vacios, localizados, declara_campos, por_ocr) -> str:
    if pertenece is True:
        carrera = f"pertenece a Ingeniería de Software. Evidencia: {motivo}"
    elif pertenece is False:
        carrera = f"NO pertenece a Ingeniería de Software. Evidencia: {motivo}"
    else:
        carrera = f"indeterminada. {motivo}"

    if not declara_campos:
        campos = "el indicador no declara campos etiquetados que verificar."
    elif por_ocr or not localizados:
        # No es lo mismo "no hay campos" que "no se pudieron localizar": afirmar lo primero
        # sería entregarle al modelo un hecho falso.
        campos = ("el indicador SÍ declara campos obligatorios, pero no se pudieron localizar "
                  "en el documento (leído por OCR, sin disposición de tabla). Verifícalos tú.")
    elif not vacios:
        campos = f"los {localizados} campos obligatorios localizados están llenos."
    else:
        campos = f"{len(vacios)} de {localizados} campos obligatorios están sin llenar: " + "; ".join(vacios)

    return ("HECHOS VERIFICADOS SOBRE EL DOCUMENTO (comprobados por coordenadas sobre el PDF; son ciertos):\n"
            "- Plantilla oficial del indicador: SÍ.\n"
            f"- Carrera: {carrera}\n"
            f"- Campos: {campos}")


# ---------------------------------------------------------------------------
# Veredicto (determinista)
# ---------------------------------------------------------------------------
def _calcular_veredicto(resultado: dict):
    """
    El veredicto no lo decide el LLM. Los campos vacíos sí lo condicionan, porque ahora la
    lista es determinista y fiable: un documento con la plantilla mayoritariamente en
    blanco no es evidencia, y uno al que sólo le falta un campo puede completarse.
    """
    if not resultado.get("plantilla_valida", True):
        return 0, "PLANTILLA NO RECONOCIDA"
    if resultado.get("pertenece_software") is False:
        return 0, "NO CUMPLE"

    checklist = resultado.get("checklist") or []
    if not checklist:
        return 0, "ERROR_SIN_CHECKLIST"

    porcentaje = round(sum(1 for i in checklist if i.get("cumple")) / len(checklist) * 100)
    vacios = resultado.get("campos_vacios") or []
    localizados = resultado.get("campos_localizados") or 0

    # Plantilla oficial pero mayoritariamente en blanco. Se exige una muestra mínima: con
    # un solo campo localizado, que esté vacío no basta para tumbar el documento.
    if localizados >= 4 and len(vacios) > localizados / 2:
        return porcentaje, "NO CUMPLE"
    if porcentaje <= 50:
        return porcentaje, "NO CUMPLE"
    if porcentaje >= 70 and not vacios:
        return porcentaje, "CUMPLE"
    return porcentaje, "CUMPLE PARCIALMENTE"


# ---------------------------------------------------------------------------
# Resultados sin LLM
# ---------------------------------------------------------------------------
def _resultado(nombre_original: str, **kwargs) -> dict:
    base = {
        "nombre_original": nombre_original, "indicador_evaluado": "Desconocido",
        "indicador_numero": None, "enrutado_por": None, "plantilla_valida": True,
        "pertenece_software": None, "justificacion_software": "",
        "campos_vacios": [], "campos_localizados": 0, "checklist": [],
        "veredicto": "ERROR", "porcentaje_estimado": 0, "justificacion": "", "analisis_libre": "",
    }
    base.update(kwargs)
    return base


MENSAJE_ERROR = {
    "ERROR_CUOTA_API": "El documento no se auditó: se agotó la cuota diaria de tokens de la API. "
                       "No tiene defecto conocido. Vuelve a subirlo cuando el límite se recargue.",
    "ERROR_LECTURA": "El PDF no pudo leerse: está corrupto, protegido, o es un escaneo sin capa de texto.",
    "ERROR_API": "El análisis falló tras agotar los reintentos. Revisa el detalle técnico.",
}


# ---------------------------------------------------------------------------
# Límites de la API
# ---------------------------------------------------------------------------
# Groq distingue límites por minuto (segundos) de límites por día (horas). Reintentar los
# primeros tiene sentido; reintentar los segundos sólo desperdicia una extracción de PDF.
ESPERA_MAXIMA_REINTENTO = 300
_ESPERA = re.compile(r"try again in (?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?", re.IGNORECASE)


def _es_limite_de_cuota(error: Exception) -> bool:
    return "rate_limit_exceeded" in str(error) or getattr(error, "status_code", None) == 429


def _segundos_de_espera(error: Exception) -> Optional[float]:
    encontrado = _ESPERA.search(str(error))
    if not encontrado:
        return None
    horas, minutos, segundos = encontrado.groups()
    return int(horas or 0) * 3600 + int(minutos or 0) * 60 + float(segundos or 0)


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def auditar_documento_pesado(self, ruta_pdf: str, nombre_original: str = None):
    if not nombre_original:
        nombre_original = os.path.basename(ruta_pdf).replace("temp_", "")

    def cerrar(resultado):
        enrutar_documento(resultado, ruta_pdf, nombre_original)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
        return resultado

    try:
        print(f"-> [CELERY] Auditando {nombre_original}")

        # --- Capa 1: hechos -------------------------------------------------
        try:
            documento = extraer_documento(ruta_pdf)
        except Exception as error_extraccion:
            print(f"-> [CELERY] PDF ilegible: {error_extraccion}")
            # No se reintenta: un PDF corrupto lo seguirá estando. El temporal se conserva
            # hasta después de enrutarlo, para que el orquestador pueda copiarlo.
            return cerrar(_resultado(nombre_original, veredicto="ERROR_LECTURA",
                                     plantilla_valida=False, pertenece_software=False,
                                     justificacion=str(error_extraccion),
                                     analisis_libre=MENSAJE_ERROR["ERROR_LECTURA"]))

        texto, cajas = documento["texto"], documento["cajas"]

        coincidencias = sum(1 for p in PALABRAS_ACADEMICAS if p in texto.lower())
        if coincidencias < 2:
            print(f"-> [CELERY] Rechazo léxico ({coincidencias} coincidencias). Sin llamada al LLM.")
            return cerrar(_resultado(
                nombre_original, veredicto="PLANTILLA NO RECONOCIDA", plantilla_valida=False,
                pertenece_software=False,
                justificacion=f"Sólo {coincidencias} palabra(s) del vocabulario académico.",
                analisis_libre="Rechazo automático: el documento no es académico. "
                               "Se abortó el análisis con IA para no consumir recursos."))

        vector_db = _abrir_base()
        norma, meta = _recuperar_norma(vector_db, texto)
        indicador = f"Indicador {meta.get('indicador')}: {meta.get('nombre')}"

        plantilla_ok, faltan = _plantilla_valida(texto, meta.get("marcadores", ""))
        if not plantilla_ok:
            print(f"-> [CELERY] Plantilla no reconocida (faltan: {faltan}). Sin llamada al LLM.")
            return cerrar(_resultado(
                nombre_original, veredicto="PLANTILLA NO RECONOCIDA", plantilla_valida=False,
                indicador_evaluado=indicador, indicador_numero=meta.get("indicador"),
                enrutado_por=meta.get("enrutado_por"),
                justificacion=f"No se hallaron los marcadores de la plantilla oficial: {'; '.join(faltan)}.",
                analisis_libre="El documento no usa la plantilla oficial de este indicador. "
                               "Es un problema distinto de una plantilla correcta mal llenada."))

        pertenece, motivo = _pertinencia(texto, cajas)
        if pertenece is False:
            print(f"-> [CELERY] Ajeno a la carrera ({motivo}). Sin llamada al LLM.")
            return cerrar(_resultado(
                nombre_original, veredicto="NO CUMPLE", indicador_evaluado=indicador,
                indicador_numero=meta.get("indicador"), enrutado_por=meta.get("enrutado_por"),
                pertenece_software=False, justificacion_software=motivo,
                justificacion="El documento no pertenece a la carrera de Ingeniería de Software.",
                analisis_libre=f"Descartado de la auditoría: {motivo}."))

        vacios, localizados = _campos_sin_llenar(cajas, meta.get("campos", ""))

        # --- Capa 2: juicio del LLM ------------------------------------------
        reglas = _recuperar_reglas(vector_db)
        maestro = _recuperar_maestro(vector_db)
        hechos = _hoja_de_hechos(pertenece, motivo, vacios, localizados,
                                 declara_campos=bool(meta.get("campos", "").strip()),
                                 por_ocr=documento["ocr"])

        print(f"-> [CELERY] {indicador} ({meta.get('enrutado_por')}) | norma {len(norma)} ch | "
              f"documento {len(texto)} ch | campos vacíos {len(vacios)}/{localizados}")

        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0).with_structured_output(DictamenAuditoria)
        respuesta = (PLANTILLA_AUDITOR | llm).invoke({
            "reglas": reglas, "norma": norma, "maestro": maestro,
            "hechos": hechos, "documento": texto,
        })

        # --- Capa 3: veredicto ------------------------------------------------
        resultado = _resultado(
            nombre_original, indicador_evaluado=indicador, indicador_numero=meta.get("indicador"),
            enrutado_por=meta.get("enrutado_por"), plantilla_valida=True,
            pertenece_software=(pertenece is not False), justificacion_software=motivo,
            campos_vacios=vacios, campos_localizados=localizados,
            checklist=[e.model_dump() for e in respuesta.checklist],
            analisis_libre=respuesta.analisis_libre)
        resultado["porcentaje_estimado"], resultado["veredicto"] = _calcular_veredicto(resultado)
        resultado["justificacion"] = (
            f"{sum(1 for e in resultado['checklist'] if e['cumple'])} de "
            f"{len(resultado['checklist'])} elementos fundamentales cumplidos; "
            f"{len(vacios)} campo(s) sin llenar.")

        print(f"-> [CELERY] {nombre_original}: {resultado['veredicto']} "
              f"({resultado['porcentaje_estimado']}%) | campos vacíos: {vacios}")
        return cerrar(resultado)

    except Exception as error:
        print(f"-> [CELERY] Error durante el análisis: {error}")

        if _es_limite_de_cuota(error):
            espera = _segundos_de_espera(error)
            if espera is not None and espera <= ESPERA_MAXIMA_REINTENTO \
                    and self.request.retries < self.max_retries:
                print(f"-> [CELERY] Límite por minuto. Reintento en {espera:.0f}s.")
                raise self.retry(exc=error, countdown=espera + 5)
            restante = f"{espera / 60:.0f} min" if espera else "desconocido"
            print(f"-> [CELERY] Cuota agotada (recarga en {restante}). No se reintenta.")
            return cerrar(_resultado(nombre_original, veredicto="ERROR_CUOTA_API",
                                     plantilla_valida=False, pertenece_software=False,
                                     justificacion=str(error),
                                     analisis_libre=MENSAJE_ERROR["ERROR_CUOTA_API"]))

        if self.request.retries >= self.max_retries:
            print("-> [CELERY] Reintentos agotados. Enviando a descarte.")
            # Se devuelve en vez de relanzar: si esta tarea falla, el chord aborta el
            # reporte ejecutivo de todo el lote.
            return cerrar(_resultado(nombre_original, veredicto="ERROR_API",
                                     plantilla_valida=False, pertenece_software=False,
                                     justificacion=str(error),
                                     analisis_libre=MENSAJE_ERROR["ERROR_API"]))

        print("-> [CELERY] Reencolando para reintento automático.")
        raise self.retry(exc=error)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generar_reporte_ejecutivo(self, resultados_lote: list, id_lote: str):
    """Callback del chord: se ejecuta cuando termina todo el lote."""
    try:
        from datetime import datetime

        from fpdf import FPDF
        from fpdf.fonts import FontFace

        resultados_lote = [r for r in resultados_lote if isinstance(r, dict)]
        print(f"-> [CELERY] Reporte ejecutivo del lote {id_lote} ({len(resultados_lote)} documentos)")

        def contar(*veredictos):
            return sum(1 for r in resultados_lote if r.get("veredicto", "") in veredictos)

        total = len(resultados_lote)
        estadisticas = {
            "total": total,
            "cumplen": contar("CUMPLE"),
            "parciales": contar("CUMPLE PARCIALMENTE"),
            "no_cumplen": contar("NO CUMPLE"),
            "sin_plantilla": contar("PLANTILLA NO RECONOCIDA"),
            # La cuota agotada no es un defecto del documento: se cuenta aparte.
            "pendientes": contar("ERROR_CUOTA_API"),
            "errores": sum(1 for r in resultados_lote
                           if "ERROR" in r.get("veredicto", "") and r.get("veredicto") != "ERROR_CUOTA_API"),
        }

        repo_dir = os.path.join("./Auditoria_CACES", "Reportes_Ejecutivos")
        os.makedirs(repo_dir, exist_ok=True)
        ruta_salida = os.path.join(repo_dir, f"Reporte_Ejecutivo_{id_lote}.pdf")

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("helvetica", style="B", size=18)
        pdf.cell(0, 10, "Reporte Ejecutivo Global de Auditoria", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 8, f"ID Lote: {id_lote}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", style="B", size=14)
        pdf.cell(0, 10, "1. Estadisticas Globales", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=12)
        for etiqueta, clave in (
            ("Total de documentos procesados", "total"),
            ("Documentos aprobados (Cumple)", "cumplen"),
            ("Documentos con observaciones (Parcial)", "parciales"),
            ("Documentos rechazados (No cumple)", "no_cumplen"),
            ("Documentos con plantilla no reconocida", "sin_plantilla"),
            ("Pendientes por cuota de API", "pendientes"),
            ("Errores de analisis", "errores"),
        ):
            pdf.cell(0, 8, f"{etiqueta}: {estadisticas[clave]}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

        pdf.set_font("helvetica", style="B", size=14)
        pdf.cell(0, 10, "2. Detalle por Documento", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("helvetica", size=9)
        with pdf.table(col_widths=(50, 40, 38, 18, 44), text_align=("L", "L", "C", "C", "L"),
                       headings_style=FontFace(emphasis="B")) as table:
            fila = table.row()
            for encabezado in ("Documento", "Indicador", "Veredicto", "Puntaje", "Campos sin llenar"):
                fila.cell(encabezado)
            for resultado in resultados_lote:
                fila = table.row()
                fila.cell(str(resultado.get("nombre_original", "Desconocido")))
                fila.cell(str(resultado.get("indicador_evaluado", "N/A")))
                veredicto = str(resultado.get("veredicto", "ERROR"))
                fila.cell(veredicto) if veredicto == "CUMPLE" else fila.cell(veredicto, style=FontFace(emphasis="B"))
                fila.cell(f"{resultado.get('porcentaje_estimado', 0)}%")
                vacios = resultado.get("campos_vacios") or []
                fila.cell(", ".join(vacios) if vacios else "-")

        pdf.output(ruta_salida)
        print(f"-> [CELERY] Reporte ejecutivo en {ruta_salida}")
        return {"reporte_ejecutivo": ruta_salida, "estadisticas": estadisticas}
    except Exception as error:
        print(f"-> [CELERY] Error generando el reporte ejecutivo: {error}")
        raise self.retry(exc=error)
