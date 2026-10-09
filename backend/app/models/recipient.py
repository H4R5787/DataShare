"""Saved recipient address book model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SavedRecipient(Base):
    __tablename__ = "saved_recipients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_number = Column(String(15), nullable=False)
    nickname = Column(String(50), nullable=False)
    operator_id = Column(String(36), ForeignKey("operators.id", ondelete="SET NULL"), nullable=True)
    circle_id = Column(String(36), ForeignKey("circles.id", ondelete="SET NULL"), nullable=True)
    last_recharged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="saved_recipients")
    operator = relationship("Operator")
    circle = relationship("Circle")
