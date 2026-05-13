# 🎧 SOC MULTI AGENT

## 📝 Descripción

SOC Multi-Agent es una solución de seguridad orientada a operaciones SOC que integra varios componentes para gestionar alertas reales y automatizar análisis de amenazas.

El sistema consta de:
- un dashboard interactivo construido con Streamlit para la creación y seguimiento de alertas.
- un servidor webhook en FastAPI que recibe datos de incidentes, valida payloads y orquesta el análisis.
- un flujo multi-agente basado en LangGraph/LangChain que ejecuta análisis de IOCs, evaluación de amenazas y notificación.
- un almacenamiento local SQLite para persistir incidentes, resultados y métricas de operación.
- una capa de correo de pruebas con Mailtrap para enviar notificaciones de incidente sin depender de un servicio SMTP real.

Características principales:
- validación de alertas con Pydantic y filtros de IP, URL, hash y correo electrónico.
- autenticación de webhook por `X-API-Key` y rate limiting para proteger el endpoint de ingestión.
- salud del sistema y monitoreo de APIs externas mediante endpoints `/health` y `/api-status`.
- diseño modular que separa UI, API, persistencia y lógica de agentes.

---

## 🐍 Requisitos de Python

* Python 3.13.2 (recomendado)
* Python 3.11 también soportado

⚠️ No usar Python 3.14+ porque algunas dependencias como Pydantic, ChromaDB y LangChain Core pueden perder compatibilidad.

---

## 📂 Estructura del proyecto

```
├── 📁 .pytest_cache
│   ├── 📁 v
│   ├── ⚙️ .gitignore
│   ├── 📄 CACHEDIR.TAG
│   └── 📝 README.md
├── 📁 app
│   ├── 📁 services
│   │   ├── 🐍 llm_client.py
│   │   └── 🐍 utils.py
│   ├── 🐍 agents.py
│   ├── 🐍 api_client.py
│   ├── 🐍 config.py
│   ├── 🐍 constants.py
│   ├── 🐍 dashboard.py
│   ├── 🐍 db.py
│   ├── 🐍 formatters.py
│   ├── 🐍 supervisor.py
│   ├── 🐍 tools.py
│   ├── 🐍 validators.py
│   └── 🐍 webhook_server.py
├── 📁 logs
├── 📁 tests
│   ├── 🐍 __init__.py
│   └── 🐍 test_api_client.py
├── ⚙️ .env.example
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 config_base.py
├── 📄 requirements.lock
├── 📄 requirements.txt
└── 🐍 run_app.py
```

---

## 🚀 Instalación y uso

### 1) Crear y activar entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate       # Windows
```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Configurar variables de entorno

Copia el archivo de ejemplo y rellena tus credenciales:

```bash
cp .env.example .env
```

Agrega o edita las siguientes variables en `.env`:

```env
OPENAI_API_KEY=API_KEY_HERE
TAVILY_API_KEY=API_KEY_HERE
VIRUSTOTAL_API_KEY=API_KEY_HERE
MAILTRAP_USERNAME=MAILTRAP_USERNAME
MAILTRAP_PASSWORD=MAILTRAP_PASSWORD
MAILTRAP_SMTP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_SMTP_PORT=2525
SOC_EMAIL_SENDER=soc@test.com
SOC_EMAIL_RECIPIENT=engineer.education.colab@gmail.com
WEBHOOK_API_KEY=YOUR_SECRET_API_KEY
DATABASE_URL=sqlite:///./app/soc_incidents.db
ENV=dev
```

> Nota: el servidor de correo usa Mailtrap para pruebas, no Gmail.

### 4) Iniciar el servidor webhook

```bash
uvicorn app.webhook_server:app --reload --host 0.0.0.0 --port 8000
```

### 5) Ejecutar el dashboard

```bash
streamlit run app/dashboard.py --server.port 8501
```

Accede al dashboard en:

- http://localhost:8501

El webhook API estará disponible en:

- http://localhost:8000

---

## 🌐 Endpoints importantes

* `POST /webhook/alert` — recibe alertas entrantes
* `GET /incidents` — obtiene incidentes persistidos
* `GET /health` — verifica el estado del servidor
* `GET /api-status` — muestra el estado de APIs externas

---

## 🧪 Pruebas

Ejecuta las pruebas unitarias con:

```bash
pytest tests
```

---

## 📝 Notas adicionales

* `run_app.py` actualmente es un placeholder; el dashboard se ejecuta desde `app/dashboard.py`.
* La base de datos SQLite por defecto se crea en `app/soc_incidents.db`.
* Mailtrap está configurado para pruebas SMTP y se utiliza para envíos de notificaciones.


