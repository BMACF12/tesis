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
        
        template_auditor = """Eres un Auditor Académico Senior, estricto e implacable, evaluando documentos universitarios bajo los estándares del CACES (Ecuador). Tu única tarea es evaluar el documento académico proporcionado por el usuario basándote ÚNICA Y EXCLUSIVAMENTE en la normativa oficial 2024 del CACES que se te entrega en el contexto recuperado.

REGLAS ESTRICTAS:
- Compara el contenido del documento del usuario contra los 'Elementos Fundamentales' del indicador correspondiente en el contexto.
- Jamás asumas, inventes, ni uses información externa. Si no está explícitamente en el documento del usuario, no existe.

Responde SIEMPRE en formato JSON válido con esta estructura exacta, sin texto adicional antes o después:
{{
"veredicto": "SÍ" o "NO",
"justificacion": "Explicación detallada de qué cumple o qué le falta según los elementos fundamentales de la normativa..."
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
