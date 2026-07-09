"""
Construye la 'Base de Oro': un documento vectorial por cada indicador del CACES.

No se trocea por caracteres. Cada bloque '=== INDICADOR n: ... ===' entra completo
como un único Document con metadatos, de modo que la recuperación devuelva siempre
todos los elementos fundamentales del indicador y nunca la mitad.

Las REGLAS GENERALES se guardan como documento aparte (tipo="reglas"): aplican a
todos los indicadores y el prompt las inyecta siempre, no se recuperan por similitud.
"""
import os
import re
import shutil

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CABECERA_INDICADOR = re.compile(r"^=== INDICADOR (\d+): (.+?) ===$", re.MULTILINE)
CABECERA_REGLAS = "=== REGLAS GENERALES DE EVALUACIÓN"


def trocear_por_indicador(texto: str):
    """Devuelve (documentos_de_indicador, texto_de_reglas_generales)."""
    corte = texto.find(CABECERA_REGLAS)
    cuerpo, reglas = (texto[:corte], texto[corte:]) if corte != -1 else (texto, "")

    documentos = []
    coincidencias = list(CABECERA_INDICADOR.finditer(cuerpo))
    for i, encontrado in enumerate(coincidencias):
        fin = coincidencias[i + 1].start() if i + 1 < len(coincidencias) else len(cuerpo)
        bloque = cuerpo[encontrado.start():fin].strip()
        documentos.append(Document(
            page_content=bloque,
            metadata={
                "tipo": "norma",
                "indicador": int(encontrado.group(1)),
                "nombre": encontrado.group(2).strip(),
                "instrumentado": "ESTADO: INSTRUMENTADO" in bloque,
            },
        ))
    return documentos, reglas.strip()


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_norma = os.path.join(base_dir, "data", "caces_2024_oficial.txt")
    persist_directory = os.path.join(base_dir, "chroma_data")

    if not os.path.exists(ruta_norma):
        print(f"Error: no se encontró {ruta_norma}")
        return

    with open(ruta_norma, encoding="utf-8") as f:
        texto = f.read()

    documentos, reglas = trocear_por_indicador(texto)
    if not documentos:
        print("Error: no se encontró ningún bloque '=== INDICADOR n: ... ==='.")
        return

    if reglas:
        documentos.append(Document(
            page_content=reglas,
            metadata={"tipo": "reglas", "indicador": 0, "nombre": "Reglas generales",
                      "instrumentado": False},
        ))
    else:
        print("Aviso: no se encontró el bloque de REGLAS GENERALES DE EVALUACIÓN.")

    # La base se reconstruye desde cero: si no, se acumulan vectores de corridas previas.
    if os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
        except PermissionError:
            print("ERROR: no se puede borrar chroma_data porque otro proceso lo tiene abierto.")
            print("       Detén el worker de Celery (Ctrl+C) y vuelve a ejecutar este script.")
            print("       Si no lo haces, la base conserva la normativa ANTIGUA sin avisar.")
            raise SystemExit(1)
        print(f"Base anterior eliminada: {persist_directory}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    for doc in documentos:
        meta = doc.metadata
        print(f"  [{meta['tipo']:6}] indicador {meta['indicador']:>2} | "
              f"{len(doc.page_content):>5} chars | {meta['nombre']}")
    print(f"\nBase de Oro creada en '{persist_directory}' con {len(documentos)} documentos.")
    print("Ejecuta después: python scripts/ingestar_maestro.py")


if __name__ == "__main__":
    main()
