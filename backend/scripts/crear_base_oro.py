import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Cargar variables de entorno desde el archivo .env (se espera GOOGLE_API_KEY)
load_dotenv()

def main():
    # Rutas absolutas calculadas desde la ubicación de este script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "caces_2024_oficial.txt")
    persist_directory = os.path.join(base_dir, "chroma_data")
    
    print(f"Intentando cargar el documento: {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo {file_path}")
        return

    try:
        # 1. Cargar el texto del documento de forma manual
        with open(file_path, "r", encoding="utf-8") as f:
            texto_completo = f.read()
        print("Documento cargado.")

        # 2. Configurar el particionado ESTRICTO (1 chunk = 1 Indicador)
        print("Dividiendo el texto en fragmentos (1 chunk por indicador)...")
        from langchain_core.documents import Document
        
        partes = texto_completo.split("=== INDICADOR")
        chunks = []
        for parte in partes:
            parte_limpia = parte.strip()
            if parte_limpia:
                # Volver a poner el prefijo para que el LLM sepa qué indicador es
                texto_chunk = "=== INDICADOR " + parte_limpia
                chunks.append(Document(page_content=texto_chunk, metadata={"source": file_path}))
                
        print(f"Se generaron {len(chunks)} fragmentos estrictos.")

        # 3. Configurar el modelo de Embeddings de Google
        # Esto automáticamente buscará la variable GOOGLE_API_KEY en tu entorno (.env)
        print("Inicializando modelo de embeddings de Google...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # 4. Crear la base de datos vectorial local con ChromaDB
        print(f"Generando vectores y guardando en la carpeta '{persist_directory}'...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        print(f"¡Éxito! Base de datos vectorial 'Base de Oro' creada y guardada persistentemente en './{persist_directory}'.")
        
        # Opcional: Mostrar los fragmentos que se vectorizaron para revisión visual
        print("-" * 40)
        print("Muestra del primer chunk vectorizado:")
        if chunks:
            print(chunks[0].page_content)
        print("-" * 40)

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()
