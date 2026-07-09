"""
Inserta el Documento Maestro de la carrera (perfil de egreso y asignaturas) en ChromaDB.

Dos correcciones sobre la versión anterior:

1. Es idempotente. Antes, cada ejecución añadía otra copia del maestro a la colección.
2. La lista de asignaturas se lee de `data/asignaturas_malla.txt`, generado desde la malla
   oficial por `scripts/extraer_asignaturas.py`. El resumen escrito a mano omitía
   asignaturas reales (por ejemplo "Aplicaciones Basadas en el Conocimiento"), de modo que
   sus sílabos no podían verificarse contra nada.

Ejecutar SIEMPRE después de `crear_base_oro.py`, que borra y recrea el directorio.
"""
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERFIL_DE_EGRESO = """DOCUMENTO MAESTRO: PERFIL Y MALLA CURRICULAR - INGENIERÍA DE SOFTWARE
Perfil de Egreso:
El futuro profesional en Ingeniería de Software utilizará una sólida formación en cada uno de los núcleos básicos de la carrera, desarrollando las competencias necesarias para resolver problemas en cualquier área de su campo profesional. Se identifican los siguientes núcleos estructurantes: Fundamentos de computación, Ingeniería y gestión de software, Infraestructura, seguridad y gestión tecnológica, e Investigación y desarrollo profesional. Guardan relación con los lineamientos de la Association for Computing Machinery e Institute of Electrical and Electronics Engineers (ACM-IEEE 2015)."""


def cargar_asignaturas(base_dir: str) -> list:
    ruta = os.path.join(base_dir, "data", "asignaturas_malla.txt")
    if not os.path.exists(ruta):
        print(f"Aviso: no existe {ruta}. Genéralo con scripts/extraer_asignaturas.py.")
        return []
    with open(ruta, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def main():
    print("Ingesta del documento maestro...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    asignaturas = cargar_asignaturas(base_dir)
    texto = PERFIL_DE_EGRESO
    if asignaturas:
        texto += (f"\n\nAsignaturas de la malla curricular vigente ({len(asignaturas)}):\n"
                  + "; ".join(asignaturas))

    ruta_maestro = os.path.join(data_dir, "maestro_software.txt")
    with open(ruta_maestro, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"[1/3] Archivo escrito en {ruta_maestro} ({len(asignaturas)} asignaturas).")

    doc = Document(page_content=texto, metadata={
        "tipo": "documento_maestro", "carrera": "Ingeniería de Software",
        "indicador": -1, "nombre": "Documento maestro",
        "estado": "", "marcadores": "", "campos": "",
    })
    print("[2/3] Documento creado con sus metadatos.")

    persist_directory = os.path.join(base_dir, "chroma_data")
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
    )

    # Idempotente: sin esto, cada ejecución añade otra copia y la base acumula maestros.
    previos = vector_db.get(where={"tipo": "documento_maestro"})
    if previos["ids"]:
        vector_db.delete(ids=previos["ids"])
        print(f"[2.5/3] Eliminados {len(previos['ids'])} maestro(s) anteriores.")

    vector_db.add_documents([doc])
    print(f"[3/3] Inserción vectorial completada en {persist_directory}.")
    # Sin emojis: la consola de Windows usa cp1252 y lanza UnicodeEncodeError.
    print("Ingesta finalizada con exito.")


if __name__ == "__main__":
    main()
