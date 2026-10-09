"""Payment processing service: checkout session creation, verification, and recharge trigger."""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.adapters.payment.factory import PaymentGatewayFactory
from backend.app.core.state_machine import TransactionState, validate_transition
from backend.app.models.audit import AuditLog
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.schemas.payment import (
    PaymentIntentResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from backend.app.services.recharge_service import RechargeService


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.recharge_service = RechargeService(session)

    async def create_payment_intent(
        self,
        user_id: str,
        order_id: str,
        payment_method: str = "UPI",
    ) -> PaymentIntentResponse:
        """Initialize payment gateway checkout session for an order."""
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if order.status != TransactionState.PAYMENT_PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot accept payment in '{order.status}' state.",
            )

        gateway = PaymentGatewayFactory.get_adapter()
        gateway_res = await gateway.create_order(
            order_id=order.id,
            amount_in_paise=order.amount_in_paise,
            currency=order.currency,
        )

        # Check existing payment record
        pay_query = select(Payment).where(Payment.order_id == order.id)
        payment = (await self.session.execute(pay_query)).scalars().first()
        if not payment:
            payment = Payment(
                order_id=order.id,
                gateway_name=gateway_res.gateway_name,
                gateway_order_id=gateway_res.gateway_order_id,
                amount_in_paise=order.amount_in_paise,
                status="PENDING",
                payment_method=payment_method,
            )
            self.session.add(payment)
        else:
            payment.gateway_order_id = gateway_res.gateway_order_id
            payment.payment_method = payment_method

        await self.session.commit()

        return PaymentIntentResponse(
            payment_id=payment.id,
            order_id=order.id,
            amount_in_paise=order.amount_in_paise,
            amount_formatted=f"₹{order.amount_in_paise // 100}",
            currency=order.currency,
            gateway_name=gateway_res.gateway_name,
            gateway_order_id=gateway_res.gateway_order_id,
            client_token=gateway_res.client_token,
            is_mock=gateway_res.is_mock,
        )

    async def verify_and_process_payment(
        self,
        user_id: str,
        payload: PaymentVerifyRequest,
    ) -> PaymentVerifyResponse:
        """Verify payment and immediately trigger telecom recharge."""
        order = await self.session.get(Order, payload.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        pay_query = select(Payment).where(Payment.order_id == order.id)
        payment = (await self.session.execute(pay_query)).scalars().first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment record not found.")

        # Guard against duplicate verification
        if payment.status == "SUCCESS":
            return PaymentVerifyResponse(
                success=True,
                order_id=order.id,
                order_status=order.status,
                message="Payment already verified and processed.",
            )

        gateway = PaymentGatewayFactory.get_adapter(payment.gateway_name)
        ver_result = await gateway.verify_payment(
            payload={
                "gateway_payment_id": payload.gateway_payment_id,
                "amount_in_paise": order.amount_in_paise,
                "payment_method": payload.payment_method,
            },
            signature=payload.signature or "",
        )

        if not ver_result.is_valid:
            # Transition PAYMENT_PENDING -> PAYMENT_FAILED
            validate_transition(TransactionState.PAYMENT_PENDING, TransactionState.PAYMENT_FAILED)
            order.status = TransactionState.PAYMENT_FAILED.value
            payment.status = "FAILED"
            payment.failure_reason = ver_result.failure_reason
            await self.session.commit()
            return PaymentVerifyResponse(
                success=False,
                order_id=order.id,
                order_status=order.status,
                message=ver_result.failure_reason or "Payment verification failed.",
            )

        # Transition PAYMENT_PENDING -> PAYMENT_SUCCESS
        validate_transition(TransactionState.PAYMENT_PENDING, TransactionState.PAYMENT_SUCCESS)
        order.status = TransactionState.PAYMENT_SUCCESS.value
        payment.status = "SUCCESS"
        payment.gateway_payment_id = ver_result.gateway_payment_id
        payment.payment_method = payload.payment_method
        payment.signature = payload.signature

        self.session.add(
            AuditLog(
                user_id=user_id,
                action="PAYMENT_SUCCESS",
                entity_type="PAYMENT",
                entity_id=payment.id,
                metadata_json=f'{{"gateway_pay_id": "{ver_result.gateway_payment_id}"}}',
            )
        )
        await self.session.commit()

        # Instantly orchestrate telecom recharge!
        recharge = await self.recharge_service.execute_order_recharge(order.id)
        await self.session.refresh(order)

        return PaymentVerifyResponse(
            success=True,
            order_id=order.id,
            order_status=order.status,
            recharge_status=recharge.status,
            telecom_reference_id=recharge.telecom_reference_id,
            message="Payment verified and telecom recharge processed.",
        )
