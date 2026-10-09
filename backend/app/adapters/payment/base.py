"""Abstract base class and DTOs for payment gateway adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class PaymentOrderResult(BaseModel):
    gateway_name: str
    gateway_order_id: str
    amount_in_paise: int
    currency: str
    client_token: Optional[str] = None
    is_mock: bool = False


class PaymentVerificationResult(BaseModel):
    is_valid: bool
    gateway_payment_id: str
    amount_in_paise: int
    payment_method: Optional[str] = None
    failure_reason: Optional[str] = None


class RefundResult(BaseModel):
    success: bool
    gateway_refund_id: Optional[str] = None
    amount_in_paise: int
    status: str                         # SUCCESS, PENDING, FAILED
    error_message: Optional[str] = None
    is_mock: bool = False


class PaymentGatewayAdapter(ABC):
    """Abstract interface for licensed payment gateways."""

    @abstractmethod
    async def create_order(self, order_id: str, amount_in_paise: int, currency: str = "INR") -> PaymentOrderResult:
        """Create payment session / order on payment provider."""
        pass

    @abstractmethod
    async def verify_payment(self, payload: Dict[str, Any], signature: str) -> PaymentVerificationResult:
        """Verify server-side payment signature or webhook callback."""
        pass

    @abstractmethod
    async def initiate_refund(self, gateway_payment_id: str, amount_in_paise: int, reason: str) -> RefundResult:
        """Execute automated refund back to payment source."""
        pass
