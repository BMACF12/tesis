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
        
        resultados = vector_db.similarity_search(query_text, k=1)
        if not resultados:
            raise ValueError("No se encontró un indicador correspondiente en la base de oro.")
            
        indicador_recuperado = resultados[0].page_content

        # 3. FASE DE EVALUACIÓN (Llama 3.3 via Groq)
        print("-> [CELERY] Evaluando documento con Groq LLM...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        
        template_auditor = """Eres un Auditor Académico Senior del CACES (Ecuador), experto y con criterio analítico. Tu tarea es evaluar el documento proporcionado por el usuario basándote ÚNICA Y EXCLUSIVAMENTE en la normativa oficial 2024 del CACES entregada en el contexto.

REGLAS DE EVALUACIÓN (CRITERIO EXPERTO):
1. Equivalencia Semántica: El documento NO necesita usar las palabras exactas de la normativa. Evalúa si el 'propósito' o la 'esencia' del elemento fundamental está presente.
2. Flexibilidad Menor: Si el documento tiene los componentes principales pero omite un detalle técnico minúsculo, no lo rechaces por completo; hazle una observación.
3. Clasificación del Veredicto:
   - "CUMPLE": Tiene todos los elementos fundamentales (o sus equivalentes semánticos).
   - "CUMPLE PARCIALMENTE": Faltan elementos secundarios o hay ambigüedad, pero el núcleo del documento es válido. Requiere correcciones.
   - "NO CUMPLE": Faltan elementos críticos e indispensables.

Responde SIEMPRE en formato JSON válido con esta estructura exacta, sin texto adicional:
{{
"indicador_evaluado": "Nombre del indicador",
"veredicto": "CUMPLE" o "CUMPLE PARCIALMENTE" o "NO CUMPLE",
"porcentaje_estimado": "Porcentaje de 0 a 100",
"justificacion": "Explicación detallada..."
}}

INDICADOR: {indicador} 

DOCUMENTO: {documento}"""

        prompt = PromptTemplate(
            input_variables=["indicador", "documento"],
            template=template_auditor
        )
        
        chain = prompt | llm
        respuesta = chain.invoke({
            "indicador": indicador_recuperado,
            "documento": texto_completo
        })
        
        # 4. Procesar respuesta JSON y enrutar
        print("-> [CELERY] Procesando dictamen y ejecutando triage de archivos...")
        contenido_llm = respuesta.content.strip()
        
        # Limpieza de backticks markdown
        if contenido_llm.startswith("```json"):
            contenido_llm = contenido_llm.replace("```json", "", 1)
        elif contenido_llm.startswith("```"):
            contenido_llm = contenido_llm.replace("```", "", 1)
        if contenido_llm.endswith("```"):
            contenido_llm = contenido_llm[:-3]
        contenido_llm = contenido_llm.strip()
            
        resultado_json = json.loads(contenido_llm)
        
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