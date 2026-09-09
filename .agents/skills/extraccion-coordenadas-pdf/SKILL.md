---
name: extraccion-coordenadas-pdf
description: >-
  Guía técnica y de calibración para el módulo de extracción geométrica de PDFs basada en coordenadas espaciales
  (pdfminer.six) para tablas complejas, mallas curriculares y resolución de campos etiqueta->valor.
---

# Runbook: Extracción Geométrica de PDFs por Coordenadas

Este skill documenta la lógica, calibración geométrica y algoritmos de reconstrucción visual implementados en `backend/services/extraccion.py`.

---

## 1. Justificación de Diseño: Por qué pdfminer.six sobre OCR

Los documentos institucionales de la ESPE y del CACES son generados digitalmente (Word / LaTeX / InDesign) y cuentan con capa de texto nativa:
- **OCR tradicional (Tesseract / Unstructured):**
  - Tarda ~28 segundos por documento (frente a 1.5s con pdfminer).
  - Colapsa tablas estructuradas en una sola línea plana (`Modalidad: PRESENCIAL Departamento: Área de Conocimiento: ...`), imposibilitando el emparejamiento etiqueta→valor.
  - Degrada códigos de asignaturas (`EXCTA0301` -> `EXCTAO301`).
  - Pierde etiquetas rotadas 90° (como los 8 periodos académicos ordinarios - PAO).
- **Extracción Geométrica (`pdfminer.six`):**
  - Extrae cajas contenedoras con coordenadas exactas `(x0, y0, x1, y1)`.
  - Agrupa líneas comparando centros verticales con tolerancia dinámica basada en `ALTURA_DE_LINEA = 20.0`.
  - Empareja etiquetas y valores en la misma fila horizontal o hasta 2 filas inferiores (`FILAS_DE_BUSQUEDA = 2`).

---

## 2. Algoritmos Principales en `extraccion.py`

### 2.1. Agrupación en Filas Visuales (`_agrupar_filas`)
No ordena únicamente por el borde superior `y1` porque las cajas de texto de los valores suelen ser más altas que las de las etiquetas. Compara la distancia entre centros verticales:
$$\text{centro} = \frac{y_0 + y_1}{2}$$
Dos cajas comparten fila si $|\text{centro}_{\text{caja}} - \text{centro}_{\text{ancla}}| \le 0.5 \times \min(\text{alto}, 20.0)$.

### 2.2. Reconstrucción de Etiquetas Rotadas 90° (`_enderezar`)
- Las etiquetas verticales ("Primer PAO", "UNIDAD BASICA") se extraen como secuencias de caracteres individuales invertidos.
- Se ordenan por columna `round(x / 8)` y altura `y`.
- Se reconstruyen invirtiendo el fragmento (`caja["t"][::-1]`) y uniendo fragmentos cuyo espacio vertical sea menor a `salto_maximo = 0.5 * median(alto)`.

### 2.3. Reconstrucción Celda por Celda de la Malla Curricular
- **Detección de Escala Dinámica (`escala_de_malla`):** Las mallas pueden estar exportadas a pliegos de tamaño variable (escala 1x a 3.3x). La escala horizontal ($e_x$) y vertical ($e_y$) se deduce calculando la separación mediana entre etiquetas `HPAO`:
  $$e_x = \frac{\text{paso}_x}{97.5}, \quad e_y = \frac{\text{paso}_y}{57.0}$$
- **Extracción de Asignatura:** Por cada código de asignatura que coincide con `COD_ASIGNATURA = r"^[A-Z]{5}[0-9A-Z]{4}$"`, busca:
  - Nombre a su derecha ($18 e_x \le \Delta x \le 72 e_x$).
  - Prerrequisito en el cuadrante inferior ($-8 e_x \le \Delta x \le 58 e_x$, $-26 e_y \le \Delta y \le -4 e_y$).
  - Horas y créditos en la subcolumna vertical de la etiqueta `HPAO`.

### 2.4. Resolución de Pares Etiqueta $\rightarrow$ Valor (`resolver_campos`)
- Busca primero a la derecha en la misma fila.
- Si no encuentra valor contiguo, busca verticalmente alineado en las 2 filas inferiores.
- Excluye rótulos decorativos impresos en la plantilla (`ROTULOS_DE_PLANTILLA`) para no confundir rótulos oficiales con respuestas en blanco.

---

## 3. Pruebas y Diagnóstico

Para probar cambios geométricos sin ejecutar el backend completo:
```bash
cd backend
python -c "from services.extraccion import extraer_documento; res = extraer_documento('ruta/a/documento.pdf'); print(res['texto'][:500])"
```

Para verificar si la extracción de mallas detecta todas las asignaturas:
```bash
python scripts/extraer_asignaturas.py "ruta/a/malla.pdf"
```
