"""
Schemas para eventos de RabbitMQ.
Definen la estructura de mensajes publicados al message broker.
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID


class EmailVerificationEvent(BaseModel):
    """
    Evento publicado cuando un usuario se registra y necesita verificar su email.
    Routing key: email.verification
    """
    user_id: UUID
    email: EmailStr
    name: str
    verification_token: str
    frontend_url: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "verification_token": "abc123xyz456",
                "frontend_url": "http://localhost:3000"
            }
        }
    )


class WelcomeEmailEvent(BaseModel):
    """
    Evento publicado cuando un usuario verifica exitosamente su email.
    Routing key: email.welcome
    """
    user_id: UUID
    email: EmailStr
    name: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
    )


class PasswordResetEvent(BaseModel):
    """
    Evento publicado cuando un usuario solicita resetear su contraseña.
    Routing key: email.password_reset
    """
    user_id: UUID
    email: EmailStr
    name: str
    reset_token: str
    frontend_url: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "reset_token": "xyz789abc123",
                "frontend_url": "http://localhost:3000"
            }
        }
    )


class PasswordChangedEvent(BaseModel):
    """
    Evento publicado cuando un usuario cambia exitosamente su contraseña.
    Routing key: email.password_changed
    """
    user_id: UUID
    email: EmailStr
    name: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
    )
