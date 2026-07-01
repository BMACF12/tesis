import os
import json
import traceback
from celery import Celery
from dotenv import load_dotenv

# Importaciones pesadas de IA trasladadas aquí
from unstructured.partition.pdf import partition_pdf
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

# Capa de Orquestación Física (Triage)
from services.orchestrator_service import enrutar_documento

load_dotenv()

# Conexión a tu servidor Redis en Docker
URL_REDIS = "redis://localhost:6379/0"

celery_app = Celery(
    "orquestador",
    broker=URL_REDIS,
    backend=URL_REDIS
)

# Esquemas de salida estructurada
class ElementoChecklist(BaseModel):
    numero_elemento: int = Field(description="El número del elemento fundamental evaluado")
    descripcion: str = Field(description="El texto literal del elemento o requisito según el contexto de la norma")
    cumple: bool = Field(description="True si el documento cumple con el elemento, False si no")
    justificacion: str = Field(description="Evidencia o motivo exacto extraído del documento evaluado")

class DictamenAuditoria(BaseModel):
    pertenece_software: bool = Field(description="True si pertenece a Ingeniería de Software, False en caso contrario")
    justificacion_software: str = Field(description="Explicación del porqué pertenece o no a la carrera")
    indicador_evaluado: str = Field(description="Nombre del indicador evaluado")
    veredicto: str = Field(description="'CUMPLE' o 'CUMPLE PARCIALMENTE' o 'NO CUMPLE'")
    porcentaje_estimado: int = Field(description="Porcentaje de 0 a 100")
    justificacion: str = Field(description="Explicación detallada de la decisión tomada")
    analisis_libre: str = Field(description="Párrafo de análisis cualitativo y general sobre el documento")
    checklist: List[ElementoChecklist] = Field(description="Lista detallada de todos los elementos evaluados")

# Configuración de resiliencia: 3 reintentos si las APIs fallan
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def auditar_documento_pesado(self, ruta_pdf: str, nombre_original: str = None):
    if not nombre_original:
        nombre_original = os.path.basename(ruta_pdf).replace("temp_", "")
        
    try:
        print(f"-> [CELERY] Inicio de auditoría asíncrona para: {nombre_original} (Temp: {ruta_pdf})")
        
        # 1. FASE DE EXTRACCIÓN
        print("-> [CELERY] Extrayendo texto con Unstructured...")
        try:
            elements = partition_pdf(
                filename=ruta_pdf,
                strategy="hi_res",
                languages=["spa"]
            )
            texto_completo = "\n".join([str(el) for el in elements])
        except Exception as extr_err:
            print(f"-> [CELERY] Error fatal de lectura PDF: {extr_err}")
            enrutar_documento({"veredicto": "ERROR_LECTURA"}, ruta_pdf, nombre_original)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            raise ValueError(f"Documento ilegible o corrupto: {extr_err}")
        
        # 2. FASE DE RECUPERACIÓN (ChromaDB)
        print("-> [CELERY] Recuperando indicador de ChromaDB...")
        texto_muestra = texto_completo[:1500].upper()
        
        # Enrutador semántico estricto
        mapeo_indicadores = {
            ("SÍLABO", "SYLLABUS", "PROGRAMA DE ASIGNATURA"): "Estándar y elementos fundamentales del indicador de Syllabus",
            ("MALLA CURRICULAR",): "Estándar y elementos fundamentales del indicador de Malla curricular",
            ("PROYECTO CURRICULAR", "DISEÑO CURRICULAR", "MACRO CURRÍCULO"): "Estándar y elementos fundamentales del indicador de Proyecto curricular",
            ("PERFIL DE EGRESO", "PERFIL PROFESIONAL"): "Estándar y elementos fundamentales del indicador de Perfil de egreso",
            ("METODOLOGÍA Y RECURSOS", "PORTAFOLIO DOCENTE"): "Estándar y elementos fundamentales del indicador de Metodología y recursos de aprendizaje",
            ("PRÁCTICAS FORMATIVAS", "ESCENARIOS DE APRENDIZAJE", "LABORATORIOS"): "Estándar y elementos fundamentales del indicador de Escenarios de prácticas formativas",
            ("TECNOLOGÍAS PARA EL APRENDIZAJE", "TAC", "ENTORNOS VIRTUALES"): "Estándar y elementos fundamentales del indicador de Tecnologías para el aprendizaje y conocimiento",
            ("AFINIDAD DEL PERSONAL", "FORMACIÓN DE POSGRADO"): "Estándar y elementos fundamentales del indicador de Afinidad del personal académico",
            ("TITULAR PERMANENTE", "NOMBRAMIENTO DEFINITIVO", "CONCURSO DE MERECIMIENTOS"): "Estándar y elementos fundamentales del indicador de Personal académico titular permanente",
            ("EVALUACIÓN INTEGRAL", "DESEMPEÑO DOCENTE", "EVALUACIÓN DEL DESEMPEÑO"): "Estándar y elementos fundamentales del indicador de Evaluación integral del desempeño del personal académico"
        }
        
        query_text = None
        for claves, valor_query in mapeo_indicadores.items():
            if any(clave in texto_muestra for clave in claves):
                query_text = valor_query
                break
                
        if not query_text:
            query_text = texto_completo[:1000]

        # Subir un nivel desde services/ a backend/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        persist_directory = os.path.join(base_dir, "chroma_data")
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        # 2.A Búsqueda del Contexto Normativo
        resultados_norma = vector_db.similarity_search(query_text, k=1)
        if not resultados_norma:
            raise ValueError("No se encontró un indicador correspondiente en la base de oro.")
        indicador_recuperado = resultados_norma[0].page_content
        
        # 2.B Búsqueda del Documento Maestro
        resultados_maestro = vector_db.similarity_search(
            query="Perfil de egreso malla curricular ingeniería de software", 
            k=1, 
            filter={"tipo": "documento_maestro"}
        )
        contexto_maestro = resultados_maestro[0].page_content if resultados_maestro else "No se encontró el documento maestro."
        
        # Consolidación del contexto
        contexto_combinado = f"--- CONTEXTO NORMATIVO CACES ---\n{indicador_recuperado}\n\n--- DOCUMENTO MAESTRO: INGENIERÍA DE SOFTWARE ---\n{contexto_maestro}"

        # 3. FASE DE EVALUACIÓN (Llama 3.3 via Groq)
        print("-> [CELERY] Evaluando documento con Groq LLM...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0
        ).with_structured_output(DictamenAuditoria)
        
        template_auditor = """Eres un auditor académico riguroso del CACES (Ecuador).
Evalúa el documento proporcionado. Primero, compara su contenido (títulos, materias, objetivos) con el Perfil de Egreso y la Malla Curricular de Ingeniería de Software presentes en el contexto maestro. Si el documento tiene relación directa o las materias coinciden con la malla de Software, marca 'pertenece_software' como True. Si es un sílabo o documento de otra disciplina ajena, marca False y explica el motivo en 'justificacion_software'. Luego, procede a evaluar el checklist del CACES.

Lee el documento proporcionado y el contexto combinado. Identifica el indicador correspondiente y evalúa el documento contra CADA UNO de los 'Elementos Fundamentales' o 'Requisitos' enumerados en el contexto normativo. Debes generar un ítem en el checklist por cada elemento, dictaminando si cumple o no, acompañado de su justificación fáctica.

REGLAS DE EVALUACIÓN (CRITERIO EXPERTO):
1. Equivalencia Semántica: El documento NO necesita usar las palabras exactas de la normativa. Evalúa si el 'propósito' o la 'esencia' del elemento fundamental está presente.
2. Flexibilidad Menor: Si el documento tiene los componentes principales pero omite un detalle técnico minúsculo, no lo rechaces por completo; hazle una observación.
3. Clasificación del Veredicto:
   - "CUMPLE": Tiene todos los elementos fundamentales (o sus equivalentes semánticos).
   - "CUMPLE PARCIALMENTE": Faltan elementos secundarios o hay ambigüedad, pero el núcleo del documento es válido. Requiere correcciones.
   - "NO CUMPLE": Faltan elementos críticos e indispensables.

CONTEXTO COMBINADO (NORMATIVA Y MAESTRO): {contexto} 

DOCUMENTO A EVALUAR: {documento}"""

        prompt = PromptTemplate(
            input_variables=["contexto", "documento"],
            template=template_auditor
        )
        
        chain = prompt | llm
        respuesta: DictamenAuditoria = chain.invoke({
            "contexto": contexto_combinado,
            "documento": texto_completo
        })
        
        # 4. Procesar respuesta y enrutar
        print("-> [CELERY] Procesando dictamen estructurado y ejecutando triage de archivos...")
        resultado_json = respuesta.model_dump()
        resultado_json["nombre_original"] = nombre_original
        
        # 4.1 Cálculo matemático estricto del porcentaje y veredicto basado en el checklist
        checklist = resultado_json.get("checklist", [])
        total_elementos = len(checklist)
        
        if total_elementos > 0:
            elementos_cumplidos = sum(1 for item in checklist if item.get("cumple") is True)
            porcentaje_calculado = int((elementos_cumplidos / total_elementos) * 100)
            
            # Asignación estricta de veredicto según los rangos acordados
            if porcentaje_calculado >= 70:
                veredicto_calculado = "CUMPLE"
            elif porcentaje_calculado >= 40:
                veredicto_calculado = "CUMPLE PARCIALMENTE"
            else:
                veredicto_calculado = "NO CUMPLE"
                
            # Sobrescribimos lo que haya devuelto el LLM para garantizar exactitud matemática
            resultado_json["porcentaje_estimado"] = porcentaje_calculado
            resultado_json["veredicto"] = veredicto_calculado
        
        # 5. Ejecutar orquestador físico
        enrutar_documento(resultado_json, ruta_pdf, nombre_original)
        
        print(f"-> [CELERY] Éxito: Auditoría asíncrona completada para {nombre_original}")
        
        # 6. Limpieza final del PDF
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
            
        return resultado_json

    except Exception as error:
        print(f"-> [CELERY] Error detectado durante el análisis: {error}")
        
        # Si ya se agotaron los reintentos, envíalo a descarte
        if self.request.retries >= self.max_retries:
            print("-> [CELERY] Se agotaron los reintentos. Enviando a descarte...")
            try:
                enrutar_documento({"veredicto": "ERROR_API"}, ruta_pdf, nombre_original)
            except Exception:
                pass
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            raise error

        # Si es un error transitorio, reintenta
        print("-> [CELERY] Reencolando la tarea en Redis para reintento automático...")
        raise self.retry(exc=error)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generar_reporte_ejecutivo(self, resultados_lote: list, id_lote: str):
    """
    Callback asíncrono ejecutado al terminar todo el lote (Chord).
    Recibe la lista de los diccionarios retornados por auditar_documento_pesado.
    """
    try:
        from fpdf import FPDF
        from fpdf.fonts import FontFace
        from datetime import datetime
        import os
        
        print(f"-> [CELERY] Generando Reporte Ejecutivo para el lote {id_lote} con {len(resultados_lote)} documentos...")
        
        # Calcular estadísticas
        total_docs = len(resultados_lote)
        cumplen = sum(1 for r in resultados_lote if r.get("veredicto", "") == "CUMPLE")
        cumplen_parcial = sum(1 for r in resultados_lote if r.get("veredicto", "") == "CUMPLE PARCIALMENTE")
        no_cumplen = sum(1 for r in resultados_lote if r.get("veredicto", "") == "NO CUMPLE")
        errores = sum(1 for r in resultados_lote if "ERROR" in r.get("veredicto", ""))
        
        # Directorio
        base_dir = "./Auditoria_CACES"
        repo_dir = os.path.join(base_dir, "Reportes_Ejecutivos")
        os.makedirs(repo_dir, exist_ok=True)
        ruta_salida = os.path.join(repo_dir, f"Reporte_Ejecutivo_{id_lote}.pdf")
        
        # Generar PDF
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
        pdf.cell(0, 8, f"Total de documentos procesados: {total_docs}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Documentos Aprobados ('Cumple'): {cumplen}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Documentos con Observaciones ('Parcial'): {cumplen_parcial}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Documentos Rechazados ('No Cumple'): {no_cumplen}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Errores de Análisis: {errores}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        
        pdf.set_font("helvetica", style="B", size=14)
        pdf.cell(0, 10, "2. Detalle por Documento", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        pdf.set_font("helvetica", size=10)
        with pdf.table(col_widths=(70, 60, 35, 25), text_align=("L", "L", "C", "C"), headings_style=FontFace(emphasis="B")) as table:
            headers = table.row()
            for h in ("Documento", "Indicador", "Veredicto", "Puntaje"):
                headers.cell(h)
                
            for res in resultados_lote:
                row = table.row()
                row.cell(str(res.get("nombre_original", "Desconocido")))
                row.cell(str(res.get("indicador_evaluado", "N/A")))
                veredicto = str(res.get("veredicto", "ERROR"))
                if "NO CUMPLE" in veredicto or "ERROR" in veredicto:
                    row.cell(veredicto, style=FontFace(emphasis="B"))
                else:
                    row.cell(veredicto)
                row.cell(f"{res.get('porcentaje_estimado', 0)}%")
                
        pdf.output(ruta_salida)
        print(f"-> [CELERY] Reporte Ejecutivo generado exitosamente en: {ruta_salida}")
        return {"reporte_ejecutivo": ruta_salida, "estadisticas": {"total": total_docs, "cumplen": cumplen}}
    except Exception as e:
        print(f"-> [CELERY] Error fatal generando reporte ejecutivo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=e)