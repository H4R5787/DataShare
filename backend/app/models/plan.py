"""Telecom data plan catalog model."""

import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operator_id = Column(String(36), ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    circle_id = Column(String(36), ForeignKey("circles.id", ondelete="SET NULL"), nullable=True, index=True)
    plan_code = Column(String(50), nullable=False)
    data_amount = Column(String(20), nullable=False)        # e.g. "1 GB", "2 GB", "12 GB"
    data_amount_mb = Column(Integer, nullable=False)         # 1024, 2048, 12288 (for sorting)
    validity_desc = Column(String(50), nullable=False)       # "Active Plan", "28 Days", "1 Day"
    price_in_paise = Column(Integer, nullable=False)         # 2900 for ₹29
    category = Column(String(30), nullable=False)            # BOOSTER, DAILY, WORK, BULK
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    operator = relationship("Operator", back_populates="plans")
    circle = relationship("Circle", back_populates="plans")
    orders = relationship("Order", back_populates="plan")
