# Guía de Despliegue Gratuito para Portafolio — Auditor IA CACES

Esta guía detalla el procedimiento paso a paso para desplegar el sistema completo (**Frontend + Backend + Worker Celery + Base de Conocimiento RAG**) en plataformas en la nube **100% gratuitas**, permitiendo que reclutadores, docentes o evaluadores prueben el sistema en vivo desde tu portafolio web.

---

## 1. Arquitectura del Despliegue en la Nube

Para maximizar los planes gratuitos (*Free Tier*) sin costos de infraestructura:

```
[Usuario / Portafolio]
        │
        ▼ (HTTPS)
┌────────────────────────────────────────┐
│           FRONTEND EN VERCEL           │  ──► Costo: $0/mes (Hobby Plan)
│     Next.js 16 + TailwindCSS 4         │  ──► Auto-deploy desde GitHub
└──────────────────┬─────────────────────┘
                   │
                   ▼ (REST API / JSON / Multipart)
┌────────────────────────────────────────┐
│     BACKEND EN RENDER / KOYEB / HF     │  ──► Costo: $0/mes (Free Web Service)
│  ┌──────────────────────────────────┐  │  ──► Dockerfile Todo-en-Uno
│  │ FastAPI (Gateway HTTP)           │  │  ──► Celery Worker + Redis embebido
│  │ Celery Worker (Pipeline IA)      │  │  ──► ChromaDB autoconstruido al boot
│  │ Redis local (Cola distribuida)   │  │
│  └──────────────────────────────────┘  │
└──────────────────┬─────────────────────┘
                   │
                   ▼ (APIs Gratuitas)
┌────────────────────────────────────────┐
│        APIs DE INTELIGENCIA            │
│  • Groq Cloud (Llama 3.3 70B - Free)   │
│  • Google AI (Gemini Embeddings - Free)│
└────────────────────────────────────────┘
```

---

## 2. Preparación Previa y Claves de API

Antes de comenzar, asegúrate de tener a mano:

1. **Cuenta de GitHub:** Con el código del repositorio en [Haptax/tesis_portafolio](https://github.com/Haptax/tesis_portafolio).
2. **Groq API Key:** [console.groq.com/keys](https://console.groq.com/keys) (Plan gratuito con cuota generosa de `llama-3.3-70b-versatile`).
3. **Google Gemini API Key:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (Plan gratuito para `models/gemini-embedding-001`).

---

## 3. Paso a Paso: Despliegue del Backend

### Despliegue en Render.com (Free Web Service con Docker)

1. Regístrate o inicia sesión en [Render.com](https://render.com).
2. Haz clic en **New +** y selecciona **Web Service**.
3. Conecta tu repositorio de GitHub: `Haptax/tesis_portafolio`.
4. Configura los siguientes campos:
   - **Name:** `tesis-backend` (o el subdominio asignado, ej: `tesis-ec9m`).
   - **Region:** Elige la más cercana (e.g. *Ohio (US East)* u *Oregon (US West)*).
   - **Branch:** `main` (o `portafolioMiguel`).
   - **Root Directory:** Deja en blanco o pon `backend` (o usa el Dockerfile de la raíz/backend).
   - **Runtime:** Selecciona **Docker**.
   - **Dockerfile Path:** `backend/Dockerfile`.
   - **Docker Context Path:** `backend`.
   - **Instance Type:** **Free** (0.5 CPU, 512 MB RAM).
5. Despliega la sección **Environment Variables** y agrega:
   | Clave | Valor |
   |---|---|
   | `GROQ_API_KEY` | `gsk_tu_clave_de_groq_aqui` |
   | `GOOGLE_API_KEY` | `AIzaSy_tu_clave_de_gemini_aqui` |
   | `PORT` | `8000` |
6. Haz clic en **Create Web Service**.
7. Render compilará el contenedor Docker, construirá la Base de Oro automáticamente y levantará FastAPI + Celery.
8. Una vez terminado el despliegue (marcado como *Live*), copia la URL pública generada (ejemplo: `https://auditor-caces-api.onrender.com`).

---

## 4. Paso a Paso: Despliegue del Frontend

### Despliegue en Vercel

1. Inicia sesión en [Vercel](https://vercel.com) con tu cuenta de GitHub.
2. Haz clic en **Add New...** $\rightarrow$ **Project**.
3. Importa tu repositorio: `Haptax/tesis_portafolio`.
4. En la configuración del proyecto:
   - **Framework Preset:** `Next.js`.
   - **Root Directory:** Haz clic en *Edit* y selecciona la carpeta `frontend` (sin barra final).
5. Despliega la sección **Environment Variables** y añade:
   | Clave | Valor |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | La URL de tu backend en Render (ej: `https://tesis-ec9m.onrender.com`) |
6. Haz clic en **Deploy**.
7. En aproximadamente 1 minuto, Vercel te entregará la URL pública de tu aplicación.

---

## 5. Recomendaciones Clave para tu Portafolio

### 1. Manejo del "Cold Start" (Suspensión en Render Free)
Los servicios web gratuitos de Render entran en reposo si no reciben tráfico durante 15 minutos. La primera petición tras un periodo de inactividad puede tardar unos 30-50 segundos en despertar el contenedor.
* **Tip:** Puedes configurar un monitor de pings gratuito cada 10 minutos con [UptimeRobot](https://uptimerobot.com) o [Cron-Job.org](https://cron-job.org) apuntando al endpoint raíz `https://tu-backend.onrender.com/` para mantener el backend siempre activo y caliente.

### 2. Documentos Demo para Visitantes
Para que cualquier reclutador o evaluador pueda probar el sistema inmediatamente sin tener que buscar PDFs académicos en su computadora:
- Agrega en tu portafolio un enlace o botón de descarga con 2 o 3 documentos de ejemplo (un sílabo válido, una malla curricular y un documento trampa/ajeno a la carrera).

### 3. Límites de Tasa de Groq
El tier gratuito de Groq tiene un límite de 100,000 tokens/día. Gracias a las **compuertas de cortocircuito**, los documentos inválidos o rechazados consumen 0 tokens, y los documentos que superan el límite diario son aislados limpiamente sin crashear el sistema.

---

## 6. Verificación del Despliegue

1. Abre la URL de Vercel en tu navegador.
2. Inicia sesión en la pantalla de bienvenida.
3. Arrastra un archivo PDF de prueba y presiona **Analizar y Clasificar**.
4. Observa el estado en tiempo real (En cola $\rightarrow$ Procesando $\rightarrow$ Completado con tarjeta de veredicto y porcentaje interactivo).
