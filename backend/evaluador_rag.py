import os
from dotenv import load_dotenv
from unstructured.partition.pdf import partition_pdf
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Cargar las API Keys (.env)
load_dotenv()

def main():
    # Rutas locales
    pdf_path = os.path.join(os.path.dirname(__file__), 'documentos_prueba', 'ejemplo_malo.pdf')
    persist_directory = "chroma_data"
    
    print("=" * 60)
    print("🚀 INICIANDO PIPELINE RAG DE AUDITORÍA CACES")
    print("=" * 60)

    if not os.path.exists(pdf_path):
        print(f"Error: No se encontró el archivo PDF en {pdf_path}")
        return

    try:
        # ---------------------------------------------------------
        # FASE 1: EXTRACCIÓN (Unstructured)
        # ---------------------------------------------------------
        print("\n[Fase 1/3] Extrayendo texto del PDF con Unstructured (hi_res)...")
        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            languages=["spa"]
        )
        
        # Juntar todos los elementos en un solo string
        texto_completo_documento = "\n".join([str(el) for el in elements])
        print(f"Texto extraído con éxito (Longitud: {len(texto_completo_documento)} caracteres).")

        # ---------------------------------------------------------
        # FASE 2: RECUPERACIÓN (Retrieval con ChromaDB)
        # ---------------------------------------------------------
        print("\n[Fase 2/3] Buscando el Indicador correspondiente en ChromaDB...")
        # Tomar los primeros 1000 caracteres como consulta semántica
        query_text = texto_completo_documento[:1000]
        
        # Conectar a la base de datos
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        # Buscar el indicador más similar
        resultados = vector_db.similarity_search(query_text, k=1)
        
        if not resultados:
            print("No se encontró ningún indicador en la base de datos.")
            return
            
        indicador_recuperado = resultados[0].page_content
        print("Indicador recuperado correctamente.")

        # ---------------------------------------------------------
        # FASE 3: GENERACIÓN / EVALUACIÓN (Llama 3.3 via Groq)
        # ---------------------------------------------------------
        print("\n[Fase 3/3] Evaluando documento con ChatGroq (llama-3.3-70b-versatile)...")
        
        # Inicializar el LLM de Groq
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0  # Queremos una respuesta determinista y analítica
        )
        
        # Crear el Prompt Template
        template_auditor = """Eres un auditor estricto del CACES. Tu tarea es revisar este DOCUMENTO y verificar si cumple con los requisitos exigidos en el INDICADOR. 

INDICADOR: {indicador} 

DOCUMENTO: {documento} 

Responde únicamente con un SÍ o NO al principio, seguido de una breve justificación de 3 líneas."""

        prompt = PromptTemplate(
            input_variables=["indicador", "documento"],
            template=template_auditor
        )
        
        # Construir la cadena (Chain)
        chain = prompt | llm
        
        print("Auditor analizando...\n")
        # Ejecutar la inferencia
        respuesta = chain.invoke({
            "indicador": indicador_recuperado,
            "documento": texto_completo_documento
        })
        
        # ---------------------------------------------------------
        # RESULTADO FINAL
        # ---------------------------------------------------------
        print("=" * 60)
        print("DICTAMEN DEL EVALUADOR:")
        print("=" * 60)
        print(respuesta.content)
        print("=" * 60)
        
    except Exception as e:
        print(f"Ocurrió un error en el pipeline: {e}")

if __name__ == "__main__":
    main()
