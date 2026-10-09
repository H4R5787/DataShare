"""Recharge dispatch and status tracking model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Recharge(Base):
    __tablename__ = "recharges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    operator_id = Column(String(36), ForeignKey("operators.id"), nullable=False)
    recipient_phone = Column(String(15), nullable=False)
    telecom_reference_id = Column(String(100), nullable=True)   # JIO-TXN-881203
    status = Column(String(30), default="PENDING", nullable=False) # PENDING, SUCCESS, FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    order = relationship("Order", back_populates="recharge")
    operator = relationship("Operator")
