import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Cargar variables de entorno
load_dotenv()

# Texto estático solicitado
TEXTO_MAESTRO = """DOCUMENTO MAESTRO: PERFIL Y MALLA CURRICULAR - INGENIERÍA DE SOFTWARE
Perfil de Egreso:
El futuro profesional en Ingeniería de Software utilizará una sólida formación en cada uno de los núcleos básicos de la carrera, desarrollando las competencias necesarias para resolver problemas en cualquier área de su campo profesional, independientemente de la naturaleza del problema, manteniendo una amplia visión y noción de las necesidades de todos los involucrados. Estos núcleos básicos articulan los saberes de la Carrera de Software, con la demanda que se identifica en la matriz productiva y las políticas del Plan Nacional del Buen Vivir, evidenciando la coherencia que debe existir entre la universidad y las necesidades del país. Se identifican los siguientes núcleos estructurantes para la Carrera de Software: Fundamentos de computación, Ingeniería y gestión de software, Infraestructura, seguridad y gestión tecnológica e Investigación y desarrollo profesional. Los núcleos estructurantes presentados guardan relación con los lineamientos emitidos por la Association for Computing Machinery – Institute of Electrical and Electronics Engineers (ACM-IEEE versión 2015), que promueve, entre otras cosas, un catálogo de conceptos y criterios en torno a las diferentes disciplinas, programas o carreras de las Ciencias de la Computación que han surgido como parte del avance vertiginoso de las Tecnologías de la Información y Comunicación.

Materias de la Malla Curricular Activas:
El currículo incluye asignaturas de ciencias básicas como Cálculo Diferencial e Integral , Química , y Álgebra Lineal. En el núcleo de especialidad se encuentran materias como Fundamentos de Programación , Fundamentos de la Ingeniería de Software , Programación Orientada a Objetos , Estructura de Datos , Sistemas de Bases de Datos , y Sistemas Operativos.Para el desarrollo avanzado, la malla contempla Programación Web , Desarrollo Web Avanzado , Desarrollo de Aplicaciones Móviles , y Aplicaciones Distribuidas. En el eje de gestión y arquitectura, destacan Modelos de Procesos de Desarrollo de Software , Ingeniería de Requisitos de Software , Análisis y diseño de software , Arquitectura de Software , Construcción y Evolución del Software , Pruebas de Software , y Gestión de Proyectos de Software."""

def main():
    print("Iniciando script utilitario de ingesta maestra...")
    
    # 1. Configuración de Rutas
    # Subimos un nivel porque el script ahora está dentro de 'scripts/'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, "maestro_software.txt")
    
    # 2. Creación del Archivo Físico
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(TEXTO_MAESTRO)
    print(f"[1/3] Archivo físico creado exitosamente en: {file_path}")
    
    # 3. Creación del Documento y Asignación de Metadatos Obligatorios
    doc = Document(
        page_content=TEXTO_MAESTRO,
        metadata={
            "tipo": "documento_maestro",
            "carrera": "Ingeniería de Software",
            "source": file_path
        }
    )
    print("[2/3] Objeto Document creado con metadatos requeridos.")
    
    # 4. Configuración e Inserción en ChromaDB
    persist_directory = os.path.join(base_dir, "chroma_data")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    vector_db.add_documents([doc])
    print(f"[3/3] Inserción vectorial exitosa en la base de datos ChromaDB ({persist_directory}).")
    print("🚀 Proceso de ingesta finalizado con éxito.")

if __name__ == "__main__":
    main()
