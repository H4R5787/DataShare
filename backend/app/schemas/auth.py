"""Authentication request and response Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


def validate_indian_phone(phone: str) -> str:
    """Validate E.164 format Indian mobile phone number."""
    clean = phone.strip().replace(" ", "").replace("-", "")
    if clean.startswith("+91"):
        digits = clean[3:]
    elif clean.startswith("91") and len(clean) == 12:
        digits = clean[2:]
    else:
        digits = clean
    
    if len(digits) != 10 or not digits.isdigit() or digits[0] not in "6789":
        raise ValueError("Invalid Indian mobile number. Must be 10 digits starting with 6, 7, 8, or 9.")
    
    return f"+91{digits}"


class OTPRequest(BaseModel):
    phone_number: str = Field(..., description="Mobile number with or without +91 prefix")

    @field_validator("phone_number")
    def check_phone(cls, v: str) -> str:
        return validate_indian_phone(v)


class OTPResponse(BaseModel):
    success: bool
    message: str
    phone_number_masked: str
    expires_in_seconds: int
    dev_otp: Optional[str] = None  # Available only in development/mock mode


class OTPVerifyRequest(BaseModel):
    phone_number: str = Field(..., description="Mobile number with or without +91 prefix")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

    @field_validator("phone_number")
    def check_phone(cls, v: str) -> str:
        return validate_indian_phone(v)

    @field_validator("otp")
    def check_otp(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be exactly 6 numeric digits.")
        return v


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone_number: str
    phone_number_masked: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserDTO
