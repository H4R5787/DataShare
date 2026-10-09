"""Order placement and status API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import mask_phone_number
from backend.app.models.operator import Operator
from backend.app.models.plan import Plan
from backend.app.models.user import User
from backend.app.schemas.order import OrderCreateRequest, OrderDTO
from backend.app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderDTO, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    x_idempotency_key: str = Header(..., description="Unique UUIDv4 idempotency key to prevent double charging"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new data gifting order.
    Protected by strict idempotency locking via 'X-Idempotency-Key'.
    """
    service = OrderService(db)
    return await service.create_order(
        user_id=current_user.id,
        payload=payload,
        idempotency_key=x_idempotency_key,
    )


@router.get("/{order_id}", response_model=OrderDTO)
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details of an order with IDOR verification."""
    service = OrderService(db)
    order = await service.get_order_by_id(order_id, current_user.id)
    operator = await db.get(Operator, order.operator_id)
    plan = await db.get(Plan, order.plan_id)

    return OrderDTO(
        order_id=order.id,
        recipient_phone=order.recipient_phone,
        recipient_phone_masked=mask_phone_number(order.recipient_phone),
        operator_id=order.operator_id,
        operator_name=operator.name if operator else "Unknown",
        circle_id=order.circle_id,
        plan_id=order.plan_id,
        plan_data=plan.data_amount if plan else "Data Pack",
        plan_validity=plan.validity_desc if plan else "Standard",
        amount_in_paise=order.amount_in_paise,
        amount_formatted=f"₹{order.amount_in_paise // 100}",
        currency=order.currency,
        status=order.status,
        created_at=order.created_at,
    )
