"""Transaction history and timeline reconstruction service."""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import mask_phone_number
from backend.app.models.operator import Operator
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.plan import Plan
from backend.app.models.recharge import Recharge
from backend.app.models.refund import Refund
from backend.app.schemas.transaction import (
    TimelineEvent,
    TransactionDetailsDTO,
    TransactionSummaryDTO,
)


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_user_transactions(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[TransactionSummaryDTO]:
        """Fetch list of user's past transactions."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        orders = (await self.session.execute(query)).scalars().all()

        summaries = []
        for o in orders:
            op = await self.session.get(Operator, o.operator_id)
            plan = await self.session.get(Plan, o.plan_id)
            summaries.append(
                TransactionSummaryDTO(
                    order_id=o.id,
                    recipient_phone_masked=mask_phone_number(o.recipient_phone),
                    operator_name=op.name if op else "Unknown",
                    operator_code=op.code if op else "MOCK",
                    plan_data=plan.data_amount if plan else "Data Pack",
                    amount_formatted=f"₹{o.amount_in_paise // 100}",
                    status=o.status,
                    created_at=o.created_at,
                )
            )
        return summaries

    async def get_transaction_details(
        self,
        order_id: str,
        user_id: str,
    ) -> TransactionDetailsDTO:
        """Fetch complete transaction details with reconstructed timeline."""
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        op = await self.session.get(Operator, order.operator_id)
        plan = await self.session.get(Plan, order.plan_id)

        # Look up recharge
        recharge_query = select(Recharge).where(Recharge.order_id == order.id)
        recharge = (await self.session.execute(recharge_query)).scalars().first()

        # Look up refund
        refund_query = select(Refund).where(Refund.order_id == order.id)
        refund = (await self.session.execute(refund_query)).scalars().first()

        # Reconstruct timeline
        timeline: List[TimelineEvent] = []
        timeline.append(
            TimelineEvent(
                state="CREATED",
                label="Order Placed",
                timestamp=order.created_at,
                is_completed=True,
            )
        )

        has_payment = order.status in (
            "PAYMENT_SUCCESS",
            "RECHARGE_PENDING",
            "SUCCESS",
            "RECHARGE_FAILED",
            "REFUND_PENDING",
            "REFUNDED",
        )
        if has_payment:
            timeline.append(
                TimelineEvent(
                    state="PAYMENT_SUCCESS",
                    label="Payment Verified",
                    timestamp=order.updated_at,
                    is_completed=True,
                )
            )

        if recharge:
            timeline.append(
                TimelineEvent(
                    state="RECHARGE_PENDING",
                    label=f"Carrier Dispatch ({op.code if op else 'Telecom'})",
                    timestamp=recharge.created_at,
                    is_completed=True,
                )
            )
            if recharge.status == "SUCCESS":
                timeline.append(
                    TimelineEvent(
                        state="SUCCESS",
                        label="Data Pack Activated",
                        timestamp=recharge.completed_at or recharge.updated_at,
                        is_completed=True,
                    )
                )
            elif recharge.status == "FAILED":
                timeline.append(
                    TimelineEvent(
                        state="RECHARGE_FAILED",
                        label="Carrier Fulfillment Failed",
                        timestamp=recharge.updated_at,
                        is_completed=True,
                    )
                )

        if refund:
            timeline.append(
                TimelineEvent(
                    state="REFUNDED",
                    label=f"Auto-Refund Completed ({refund.gateway_refund_id or 'Gateway'})",
                    timestamp=refund.created_at,
                    is_completed=True,
                )
            )

        return TransactionDetailsDTO(
            order_id=order.id,
            recipient_phone=order.recipient_phone,
            recipient_phone_masked=mask_phone_number(order.recipient_phone),
            operator_id=order.operator_id,
            operator_name=op.name if op else "Unknown",
            operator_code=op.code if op else "MOCK",
            plan_id=order.plan_id,
            plan_data=plan.data_amount if plan else "Data Pack",
            plan_validity=plan.validity_desc if plan else "Standard",
            amount_in_paise=order.amount_in_paise,
            amount_formatted=f"₹{order.amount_in_paise // 100}",
            currency=order.currency,
            current_state=order.status,
            telecom_reference_id=recharge.telecom_reference_id if recharge else None,
            refund_status=refund.status if refund else None,
            created_at=order.created_at,
            updated_at=order.updated_at,
            timeline=timeline,
        )
