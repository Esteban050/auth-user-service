from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token, verify_token_type
from app.crud import user as user_crud
from app.models.user import User, UserRole


# Configuración de seguridad HTTP Bearer
security = HTTPBearer()




def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency para obtener el usuario actual autenticado.
    Valida el token JWT y retorna el usuario.

    Args:
        db: Sesión de base de datos
        credentials: Credenciales del token Bearer

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials

    # Decodificar token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que sea un access token
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener user_id del token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener usuario de la base de datos
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para obtener el usuario actual y verificar que esté activo.

    Args:
        current_user: Usuario autenticado

    Returns:
        Usuario activo

    Raises:
        HTTPException 403: Si el usuario está inactivo
    """
    if not user_crud.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency para obtener el usuario actual y verificar que su email esté verificado.

    Args:
        current_user: Usuario activo

    Returns:
        Usuario verificado

    Raises:
        HTTPException 403: Si el email no está verificado
    """
    if not user_crud.is_verified(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email no verificado. Por favor verifica tu correo electrónico."
        )
    return current_user




def get_current_admin_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Dependency para verificar que el usuario actual sea administrador.

    Args:
        current_user: Usuario verificado

    Returns:
        Usuario administrador

    Raises:
        HTTPException 403: Si el usuario no es administrador
    """
    if current_user.role != UserRole.ADMIN_PARQUEADERO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user




def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """
    Dependency para obtener el usuario actual si está autenticado.
    Si no hay token o es inválido, retorna None en lugar de lanzar error.

    Args:
        db: Sesión de base de datos
        credentials: Credenciales del token Bearer (opcional)

    Returns:
        Usuario autenticado o None
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        return None

    if not verify_token_type(payload, "access"):
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    user = user_crud.get(db, user_id=user_id)
    return user




def validate_refresh_token(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency para validar un refresh token y retornar el usuario.

    Args:
        db: Sesión de base de datos
        credentials: Credenciales del token Bearer

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido
    """
    token = credentials.credentials

    # Decodificar token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que sea un refresh token
    if not verify_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token incorrecto. Se esperaba refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener user_id del token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener usuario de la base de datos
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario esté activo
    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user
