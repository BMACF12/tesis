import os
from fastapi import HTTPException
from unstructured.partition.pdf import partition_pdf
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from core.config import settings

class RAGService:
    def __init__(self):
        # Inicializar embeddings una sola vez (es más eficiente)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.persist_directory = settings.CHROMA_DIR

    def procesar_documento(self, temp_pdf_path: str) -> dict:
        """
        Contiene toda la lógica de negocio (Extracción, Retrieval y Generación)
        """
        try:
            # 1. Fase de Extracción (Unstructured)
            elements = partition_pdf(
                filename=temp_pdf_path,
                strategy="hi_res",
                languages=["spa"]
            )
            texto_completo = "\n".join([str(el) for el in elements])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en la extracción del PDF: {str(e)}")

        # 2. Fase de Recuperación (Retrieval - ChromaDB)
        query_text = texto_completo[:1000]
        vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        
        resultados = vector_db.similarity_search(query_text, k=1)
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontró un indicador correspondiente en la base de oro.")
            
        indicador_recuperado = resultados[0].page_content

        # 3. Fase de Evaluación (LLM Groq)
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0  # Respuesta determinista
        )
        
        template_auditor = """Eres un Auditor Académico Senior del CACES (Ecuador), experto y con criterio analítico. Tu tarea es evaluar el documento proporcionado por el usuario basándote ÚNICA Y EXCLUSIVAMENTE en la normativa oficial 2024 del CACES entregada en el contexto.

REGLAS DE EVALUACIÓN (CRITERIO EXPERTO):
1. Equivalencia Semántica: El documento NO necesita usar las palabras exactas de la normativa. Evalúa si el 'propósito' o la 'esencia' del elemento fundamental está presente (ej. "Objetivos" puede equivaler a "Resultados de aprendizaje").
2. Flexibilidad Menor: Si el documento tiene los componentes principales pero omite un detalle técnico minúsculo, no lo rechaces por completo; hazle una observación.
3. Clasificación del Veredicto:
   - "CUMPLE": Tiene todos los elementos fundamentales (o sus equivalentes semánticos).
   - "CUMPLE PARCIALMENTE": Faltan elementos secundarios o hay ambigüedad, pero el núcleo del documento es válido. Requiere correcciones.
   - "NO CUMPLE": Faltan elementos críticos e indispensables (ej. no hay bibliografía, no hay metodologías, o el documento no tiene nada que ver con el indicador).

Responde SIEMPRE en formato JSON válido con esta estructura exacta, sin texto adicional:
{{
"veredicto": "CUMPLE" o "CUMPLE PARCIALMENTE" o "NO CUMPLE",
"porcentaje_estimado": "Asigna un porcentaje del 0 al 100 de cuánto cumple",
"justificacion": "Explica qué elementos se encontraron (aunque tengan otros nombres), qué falta exactamente y por qué le diste esa calificación..."
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
        
        # 4. Procesar y estructurar la respuesta JSON del LLM
        contenido_llm = respuesta.content.strip()
        
        import json
        try:
            # Limpiar backticks de markdown si el modelo los añade por error
            if contenido_llm.startswith("```json"):
                contenido_llm = contenido_llm.replace("```json", "", 1)
                if contenido_llm.endswith("```"):
                    contenido_llm = contenido_llm[:-3]
                contenido_llm = contenido_llm.strip()
            elif contenido_llm.startswith("```"):
                contenido_llm = contenido_llm.replace("```", "", 1)
                if contenido_llm.endswith("```"):
                    contenido_llm = contenido_llm[:-3]
                contenido_llm = contenido_llm.strip()
                
            resultado_json = json.loads(contenido_llm)
            return resultado_json
        except json.JSONDecodeError:
            # Fallback en caso de que el modelo falle en el formato
            return {
                "veredicto": "ERROR",
                "justificacion": f"El LLM no generó un JSON válido. Salida: {contenido_llm}"
            }
