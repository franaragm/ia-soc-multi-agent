import requests
from typing import Tuple, Dict, List, Optional
import logging
from app.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SOCAPIClient:
    """Cliente para interactuar con la API del SOC."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'SOC-Dashboard/2.0'})
    
    def get_server_status(self) -> Tuple[bool, Optional[Dict]]:
        """
        Verifica el estado del servidor.
        
        Returns:
            Tuple[bool, Optional[Dict]]: (servidor_online, health_data)
        """
        try:
            response = self.session.get(Config.API_HEALTH_ENDPOINT, timeout=Config.API_HEALTH_TIMEOUT)
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout conectando a health: {e}")
            return False, None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión: {e}")
            return False, None
        except Exception as e:
            logger.exception(f"Error inesperado en health check: {e}")
            return False, None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def get_incidents(self) -> List[Dict]:
        """Obtiene incidentes del servidor."""
        try:
            response = self.session.get(Config.API_INCIDENTS_ENDPOINT, timeout=Config.API_INCIDENTS_TIMEOUT)
            if response.status_code == 200:
                return response.json().get("incidents", [])
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout obteniendo incidentes: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión obteniendo incidentes: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado obteniendo incidentes: {e}")
        return []
    
    def check_alert_status(self, incident_id: str) -> Optional[Dict]:
        """Verifica el estado de una alerta específica."""
        incidents = self.get_incidents()
        for incident in incidents:
            if incident.get('incident_id') == incident_id:
                return incident
        return None
    
    def submit_alert(self, alert_payload: Dict) -> Dict:
        """Envía una alerta al servidor."""
        try:
            response = self.session.post(
                Config.API_WEBHOOK_ALERT,
                json=alert_payload,
                timeout=Config.API_WEBHOOK_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout enviando alerta: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión enviando alerta: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error inesperado enviando alerta: {e}")
            raise

# Instancia global
api_client = SOCAPIClient()