from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    VerifyEmailResponse,
    LogoutResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
)
from app.schemas.user import UserResponse
from app.models.user import User
from app.services.auth_service import auth_service
from app.core.dependencies import validate_refresh_token


router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario y envía email de verificación"
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema.

    - **name**: Nombre completo del usuario
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)
    - **role**: Rol del usuario (Usuario o Administrador de Parqueadero)

    Retorna el usuario creado y envía un email de verificación.
    """
    user = auth_service.register_user(db, user_data)

    return RegisterResponse(
        message="Usuario registrado exitosamente. Por favor verifica tu email.",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna tokens de acceso"
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión con email y contraseña.

    - **email**: Email del usuario
    - **password**: Contraseña del usuario

    Retorna access token, refresh token y datos del usuario.

    Requiere:
    - Credenciales válidas
    - Email verificado
    - Usuario activo
    """
    access_token, refresh_token, user = auth_service.login(
        db,
        email=credentials.email,
        password=credentials.password
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refrescar access token",
    description="Genera un nuevo access token usando un refresh token válido"
)
def refresh_token(
    user: User = Depends(validate_refresh_token)
):
    """
    Refresca el access token.

    Requiere:
    - Refresh token válido en el header Authorization

    Retorna un nuevo access token.
    """
    access_token = auth_service.refresh_access_token(user)

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/verify-email/{token}",
    response_model=VerifyEmailResponse,
    summary="Verificar email",
    description="Verifica el email del usuario usando el token recibido por correo"
)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verifica el email del usuario.

    - **token**: Token de verificación recibido por email

    Marca el email como verificado y envía email de bienvenida.
    """
    user = auth_service.verify_email(db, token)

    return VerifyEmailResponse(
        message="Email verificado exitosamente. Ya puedes iniciar sesión.",
        email_verified=True
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    summary="Reenviar email de verificación",
    description="Reenvía el email de verificación a un usuario"
)
def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Reenvía el email de verificación.

    - **email**: Email del usuario

    Genera un nuevo token y reenvía el email de verificación.
    """
    auth_service.resend_verification_email(db, request.email)

    return ResendVerificationResponse(
        message="Email de verificación reenviado. Por favor revisa tu bandeja de entrada."
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario (el cliente debe eliminar los tokens)"
)
def logout():
    """
    Cierra la sesión del usuario.

    Nota: Esta es una operación del lado del cliente.
    El cliente debe eliminar los tokens almacenados.

    Para implementar una blacklist de tokens, se requeriría
    almacenar los tokens revocados en Redis o similar.
    """
    return LogoutResponse(
        message="Sesión cerrada exitosamente"
    )
