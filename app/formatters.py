from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def format_timestamp(ts_string: str) -> str:
    """
    Formatea timestamp ISO a formato legible.
    
    Args:
        ts_string: Timestamp en formato ISO (ej: '2026-05-13T10:30:00Z')
    
    Returns:
        Timestamp formateado (ej: '10:30:00 - 13/05/2026')
    
    Raises:
        ValueError: Si el formato no es válido
    """
    try:
        dt = datetime.fromisoformat(ts_string.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S - %d/%m/%Y')
    except ValueError as e:
        logger.warning(f"Formato de timestamp inválido: {ts_string}")
        return ts_string