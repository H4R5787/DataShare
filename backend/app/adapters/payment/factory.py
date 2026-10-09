"""Factory to resolve payment gateway adapter."""

from backend.app.adapters.payment.base import PaymentGatewayAdapter
from backend.app.adapters.payment.mock import MockPaymentAdapter
from backend.app.adapters.payment.razorpay import RazorpayAdapter
from backend.app.core.config import settings


class PaymentGatewayFactory:
    @staticmethod
    def get_adapter(gateway_name: str = "") -> PaymentGatewayAdapter:
        name = (gateway_name or settings.PAYMENT_MODE).upper()
        if name == "RAZORPAY":
            return RazorpayAdapter()
        return MockPaymentAdapter()
