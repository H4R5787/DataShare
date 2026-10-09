"""Carrier-specific telecom adapters (Jio, Airtel, Vi, BSNL)."""

from backend.app.adapters.telecom.mock import MockOperatorAdapter


class JioAdapter(MockOperatorAdapter):
    """Reliance Jio carrier integration adapter."""
    def __init__(self):
        super().__init__(operator_code="JIO")


class AirtelAdapter(MockOperatorAdapter):
    """Bharti Airtel carrier integration adapter."""
    def __init__(self):
        super().__init__(operator_code="AIRTEL")


class ViAdapter(MockOperatorAdapter):
    """Vodafone Idea (Vi) carrier integration adapter."""
    def __init__(self):
        super().__init__(operator_code="VI")


class BSNLAdapter(MockOperatorAdapter):
    """BSNL carrier integration adapter."""
    def __init__(self):
        super().__init__(operator_code="BSNL")
