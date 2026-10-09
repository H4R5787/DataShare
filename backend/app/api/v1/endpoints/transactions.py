"""Transaction history and live tracking API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.transaction import (
    TransactionDetailsDTO,
    TransactionSummaryDTO,
)
from backend.app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionSummaryDTO])
async def list_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve authenticated user's transaction history."""
    service = TransactionService(db)
    return await service.list_user_transactions(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/{order_id}", response_model=TransactionDetailsDTO)
async def get_transaction_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full transaction details with state timeline and telecom reference."""
    service = TransactionService(db)
    return await service.get_transaction_details(
        order_id=order_id,
        user_id=current_user.id,
    )
