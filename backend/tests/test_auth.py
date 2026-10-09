"""Test authentication flow, OTP generation, verification, and rate limiting."""

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.core.database import Base
from backend.app.services.auth_service import AuthService
from backend.app.schemas.auth import validate_indian_phone


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session
    await engine.dispose()


def test_phone_validation():
    """Verify phone validation logic."""
    assert validate_indian_phone("9876543210") == "+919876543210"
    assert validate_indian_phone("+91 98765 43210") == "+919876543210"
    assert validate_indian_phone("919876543210") == "+919876543210"

    with pytest.raises(ValueError):
        validate_indian_phone("1234567890")  # Invalid starting digit
    with pytest.raises(ValueError):
        validate_indian_phone("98765")  # Too short


@pytest.mark.asyncio
async def test_otp_request_and_verify(db_session: AsyncSession):
    """Verify end-to-end OTP request and verification."""
    auth_service = AuthService(db_session)
    phone = "+919876543210"

    # Request OTP
    otp_resp = await auth_service.request_otp(phone)
    assert otp_resp.success is True
    assert otp_resp.dev_otp == "123456"

    # Verify with correct OTP
    token_resp = await auth_service.verify_otp(phone, "123456")
    assert token_resp.access_token is not None
    assert token_resp.user.phone_number == phone

    # Verify user token can retrieve user
    user = await auth_service.get_user_from_token(token_resp.access_token)
    assert user.phone_number == phone


@pytest.mark.asyncio
async def test_otp_rate_limiting(db_session: AsyncSession):
    """Verify rate limiter blocks after 3 OTP requests within 10 minutes."""
    auth_service = AuthService(db_session)
    phone = "+919876543211"

    # 3 allowed requests
    for _ in range(3):
        resp = await auth_service.request_otp(phone)
        assert resp.success is True

    # 4th request must trigger HTTP 429
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.request_otp(phone)
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_otp_invalid_code_handling(db_session: AsyncSession):
    """Verify invalid OTP triggers HTTP 400."""
    auth_service = AuthService(db_session)
    phone = "+919876543212"

    await auth_service.request_otp(phone)
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_otp(phone, "000000")
    assert exc_info.value.status_code == 400
