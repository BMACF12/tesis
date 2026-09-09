---
name: base-de-oro-gestion
description: >-
  Procedimiento para crear, actualizar, indexar y mantener la base de conocimiento vectorial ("Base de Oro" en ChromaDB)
  y el documento maestro de la carrera para el sistema RAG.
---

# Runbook: Gestión de la Base de Oro (ChromaDB)

Este skill documenta la construcción, actualización y verificación de la base vectorial normativa del sistema de auditoría CACES.

---

## 1. Componentes de la Base de Oro

La Base de Oro reside en `backend/chroma_data/` y almacena tres tipos de documentos bajo una misma colección:

1. **Normativa CACES 2024 (`tipo="norma"`):** Un documento vectorial completo por cada indicador instrumentado (1, 2, 3, 4 y 6), extraído de `backend/data/caces_2024_oficial.txt`.
   - Incluye metadatos: `indicador` (int), `nombre` (str), `marcadores` (str con alternativas separadas por `;` y `|`), y `campos` (str con campos obligatorios).
2. **Reglas Globales de Auditoría (`tipo="reglas"`):** Directrices del CACES sobre severidad, evaluación de evidencias y prohibición de alucinaciones.
3. **Documento Maestro (`tipo="documento_maestro"`):** Contexto institucional de la carrera de Ingeniería de Software (misión, visión, perfil de egreso, objetivos formativos).

---

## 2. Flujo de Reconstrucción de la Base Vectorial

> [!CAUTION]
> `crear_base_oro.py` **elimina completamente** el directorio `backend/chroma_data/` y lo reconstruye desde cero. Además, si el worker de Celery está corriendo, mantendrá bloqueada la base de datos y el script fallará.

### Procedimiento Paso a Paso:

#### 1. Detener el Worker de Celery
Si el worker está activo en alguna terminal o proceso en segundo plano, presiona `Ctrl+C` para liberar el bloqueo sobre `chroma_data/`.

#### 2. (Opcional) Actualizar la Lista de Asignaturas de la Malla
Si la malla curricular oficial cambió, extrae las 44 asignaturas ejecutando:
```bash
cd backend
python scripts/extraer_asignaturas.py "ruta/a/malla_oficial.pdf"
```
Esto actualiza `backend/data/asignaturas_malla.txt`.

#### 3. Recrear los Vectores Normativos e Indicadores
```bash
cd backend
python scripts/crear_base_oro.py
```
Este script:
- Lee `backend/data/caces_2024_oficial.txt`.
- Separa las reglas generales y cada bloque de indicador.
- Extrae las directivas `MARCADORES:` y `CAMPOS:` para guardarlas como metadatos en ChromaDB (para uso exclusivo del código determinista de Capa 1).
- Genera embeddings con `models/gemini-embedding-001` de Google.

#### 4. Ingestar el Documento Maestro de la Carrera
```bash
cd backend
python scripts/ingestar_maestro.py
```
Añade el contexto institucional con metadato `tipo="documento_maestro"`.

---

## 3. Invariantes y Buenas Prácticas

- **No fragmentar por caracteres:** Cada indicador debe indexarse como un único documento integral para evitar que el checklist de elementos fundamentales quede truncado.
- **Metadatos aislados:** Los campos obligatorios y marcadores de plantilla deben residir exclusivamente en los metadatos del vector; no deben enviarse al prompt del LLM para no inducir sesgos o alucinaciones.
- **Recuperación Exacta Primero:** El sistema siempre intenta recuperar la norma usando `get(where={"indicador": N})`. La búsqueda por similitud (`similarity_search`) es sólo un respaldo y debe incluir siempre `filter={"tipo": "norma"}` para no confundir la norma con el documento maestro.
