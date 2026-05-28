import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Cargar variables de entorno desde el archivo .env (se espera GOOGLE_API_KEY)
load_dotenv()

def main():
    # 1. Obtiene la ruta de la carpeta 'scripts'
    carpeta_scripts = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Retrocede un nivel para llegar a la carpeta 'backend'
    carpeta_backend = os.path.dirname(carpeta_scripts)

    # 3. Construye las rutas exactas uniendo la carpeta backend con el resto
    file_path = os.path.join(carpeta_backend, "data", "caces_2024_oficial.txt")
    persist_directory = os.path.join(carpeta_backend, "chroma_data")
    
    print(f"Intentando cargar el documento: {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo {file_path}")
        return

    try:
        # 1. Cargar el texto del documento
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        print("Documento cargado.")

        # 2. Configurar el text splitter
        # Dividimos el texto en chunks; se configuran tamaños pequeños por la naturaleza de los indicadores cortos
        print("Dividiendo el texto en fragmentos (chunks)...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,      # Aumentamos el tamaño para que quepa un indicador entero
            chunk_overlap=200,    # Solapamiento para no perder contexto
            separators=["=== INDICADOR", "\n\n", "\n", " ", ""] # Separadores estratégicos
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Se generaron {len(chunks)} fragmentos.")

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
