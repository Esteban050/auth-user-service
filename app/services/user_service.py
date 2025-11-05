from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserUpdate
from app.crud import user as user_crud
from app.services.email_service import email_service


class UserService:
    """
    Servicio para gestión de perfiles de usuario.
    """

    @staticmethod
    def get_user_profile(user: User) -> User:
        """
        Obtiene el perfil del usuario actual.

        Args:
            user: Usuario autenticado

        Returns:
            Usuario con todos sus datos
        """
        return user

    @staticmethod
    def update_user_profile(
        db: Session,
        user: User,
        user_update: UserUpdate
    ) -> User:
        """
        Actualiza el perfil del usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario a actualizar
            user_update: Datos a actualizar

        Returns:
            Usuario actualizado

        Raises:
            HTTPException 400: Si el nuevo email ya está en uso
        """
        # Si se está actualizando el email, verificar que no exista
        if user_update.email and user_update.email != user.email:
            existing_user = user_crud.get_by_email(db, email=user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este email ya está en uso"
                )

            # Si cambia el email, marcar como no verificado
            user.is_verified = False

            # Aquí podrías generar un nuevo token de verificación si lo deseas
            # from app.services.token_service import token_service
            # verification_token = token_service.create_verification_token(db, user)
            # email_service.send_verification_email(...)

        # Actualizar usuario
        updated_user = user_crud.update(db, db_obj=user, obj_in=user_update)

        return updated_user

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Cambia la contraseña del usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario autenticado
            current_password: Contraseña actual
            new_password: Nueva contraseña

        Raises:
            HTTPException 400: Si la contraseña actual es incorrecta
        """
        # Verificar contraseña actual
        from app.core.security import verify_password

        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )

        # Verificar que la nueva contraseña sea diferente
        if verify_password(new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )

        # Actualizar contraseña
        user_crud.update_password(db, db_obj=user, new_password=new_password)

        # Enviar email de confirmación
        email_service.send_password_changed_email(
            email=user.email,
            user_name=user.name
        )

    @staticmethod
    def deactivate_account(db: Session, user: User) -> None:
        """
        Desactiva la cuenta del usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario a desactivar
        """
        user_crud.deactivate(db, db_obj=user)

    @staticmethod
    def delete_account(db: Session, user: User, password: str) -> None:
        """
        Elimina permanentemente la cuenta del usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario a eliminar
            password: Contraseña para confirmar

        Raises:
            HTTPException 400: Si la contraseña es incorrecta
        """
        from app.core.security import verify_password

        # Verificar contraseña
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña incorrecta"
            )

        # Eliminar usuario
        user_crud.delete(db, user_id=user.id)


# Instancia única del servicio
user_service = UserService()
