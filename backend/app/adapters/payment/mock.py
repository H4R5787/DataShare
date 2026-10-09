"""High-fidelity Mock Payment Gateway Adapter for offline testing and development."""

import hashlib
import random
import uuid
from typing import Any, Dict
from backend.app.adapters.payment.base import (
    PaymentGatewayAdapter,
    PaymentOrderResult,
    PaymentVerificationResult,
    RefundResult,
)


class MockPaymentAdapter(PaymentGatewayAdapter):
    """
    Simulates payment operations (Orders, Checkout, Webhooks, Refunds).
    Test hooks:
      - payment_method == 'FAIL_TEST': Simulates payment decline.
    """

    async def create_order(self, order_id: str, amount_in_paise: int, currency: str = "INR") -> PaymentOrderResult:
        mock_order_id = f"mock_order_{uuid.uuid4().hex[:12]}"
        return PaymentOrderResult(
            gateway_name="MOCK",
            gateway_order_id=mock_order_id,
            amount_in_paise=amount_in_paise,
            currency=currency,
            client_token=f"mock_token_{uuid.uuid4().hex[:16]}",
            is_mock=True,
        )

    async def verify_payment(self, payload: Dict[str, Any], signature: str) -> PaymentVerificationResult:
        # Check if simulated failure was requested
        payment_method = payload.get("payment_method", "UPI")
        if payment_method == "FAIL_TEST":
            return PaymentVerificationResult(
                is_valid=False,
                gateway_payment_id=payload.get("gateway_payment_id", f"mock_pay_{uuid.uuid4().hex[:10]}"),
                amount_in_paise=payload.get("amount_in_paise", 0),
                payment_method=payment_method,
                failure_reason="Card declined by issuing bank (Simulated failure).",
            )

        pay_id = payload.get("gateway_payment_id") or f"mock_pay_{uuid.uuid4().hex[:10]}"
        return PaymentVerificationResult(
            is_valid=True,
            gateway_payment_id=pay_id,
            amount_in_paise=payload.get("amount_in_paise", 0),
            payment_method=payment_method,
            failure_reason=None,
        )

    async def initiate_refund(self, gateway_payment_id: str, amount_in_paise: int, reason: str) -> RefundResult:
        mock_refund_id = f"mock_rfnd_{uuid.uuid4().hex[:12]}"
        return RefundResult(
            success=True,
            gateway_refund_id=mock_refund_id,
            amount_in_paise=amount_in_paise,
            status="SUCCESS",
            error_message=None,
            is_mock=True,
        )
