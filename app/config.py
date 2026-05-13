import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

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
    WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY")
    WEBHOOK_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("WEBHOOK_ALLOWED_ORIGINS", "http://localhost:8501").split(",")]
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'app' / 'soc_incidents.db'}")
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 10))
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60))

    # URLs de API para dashboard
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{WEBHOOK_PORT}")
    API_HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
    API_INCIDENTS_ENDPOINT = f"{API_BASE_URL}/incidents"
    API_WEBHOOK_ALERT = f"{API_BASE_URL}/webhook/alert"
    
    # Timeouts (segundos)
    API_HEALTH_TIMEOUT = 5
    API_INCIDENTS_TIMEOUT = 10
    API_WEBHOOK_TIMEOUT = 15
    
    # Límites de UI
    INCIDENTS_MIN_LIMIT = 5
    INCIDENTS_MAX_LIMIT = 50
    INCIDENTS_DEFAULT_LIMIT = 10
    
    # Tiempos de espera esperados
    EXPECTED_ANALYSIS_TIME = 90  # segundos
    
    # Alertas
    ACTIVE_ALERT_MAX_AGE = 300  # 5 minutos
    COMPLETED_ALERTS_TO_SHOW = 3
    
    # Opciones de formulario
    ALERT_TYPES = [
        "Malware Detection",
        "Phishing Attempt",
        "Unauthorized Access",
        "Port Scan",
        "Suspicious Activity"
    ]
    SEVERITY_LEVELS = ["Critical", "High", "Medium", "Low"]
    PRIORITY_OPTIONS = ["Normal", "Urgente"]
    
    # Filtros de tiempo
    TIME_FILTERS = {
        "Última hora": 1,  # horas
        "Últimas 24h": 24,
        "Última semana": 168,  # horas
    }
    
    # Palabras clave de análisis
    TRUE_POSITIVE_KEYWORDS = ["VERDADERO POSITIVO", "TRUE POSITIVE"]
    FALSE_POSITIVE_KEYWORDS = ["FALSO POSITIVO", "FALSE POSITIVE"]
    EMAIL_SENT_KEYWORDS = ["EMAIL ENVIADO", "EMAIL SENT"]
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10

    # Validación de configuración crítica
    @classmethod
    def validate_required_config(cls):
        required_keys = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
            ("VIRUSTOTAL_API_KEY", cls.VIRUSTOTAL_API_KEY),
            ("MAILTRAP_USERNAME", cls.MAILTRAP_USERNAME),
            ("MAILTRAP_PASSWORD", cls.MAILTRAP_PASSWORD),
            ("WEBHOOK_API_KEY", cls.WEBHOOK_API_KEY),
        ]
       
        missing_keys = [key for key, value in required_keys if not value]

        if missing_keys:
            raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_keys)}")
        
        return True
    
config = Config()