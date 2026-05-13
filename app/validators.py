from pydantic import BaseModel, EmailStr, validator, ValidationError
import ipaddress
import re

class AlertPayload(BaseModel):
    """Validación de alerta usando Pydantic"""
    source: str
    alert_type: str
    severity: str
    message: str
    source_ip: str = None
    destination_ip: str = None
    url: str = None
    file_hash: str = None
    email_recipient: EmailStr = None
    priority: str
    timestamp: str
    real_apis: bool
    
    @validator('source_ip', 'destination_ip')
    def validate_ip(cls, v):
        if v is None:
            return v
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"IP inválida: {v}")
    
    @validator('url')
    def validate_url(cls, v):
        if v is None:
            return v
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, v):
            raise ValueError("URL inválida")
        return v
    
    @validator('file_hash')
    def validate_hash(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$', v):
            raise ValueError("Hash inválido (MD5/SHA1/SHA256)")
        return v