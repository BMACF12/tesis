# Descartadas — por qué

Nada se borra sin dejar constancia: si una fuente vuelve a aparecer en una búsqueda, aquí está
la razón por la que ya se rechazó. **Estos archivos se pueden borrar cuando quieras**; sólo
conserva este registro.

**Conservan su nombre de origen a propósito.** Sólo se renombra lo que se acepta; así, si el
mismo archivo se vuelve a descargar, llega con este mismo nombre y se reconoce como ya rechazado.

| Archivo | Motivo | Sustituido por |
|---|---|---|
| `T-ESPE-052813.pdf` | Copia idéntica (mismo MD5 `4742afca`) | `2022 - Lopez Navas - RPA en logistica y bodega con SAP [33].pdf` |
| `s12525-024-00737-9.pdf` | Copia idéntica (mismo MD5 `735dd855`) | `2024 - Mayr et al - Determinantes de adopcion de IPA [35].pdf` |
| `sustainability-14-08804.pdf` | Copia idéntica (mismo MD5 `da32a0e2`) | `2022 - Lievano-Martinez et al - IPA aplicado a manufactura [37].pdf` |
| `Automatización Inteligente … n8n …pdf` | Mismo trabajo, archivo distinto. **Ambas copias son ilegibles** (11 caracteres extraídos) | `SIN DATOS - n8n automatizacion administrativa universitaria [36].pdf` |
| `[39]S1877050926007957.htm` | Versión HTML recortada del mismo DOI `10.1016/j.procs.2026.03.200`: 2 654 caracteres frente a 69 437 del PDF | `2026 - Ben Hassen y Bellaaj - Copilot para Jira en gestion agil [39].pdf` |
| `Modelo-generico-para-la-evaluación-…-carreras-de-grado.pdf` | Copia idéntica del modelo CACES (mismo MD5 `41996f42`) | `04_normativa/2024 - CACES - Modelo generico evaluacion entorno de aprendizaje carreras de grado.pdf` |

## Ronda de 2026-07-22 — candidatas de ISO 25010, métricas, multietiqueta y Jaccard

| Archivo | Motivo | Sustituido por |
|---|---|---|
| `ISO-IEC-25010-2011.pdf` | Preview de standards.iteh.ai (13 pág., corta en la cláusula 3.6). Misma norma, misma edición 2011 y **mismo número IEEE** que el archivo completo: una norma ocupa una sola entrada bibliográfica. **Valor residual: es el único texto ISO oficial e inalterado del corpus** — sirve para contrastar la traducción automática en las cláusulas 1-3.6. No lo borres a la ligera | `[42]` |
| `Dialnet-UsoDeLaNormaISO25010…-10343572.pdf` | Tercera fuente sobre ISO 25010; conocimiento de la norma de segunda mano desde `iso25000.com`, dominio ajeno (realidad aumentada educativa), indexación débil | `[41]` y `[42]` |
| `Clasificacion de documentos con Inteligencia Artificial.pdf` | TFG (Univ. La Laguna, 2023). Usa accuracy/precision/recall/F1 sin definirlas; no es autoridad metodológica | `[47]`, `[48]` |
| `M.Orois_García_2020_Técnicas_de_aprendizaje_máquina.pdf` | TFG (UDC, 2020). Define Jaccard en una viñeta de segunda mano y lo usa como atributo en redes de datos, no como métrica de evaluación. Dominio sin relación | — |
| `Análisis, interpretación, clasificación y búsqueda automática de la gestión documental.pdf` | Monografía de especialización (UNAD, 2025) **e ilegible** (52 caracteres extraídos). Mismo terreno que `[44]`, sin indexación ni verificabilidad | `[44]` |
| `Dialnet-ClasificacionDeDatos-5678848.pdf` | Escaneo sin capa de texto (8 caracteres). Trata de clustering difuso c-means, no de clasificación supervisada. Tecnología en Marcha vol. 12, ~1998 | — |
| `content.pdf` | Monografía de especialización (UNIMINUTO, 2025) sobre selección de herramienta RPA comercial. Terreno saturado por `[33]`, `[34]` y `[38]`, sin dato nuevo | `[33]`, `[34]`, `[38]` |
| `SISTEMA AUTOMATIZADO … PQR …-1.pdf` | Tesis de maestría (UNAB, 2025). Define F1 en glosario, no en marco metodológico. Antecedentes grises ya saturados por `[5]`, `[12]`, `[13]`, `[15]` | — |
| `out.pdf` | RISTI E47/2022, calidad aceptable pero **sin ancla**: compara UiPath/Automation Anywhere/Agility/IRPA y el manuscrito no menciona ninguna plataforma RPA comercial. Reevaluar si se añade una sección de selección de plataforma | — |
| `Lopez Robayo, William Alexander 2025` | Proyecto de grado (Univ. Distrital, 2025), vigilancia tecnológica de mercado sobre IDP. 0 apariciones de Jaccard, 25010, multietiqueta y matriz de confusión en sus 134 219 caracteres | — |

## Pendiente

- **`[36]` (n8n) no tiene capa de texto en ninguna de sus dos copias.** No se puede verificar su
  contenido ni comprobar que respalda lo que se le atribuya. O se consigue una copia con texto,
  o esa fuente no debería citarse.
