from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.password import ChangePasswordRequest, ChangePasswordResponse
from app.models.user import User
from app.core.dependencies import get_current_verified_user
from app.services.user_service import user_service


router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil actual",
    description="Retorna el perfil del usuario autenticado"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Obtiene el perfil del usuario actual.

    Requiere:
    - Token de acceso válido
    - Email verificado

    Retorna toda la información del perfil del usuario.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil",
    description="Actualiza los datos del perfil del usuario"
)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Actualiza el perfil del usuario.

    Campos actualizables:
    - **name**: Nombre del usuario
    - **email**: Email del usuario (requerirá nueva verificación)

    Requiere:
    - Token de acceso válido
    - Email verificado

    Si se cambia el email, el usuario deberá verificarlo nuevamente.
    """
    updated_user = user_service.update_user_profile(
        db,
        current_user,
        user_update
    )

    return UserResponse.model_validate(updated_user)


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Cambia la contraseña del usuario.

    - **current_password**: Contraseña actual (para verificación)
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)

    Requiere:
    - Token de acceso válido
    - Email verificado
    - Contraseña actual correcta

    Envía un email de confirmación del cambio.
    """
    user_service.change_password(
        db,
        current_user,
        password_data.current_password,
        password_data.new_password
    )

    return ChangePasswordResponse(
        message="Contraseña cambiada exitosamente"
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar cuenta",
    description="Desactiva la cuenta del usuario (soft delete)"
)
def deactivate_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Desactiva la cuenta del usuario.

    Requiere:
    - Token de acceso válido
    - Email verificado

    La cuenta se desactiva pero no se elimina.
    Contacta con soporte para reactivarla.
    """
    user_service.deactivate_account(db, current_user)
    return None
