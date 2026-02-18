from pathlib import Path

# === Rutas base ===

# Ruta absoluta a la raíz del repositorio
ROOT_DIR = Path(__file__).resolve().parent

# Carpeta de aplicación
APP_PATH = ROOT_DIR / "app"

# Modelos LLMs default
OPENAI_LLM_MODEL = "gpt-4o-mini"
GOOGLE_LLM_MODEL = "gemini-2.5-flash"
