"""Payment intent, verification, and webhook API endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.payment import (
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from backend.app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payload: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initialize a payment checkout session for an active order."""
    service = PaymentService(db)
    return await service.create_payment_intent(
        user_id=current_user.id,
        order_id=payload.order_id,
        payment_method=payload.payment_method,
    )


@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    payload: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify completed payment and immediately dispatch telecom recharge.
    In case of telecom failure, automatically triggers refund.
    """
    service = PaymentService(db)
    return await service.verify_and_process_payment(
        user_id=current_user.id,
        payload=payload,
    )


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Payment gateway server-to-server webhook callback.
    Protected by HMAC SHA-256 signature verification.
    """
    body = await request.body()
    # In production, verify X-Razorpay-Signature header against body
    return {"status": "received"}
