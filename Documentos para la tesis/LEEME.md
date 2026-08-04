# Documentos para la tesis

Material del **documento** escrito: el manuscrito y su bibliografía. Lo navegan los agentes
`tesis-escritura` (redacta y revisa) y `curador-fuentes` (valida lo que entra).

## Las carpetas

| Carpeta | Qué va aquí | Quién la toca |
|---|---|---|
| `00_manuscrito/` | El avance de la tesis (`.docx`). **Un solo archivo vivo.** Las versiones viejas se borran o se archivan fuera del repo. | El usuario, desde Word |
| `01_referencias/` | Fuentes **validadas**: pasaron el filtro de calidad y pertinencia. Prefijo `[nn]` = etiqueta de estante. | `curador-fuentes` propone, el usuario mueve |
| `02_candidatas/` | Lo que acabas de descargar y **aún no ha pasado por el curador**. Zona de entrada: si dudas, déjalo aquí. | El usuario |
| `03_descartadas/` | Rechazadas o redundantes. **No se borran de inmediato**: se guardan con su motivo en `MOTIVOS.md` para no volver a traerlas por error. | `curador-fuentes` |
| `04_normativa/` | Fuente **primaria**: CACES, CES, INQAAHE, reglamentos ESPE. No es bibliografía de respaldo. | El usuario |

## Cómo entra una fuente nueva

1. La sueltas en **`02_candidatas/`**.
2. Pides el curador. Ejecuta el inventario y devuelve un veredicto por archivo:
   ```bash
   venv/Scripts/python.exe scripts/extraer_texto_tesis.py
   venv/Scripts/python.exe scripts/revisar_fuentes.py
   ```
3. Según el veredicto pasa a **`01_referencias/`** (con su etiqueta `[nn]`) o a **`03_descartadas/`**.

## Cómo se nombran los archivos

**Sólo se renombra lo que fue aceptado.** Un archivo estrena nombre al entrar en
`01_referencias/`, nunca antes:

| Carpeta | Nombre |
|---|---|
| `02_candidatas/` | El de origen. Sin tocar: el nombre feo delata que aún no está validado. |
| `01_referencias/` | El formato de abajo. |
| `03_descartadas/` | **El de origen, intacto.** Si vuelves a descargar ese archivo llegará con el mismo nombre y se reconocerá como ya rechazado. Renombrarlo borraría esa pista. |

```
AÑO - Autor - Título corto [nn].pdf
```
Ejemplo: `2024 - Mayr et al - Determinantes de adopcion de IPA [35].pdf`

El año va delante **a propósito**: la carpeta se ordena cronológicamente y de un vistazo ves si
tu bibliografía está actualizada. Para LLMs, RAG e IPA se exigen fuentes de 2023 en adelante, y
con este orden el material viejo se agrupa solo al principio.

| Parte | Regla |
|---|---|
| **AÑO** | El de **publicación**, nunca el de descarga. Cuidado: los PDFs de repositorio traen un «Download date» que no es el año del trabajo. Si no se puede determinar, `SIN DATOS`. |
| **Autor** | Sólo el apellido. Un autor → `Termite`. Dos → `Ben Hassen y Bellaaj`. Tres o más → `Mayr et al`. |
| **Título corto** | En español, 4-8 palabras, lo justo para reconocerlo. No es el título completo. |
| **`[nn]`** | Etiqueta de estante, al final y entre corchetes. **Sólo en `01_referencias/`**; las candidatas no llevan porque aún no están validadas. |
| **Caracteres** | Sin tildes ni `ñ`, y nada de `: ? " < > \| * / \`. Windows los prohíbe o los guarda en formas Unicode distintas que rompen las búsquedas. |

## Sobre el sufijo `[nn]`

**Es una etiqueta de estante, no el número IEEE definitivo.** En IEEE el número lo fija el
**orden de primera aparición en el texto**, así que sólo se cierra cuando la cita está insertada
en el manuscrito. Insertar una cita a mitad del documento renumera todo lo posterior en cascada.
Sirve para saber de qué archivo hablamos, nada más.

## Reglas

- **Un trabajo, un archivo.** Si el mismo paper aparece en PDF y en HTML, se conserva el más
  completo (el que más texto extrae) y el otro va a `03_descartadas/`.
- **Nada suelto en la raíz.** Todo archivo vive en una de las cinco carpetas.
- Nada de esto se versiona en git: los `*.pdf` están en `.gitignore`.
- El texto plano buscable se genera aparte, en `docs/conocimiento/tesis-escritura/texto/`,
  espejando esta misma estructura.
