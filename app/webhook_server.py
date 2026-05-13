import asyncio
import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Optional

import uvicorn
import uuid
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, ValidationError, validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from config import config
from db import Incident, SessionLocal, init_db
from supervisor import process_security_alert

# Configurar logging
logger = logging.getLogger("webhook_server")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "logs/webhook_server.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())

# Validar configuración al iniciar
try:
    config.validate_required_config()
    logger.info("✅ Configuración de APIs validada correctamente")
except ValueError as e:
    logger.error(f"❌ Error de configuración: {e}")
    raise

app = FastAPI(title="SOC Webhook Server - PRODUCCIÓN", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.WEBHOOK_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

rate_limit_store: dict[str, deque[datetime]] = defaultdict(deque)
rate_limit_lock = asyncio.Lock()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SecurityAlert(BaseModel):
    source: str = Field(..., min_length=1, max_length=100)
    alert_type: str = Field(..., min_length=1, max_length=100)
    severity: str = Field(..., regex="^(Critical|High|Medium|Low)$")
    message: str = Field(..., min_length=5, max_length=5000)
    priority: str = Field(..., regex="^(Normal|Urgente)$")
    source_ip: Optional[str] = Field(None, max_length=45)
    destination_ip: Optional[str] = Field(None, max_length=45)
    url: Optional[str] = Field(None, max_length=1024)
    file_hash: Optional[str] = Field(None, max_length=128)
    timestamp: Optional[datetime] = None
    email_recipient: Optional[EmailStr] = None
    real_apis: bool = True

    @validator("source_ip", "destination_ip")
    def validate_ip(cls, value):
        if value is None:
            return value
        try:
            import ipaddress

            ipaddress.ip_address(value)
        except ValueError:
            raise ValueError(f"IP inválida: {value}")
        return value

    @validator("url")
    def validate_url(cls, value):
        if value is None:
            return value
        if not value.startswith(("http://", "https://")):
            raise ValueError("URL inválida: debe comenzar con http:// o https://")
        return value

    @validator("file_hash")
    def validate_hash(cls, value):
        if value is None:
            return value
        if not value.isalnum() or len(value) not in (32, 40, 64):
            raise ValueError("Hash MD5, SHA1 o SHA256 inválido")
        return value


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key != config.WEBHOOK_API_KEY:
        logger.warning("Intento de acceso no autorizado con API Key inválida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida",
        )
    return x_api_key


async def enforce_rate_limit(api_key: str = Depends(verify_api_key)) -> str:
    now = datetime.utcnow()
    window = timedelta(seconds=config.RATE_LIMIT_WINDOW_SECONDS)
    async with rate_limit_lock:
        queue = rate_limit_store[api_key]
        while queue and queue[0] < now - window:
            queue.popleft()
        if len(queue) >= config.RATE_LIMIT_MAX_REQUESTS:
            logger.warning("Rate limit excedido para API Key")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Límite de {config.RATE_LIMIT_MAX_REQUESTS} solicitudes por minuto excedido",
            )
        queue.append(now)
    return api_key


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    logger.info("Base de datos inicializada y servidor en arranque")


@app.post("/webhook/alert", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    alert: SecurityAlert,
    api_key: str = Depends(enforce_rate_limit),
    db: Session = Depends(get_db),
):
    """Recibe alertas de seguridad y las procesa con agentes REALES usando APIs externas."""
    incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6]}"
    alert_data = alert.model_dump()
    alert_data["timestamp"] = alert.timestamp.isoformat() if alert.timestamp else datetime.utcnow().isoformat()
    alert_data["incident_id"] = incident_id

    processing_context = {
        "email_recipient": alert_data.get("email_recipient"),
        "use_real_apis": alert_data.get("real_apis", True),
    }

    logger.info(f"🚨 Procesando alerta REAL: {incident_id}")
    logger.debug(f"📊 Datos de alerta: {alert_data}")

    try:
        result = await asyncio.to_thread(
            process_security_alert,
            alert_data,
            incident_id,
            processing_context,
        )

        incident = Incident(
            incident_id=incident_id,
            source=alert_data["source"],
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            priority=alert_data["priority"],
            message=alert_data["message"],
            source_ip=alert_data.get("source_ip"),
            destination_ip=alert_data.get("destination_ip"),
            url=alert_data.get("url"),
            file_hash=alert_data.get("file_hash"),
            email_recipient=alert_data.get("email_recipient"),
            timestamp=datetime.fromisoformat(alert_data["timestamp"]),
            real_apis=alert_data.get("real_apis", True),
            status=result.get("status", "completed"),
            tools_used=json.dumps(result.get("tools_used", []), ensure_ascii=False),
            analysis_result=result.get("analysis_result", ""),
            notification_sent=result.get("notification_sent", ""),
            raw_result=json.dumps(result, ensure_ascii=False),
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        logger.info(f"✅ Alerta procesada exitosamente: {incident_id}")
        logger.info(f"📊 Herramientas utilizadas: {result.get('tools_used', [])}")

        return {
            "status": "success",
            "incident_id": incident_id,
            "message": "Alerta procesada por agentes SOC con APIs reales",
            "processing_time": "45-90 segundos",
            "apis_used": result.get("tools_used", []),
            "result": result,
        }

    except ValidationError as e:
        logger.warning(f"Error de validación al procesar alerta: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors(),
        )
    except Exception as e:
        logger.exception(f"Error procesando alerta: {e}")
        error_message = str(e)
        if "timeout" in error_message.lower():
            error_type = "timeout_error"
            suggestion = "Las APIs externas están tardando más de lo esperado. Intenta de nuevo."
            status_code = status.HTTP_504_GATEWAY_TIMEOUT
        elif "mailtrap" in error_message.lower() or "smtp" in error_message.lower():
            error_type = "mailtrap_error"
            suggestion = "Mailtrap no está configurado correctamente. Verifica MAILTRAP_USERNAME y MAILTRAP_PASSWORD."
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            error_type = "unknown_error"
            suggestion = "Error inesperado en el procesamiento"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        raise HTTPException(
            status_code=status_code,
            detail={
                "error": error_message,
                "error_type": error_type,
                "suggestion": suggestion,
                "timestamp": datetime.utcnow().isoformat(),
                "incident_id": incident_id,
            },
        )


@app.get("/incidents")
async def get_incidents(
    page: int = 1,
    limit: int = 50,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Obtiene lista de incidentes procesados con paginación y filtros."""
    query = db.query(Incident)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status_filter:
        query = query.filter(Incident.status == status_filter)

    total = query.count()
    incidents = (
        query.order_by(Incident.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "incidents": [incident.to_dict() for incident in incidents],
        "page": page,
        "limit": limit,
        "total": total,
        "last_updated": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check del sistema con estado de APIs."""
    total_incidents = db.query(func.count(Incident.incident_id)).scalar() or 0
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "total_incidents_processed": total_incidents,
        "api_configuration": {
            "openai": "✅ Configurada" if config.OPENAI_API_KEY else "❌ Falta",
            "tavily": "✅ Configurada" if config.TAVILY_API_KEY else "❌ Falta",
            "virustotal": "✅ Configurada" if config.VIRUSTOTAL_API_KEY else "❌ Falta",
            "mailtrap": "✅ Configurada" if config.MAILTRAP_USERNAME and config.MAILTRAP_PASSWORD else "❌ Falta",
        },
    }
    missing_apis = [k for k, v in health_status["api_configuration"].items() if "❌" in v]
    if missing_apis:
        health_status["status"] = "degraded"
        health_status[
            "warnings"
        ] = f"APIs faltantes: {', '.join(missing_apis)}"
    return health_status


@app.get("/api-status")
async def api_status():
    """Estado detallado de todas las APIs externas."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "apis": {
            "openai": {
                "configured": bool(config.OPENAI_API_KEY),
                "description": "LLM para agentes multiagente",
                "required": True,
            },
            "tavily": {
                "configured": bool(config.TAVILY_API_KEY),
                "description": "Búsqueda web para AI agents",
                "required": True,
                "free_tier": "1000 búsquedas/mes",
            },
            "virustotal": {
                "configured": bool(config.VIRUSTOTAL_API_KEY),
                "description": "Análisis de IOCs real",
                "required": True,
                "rate_limits": "4 requests/min (gratis)",
            },
            "mailtrap": {
                "configured": bool(config.MAILTRAP_USERNAME and config.MAILTRAP_PASSWORD),
                "description": "Envío de correo de prueba usando Mailtrap",
                "required": False,
                "setup_required": "Configura MAILTRAP_USERNAME y MAILTRAP_PASSWORD en .env",
            },
            "abuseipdb": {
                "configured": bool(config.ABUSEIPDB_API_KEY),
                "description": "Threat intelligence de IPs",
                "required": False,
                "free_tier": "1000 requests/día",
            },
        },
    }


if __name__ == "__main__":
    logger.info("🛡️ Iniciando servidor webhook SOC con APIs REALES...")
    logger.info(f"🌐 Puerto: {config.WEBHOOK_PORT}")
    logger.info("🔧 Verificando configuración...")
    logger.info(f"✅ OpenAI: {'Configurada' if config.OPENAI_API_KEY else 'FALTA'}")
    logger.info(f"✅ Tavily: {'Configurada' if config.TAVILY_API_KEY else 'FALTA'}")
    logger.info(f"✅ VirusTotal: {'Configurada' if config.VIRUSTOTAL_API_KEY else 'FALTA'}")
    logger.info(f"✅ Mailtrap: {'Configurada' if config.MAILTRAP_USERNAME and config.MAILTRAP_PASSWORD else 'FALTA (opcional)'}")
    logger.info("🚀 Servidor listo para procesar alertas reales!")
    logger.info("📊 Dashboard: http://localhost:8501")
    logger.info("🌐 API Health: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=config.WEBHOOK_PORT)
