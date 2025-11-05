from sqlalchemy.orm import Session

from app.models.user import User
from app.crud import user as user_crud
from app.core.security import (
    generate_verification_token,
    generate_reset_token,
)
from app.core.config import settings


class TokenService:
    """
    Servicio para gestión de tokens de verificación y reset de contraseña.
    """

    @staticmethod
    def create_verification_token(db: Session, user: User) -> str:
        """
        Crea y asigna un token de verificación a un usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario al que asignar el token

        Returns:
            Token de verificación generado
        """
        token = generate_verification_token()
        user_crud.set_verification_token(
            db,
            db_obj=user,
            token=token,
            expires_hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
        )
        return token

    @staticmethod
    def verify_email_token(db: Session, token: str) -> tuple[bool, str, User | None]:
        """
        Verifica un token de verificación de email.

        Args:
            db: Sesión de base de datos
            token: Token a verificar

        Returns:
            Tupla (success, message, user)
            - success: True si el token es válido y el email fue verificado
            - message: Mensaje descriptivo del resultado
            - user: Usuario verificado o None si hubo error
        """
        user = user_crud.get_by_verification_token(db, token=token)

        if not user:
            return False, "Token de verificación inválido o expirado", None

        if user.is_verified:
            return False, "Este email ya ha sido verificado", user

        # Verificar el email
        user = user_crud.verify_email(db, db_obj=user)

        return True, "Email verificado exitosamente", user

    @staticmethod
    def create_reset_token(db: Session, user: User) -> str:
        """
        Crea y asigna un token de reset de contraseña a un usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario al que asignar el token

        Returns:
            Token de reset generado
        """
        token = generate_reset_token()
        user_crud.set_reset_token(
            db,
            db_obj=user,
            token=token,
            expires_hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        return token

    @staticmethod
    def verify_reset_token(db: Session, token: str) -> tuple[bool, str, User | None]:
        """
        Verifica un token de reset de contraseña.

        Args:
            db: Sesión de base de datos
            token: Token a verificar

        Returns:
            Tupla (success, message, user)
            - success: True si el token es válido
            - message: Mensaje descriptivo del resultado
            - user: Usuario asociado al token o None si hubo error
        """
        user = user_crud.get_by_reset_token(db, token=token)

        if not user:
            return False, "Token de reset inválido o expirado", None

        return True, "Token válido", user

    @staticmethod
    def clear_reset_token(db: Session, user: User) -> None:
        """
        Limpia el token de reset de contraseña de un usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario al que limpiar el token
        """
        user_crud.clear_reset_token(db, db_obj=user)

    @staticmethod
    def resend_verification_token(db: Session, user: User) -> str:
        """
        Regenera y reenvía un token de verificación.

        Args:
            db: Sesión de base de datos
            user: Usuario al que regenerar el token

        Returns:
            Nuevo token de verificación
        """
        token = generate_verification_token()
        user_crud.set_verification_token(
            db,
            db_obj=user,
            token=token,
            expires_hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
        )
        return token


# Instancia única del servicio
token_service = TokenService()
