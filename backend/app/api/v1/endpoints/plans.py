"""Telecom data plans endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.plan import PlanDTO
from backend.app.services.telecom_service import TelecomService

router = APIRouter(prefix="/plans", tags=["Data Plans"])


@router.get("", response_model=List[PlanDTO])
async def list_plans(
    operator_id: Optional[str] = Query(None, description="Operator unique ID"),
    operator_code: Optional[str] = Query(None, description="Operator code (JIO, AIRTEL, VI, BSNL)"),
    category: Optional[str] = Query(None, description="Plan category (BOOSTER, WORK, BULK)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve available retail mobile data packs.
    Returns real-time data allowance, price in paise, validity, and carrier disclosures.
    """
    service = TelecomService(db)
    return await service.get_plans_for_operator(
        operator_id=operator_id,
        operator_code=operator_code,
        category=category,
    )
