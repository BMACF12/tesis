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

from services.extraccion import extraer_documento, normalizar, resolver_campos
from services.orchestrator_service import enrutar_documento

load_dotenv()

URL_REDIS = "redis://localhost:6379/0"

celery_app = Celery("orquestador", broker=URL_REDIS, backend=URL_REDIS)


# ---------------------------------------------------------------------------
# Esquema de salida estructurada
# ---------------------------------------------------------------------------
class ElementoChecklist(BaseModel):
    numero_elemento: int = Field(description="Número del elemento fundamental según la norma")
    descripcion: str = Field(description="Texto del elemento fundamental según la norma")
    cumple: bool = Field(description="True si el documento cumple el elemento")
    justificacion: str = Field(
        description="Cita textual EXACTA del documento que lo demuestra. Si el campo está vacío, "
                    "escribe 'CAMPO VACÍO - SIN CONTENIDO'. NO inventes explicaciones.")


class DictamenAuditoria(BaseModel):
    plantilla_valida: bool = Field(
        description="True si el documento contiene los MARCADORES DE IDENTIFICACIÓN de la plantilla oficial")
    pertenece_software: bool = Field(
        description="True sólo si el documento declara pertenecer a la carrera de Software")
    justificacion_software: str = Field(
        description="Cita textual del campo de identificación en que basas la decisión (Carrera, "
                    "Área de Conocimiento o Resultado de Aprendizaje de la Carrera)")
    indicador_evaluado: str = Field(description="Nombre del indicador evaluado")
    campos_vacios: List[str] = Field(
        description="Nombres exactos de los campos que la norma lista y el documento deja sin contenido")
    veredicto: str = Field(description="'CUMPLE', 'CUMPLE PARCIALMENTE' o 'NO CUMPLE'")
    porcentaje_estimado: int = Field(description="Porcentaje de 0 a 100")
    justificacion: str = Field(description="Explicación de la decisión")
    analisis_libre: str = Field(
        description="Diagnóstico específico de ESTE documento en 3 a 5 frases: nómbralo, di qué "
                    "elementos fallaron y por qué, y qué debe corregir el responsable. Prohibidas "
                    "las frases genéricas. No repitas la lista de campos_vacios.")
    checklist: List[ElementoChecklist] = Field(description="Un ítem por cada elemento fundamental de la norma")


# ---------------------------------------------------------------------------
# Recuperación de contexto
# ---------------------------------------------------------------------------
# El orden importa y no es arbitrario:
#  - El sílabo va primero: menciona "Prácticas de Laboratorio" entre sus métodos.
#  - El proyecto curricular va antes que el perfil de egreso: casi siempre cita el
#    perfil en sus primeras páginas, mientras que un perfil no cita al proyecto.
#  - No se usa "LABORATORIO" a secas: aparece en documentos de otros indicadores.
MAPEO_INDICADORES = (
    (("PROGRAMA DE ASIGNATURA", "SÍLABO", "SILABO", "SYLLABUS"), 4),
    (("MALLA CURRICULAR", "HPAO"), 3),
    (("GUIA DE USO DE LABORATORIO", "GUÍA DE USO DE LABORATORIO", "GUÍA DE LABORATORIO",
      "GUÍA DE PRÁCTICA", "PRÁCTICAS FORMATIVAS", "ESCENARIOS DE APRENDIZAJE"), 6),
    (("PROYECTO CURRICULAR", "DISEÑO CURRICULAR", "MACRO CURRÍCULO"), 2),
    (("PERFIL DE EGRESO", "PERFIL PROFESIONAL"), 1),
)

PALABRAS_ACADEMICAS = (
    "universidad", "instituto", "sílabo", "syllabus", "caces", "asignatura", "evaluación",
    "carrera", "educación", "estudiante", "aprendizaje", "perfil", "malla", "facultad",
    "currículo", "proyecto", "profesional", "metodología", "recursos", "portafolio",
    "prácticas", "laboratorio", "escenario", "tecnología", "virtual", "afinidad",
    "posgrado", "titular", "nombramiento", "concurso", "desempeño", "docente", "académico",
)


# ---------------------------------------------------------------------------
# Pertinencia: ¿la asignatura del documento está en la malla de Software?
# ---------------------------------------------------------------------------
_VACIAS = {"de", "del", "la", "el", "los", "las", "en", "y", "e", "para", "con", "por", "al", "un", "una"}


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


def _asignatura_en_malla(nombre: str):
    """
    El sílabo abrevia y trunca el nombre: "APL. BASADAS EN EL CONOCIMIENT" es
    "Aplicaciones Basadas en el Conocimiento". Se comparan las palabras significativas
    admitiendo que cada una del sílabo sea el principio de la de la malla.
    """
    fichas = _fichas(nombre)
    if len(fichas) < 2:
        return None
    for asignatura in ASIGNATURAS_MALLA:
        candidatas = _fichas(asignatura)
        if all(any(c.startswith(f) for c in candidatas) for f in fichas):
            return asignatura
    return None


_ASIGNATURA_EN_IDENT = re.compile(r"^- (?:Nombre Asignatura|ASIGNATURA): (.+)$", re.MULTILINE)


def _linea_malla(identificacion: str) -> str:
    """Comprueba la asignatura contra la malla y lo declara como hecho en el prompt."""
    encontrado = _ASIGNATURA_EN_IDENT.search(identificacion)
    if not encontrado:
        return ""
    coincide = _asignatura_en_malla(encontrado.group(1))
    if coincide:
        return f"\n- Asignatura en la malla de Software: SÍ ({coincide})"
    return "\n- Asignatura en la malla de Software: NO"


def _detectar_indicador(texto: str):
    muestra = texto[:1500].upper()
    for claves, numero in MAPEO_INDICADORES:
        if any(clave in muestra for clave in claves):
            return numero
    return None


def _abrir_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return Chroma(
        persist_directory=os.path.join(base_dir, "chroma_data"),
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
    )


def _recuperar_norma(vector_db, texto: str):
    """
    Recupera el bloque normativo del indicador. Devuelve (texto, metadatos).

    Si el enrutador lo identifica, se lee por metadatos: es exacto y no gasta una
    llamada de embeddings. El respaldo por similitud filtra tipo="norma" para no
    devolver nunca el documento maestro, que vive en la misma colección de Chroma.
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
    Contexto de la carrera para el LLM. Se recorta por los dos extremos: fuera el perfil
    de egreso entero, y fuera la lista completa de las 44 asignaturas, que ya se verifica
    de forma determinista en `_asignatura_en_malla` y no hace falta que el modelo lea.
    """
    documentos = vector_db.get(where={"tipo": "documento_maestro"})["documents"]
    if not documentos:
        return "No se encontró el documento maestro."
    texto = documentos[0]
    inicio = texto.find("Materias de la Malla Curricular Activas:")
    fin = texto.find("Asignaturas de la malla curricular vigente")
    return texto[inicio if inicio != -1 else 0: fin if fin != -1 else len(texto)].strip()


PLANTILLA_AUDITOR = PromptTemplate(
    input_variables=["reglas", "norma", "maestro", "identificacion", "documento"],
    template="""Eres un auditor académico riguroso del CACES (Ecuador). Evalúas un documento contra la norma de su indicador.

{reglas}

7. PERTINENCIA. Decídela SÓLO con el bloque CAMPOS DE IDENTIFICACIÓN, nunca por el tema del documento:
   - La línea "Asignatura en la malla de Software" ya está verificada contra la malla curricular vigente. Si dice NO, pertenece_software=False, salvo que CARRERA diga explícitamente Software.
   - Si dice SÍ, o si CARRERA dice Software, pertenece_software=True.
   - "Departamento" y "Área de Conocimiento" NO deciden nada: son idénticos en sílabos de carreras distintas.
   - Que el documento hable de auditoría de TI, bases de datos o redes NO prueba nada: otras carreras también las imparten.
   - En justificacion_software copia el campo y su valor exacto. NUNCA uses el código del formulario (p. ej. SGC.DI.321) como prueba.
8. Genera exactamente un ítem de checklist por CADA elemento fundamental de la norma, respetando su numeración. No añadas elementos que la norma no enumere.
9. En campos_vacios enumera, con el nombre exacto de la norma, sólo los campos de CAMPOS QUE DEBEN ESTAR LLENOS que el documento deja sin contenido. Respeta los VALORES QUE NO CUENTAN COMO CAMPO VACÍO.
10. analisis_libre: 3 a 5 frases sobre ESTE documento. Nombra la asignatura y la carrera, di qué elementos fundamentales fallaron y por qué, y qué debe hacer el responsable. NO escribas frases como "cumple con la mayoría de los elementos" o "se detectaron algunos campos vacíos": son inútiles. No repitas la lista de campos_vacios, ya se muestra aparte.

NORMA DEL INDICADOR:
{norma}

CONTEXTO MAESTRO (Ingeniería de Software):
{maestro}

CAMPOS DE IDENTIFICACIÓN (extraídos del documento por coordenadas; son fiables):
{identificacion}

DOCUMENTO A EVALUAR:
{documento}""",
)


# ---------------------------------------------------------------------------
# Guardarraíl sobre la lista de campos vacíos que emite el LLM
# ---------------------------------------------------------------------------
_LINEA_CAMPOS = re.compile(r"^CAMPOS QUE DEBEN ESTAR LLENOS:(.*)$", re.MULTILINE)


def _campos_declarados(norma: str) -> list:
    """Los campos que la norma del indicador exige llenos. Vacío si no está instrumentado."""
    encontrado = _LINEA_CAMPOS.search(norma)
    if not encontrado:
        return []
    linea = encontrado.group(1).strip()
    if linea.startswith("("):  # "(no instrumentado; devuelve campos_vacios vacío)"
        return []
    return [c.strip().rstrip(".") for c in linea.split(";") if c.strip()]


def _coincide(reportado: str, declarados: list):
    """
    Empareja el nombre que devolvió el LLM con el nombre canónico de la norma.

    Sólo por prefijo, nunca por subcadena suelta: "Correo electrónico del docente"
    contiene "Docente", pero no es ese campo. Ante varias coincidencias gana la más
    larga, para que "Perfil sugerido del docente" no acabe emparejado con "Docente".
    """
    objetivo = normalizar(reportado)
    if not objetivo:
        return None
    coincidencias = [d for d in declarados
                     if (c := normalizar(d)) and (objetivo == c
                                                  or c.startswith(objetivo)
                                                  or objetivo.startswith(c))]
    return max(coincidencias, key=lambda d: len(normalizar(d))) if coincidencias else None


def _depurar_campos_vacios(reportados: list, norma: str, cajas: list):
    """
    Verifica la lista del LLM contra el documento. Devuelve (válidos, descartados).

    Se descarta un campo cuando no figura entre los que la norma exige, o cuando la
    extracción por coordenadas demuestra que sí tiene contenido. Nunca se añade un
    campo: si la etiqueta no aparece en el documento, no se puede afirmar nada.
    """
    declarados = _campos_declarados(norma)
    if not declarados:
        return [], [(c, "el indicador no declara campos obligatorios") for c in reportados]

    resueltos = resolver_campos(cajas, declarados) if cajas else {}
    validos, descartados = [], []

    for reportado in reportados:
        canonico = _coincide(reportado, declarados)
        if canonico is None:
            descartados.append((reportado, "no es un campo de la norma"))
            continue
        valor = resueltos.get(canonico)
        if valor:
            descartados.append((reportado, f"tiene contenido: {valor[:40]}"))
            continue
        if canonico not in validos:
            validos.append(canonico)

    return validos, descartados


def _calcular_veredicto(resultado: dict):
    """
    El veredicto lo decide el checklist, no el LLM y no la lista de campos vacíos.

    `campos_vacios` se reporta como observación para el responsable, pero NO influye en
    el veredicto: el modelo la produce de forma poco fiable (inventa campos, se salta
    los que dicen "No aplica", y varía entre corridas del mismo documento). Si un campo
    vacío pudiera topar el veredicto, ningún documento alcanzaría nunca CUMPLE.
    """
    if not resultado.get("plantilla_valida", True):
        return 0, "PLANTILLA NO RECONOCIDA"
    if not resultado.get("pertenece_software", True):
        return 0, "NO CUMPLE"

    checklist = resultado.get("checklist", [])
    if not checklist:
        return 0, "ERROR_SIN_CHECKLIST"

    porcentaje = round(sum(1 for i in checklist if i.get("cumple")) / len(checklist) * 100)

    if porcentaje >= 70:
        return porcentaje, "CUMPLE"
    if porcentaje > 50:
        return porcentaje, "CUMPLE PARCIALMENTE"
    return porcentaje, "NO CUMPLE"


def _rechazo_lexico(texto: str, nombre_original: str, coincidencias: int) -> dict:
    return {
        "plantilla_valida": False,
        "pertenece_software": False,
        "justificacion_software": f"Sólo {coincidencias} palabra(s) del vocabulario académico. No es un documento pertinente.",
        "indicador_evaluado": "Indicador_Desconocido",
        "campos_vacios": [],
        "veredicto": "PLANTILLA NO RECONOCIDA",
        "porcentaje_estimado": 0,
        "justificacion": "El documento no supera el filtro léxico: carece de vocabulario universitario básico.",
        "analisis_libre": "RECHAZO AUTOMÁTICO: se abortó el análisis con IA para ahorrar recursos.",
        "checklist": [],
        "nombre_original": nombre_original,
    }


# Groq distingue límites por minuto (recuperables en segundos) de límites por día
# (recuperables en horas). Reintentar los segundos tiene sentido; reintentar los días
# sólo desperdicia una extracción de PDF y, en el respaldo, una llamada de embeddings.
ESPERA_MAXIMA_REINTENTO = 300  # segundos

_ESPERA = re.compile(r"try again in (?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?", re.IGNORECASE)


def _es_limite_de_cuota(error: Exception) -> bool:
    return "rate_limit_exceeded" in str(error) or getattr(error, "status_code", None) == 429


def _segundos_de_espera(error: Exception) -> Optional[float]:
    encontrado = _ESPERA.search(str(error))
    if not encontrado:
        return None
    horas, minutos, segundos = encontrado.groups()
    return int(horas or 0) * 3600 + int(minutos or 0) * 60 + float(segundos or 0)


MENSAJE_ERROR = {
    "ERROR_CUOTA_API": "El documento no se auditó: se agotó la cuota diaria de tokens de la API. "
                       "No tiene ningún defecto conocido. Vuelve a subirlo cuando el límite se recargue.",
    "ERROR_LECTURA": "El PDF no pudo leerse: está corrupto, protegido, o es un escaneo sin capa de texto.",
    "ERROR_API": "El análisis falló tras agotar los reintentos. Revisa el detalle técnico y reinténtalo.",
}


def _resultado_error(nombre_original: str, veredicto: str, detalle: str) -> dict:
    return {
        "plantilla_valida": False,
        "pertenece_software": False,
        "justificacion_software": "",
        "indicador_evaluado": "N/A",
        "campos_vacios": [],
        "veredicto": veredicto,
        "porcentaje_estimado": 0,
        "justificacion": detalle,  # detalle técnico, para el log y la depuración
        "analisis_libre": MENSAJE_ERROR.get(veredicto, "El documento no pudo auditarse."),
        "checklist": [],
        "nombre_original": nombre_original,
    }


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def auditar_documento_pesado(self, ruta_pdf: str, nombre_original: str = None):
    if not nombre_original:
        nombre_original = os.path.basename(ruta_pdf).replace("temp_", "")

    try:
        print(f"-> [CELERY] Auditando {nombre_original}")

        try:
            texto_completo, identificacion, cajas = extraer_documento(ruta_pdf)
            identificacion += _linea_malla(identificacion)
        except Exception as error_extraccion:
            print(f"-> [CELERY] PDF ilegible: {error_extraccion}")
            resultado = _resultado_error(nombre_original, "ERROR_LECTURA", str(error_extraccion))
            enrutar_documento(resultado, ruta_pdf, nombre_original)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            return resultado  # un PDF corrupto lo seguirá estando: no se reintenta

        coincidencias = sum(1 for palabra in PALABRAS_ACADEMICAS if palabra in texto_completo.lower())
        if coincidencias < 2:
            print(f"-> [CELERY] Rechazo léxico ({coincidencias} coincidencias). No se llama al LLM.")
            resultado = _rechazo_lexico(texto_completo, nombre_original, coincidencias)
            enrutar_documento(resultado, ruta_pdf, nombre_original)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            return resultado

        vector_db = _abrir_base()
        norma, meta_norma = _recuperar_norma(vector_db, texto_completo)
        reglas = _recuperar_reglas(vector_db)
        maestro = _recuperar_maestro(vector_db)

        print(f"-> [CELERY] Indicador {meta_norma.get('indicador')} "
              f"({meta_norma.get('enrutado_por')}) | norma {len(norma)} ch | reglas {len(reglas)} ch | "
              f"maestro {len(maestro)} ch | ident {len(identificacion)} ch | "
              f"documento {len(texto_completo)} ch")

        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0).with_structured_output(DictamenAuditoria)
        respuesta = (PLANTILLA_AUDITOR | llm).invoke({
            "reglas": reglas,
            "norma": norma,
            "maestro": maestro,
            "identificacion": identificacion,
            "documento": texto_completo,
        })

        resultado = respuesta.model_dump()
        resultado["nombre_original"] = nombre_original

        # El indicador ya lo conoce el enrutador. Pedírselo al LLM sólo introduce ruido:
        # devolvía "Syllabus", "INDICADOR 4: Syllabus" o el indicador equivocado, y de eso
        # depende la carpeta de destino y la matriz de confusión de la evaluación.
        resultado["indicador_numero"] = meta_norma.get("indicador")
        resultado["indicador_evaluado"] = (
            f"Indicador {meta_norma.get('indicador')}: {meta_norma.get('nombre')}")
        resultado["enrutado_por"] = meta_norma.get("enrutado_por")

        # Los indicadores no instrumentados no declaran marcadores de plantilla, así que
        # la regla 1 haría que el LLM los rechace por una plantilla que no existe.
        if not meta_norma.get("instrumentado"):
            resultado["plantilla_valida"] = True

        # El LLM enumera campos vacíos de forma poco fiable: inventa nombres y no logra
        # emparejar una etiqueta con el valor que está en la fila de abajo. Se verifica
        # su lista contra el documento antes de mostrarla.
        validos, descartados = _depurar_campos_vacios(
            resultado.get("campos_vacios") or [], norma, cajas)
        resultado["campos_vacios"] = validos
        resultado["campos_vacios_descartados"] = [f"{c} ({motivo})" for c, motivo in descartados]
        if descartados:
            print(f"-> [CELERY] Descartados {len(descartados)} campos vacíos falsos: "
                  + "; ".join(f"{c} -> {m}" for c, m in descartados))

        resultado["porcentaje_estimado"], resultado["veredicto"] = _calcular_veredicto(resultado)

        if not resultado["pertenece_software"]:
            for item in resultado["checklist"]:
                item["cumple"] = False
                item["justificacion"] = "RECHAZADO: el documento no pertenece a Ingeniería de Software."

        print(f"-> [CELERY] {nombre_original}: {resultado['veredicto']} ({resultado['porcentaje_estimado']}%) | "
              f"campos vacíos: {resultado['campos_vacios']}")

        enrutar_documento(resultado, ruta_pdf, nombre_original)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
        return resultado

    except Exception as error:
        print(f"-> [CELERY] Error durante el análisis: {error}")

        if _es_limite_de_cuota(error):
            espera = _segundos_de_espera(error)
            if espera is not None and espera <= ESPERA_MAXIMA_REINTENTO \
                    and self.request.retries < self.max_retries:
                print(f"-> [CELERY] Límite por minuto. Reintento en {espera:.0f}s.")
                raise self.retry(exc=error, countdown=espera + 5)

            # Cuota agotada durante horas: reintentar cada 30 s no la devuelve, y cada
            # intento vuelve a extraer el PDF y a consumir embeddings.
            restante = f"{espera / 60:.0f} min" if espera else "desconocido"
            print(f"-> [CELERY] Cuota de la API agotada (recarga en {restante}). No se reintenta.")
            resultado = _resultado_error(nombre_original, "ERROR_CUOTA_API", str(error))
            try:
                enrutar_documento(resultado, ruta_pdf, nombre_original)
            except Exception:
                pass
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            return resultado

        if self.request.retries >= self.max_retries:
            print("-> [CELERY] Reintentos agotados. Enviando a descarte.")
            resultado = _resultado_error(nombre_original, "ERROR_API", str(error))
            try:
                enrutar_documento(resultado, ruta_pdf, nombre_original)
            except Exception:
                pass
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            # Se devuelve en vez de relanzar: si esta tarea falla, el chord aborta el
            # reporte ejecutivo de todo el lote.
            return resultado

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
        cumplen = contar("CUMPLE")
        parciales = contar("CUMPLE PARCIALMENTE")
        no_cumplen = contar("NO CUMPLE")
        sin_plantilla = contar("PLANTILLA NO RECONOCIDA")
        errores = sum(1 for r in resultados_lote if "ERROR" in r.get("veredicto", ""))

        repo_dir = os.path.join("./Auditoria_CACES", "Reportes_Ejecutivos")
        os.makedirs(repo_dir, exist_ok=True)
        ruta_salida = os.path.join(repo_dir, f"Reporte_Ejecutivo_{id_lote}.pdf")

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("helvetica", style="B", size=18)
        pdf.cell(0, 10, "Reporte Ejecutivo Global de Auditoría", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 8, f"ID Lote: {id_lote}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", style="B", size=14)
        pdf.cell(0, 10, "1. Estadísticas Globales", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=12)
        for etiqueta, valor in (
            ("Total de documentos procesados", total),
            ("Documentos aprobados ('Cumple')", cumplen),
            ("Documentos con observaciones ('Parcial')", parciales),
            ("Documentos rechazados ('No cumple')", no_cumplen),
            ("Documentos con plantilla no reconocida", sin_plantilla),
            ("Errores de análisis", errores),
        ):
            pdf.cell(0, 8, f"{etiqueta}: {valor}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

        pdf.set_font("helvetica", style="B", size=14)
        pdf.cell(0, 10, "2. Detalle por Documento", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("helvetica", size=9)
        with pdf.table(col_widths=(50, 40, 38, 18, 44), text_align=("L", "L", "C", "C", "L"),
                       headings_style=FontFace(emphasis="B")) as table:
            fila = table.row()
            for encabezado in ("Documento", "Indicador", "Veredicto", "Puntaje", "Campos vacíos"):
                fila.cell(encabezado)

            for resultado in resultados_lote:
                fila = table.row()
                fila.cell(str(resultado.get("nombre_original", "Desconocido")))
                fila.cell(str(resultado.get("indicador_evaluado", "N/A")))
                veredicto = str(resultado.get("veredicto", "ERROR"))
                fila.cell(veredicto) if veredicto == "CUMPLE" else fila.cell(veredicto, style=FontFace(emphasis="B"))
                fila.cell(f"{resultado.get('porcentaje_estimado', 0)}%")
                faltantes = resultado.get("campos_vacios") or []
                fila.cell(", ".join(faltantes) if faltantes else "-")

        pdf.output(ruta_salida)
        print(f"-> [CELERY] Reporte ejecutivo en {ruta_salida}")
        return {"reporte_ejecutivo": ruta_salida,
                "estadisticas": {"total": total, "cumplen": cumplen, "parciales": parciales,
                                 "no_cumplen": no_cumplen, "sin_plantilla": sin_plantilla,
                                 "errores": errores}}
    except Exception as error:
        print(f"-> [CELERY] Error generando el reporte ejecutivo: {error}")
        raise self.retry(exc=error)
