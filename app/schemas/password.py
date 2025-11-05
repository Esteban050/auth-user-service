from pydantic import BaseModel, EmailStr, Field, field_validator


# Schema para solicitud de recuperación de contraseña
class ForgotPasswordRequest(BaseModel):
    """Schema para solicitud de recuperación de contraseña"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Schema para respuesta de solicitud de recuperación"""
    message: str


# Schema para reset de contraseña
class ResetPasswordRequest(BaseModel):
    """Schema para reset de contraseña con token"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """
        Valida que la nueva contraseña cumpla con los requisitos mínimos:
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


class ResetPasswordResponse(BaseModel):
    """Schema para respuesta de reset de contraseña exitoso"""
    message: str


# Schema para cambio de contraseña (usuario autenticado)
class ChangePasswordRequest(BaseModel):
    """Schema para cambio de contraseña del usuario autenticado"""
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


class ChangePasswordResponse(BaseModel):
    """Schema para respuesta de cambio de contraseña exitoso"""
    message: str


# Schema para validar token de reset
class ValidateResetTokenRequest(BaseModel):
    """Schema para validar si un token de reset es válido"""
    token: str = Field(..., min_length=1)


class ValidateResetTokenResponse(BaseModel):
    """Schema para respuesta de validación de token"""
    valid: bool
    message: str
