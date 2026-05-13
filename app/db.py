import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from config import config

Base = declarative_base()
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=True)
    source_ip = Column(String(45), nullable=True)
    destination_ip = Column(String(45), nullable=True)
    url = Column(String(1024), nullable=True)
    file_hash = Column(String(128), nullable=True)
    email_recipient = Column(String(254), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    real_apis = Column(Boolean, nullable=False, default=True)
    status = Column(String(50), nullable=False, default="processing", index=True)
    tools_used = Column(Text, nullable=True)
    analysis_result = Column(Text, nullable=True)
    notification_sent = Column(Text, nullable=True)
    raw_result = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "incident_id": self.incident_id,
            "source": self.source,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "priority": self.priority,
            "message": self.message,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "url": self.url,
            "file_hash": self.file_hash,
            "email_recipient": self.email_recipient,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "real_apis": self.real_apis,
            "status": self.status,
            "tools_used": json.loads(self.tools_used) if self.tools_used else [],
            "analysis_result": self.analysis_result,
            "notification_sent": self.notification_sent,
            "raw_result": json.loads(self.raw_result) if self.raw_result else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
