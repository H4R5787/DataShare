"""Security utilities: JWT handling, OTP hashing, phone masking, and idempotency hashing."""

import hashlib
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from backend.app.core.config import settings


def hash_otp(phone: str, otp: str) -> str:
    """Generate SHA-256 salted hash of OTP for secure persistence."""
    salt = settings.SECRET_KEY[:16]
    content = f"{phone}:{otp}:{salt}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def verify_otp_hash(phone: str, otp: str, expected_hash: str) -> bool:
    """Constant-time verification of OTP against stored hash."""
    computed = hash_otp(phone, otp)
    return hashlib.sha256(computed.encode()).hexdigest() == hashlib.sha256(expected_hash.encode()).hexdigest()


def generate_otp() -> str:
    """Generate 6-digit numeric OTP."""
    if settings.ENABLE_MOCK_OTP:
        return settings.MOCK_OTP_DEFAULT
    return f"{random.randint(100000, 999999)}"


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def mask_phone_number(phone: str) -> str:
    """
    Mask phone number for privacy display.
    Example: '+919876543210' -> '+91 98765 •••••'
    """
    if not phone or len(phone) < 10:
        return phone
    # Strip any spaces
    clean = phone.replace(" ", "")
    if clean.startswith("+91") and len(clean) == 13:
        return f"+91 {clean[3:8]} •••••"
    if len(clean) == 10:
        return f"+91 {clean[:5]} •••••"
    return f"{clean[:5]}•••••"


def hash_request_payload(data: str) -> str:
    """Compute SHA-256 hash of payload string for idempotency check."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
