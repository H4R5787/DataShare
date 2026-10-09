"""Authentication domain service: OTP dispatch, verification, rate limiting, and JWT sessions."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    generate_otp,
    hash_otp,
    mask_phone_number,
    verify_otp_hash,
)
from backend.app.models.user import OTPVerification, User, UserSession
from backend.app.models.audit import AuditLog
from backend.app.schemas.auth import OTPResponse, TokenResponse, UserDTO


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def request_otp(self, phone_number: str, ip_address: Optional[str] = None) -> OTPResponse:
        """Rate-limited OTP request with secure salted hash persistence."""
        now = datetime.now(timezone.utc)
        ten_mins_ago = now - timedelta(minutes=10)

        # Check rate limiting: max 3 requests in the last 10 minutes
        recent_count = await self.session.scalar(
            select(func.count(OTPVerification.id)).where(
                OTPVerification.phone_number == phone_number,
                OTPVerification.created_at >= ten_mins_ago,
            )
        )
        if (recent_count or 0) >= 3:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please wait 10 minutes before trying again.",
            )

        # Generate OTP
        otp = generate_otp()
        otp_hash_val = hash_otp(phone_number, otp)
        expires_at = now + timedelta(seconds=settings.OTP_EXPIRE_SECONDS)

        # Invalidate previous unused OTPs for this phone
        await self.session.execute(
            update(OTPVerification)
            .where(OTPVerification.phone_number == phone_number, OTPVerification.is_used == False)
            .values(is_used=True)
        )

        # Create new OTP record
        record = OTPVerification(
            phone_number=phone_number,
            otp_hash=otp_hash_val,
            expires_at=expires_at,
            is_used=False,
            attempts=0,
        )
        self.session.add(record)

        # Audit log
        audit = AuditLog(
            action="AUTH_OTP_REQUESTED",
            entity_type="AUTH",
            entity_id=phone_number,
            ip_address=ip_address,
        )
        self.session.add(audit)
        await self.session.commit()

        dev_otp = otp if settings.ENABLE_MOCK_OTP else None
        return OTPResponse(
            success=True,
            message="Verification OTP sent successfully",
            phone_number_masked=mask_phone_number(phone_number),
            expires_in_seconds=settings.OTP_EXPIRE_SECONDS,
            dev_otp=dev_otp,
        )

    async def verify_otp(
        self,
        phone_number: str,
        otp: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Verify OTP, authenticate user, create session and issue JWT."""
        now = datetime.now(timezone.utc)

        # Fetch latest active OTP
        query = (
            select(OTPVerification)
            .where(
                OTPVerification.phone_number == phone_number,
                OTPVerification.is_used == False,
                OTPVerification.expires_at >= now,
            )
            .order_by(OTPVerification.created_at.desc())
        )
        record = (await self.session.execute(query)).scalars().first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP. Please request a new code.",
            )

        if record.attempts >= 5:
            record.is_used = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please request a new OTP.",
            )

        # Verify hash
        if not verify_otp_hash(phone_number, otp, record.otp_hash):
            record.attempts += 1
            await self.session.commit()
            remaining = 5 - record.attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect OTP. {remaining} attempts remaining.",
            )

        # Mark OTP consumed
        record.is_used = True

        # Find or create user
        user_query = select(User).where(User.phone_number == phone_number)
        user = (await self.session.execute(user_query)).scalars().first()
        if not user:
            user = User(
                phone_number=phone_number,
                is_active=True,
                is_verified=True,
            )
            self.session.add(user)
            await self.session.flush()

        # Generate JWT Access Token
        access_token = create_access_token(subject=user.id)
        token_hash = hash_otp(user.id, access_token[:16])

        # Create session
        session_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session_record = UserSession(
            user_id=user.id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=session_expires,
        )
        self.session.add(session_record)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="AUTH_LOGIN_SUCCESS",
            entity_type="AUTH",
            entity_id=user.id,
            ip_address=ip_address,
        )
        self.session.add(audit)
        await self.session.commit()

        user_dto = UserDTO(
            id=user.id,
            phone_number=user.phone_number,
            phone_number_masked=mask_phone_number(user.phone_number),
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_dto,
        )

    async def get_user_from_token(self, token: str) -> User:
        """Validate token and retrieve active user."""
        payload = decode_access_token(token)
        if not payload or not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload["sub"]
        user = await self.session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated or does not exist.",
            )
        return user
