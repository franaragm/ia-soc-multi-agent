from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .utils import get_env
from config_base import (
    OPENAI_LLM_MODEL,
    GOOGLE_LLM_MODEL,
)

OPENAI_API_KEY = get_env("OPENAI_API_KEY")
GOOGLEAI_API_KEY = get_env("GOOGLEAI_API_KEY")

# ============================================================
# CLIENTES LLM
# ============================================================

def llm_chain_openai(model: str | None = None, temperature: float = 0.7,) -> ChatOpenAI:
    """
    Devuelve un objeto ChatOpenAI configurado para OpenAI. Compatible con LLMChain, RouterChain, MultiPromptChain, agentes, etc.
    
    :param model: Modelo a usar (ej. "gpt-3.5-turbo"). Si no se especifica, se usará el valor por defecto de OPENAI_LLM_MODEL.
    :type model: str | None
    :param temperature: Temperatura para la generación de texto (entre 0 y 1). Controla la creatividad de las respuestas. Valor por defecto: 0.7.
    :type temperature: float
    :return: Objeto ChatOpenAI configurado
    :rtype: Any
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no está configurada.")
    
    model_to_use = model or OPENAI_LLM_MODEL

    llm_params = {
        "api_key": OPENAI_API_KEY,
        "temperature": temperature,
    }
    
    try:
        return ChatOpenAI(model=model_to_use, **llm_params)
    except Exception as e:
        raise RuntimeError(f"Error inicializando ChatOpenAI con el modelo '{model_to_use}'.") from e

def llm_chain_google(model: str | None = None, temperature: float = 0.7,) -> ChatGoogleGenerativeAI:
    """
    Devuelve un objeto ChatGoogleGenerativeAI configurado para Google Gemini. Compatible con LLMChain, RouterChain, MultiPromptChain, agentes, etc.
    
    :param model: Modelo a usar (ej. "gemini-1.5-pro"). Si no se especifica, se usará el valor por defecto de GOOGLE_LLM_MODEL.
    :type model: str | None
    :param temperature: Temperatura para la generación de texto (entre 0 y 1). Controla la creatividad de las respuestas. Valor por defecto: 0.7.
    :type temperature: float
    :return: Objeto ChatGoogleGenerativeAI configurado
    :rtype: Any
    """
    if not GOOGLEAI_API_KEY:
        raise ValueError("GOOGLEAI_API_KEY no está configurada.")
    
    model_to_use = model or GOOGLE_LLM_MODEL

    llm_params = {
        "api_key": GOOGLEAI_API_KEY,
        "temperature": temperature,
    }

    try:
        return ChatGoogleGenerativeAI(model=model_to_use, **llm_params)
    except Exception as e:
        raise RuntimeError(f"No se pudo inicializar el modelo Google '{model_to_use}'.") from e
