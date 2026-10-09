"""Transaction history and timeline Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TimelineEvent(BaseModel):
    state: str
    label: str
    timestamp: datetime
    is_completed: bool


class TransactionSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    recipient_phone_masked: str
    operator_name: str
    operator_code: str
    plan_data: str
    amount_formatted: str
    status: str
    created_at: datetime


class TransactionDetailsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    recipient_phone: str
    recipient_phone_masked: str
    operator_id: str
    operator_name: str
    operator_code: str
    plan_id: str
    plan_data: str
    plan_validity: str
    amount_in_paise: int
    amount_formatted: str
    currency: str
    current_state: str
    telecom_reference_id: Optional[str] = None
    refund_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    timeline: List[TimelineEvent]
