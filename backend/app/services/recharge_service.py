"""Recharge fulfillment orchestration, retry logic, and automated refund triggers."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.adapters.payment.factory import PaymentGatewayFactory
from backend.app.adapters.telecom.base import RechargeRequest
from backend.app.adapters.telecom.factory import OperatorAdapterFactory
from backend.app.core.state_machine import TransactionState, validate_transition
from backend.app.models.audit import AuditLog
from backend.app.models.operator import Operator
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.plan import Plan
from backend.app.models.recharge import Recharge
from backend.app.models.refund import Refund


class RechargeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute_order_recharge(self, order_id: str) -> Recharge:
        """
        Orchestrate telecom fulfillment for an order that reached PAYMENT_SUCCESS.
        Handles carrier dispatch, status updating, and automated refund on failure.
        """
        order = await self.session.get(Order, order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        # Transition PAYMENT_SUCCESS -> RECHARGE_PENDING
        validate_transition(TransactionState(order.status), TransactionState.RECHARGE_PENDING)
        order.status = TransactionState.RECHARGE_PENDING.value

        operator = await self.session.get(Operator, order.operator_id)
        plan = await self.session.get(Plan, order.plan_id)

        # Create or update Recharge record
        recharge_query = select(Recharge).where(Recharge.order_id == order.id)
        recharge = (await self.session.execute(recharge_query)).scalars().first()
        if not recharge:
            recharge = Recharge(
                order_id=order.id,
                operator_id=operator.id,
                recipient_phone=order.recipient_phone,
                status="PENDING",
                retry_count=0,
            )
            self.session.add(recharge)

        await self.session.flush()

        # Invoke Telecom Adapter
        adapter = OperatorAdapterFactory.get_adapter(operator.code)
        req = RechargeRequest(
            order_id=order.id,
            recipient_phone=order.recipient_phone,
            operator_code=operator.code,
            plan_code=plan.plan_code if plan else "UNKNOWN",
            amount_in_paise=order.amount_in_paise,
        )
        response = await adapter.execute_recharge(req)

        now = datetime.now(timezone.utc)

        if response.status == "SUCCESS":
            # RECHARGE_PENDING -> SUCCESS
            validate_transition(TransactionState.RECHARGE_PENDING, TransactionState.SUCCESS)
            order.status = TransactionState.SUCCESS.value
            recharge.status = "SUCCESS"
            recharge.telecom_reference_id = response.telecom_reference_id
            recharge.completed_at = now

            self.session.add(
                AuditLog(
                    user_id=order.user_id,
                    action="RECHARGE_SUCCESS",
                    entity_type="RECHARGE",
                    entity_id=order.id,
                    metadata_json=f'{{"ref_id": "{response.telecom_reference_id}"}}',
                )
            )

        elif response.status == "FAILED":
            # RECHARGE_PENDING -> RECHARGE_FAILED
            validate_transition(TransactionState.RECHARGE_PENDING, TransactionState.RECHARGE_FAILED)
            order.status = TransactionState.RECHARGE_FAILED.value
            recharge.status = "FAILED"
            recharge.last_error = response.operator_message

            self.session.add(
                AuditLog(
                    user_id=order.user_id,
                    action="RECHARGE_FAILED",
                    entity_type="RECHARGE",
                    entity_id=order.id,
                    metadata_json=f'{{"reason": "{response.operator_message}"}}',
                )
            )

            # Trigger automated refund immediately!
            await self._trigger_automated_refund(order, reason=response.operator_message)

        else:  # PENDING (timeout / processing)
            recharge.status = "PENDING"
            recharge.telecom_reference_id = response.telecom_reference_id
            recharge.last_error = response.operator_message

        await self.session.commit()
        return recharge

    async def _trigger_automated_refund(self, order: Order, reason: str) -> None:
        """Trigger payment refund when recharge fails permanently."""
        # RECHARGE_FAILED -> REFUND_PENDING
        validate_transition(TransactionState.RECHARGE_FAILED, TransactionState.REFUND_PENDING)
        order.status = TransactionState.REFUND_PENDING.value

        payment_query = select(Payment).where(Payment.order_id == order.id)
        payment = (await self.session.execute(payment_query)).scalars().first()

        gateway = PaymentGatewayFactory.get_adapter(payment.gateway_name if payment else "MOCK")
        refund_res = await gateway.initiate_refund(
            gateway_payment_id=payment.gateway_payment_id if payment else "mock_pay",
            amount_in_paise=order.amount_in_paise,
            reason=f"Automated refund: {reason}",
        )

        # REFUND_PENDING -> REFUNDED
        validate_transition(TransactionState.REFUND_PENDING, TransactionState.REFUNDED)
        order.status = TransactionState.REFUNDED.value

        refund = Refund(
            payment_id=payment.id if payment else "no_pay_id",
            order_id=order.id,
            gateway_refund_id=refund_res.gateway_refund_id,
            amount_in_paise=order.amount_in_paise,
            status="SUCCESS",
            reason=f"Carrier rejection auto-refund: {reason}",
        )
        self.session.add(refund)

        self.session.add(
            AuditLog(
                user_id=order.user_id,
                action="REFUND_COMPLETED",
                entity_type="REFUND",
                entity_id=order.id,
                metadata_json=f'{{"refund_id": "{refund_res.gateway_refund_id}", "amount": {order.amount_in_paise}}}',
            )
        )
