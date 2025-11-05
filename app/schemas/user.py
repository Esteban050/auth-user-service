from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


# Schemas Base
class UserBase(BaseModel):
    """Schema base con campos comunes de usuario"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)


# Schemas para creación
class UserCreate(UserBase):
    """Schema para registro de nuevo usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.USUARIO

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla con los requisitos mínimos:
        - Al menos 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')

        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')

        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')

        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')

        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida que el nombre no esté vacío ni contenga solo espacios"""
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


# Schemas para actualización
class UserUpdate(BaseModel):
    """Schema para actualización de perfil de usuario"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el nombre no esté vacío ni contenga solo espacios"""
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            return v.strip()
        return v


class UserUpdatePassword(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Valida que la nueva contraseña cumpla con los requisitos"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')

        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')

        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')

        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')

        return v


# Schemas para respuesta
class UserResponse(UserBase):
    """Schema para respuesta con datos de usuario (sin contraseña)"""
    id: UUID
    role: UserRole
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Permite crear desde objetos ORM
    }


class UserInDB(UserResponse):
    """Schema interno que incluye campos sensibles (usado internamente)"""
    password: str
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None


# Schema simplificado para listas
class UserListResponse(BaseModel):
    """Schema simplificado para listados de usuarios"""
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    is_verified: bool
    is_active: bool

    model_config = {
        "from_attributes": True
    }
