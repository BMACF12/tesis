import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from unstructured.partition.pdf import partition_pdf
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="API Gateway - Sistema CACES RAG")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway - Sistema CACES RAG")

# Añadir esto para permitir que Next.js se conecte al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción poner: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Sistema CACES RAG inicializado y en línea"}

@app.post("/evaluar_documento/")
async def evaluar_documento(file: UploadFile = File(...)):
    # 1. Validar que el archivo subido sea un PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pdf")

    # Configurar rutas
    base_dir = os.path.dirname(__file__)
    doc_dir = os.path.join(base_dir, 'documentos_prueba')
    os.makedirs(doc_dir, exist_ok=True)  # Crear carpeta si no existe
    
    # Nombre temporal único
    temp_pdf_path = os.path.join(doc_dir, f"temp_{file.filename}")
    persist_directory = os.path.join(base_dir, "chroma_data")

    try:
        # 2. Guardar el archivo PDF temporalmente en el disco
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Fase de Extracción (Unstructured)
        try:
            elements = partition_pdf(
                filename=temp_pdf_path,
                strategy="hi_res",
                languages=["spa"]
            )
            texto_completo = "\n".join([str(el) for el in elements])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en la extracción del PDF: {str(e)}")

        # 4. Fase de Recuperación (Retrieval - ChromaDB)
        query_text = texto_completo[:1000]
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        resultados = vector_db.similarity_search(query_text, k=1)
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontró un indicador correspondiente en la base de oro.")
            
        indicador_recuperado = resultados[0].page_content

        # 5. Fase de Evaluación (LLM Groq)
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
        
        # 6. Procesar y estructurar la respuesta del LLM
        contenido_llm = respuesta.content.strip()
        
        # Determinar el veredicto asegurándonos de extraer solo el "SÍ" o "NO" inicial
        es_si = contenido_llm.upper().startswith("SÍ") or contenido_llm.upper().startswith("SI")
        veredicto = "SÍ" if es_si else "NO"
        
        # Limpiar la justificación quitando la primera línea o palabra
        # Se reemplaza el SÍ/NO inicial para dejar solo la explicación
        justificacion = contenido_llm.replace("SÍ", "", 1).replace("SI", "", 1).replace("NO", "", 1).strip(" \n-.:")

        # 7. Retornar el JSON
        return {
            "veredicto": veredicto,
            "justificacion": justificacion
        }

    except HTTPException as http_exc:
        # Relanzar las excepciones controladas de FastAPI
        raise http_exc
    except Exception as e:
        # Atrapar cualquier otro error no contemplado
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
        
    finally:
        # 8. Limpieza: Eliminar siempre el archivo temporal, haya éxito o error
        if os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as cleanup_error:
                print(f"Advertencia: No se pudo eliminar el archivo temporal {temp_pdf_path}. Error: {cleanup_error}")
