"""Order and transaction state model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_phone = Column(String(15), nullable=False)
    operator_id = Column(String(36), ForeignKey("operators.id"), nullable=False)
    circle_id = Column(String(36), ForeignKey("circles.id"), nullable=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False)
    amount_in_paise = Column(Integer, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(30), default="CREATED", index=True, nullable=False)
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="orders")
    operator = relationship("Operator")
    circle = relationship("Circle")
    plan = relationship("Plan", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    recharge = relationship("Recharge", back_populates="order", uselist=False, cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")
