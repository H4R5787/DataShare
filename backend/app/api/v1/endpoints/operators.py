"""Telecom operator and circle detection endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.operator import (
    CircleDTO,
    OperatorDetectRequest,
    OperatorDetectResponse,
    OperatorDTO,
)
from backend.app.services.telecom_service import TelecomService

router = APIRouter(prefix="/operators", tags=["Telecom Operators"])


@router.get("", response_model=List[OperatorDTO])
async def list_operators(db: AsyncSession = Depends(get_db)):
    """List all supported telecom operators (Jio, Airtel, Vi, BSNL)."""
    service = TelecomService(db)
    return await service.list_operators()


@router.get("/circles", response_model=List[CircleDTO])
async def list_circles(db: AsyncSession = Depends(get_db)):
    """List supported telecom circles."""
    service = TelecomService(db)
    return await service.list_circles()


@router.post("/detect", response_model=OperatorDetectResponse)
async def detect_operator(
    payload: OperatorDetectRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate recipient mobile number and detect operator and circle.
    Supports MNP detection with confidence rating.
    """
    try:
        validated_phone = payload.get_validated_phone()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    service = TelecomService(db)
    return await service.detect_operator_for_phone(validated_phone)
