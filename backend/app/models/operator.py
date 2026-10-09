"""Telecom operator and circle models."""

import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Operator(Base):
    __tablename__ = "operators"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(20), unique=True, index=True, nullable=False)  # JIO, AIRTEL, VI, BSNL
    name = Column(String(50), nullable=False)
    logo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    plans = relationship("Plan", back_populates="operator")


class Circle(Base):
    __tablename__ = "circles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(20), unique=True, index=True, nullable=False)  # DL, MUM, MAH, KA, etc.
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True)

    plans = relationship("Plan", back_populates="circle")
