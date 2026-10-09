"""High-fidelity Mock Telecom Adapter with configurable testing hooks and realistic MNP resolution."""

import asyncio
import random
import uuid
from typing import Optional
from backend.app.adapters.telecom.base import (
    OperatorAdapter,
    OperatorDetectionResult,
    RechargeRequest,
    RechargeResponse,
    RechargeStatusResponse,
)


class MockOperatorAdapter(OperatorAdapter):
    """
    Simulates telecom provider APIs for development and automated testing.
    Test Number Conventions:
      - Ending in '000': Simulates permanent carrier rejection (triggers auto-refund flow).
      - Ending in '999': Simulates carrier timeout / pending state (triggers background retry worker).
      - All other valid numbers: Instant carrier confirmation.
    """

    def __init__(self, operator_code: str = "MOCK"):
        self.operator_code = operator_code

    async def validate_number(self, phone: str) -> bool:
        clean = phone.replace("+91", "").replace(" ", "").strip()
        return len(clean) == 10 and clean.isdigit() and clean[0] in "6789"

    async def detect_operator(self, phone: str) -> OperatorDetectionResult:
        clean = phone.replace("+91", "").replace(" ", "").strip()
        prefix2 = clean[:2] if len(clean) >= 2 else "98"

        # Heuristic mapping for standard Indian telecom prefixes
        if prefix2 in ("70", "79", "62", "63", "80"):
            op_code, op_name = "JIO", "Reliance Jio"
            cir_code, cir_name = "MUM", "Mumbai"
        elif prefix2 in ("98", "99", "90", "81", "84"):
            op_code, op_name = "AIRTEL", "Bharti Airtel"
            cir_code, cir_name = "DL", "Delhi NCR"
        elif prefix2 in ("91", "97", "77", "88", "78"):
            op_code, op_name = "VI", "Vodafone Idea (Vi)"
            cir_code, cir_name = "MAH", "Maharashtra & Goa"
        elif prefix2 in ("94", "95", "89"):
            op_code, op_name = "BSNL", "BSNL"
            cir_code, cir_name = "KA", "Karnataka"
        else:
            op_code, op_name = "JIO", "Reliance Jio"
            cir_code, cir_name = "MUM", "Mumbai"

        return OperatorDetectionResult(
            phone_number=f"+91{clean}",
            operator_code=op_code,
            operator_name=op_name,
            circle_code=cir_code,
            circle_name=cir_name,
            is_portable=True,
            confidence=0.98,
        )

    async def execute_recharge(self, request: RechargeRequest) -> RechargeResponse:
        clean = request.recipient_phone.replace("+91", "").replace(" ", "").strip()

        # Test hook 1: Ending in '000' triggers carrier rejection
        if clean.endswith("000"):
            return RechargeResponse(
                success=False,
                status="FAILED",
                telecom_reference_id=None,
                operator_message="Operator rejected recharge: Recipient SIM inactive or prepaid balance barred.",
                is_mock=True,
                raw_response={"error_code": "ERR_SIM_BARRED", "provider": "MOCK_GATEWAY"},
            )

        # Test hook 2: Ending in '999' triggers pending timeout
        if clean.endswith("999"):
            txn_id = f"{request.operator_code}-PEND-{random.randint(100000, 999999)}"
            return RechargeResponse(
                success=True,
                status="PENDING",
                telecom_reference_id=txn_id,
                operator_message="Recharge submitted. Telecom operator processing in progress.",
                is_mock=True,
                raw_response={"status": "IN_PROGRESS", "provider": "MOCK_GATEWAY"},
            )

        # Normal successful recharge
        txn_id = f"{request.operator_code}-TXN-{random.randint(10000000, 99999999)}"
        return RechargeResponse(
            success=True,
            status="SUCCESS",
            telecom_reference_id=txn_id,
            operator_message="Data pack successfully activated on recipient mobile number.",
            is_mock=True,
            raw_response={"ref_id": txn_id, "provider": "MOCK_GATEWAY", "status": "CONFIRMED"},
        )

    async def query_recharge_status(self, telecom_reference_id: str) -> RechargeStatusResponse:
        # If it was a pending test ID, resolve it to SUCCESS
        return RechargeStatusResponse(
            telecom_reference_id=telecom_reference_id,
            status="SUCCESS",
            operator_message="Confirmed by operator network.",
            completed_at="2026-10-09T23:25:00Z",
        )
