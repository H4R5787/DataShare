"""Abstract base class and DTOs for telecom operator adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OperatorDetectionResult(BaseModel):
    phone_number: str
    operator_code: str  # JIO, AIRTEL, VI, BSNL
    operator_name: str
    circle_code: str    # MUM, DL, MAH, KA, etc.
    circle_name: str
    is_portable: bool = True
    confidence: float = 1.0


class TelecomPlanDTO(BaseModel):
    id: str
    plan_code: str
    operator_code: str
    data_amount: str
    data_amount_mb: int
    validity_desc: str
    price_in_paise: int
    category: str
    description: str


class RechargeRequest(BaseModel):
    order_id: str
    recipient_phone: str
    operator_code: str
    circle_code: Optional[str] = None
    plan_code: str
    amount_in_paise: int


class RechargeResponse(BaseModel):
    success: bool
    status: str                         # SUCCESS, PENDING, FAILED
    telecom_reference_id: Optional[str] # e.g. JIO-TXN-998124
    operator_message: str
    is_mock: bool = False
    raw_response: Optional[Dict[str, Any]] = None


class RechargeStatusResponse(BaseModel):
    telecom_reference_id: str
    status: str                         # SUCCESS, PENDING, FAILED
    operator_message: str
    completed_at: Optional[str] = None


class OperatorAdapter(ABC):
    """Abstract contract for telecom recharge and plan discovery."""

    @abstractmethod
    async def validate_number(self, phone: str) -> bool:
        """Verify recipient number format and network eligibility."""
        pass

    @abstractmethod
    async def detect_operator(self, phone: str) -> OperatorDetectionResult:
        """Resolve operator and circle via MNP resolver or series database."""
        pass

    @abstractmethod
    async def execute_recharge(self, request: RechargeRequest) -> RechargeResponse:
        """Submit retail data-pack recharge to carrier gateway."""
        pass

    @abstractmethod
    async def query_recharge_status(self, telecom_reference_id: str) -> RechargeStatusResponse:
        """Query real-time status of an in-flight recharge."""
        pass
