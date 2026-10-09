"""Idempotency record model for duplicate-execution protection."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from backend.app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_keys"

    key = Column(String(64), primary_key=True)                 # UUIDv4 key
    user_id = Column(String(36), nullable=False, index=True)
    request_path = Column(String(100), nullable=False)
    request_hash = Column(String(64), nullable=False)
    status = Column(String(20), default="PROCESSING", nullable=False) # PROCESSING, COMPLETED
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
