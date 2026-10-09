"""Order placement and state lifecycle service."""

import random
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import mask_phone_number
from backend.app.core.state_machine import TransactionState, validate_transition
from backend.app.models.audit import AuditLog
from backend.app.models.operator import Operator
from backend.app.models.order import Order
from backend.app.models.plan import Plan
from backend.app.schemas.order import OrderCreateRequest, OrderDTO
from backend.app.services.idempotency_service import IdempotencyService


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.idempotency_service = IdempotencyService(session)

    async def create_order(
        self,
        user_id: str,
        payload: OrderCreateRequest,
        idempotency_key: str,
    ) -> OrderDTO:
        """Create an order with strict idempotency and validation."""
        # Check plan
        plan = await self.session.get(Plan, payload.plan_id)
        if not plan or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected data pack is unavailable or inactive.",
            )

        # Check operator
        operator = await self.session.get(Operator, payload.operator_id)
        if not operator or not operator.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected telecom operator is unavailable.",
            )

        # Acquire idempotency lock or replay completed response
        cached = await self.idempotency_service.acquire_lock_or_replay(
            key=idempotency_key,
            user_id=user_id,
            request_path="/api/v1/orders",
            payload_data=payload.model_dump(),
        )
        if cached:
            _, response_data = cached
            return OrderDTO(**response_data)

        try:
            validated_phone = payload.get_validated_phone()
        except ValueError as e:
            await self.idempotency_service.release_lock_on_failure(idempotency_key)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Generate unique human-readable Order ID
        now = datetime.now(timezone.utc)
        order_id = f"ORD_{now.strftime('%Y%m%d')}_{random.randint(10000, 99999)}"

        # Initial order state: CREATED
        order = Order(
            id=order_id,
            user_id=user_id,
            recipient_phone=validated_phone,
            operator_id=operator.id,
            circle_id=payload.circle_id,
            plan_id=plan.id,
            amount_in_paise=plan.price_in_paise,
            currency="INR",
            status=TransactionState.CREATED.value,
            idempotency_key=idempotency_key,
        )
        self.session.add(order)
        await self.session.flush()

        # Transition CREATED -> PAYMENT_PENDING
        validate_transition(TransactionState.CREATED, TransactionState.PAYMENT_PENDING)
        order.status = TransactionState.PAYMENT_PENDING.value

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="ORDER_CREATED",
            entity_type="ORDER",
            entity_id=order_id,
            metadata_json=f'{{"amount": {plan.price_in_paise}, "recipient": "{validated_phone}"}}',
        )
        self.session.add(audit)
        await self.session.commit()

        order_dto = OrderDTO(
            order_id=order.id,
            recipient_phone=order.recipient_phone,
            recipient_phone_masked=mask_phone_number(order.recipient_phone),
            operator_id=operator.id,
            operator_name=operator.name,
            circle_id=order.circle_id,
            plan_id=plan.id,
            plan_data=plan.data_amount,
            plan_validity=plan.validity_desc,
            amount_in_paise=order.amount_in_paise,
            amount_formatted=f"₹{order.amount_in_paise // 100}",
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
        )

        # Cache completed response in idempotency record
        await self.idempotency_service.record_completed(
            key=idempotency_key,
            response_code=201,
            response_body=order_dto.model_dump(),
        )

        return order_dto

    async def get_order_by_id(self, order_id: str, user_id: str) -> Order:
        """Fetch order with IDOR protection."""
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order '{order_id}' was not found.",
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this order.",
            )
        return order
