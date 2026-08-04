# Personalización de Google Antigravity (Gemini)

Esta carpeta contiene la configuración del entorno y los agentes especializados de la tesis adaptados para **Google Antigravity (Gemini)**.

## Estructura de carpetas

*   **`rules/`**: Contiene reglas y políticas de comportamiento generales que se aplican automáticamente a la sesión principal del agente.
    *   [`rules/general.md`](file:///c:/Users/User/Desktop/tesis/.agents/rules/general.md): Reglas generales del proyecto, advertencias de venv/glob, stack técnico y flujo de lectura inicial (reemplazo directo de `CLAUDE.md`). Está configurado con `alwaysApply: true`.
*   **`agents/`**: Contiene las definiciones de los 16 agentes especializados del proyecto. Cada archivo `.md` define el nombre, la descripción y el prompt del sistema del agente para que Gemini pueda descubrirlos y delegar tareas en ellos.
    *   Todos los agentes tienen `subagent: true` para poder ser invocados a través de `/agents` o mediante la API/herramienta de subagentes.

## Equivalencia con el roster de Claude

Esta configuración es la traducción directa y compatible de la estructura anterior en `.claude/` y `CLAUDE.md`.
