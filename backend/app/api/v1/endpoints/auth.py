"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import mask_phone_number
from backend.app.models.user import User
from backend.app.schemas.auth import (
    OTPRequest,
    OTPResponse,
    OTPVerifyRequest,
    TokenResponse,
    UserDTO,
)
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    payload: OTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a 6-digit verification code.
    In development/mock mode, the code '123456' is also returned in `dev_otp`.
    """
    client_ip = request.client.host if request.client else None
    service = AuthService(db)
    return await service.request_otp(payload.phone_number, ip_address=client_ip)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    payload: OTPVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify OTP code and authenticate user.
    Returns signed JWT access token and user profile.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "Unknown Client")
    service = AuthService(db)
    return await service.verify_otp(
        phone_number=payload.phone_number,
        otp=payload.otp,
        device_info=user_agent,
        ip_address=client_ip,
    )


@router.get("/me", response_model=UserDTO)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve profile of currently authenticated user."""
    return UserDTO(
        id=current_user.id,
        phone_number=current_user.phone_number,
        phone_number_masked=mask_phone_number(current_user.phone_number),
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
