import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys principales
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
    
    # Mailtrap Configuration
    MAILTRAP_SMTP_HOST = os.getenv("MAILTRAP_SMTP_HOST", "sandbox.smtp.mailtrap.io")
    MAILTRAP_SMTP_PORT = int(os.getenv("MAILTRAP_SMTP_PORT", 2525))
    MAILTRAP_USERNAME = os.getenv("MAILTRAP_USERNAME")
    MAILTRAP_PASSWORD = os.getenv("MAILTRAP_PASSWORD")
    
    # SOC Email Configuration
    SOC_EMAIL_RECIPIENT = os.getenv("SOC_EMAIL_RECIPIENT")
    SOC_EMAIL_SENDER = os.getenv("SOC_EMAIL_SENDER")
    
    # Configuración del SOC
    WEBHOOK_PORT = 8000
    DASHBOARD_PORT = 8501

    # Validación de configuración crítica
    @classmethod
    def validate_required_config(cls):
        required_keys = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
            ("VIRUSTOTAL_API_KEY", cls.VIRUSTOTAL_API_KEY),
            ("MAILTRAP_USERNAME", cls.MAILTRAP_USERNAME),
            ("MAILTRAP_PASSWORD", cls.MAILTRAP_PASSWORD),
        ]
       
        missing_keys = [key for key, value in required_keys if not value]

        if missing_keys:
            raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_keys)}")
        
        return True
    
config = Config()