"""
Construye la 'Base de Oro': un documento vectorial por cada indicador del CACES.

Tres decisiones de diseño, todas correcciones de errores reales:

1. No se trocea por caracteres. Cada bloque '=== INDICADOR n ===' entra completo, así la
   recuperación devuelve siempre todos los elementos fundamentales y nunca la mitad.
2. Cada documento lleva metadatos (`tipo`, `indicador`, `marcadores`, `campos`). Sin ellos
   la búsqueda por similitud de la norma podía devolver el documento maestro, que vive en
   la misma colección de Chroma, y el LLM evaluaba contra un texto que no era la norma.
3. Los MARCADORES y CAMPOS viajan en los metadatos, no en el texto: los usa el código para
   comprobar la plantilla y los campos vacíos. El LLM sólo recibe el criterio.

La base se borra y se recrea. Sin eso, cada ejecución acumulaba duplicados.
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

# Claves que se extraen del bloque y NO se envían al LLM.
CLAVES_DE_MAQUINA = ("ESTADO", "MARCADORES", "CAMPOS")


def _leer_clave(bloque: str, clave: str) -> str:
    encontrado = re.search(rf"^{clave}:(.*)$", bloque, re.MULTILINE)
    return encontrado.group(1).strip() if encontrado else ""


def _criterio(bloque: str) -> str:
    """El texto que verá el LLM: sin la cabecera de máquina."""
    lineas = [l for l in bloque.split("\n")
              if not any(l.startswith(c + ":") for c in CLAVES_DE_MAQUINA)]
    return "\n".join(lineas).strip()


def trocear_por_indicador(texto: str):
    """Devuelve (documentos de indicador, texto de reglas generales)."""
    corte = texto.find(CABECERA_REGLAS)
    cuerpo, reglas = (texto[:corte], texto[corte:]) if corte != -1 else (texto, "")

    documentos = []
    coincidencias = list(CABECERA_INDICADOR.finditer(cuerpo))
    for i, encontrado in enumerate(coincidencias):
        fin = coincidencias[i + 1].start() if i + 1 < len(coincidencias) else len(cuerpo)
        bloque = cuerpo[encontrado.start():fin].strip()
        documentos.append(Document(
            page_content=_criterio(bloque),
            metadata={
                "tipo": "norma",
                "indicador": int(encontrado.group(1)),
                "nombre": encontrado.group(2).strip(),
                "estado": _leer_clave(bloque, "ESTADO") or "SEMANTICO",
                # Chroma no admite listas en los metadatos: se guardan como texto.
                "marcadores": _leer_clave(bloque, "MARCADORES"),
                "campos": _leer_clave(bloque, "CAMPOS"),
            },
        ))
    return documentos, reglas.strip()


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_norma = os.path.join(base_dir, "data", "caces_2024_oficial.txt")
    persist_directory = os.path.join(base_dir, "chroma_data")

    if not os.path.exists(ruta_norma):
        print(f"Error: no se encontró {ruta_norma}")
        raise SystemExit(1)

    with open(ruta_norma, encoding="utf-8") as f:
        texto = f.read()

    documentos, reglas = trocear_por_indicador(texto)
    if not documentos:
        print("Error: no se encontró ningún bloque '=== INDICADOR n: ... ==='.")
        raise SystemExit(1)

    if reglas:
        documentos.append(Document(
            page_content=reglas,
            metadata={"tipo": "reglas", "indicador": 0, "nombre": "Reglas generales",
                      "estado": "", "marcadores": "", "campos": ""},
        ))
    else:
        print("Aviso: no se encontró el bloque de REGLAS GENERALES DE EVALUACIÓN.")

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
    Chroma.from_documents(documents=documentos, embedding=embeddings,
                          persist_directory=persist_directory)

    for doc in documentos:
        meta = doc.metadata
        campos = len([c for c in meta["campos"].split(";") if c.strip()])
        print(f"  [{meta['tipo']:6}] indicador {meta['indicador']:>2} | {len(doc.page_content):>4} chars "
              f"| {meta['estado']:12} | {campos:>2} campos | {meta['nombre']}")
    print(f"\nBase de Oro creada en '{persist_directory}' con {len(documentos)} documentos.")
    print("Ejecuta ahora: python scripts/ingestar_maestro.py")


if __name__ == "__main__":
    main()
