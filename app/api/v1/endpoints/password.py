from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.password import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ValidateResetTokenRequest,
    ValidateResetTokenResponse,
)
from app.services.auth_service import auth_service
from app.services.token_service import token_service


router = APIRouter()


@router.post(
    "/forgot",
    response_model=ForgotPasswordResponse,
    summary="Solicitar recuperación de contraseña",
    description="Envía un email con instrucciones para recuperar la contraseña"
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita recuperación de contraseña.

    - **email**: Email del usuario que olvidó su contraseña

    Genera un token temporal y envía un email con instrucciones.
    El token expira en 1 hora.

    Nota: Por seguridad, siempre retorna éxito aunque el email no exista.
    """
    auth_service.request_password_reset(db, request.email)

    return ForgotPasswordResponse(
        message="Si el email existe, recibirás instrucciones para recuperar tu contraseña."
    )


@router.post(
    "/reset",
    response_model=ResetPasswordResponse,
    summary="Restablecer contraseña",
    description="Restablece la contraseña usando el token recibido por email"
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Restablece la contraseña del usuario.

    - **token**: Token de reset recibido por email
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)

    Valida el token, actualiza la contraseña y envía email de confirmación.
    """
    auth_service.reset_password(db, request.token, request.new_password)

    return ResetPasswordResponse(
        message="Contraseña restablecida exitosamente. Ya puedes iniciar sesión."
    )


@router.post(
    "/validate-token",
    response_model=ValidateResetTokenResponse,
    summary="Validar token de reset",
    description="Verifica si un token de reset es válido"
)
def validate_reset_token(
    request: ValidateResetTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Valida un token de reset de contraseña.

    - **token**: Token a validar

    Retorna si el token es válido o ha expirado.
    Útil para validar en el frontend antes de mostrar el formulario.
    """
    success, message, _ = token_service.verify_reset_token(db, request.token)

    return ValidateResetTokenResponse(
        valid=success,
        message=message
    )
