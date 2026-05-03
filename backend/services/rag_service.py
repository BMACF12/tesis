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
        
        template_auditor = """Eres un auditor estricto del CACES. Tu tarea es revisar este DOCUMENTO y verificar si cumple con los requisitos exigidos en el INDICADOR. 

INDICADOR: {indicador} 

DOCUMENTO: {documento} 

Responde únicamente con un SÍ o NO al principio, seguido de un salto de línea y luego una breve justificación de 3 líneas."""

        prompt = PromptTemplate(
            input_variables=["indicador", "documento"],
            template=template_auditor
        )
        
        chain = prompt | llm
        respuesta = chain.invoke({
            "indicador": indicador_recuperado,
            "documento": texto_completo
        })
        
        # 4. Procesar y estructurar la respuesta del LLM
        contenido_llm = respuesta.content.strip()
        es_si = contenido_llm.upper().startswith("SÍ") or contenido_llm.upper().startswith("SI")
        veredicto = "SÍ" if es_si else "NO"
        justificacion = contenido_llm.replace("SÍ", "", 1).replace("SI", "", 1).replace("NO", "", 1).strip(" \n-.:")

        return {
            "veredicto": veredicto,
            "justificacion": justificacion
        }
