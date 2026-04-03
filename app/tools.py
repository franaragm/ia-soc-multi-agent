import vt
import smtplib
from email.message import EmailMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from config import config
from datetime import datetime

# Validar configuracion al importar
config.validate_required_config()

# 1. TavilySearch
search_tool = TavilySearchResults(
    max_results=3,
    tavily_api_key=config.TAVILY_API_KEY
)

# 2. Mailtrap Tool
@tool
def send_mailtrap_email(to: str, subject: str, message: str) -> str:
    """Envía un email usando Mailtrap SMTP."""

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = config.SOC_EMAIL_SENDER or "soc@test.com"
        msg["To"] = to

        # Texto fallback + HTML
        msg.set_content("Este email requiere un cliente HTML.")
        msg.add_alternative(message, subtype="html")

        with smtplib.SMTP(config.MAILTRAP_SMTP_HOST, config.MAILTRAP_SMTP_PORT) as server:
            server.starttls()
            server.login(config.MAILTRAP_USERNAME, config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        return f"Email enviado correctamente a {to}"

    except Exception as e:
        return f"Error enviando email: {str(e)}"

# 3. VirusTotal Tool
@tool
def virustotal_checker(indicator: str, indicator_type: str) -> str:
    """Analiza URLs, IPs y hashes usando la API de VirusTotal."""
    try:
        with vt.Client(config.VIRUSTOTAL_API_KEY) as client:
            if indicator_type == "url":
                url_id = vt.url_id(indicator)
                analysis = client.get_object(f"/urls/{url_id}")
            elif indicator_type == "ip":
                analysis = client.get_object(f"/ip-addresses/{indicator}")
            elif indicator_type == "hash":
                analysis = client.get_object(f"/files/{indicator}")
            else:
                return f"Tipo no soportado: {indicator_type}"
            
            stats = analysis.last_analysis_stats or {}
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 0

            if malicious > 5:
                threat_level = "MALICIOSO"
            elif malicious > 0 or suspicious > 3:
                threat_level = "SOSPECHOSO"
            else:
                threat_level = "LIMPIO"

            return f"""ANALISIS VIRUSTOTAL:
Indicador: {indicator}
Detecciones: {malicious}/{total} maliciosas, {suspicious}/{total} sospechosas
Clasificacion: {threat_level}
Análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    except Exception as e:
        return f"Error VirusTotal: {str(e)}"

# Lista de herramientas
mailtrap_tools = [send_mailtrap_email]

all_tools = [search_tool, virustotal_checker] + mailtrap_tools