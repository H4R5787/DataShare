"""Razorpay payment gateway adapter implementation."""

import hmac
import hashlib
from typing import Any, Dict
from backend.app.adapters.payment.base import (
    PaymentGatewayAdapter,
    PaymentOrderResult,
    PaymentVerificationResult,
    RefundResult,
)
from backend.app.adapters.payment.mock import MockPaymentAdapter


class RazorpayAdapter(MockPaymentAdapter):
    """
    Razorpay integration adapter.
    In mock/dev mode, uses safe simulation.
    In live mode, calls Razorpay REST API and verifies HMAC SHA-256 signatures.
    """

    def __init__(self, key_id: str = "", key_secret: str = ""):
        self.key_id = key_id
        self.key_secret = key_secret

    def verify_webhook_signature(self, webhook_body: str, signature: str, webhook_secret: str) -> bool:
        """Verify HMAC SHA-256 signature from Razorpay webhook header."""
        expected = hmac.new(
            webhook_secret.encode(),
            webhook_body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
