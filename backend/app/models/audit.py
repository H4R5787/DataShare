"""Audit logging model for compliance and security forensics."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Text
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)    # ORDER_CREATED, PAYMENT_VERIFIED, etc.
    entity_type = Column(String(30), nullable=False)           # ORDER, PAYMENT, RECHARGE, AUTH
    entity_id = Column(String(36), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
