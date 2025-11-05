from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """Roles disponibles para usuarios"""
    USUARIO = "Usuario"
    ADMIN_PARQUEADERO = "Administrador de Parqueadero"


class User(Base):
    """
    Modelo de Usuario para autenticación y autorización

    Attributes:
        id: Identificador único UUID
        name: Nombre completo del usuario
        email: Correo electrónico único
        password: Contraseña hasheada con bcrypt
        role: Rol del usuario (Usuario o Administrador de Parqueadero)
        is_verified: Indica si el email ha sido verificado
        is_active: Indica si la cuenta está activa
        verification_token: Token temporal para verificación de email
        verification_token_expires: Fecha de expiración del token de verificación
        reset_token: Token temporal para recuperación de contraseña
        reset_token_expires: Fecha de expiración del token de reset
        created_at: Fecha de creación del registro
        updated_at: Fecha de última actualización
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role"),
        nullable=True,
        default=UserRole.USUARIO
    )

    # Estado de la cuenta
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Tokens de verificación y recuperación
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
