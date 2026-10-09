"""Factory to resolve telecom operator adapter by carrier code."""

from backend.app.adapters.telecom.base import OperatorAdapter
from backend.app.adapters.telecom.carriers import AirtelAdapter, BSNLAdapter, JioAdapter, ViAdapter
from backend.app.adapters.telecom.mock import MockOperatorAdapter


class OperatorAdapterFactory:
    @staticmethod
    def get_adapter(operator_code: str) -> OperatorAdapter:
        normalized = (operator_code or "").upper().strip()
        if normalized == "JIO":
            return JioAdapter()
        elif normalized == "AIRTEL":
            return AirtelAdapter()
        elif normalized == "VI":
            return ViAdapter()
        elif normalized == "BSNL":
            return BSNLAdapter()
        return MockOperatorAdapter(operator_code=normalized)
