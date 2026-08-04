# Conocimiento — `tesis-escritura`

Material del **documento** de la tesis (no del código). El agente `tesis-escritura` trabaja
sobre esta carpeta.

## Qué hay aquí

- **`texto/`** — *(generado, no editar a mano)* volcado a texto plano de todo lo que hay en
  `Documentos para la tesis/`, espejando sus subcarpetas. Existe para poder hacer `Grep` sobre
  el manuscrito y sobre los papers, cosa que ni el .docx ni el PDF permiten.
  Se regenera con:
  ```bash
  venv/Scripts/python.exe scripts/extraer_texto_tesis.py            # sólo lo que falte
  venv/Scripts/python.exe scripts/extraer_texto_tesis.py --forzar   # tras editar el .docx en Word
  ```
- **`borradores/`** — texto redactado por el agente en Markdown, listo para pegar en Word.
  El agente no puede escribir dentro del .docx.
- **`AVISOS_DE_CITACION.md`** — **léelo antes de citar**. Fuentes aceptadas que sólo se pueden
  citar de una forma concreta: la ISO 25010 en español es traducción automática y su
  terminología invierte la jerarquía del modelo; Sebastiani es preprint y su paginación no
  coincide con la publicada; el PDF de Tsoumakas no declara su sede.

## Qué colocar aquí (aportado por el usuario)

- La **rúbrica de evaluación** del trabajo de integración curricular de la ESPE.
- La **guía de estilo / plantilla institucional** (norma de citación exigida, márgenes, formato
  de tablas y figuras).
- **Actas o correcciones del tutor** (Dr. José Luis Carrillo Medina) — son la fuente de verdad
  sobre qué hay que arreglar.
- El **anteproyecto** aprobado, si el manuscrito debe rendirle cuentas.

## Fuente original

`Documentos para la tesis/` en la raíz del repo:

| Ruta | Contenido |
|---|---|
| `00_manuscrito/` | El avance del manuscrito (`.docx`) |
| `01_referencias/` | Fuentes validadas, con etiqueta de estante `[nn]` |
| `02_candidatas/` | Zona de entrada: sin validar |
| `03_descartadas/` | Rechazadas o redundantes, con `MOTIVOS.md` |
| `04_normativa/` | CACES/CES — fuente primaria |

Las reglas de esa carpeta están en su propio `LEEME.md`. El agente `curador-fuentes` decide
qué entra.

Nada de esto se versiona (los PDFs y `docs/conocimiento/**` están en `.gitignore`).
