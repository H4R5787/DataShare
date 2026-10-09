"""Payment request and response Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaymentIntentRequest(BaseModel):
    order_id: str = Field(..., description="Order ID to initiate checkout for")
    payment_method: str = Field("UPI", description="Payment method: UPI, CARD, NETBANKING")


class PaymentIntentResponse(BaseModel):
    payment_id: str
    order_id: str
    amount_in_paise: int
    amount_formatted: str
    currency: str
    gateway_name: str
    gateway_order_id: str
    client_token: Optional[str] = None
    is_mock: bool = False


class PaymentVerifyRequest(BaseModel):
    order_id: str
    payment_id: str
    gateway_payment_id: Optional[str] = None
    payment_method: str = "UPI"
    signature: Optional[str] = "mock_valid_sig"


class PaymentVerifyResponse(BaseModel):
    success: bool
    order_id: str
    order_status: str
    recharge_status: Optional[str] = None
    telecom_reference_id: Optional[str] = None
    message: str
