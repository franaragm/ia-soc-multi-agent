# 🎧 SOC MULTI AGENT

## 📝 Descripción


---

## 🐍 Requisitos de Python

* Python 3.13.2 (recomendado, probado en macOS Apple Silicon y Windows)
* Python 3.11 (ideal para Mac Intel)

⚠️ No usar Python 3.14+, ya que rompe compatibilidad con:

* Pydantic
* ChromaDB
* LangChain Core

---

## 📂 Estructura del proyecto

```

```


---

---

## 🚀 Instalación y uso

### 🔧 1) Crear entorno virtual y activar entorno virtual

```bash
python -m venv .venv           # crear entorno virtual
source .venv/bin/activate      # iniciar entorno virtual en macOS / Linux
.venv\Scripts\activate         # iniciar entorno virtual en Windows
```

---

### 📦 2) Instalar dependencias en el entorno virtual iniciado

Hay dos opciones, se recomienda usar `requirements.lock` para asegurar la reproducibilidad del entorno.

```bash
pip install -r requirements.txt   # instalar dependencias principales del proyecto
pip install -r requirements.lock  # instalar dependencias fijadas
```

Para fijar nuevas dependencias, añadir paquete en requeriments.txt:

```bash
pip install -r requirements.txt # Instala las dependencias listadas en requirements.txt (si hay nuevas)
pip freeze > requirements.lock  # Genera un nuevo archivo lock con las dependencias actuales
```

---

### 🔐 3) Configurar variables de entorno

Copiar y renombrar el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

Editar `.env` con tus claves:

```
OPENAI_API_KEY=API_KEY_HERE
GOOGLEAI_API_KEY=API_KEY_HERE
ENV=dev
```

> IMPORTANTE - El cliente usado en este proyecto es el de OpenAI, con lo que solo hace falta indicar OPENAI_API_KEY

#### 🔑 Obtener API keys:

* OpenAI → [https://platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys)
* Google AI → [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)

---

### ▶️ 4) Ejecutar la aplicación en el entorno virtual iniciado

```bash
streamlit run run_app.py
```

Disponible en: [http://localhost:8501](http://localhost:8501)

---


