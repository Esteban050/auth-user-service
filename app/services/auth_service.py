from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.crud import user as user_crud
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.services.message_service import message_service
from app.services.token_service import token_service
from app.schemas.events import (
    EmailVerificationEvent,
    WelcomeEmailEvent,
    PasswordResetEvent,
    PasswordChangedEvent
)


class AuthService:
    """
    Servicio de autenticación y registro de usuarios.
    """

    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> User:
        """
        Registra un nuevo usuario y envía email de verificación.

        Args:
            db: Sesión de base de datos
            user_create: Datos del usuario a crear

        Returns:
            Usuario creado

        Raises:
            HTTPException 400: Si el email ya está registrado
        """
        # Verificar si el email ya existe
        existing_user = user_crud.get_by_email(db, email=user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )

        # Crear usuario
        user = user_crud.create(db, obj_in=user_create)

        # Generar token de verificación
        verification_token = token_service.create_verification_token(db, user)

        # Publicar evento de verificación a RabbitMQ
        event = EmailVerificationEvent(
            user_id=user.id,
            email=user.email,
            name=user.name,
            verification_token=verification_token,
            frontend_url=settings.FRONTEND_URL
        )
        message_service.publish_verification_email(event)

        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[str, str, User]:
        """
        Autentica un usuario y genera tokens de acceso.

        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña del usuario

        Returns:
            Tupla (access_token, refresh_token, user)

        Raises:
            HTTPException 401: Si las credenciales son inválidas
            HTTPException 403: Si el usuario está inactivo o no verificado
        """
        # Autenticar usuario
        user = user_crud.authenticate(db, email=email, password=password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        # Verificar que el usuario esté activo
        if not user_crud.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacta con soporte."
            )

        # Verificar que el email esté verificado
        if not user_crud.is_verified(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email no verificado. Por favor verifica tu correo electrónico."
            )

        # Generar tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return access_token, refresh_token, user

    @staticmethod
    def refresh_access_token(user: User) -> str:
        """
        Genera un nuevo access token usando un refresh token válido.

        Args:
            user: Usuario autenticado

        Returns:
            Nuevo access token

        Raises:
            HTTPException 403: Si el usuario está inactivo
        """
        # Verificar que el usuario esté activo
        if not user_crud.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )

        # Generar nuevo access token
        access_token = create_access_token(subject=str(user.id))
        return access_token

    @staticmethod
    def verify_email(db: Session, token: str) -> User:
        """
        Verifica el email de un usuario usando el token.

        Args:
            db: Sesión de base de datos
            token: Token de verificación

        Returns:
            Usuario verificado

        Raises:
            HTTPException 400: Si el token es inválido o el email ya fue verificado
        """
        success, message, user = token_service.verify_email_token(db, token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Publicar evento de bienvenida a RabbitMQ
        event = WelcomeEmailEvent(
            user_id=user.id,
            email=user.email,
            name=user.name
        )
        message_service.publish_welcome_email(event)

        return user

    @staticmethod
    def resend_verification_email(db: Session, email: str) -> None:
        """
        Reenvía el email de verificación a un usuario.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Raises:
            HTTPException 404: Si el usuario no existe
            HTTPException 400: Si el email ya está verificado
        """
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya ha sido verificado"
            )

        # Regenerar token
        verification_token = token_service.resend_verification_token(db, user)

        # Publicar evento de verificación a RabbitMQ
        event = EmailVerificationEvent(
            user_id=user.id,
            email=user.email,
            name=user.name,
            verification_token=verification_token,
            frontend_url=settings.FRONTEND_URL
        )
        message_service.publish_verification_email(event)

    @staticmethod
    def request_password_reset(db: Session, email: str) -> None:
        """
        Solicita un reset de contraseña y envía email con el token.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Note:
            Por seguridad, no revela si el email existe o no.
            Siempre retorna éxito para evitar enumerar usuarios.
        """
        user = user_crud.get_by_email(db, email=email)

        # Si el usuario no existe, no hacer nada pero retornar éxito (seguridad)
        if not user:
            return

        # Generar token de reset
        reset_token = token_service.create_reset_token(db, user)

        # Publicar evento de reset de contraseña a RabbitMQ
        event = PasswordResetEvent(
            user_id=user.id,
            email=user.email,
            name=user.name,
            reset_token=reset_token,
            frontend_url=settings.FRONTEND_URL
        )
        message_service.publish_password_reset_email(event)

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> None:
        """
        Resetea la contraseña de un usuario usando el token.

        Args:
            db: Sesión de base de datos
            token: Token de reset
            new_password: Nueva contraseña

        Raises:
            HTTPException 400: Si el token es inválido o expiró
        """
        success, message, user = token_service.verify_reset_token(db, token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Actualizar contraseña
        user_crud.update_password(db, db_obj=user, new_password=new_password)

        # Limpiar token de reset
        token_service.clear_reset_token(db, user)

        # Publicar evento de cambio de contraseña a RabbitMQ
        event = PasswordChangedEvent(
            user_id=user.id,
            email=user.email,
            name=user.name
        )
        message_service.publish_password_changed_email(event)


# Instancia única del servicio
auth_service = AuthService()
