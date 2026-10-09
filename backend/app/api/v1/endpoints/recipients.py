"""Saved recipients address book API endpoints."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import mask_phone_number
from backend.app.models.operator import Operator
from backend.app.models.recipient import SavedRecipient
from backend.app.models.user import User
from backend.app.schemas.auth import validate_indian_phone

router = APIRouter(prefix="/recipients", tags=["Saved Recipients"])


class RecipientCreateRequest(BaseModel):
    phone_number: str
    nickname: str
    operator_id: Optional[str] = None
    circle_id: Optional[str] = None


class RecipientDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone_number: str
    phone_number_masked: str
    nickname: str
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    operator_code: Optional[str] = None


@router.get("", response_model=List[RecipientDTO])
async def list_saved_recipients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List frequent saved recipients for 1-tap re-gifting."""
    query = (
        select(SavedRecipient)
        .where(SavedRecipient.user_id == current_user.id)
        .order_by(SavedRecipient.last_recharged_at.desc().nullslast())
    )
    recipients = (await db.execute(query)).scalars().all()

    results = []
    for r in recipients:
        op = await db.get(Operator, r.operator_id) if r.operator_id else None
        results.append(
            RecipientDTO(
                id=r.id,
                phone_number=r.phone_number,
                phone_number_masked=mask_phone_number(r.phone_number),
                nickname=r.nickname,
                operator_id=r.operator_id,
                operator_name=op.name if op else None,
                operator_code=op.code if op else None,
            )
        )
    return results


@router.post("", response_model=RecipientDTO, status_code=status.HTTP_201_CREATED)
async def save_recipient(
    payload: RecipientCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or bookmark a recipient contact."""
    clean_phone = validate_indian_phone(payload.phone_number)

    # Check if already saved
    existing = await db.scalar(
        select(SavedRecipient).where(
            SavedRecipient.user_id == current_user.id,
            SavedRecipient.phone_number == clean_phone,
        )
    )
    if existing:
        existing.nickname = payload.nickname
        if payload.operator_id:
            existing.operator_id = payload.operator_id
        await db.commit()
        recipient = existing
    else:
        recipient = SavedRecipient(
            user_id=current_user.id,
            phone_number=clean_phone,
            nickname=payload.nickname,
            operator_id=payload.operator_id,
            circle_id=payload.circle_id,
        )
        db.add(recipient)
        await db.commit()

    op = await db.get(Operator, recipient.operator_id) if recipient.operator_id else None
    return RecipientDTO(
        id=recipient.id,
        phone_number=recipient.phone_number,
        phone_number_masked=mask_phone_number(recipient.phone_number),
        nickname=recipient.nickname,
        operator_id=recipient.operator_id,
        operator_name=op.name if op else None,
        operator_code=op.code if op else None,
    )
