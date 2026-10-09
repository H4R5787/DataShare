"""Order request and response Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.auth import validate_indian_phone


class OrderCreateRequest(BaseModel):
    recipient_phone: str = Field(..., description="Recipient mobile phone number")
    operator_id: str = Field(..., description="Selected operator ID")
    circle_id: Optional[str] = Field(None, description="Selected circle ID")
    plan_id: str = Field(..., description="Selected data pack ID")

    def get_validated_phone(self) -> str:
        return validate_indian_phone(self.recipient_phone)


class OrderDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    recipient_phone: str
    recipient_phone_masked: str
    operator_id: str
    operator_name: str
    circle_id: Optional[str] = None
    plan_id: str
    plan_data: str
    plan_validity: str
    amount_in_paise: int
    amount_formatted: str
    currency: str
    status: str
    created_at: datetime
