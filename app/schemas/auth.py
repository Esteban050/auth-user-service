from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.user import UserResponse


# Schema para login
class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Schema para respuesta de login exitoso"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# Schema para registro
class RegisterRequest(BaseModel):
    """Schema para solicitud de registro"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[UserRole] = UserRole.USUARIO


class RegisterResponse(BaseModel):
    """Schema para respuesta de registro exitoso"""
    message: str
    user: UserResponse


# Schemas para tokens
class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    """Schema para par de tokens (access y refresh)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema para payload del token JWT"""
    sub: str  # Subject (user_id)
    exp: int  # Expiration time
    type: str  # Token type: "access" o "refresh"


class RefreshTokenRequest(BaseModel):
    """Schema para solicitud de refresh token"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema para respuesta de refresh token"""
    access_token: str
    token_type: str = "bearer"


# Schema para verificación de email
class VerifyEmailResponse(BaseModel):
    """Schema para respuesta de verificación de email"""
    message: str
    email_verified: bool


# Schema para logout
class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    message: str


# Schema para resend verification email
class ResendVerificationRequest(BaseModel):
    """Schema para reenvío de email de verificación"""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """Schema para respuesta de reenvío de verificación"""
    message: str
