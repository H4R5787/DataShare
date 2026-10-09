"""Operator and circle Pydantic schemas."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.auth import validate_indian_phone


class OperatorDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    logo_url: Optional[str] = None
    is_active: bool


class CircleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    region: Optional[str] = None


class OperatorDetectRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient phone number")

    def get_validated_phone(self) -> str:
        return validate_indian_phone(self.phone_number)


class OperatorDetectResponse(BaseModel):
    phone_number: str
    phone_number_masked: str
    operator: OperatorDTO
    circle: CircleDTO
    is_portable: bool
    confidence: float
