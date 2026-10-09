"""Payment record model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    gateway_name = Column(String(30), nullable=False)           # MOCK, RAZORPAY, CASHFREE
    gateway_payment_id = Column(String(100), nullable=True)     # pay_xxxx
    gateway_order_id = Column(String(100), nullable=True)       # order_xxxx
    amount_in_paise = Column(Integer, nullable=False)
    status = Column(String(30), default="PENDING", nullable=False) # PENDING, SUCCESS, FAILED
    payment_method = Column(String(30), nullable=True)          # UPI, CARD, NETBANKING
    signature = Column(String(255), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    order = relationship("Order", back_populates="payment")
    refunds = relationship("Refund", back_populates="payment")
