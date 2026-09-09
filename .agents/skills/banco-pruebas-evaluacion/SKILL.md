---
name: banco-pruebas-evaluacion
description: >-
  Guía operativa para ejecutar el banco de pruebas determinista sin consumo de cuota de LLM
  y realizar la evaluación experimental (Objetivo Específico 3 de la tesis) con métricas de desempeño.
---

# Runbook: Banco de Pruebas y Evaluación Experimental (OE3)

Este skill define el procedimiento para validar la capa determinista del sistema sin consumir tokens de Groq, así como la metodología para medir la exactitud del juicio semántico del LLM contra el *ground truth* etiquetado.

---

## 1. Banco de Pruebas Determinista (Capa 1 y Compuertas)

El script `backend/scripts/banco_pruebas.py` evalúa de extremo a extremo la extracción por coordenadas, el enrutamiento a indicadores, la validación de plantillas, la pertinencia institucional y la detección de campos vacíos sobre el corpus de prueba.

### Ejecución Rápida
```bash
cd backend
python scripts/banco_pruebas.py
```

### Qué valida el banco de pruebas:
1. **Detección de Indicador:** Verifica que los documentos oficiales (Perfil, Proyecto, Malla, Sílabo, Guía) se clasifiquen en su indicador correspondiente (1, 2, 3, 4, 6) sin colisiones léxicas.
2. **Reconocimiento de Plantilla:** Comprueba que las plantillas oficiales se acepten y que documentos ajenos o no académicos sean rechazados con veredicto `PLANTILLA NO RECONOCIDA`.
3. **Pertinencia a la Carrera de Software:**
   - Comprueba la coincidencia contra las 44 asignaturas de `backend/data/asignaturas_malla.txt`.
   - Verifica que sílabos de otras carreras (e.g. Mecatrónica, Electrónica) sean marcados como `NO CUMPLE` por falta de pertinencia.
4. **Trampas de Campos Vacíos:**
   - Verifica que un formulario en blanco o con campos omitidos sea detectado con exactitud sin confundir los rótulos impresos con contenido (`ROTULOS_DE_PLANTILLA`).
   - Comprueba el umbral de `_plantilla_vacia`: si más del 50% de los campos obligatorios están en blanco, emite `NO CUMPLE` antes de invocar al LLM.

---

## 2. Inspección Detallada de Campos Extraídos

Para auditar individualmente los pares etiqueta→valor resueltos por `pdfminer.six` en un documento específico:

```bash
cd backend
python scripts/evaluar_campos.py ver <ID_DOCUMENTO_O_RUTA>
```

Muestra en consola la lista completa de campos localizados y el valor asignado a cada uno, facilitando la depuración geométrica de desplazamientos verticales u horizontales.

---

## 3. Evaluación Experimental del LLM (Capa 2 y Métricas OE3)

Para evaluar la concordancia del juicio semántico del modelo frente al dictamen de expertos humanos (*ground truth*):

### Métricas de Evaluación
1. **Índice de Jaccard ($J$):** Mide la similitud de conjuntos entre los elementos marcados como cumplidos por el modelo vs el ground truth.
   $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
2. **Kappa de Cohen ($\kappa$):** Mide el acuerdo inter-evaluador corrigiendo el acuerdo por azar.
3. **Precisión, Exhaustividad y F1-Score:** Evaluados a nivel de cada elemento fundamental del indicador.

### Scripts de Medición
```bash
cd backend

# 1. Evaluación de similitud de checklist con Jaccard
python scripts/evaluar_jaccard.py

# 2. Experimento de tablas del sílabo (secciones 3-10)
python scripts/experimento_tablas.py
```

---

## 4. Invariantes para la Evaluación Experimental

- **Determinismo en Capa 1:** Los resultados de extracción de texto, cajas y campos deben ser 100% deterministas e idénticos entre ejecuciones.
- **Temperatura del LLM:** Se fija en `temperature=0` para reducir la variabilidad estocástica, aunque Groq Llama 3.3 puede presentar ligeras variaciones de redacción en el `analisis_libre`.
- **Cero Tokens en Rechazos:** Asegurar que los casos de prueba de documentos ajenos o plantillas no reconocidas no generen llamadas al API de Groq ni consuman cuota.
