from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from app.core.config import settings


# Configuración de bcrypt para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




def get_password_hash(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña coincida con su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en la base de datos

    Returns:
        True si coinciden, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)




def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        subject: Subject del token (generalmente user_id)
        expires_delta: Tiempo de expiración personalizado (opcional)

    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de refresh.

    Args:
        subject: Subject del token (generalmente user_id)
        expires_delta: Tiempo de expiración personalizado (opcional)

    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica y valida un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Payload del token si es válido, None en caso contrario
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except PyJWTError:
        return None


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verifica que el tipo de token sea el esperado.

    Args:
        payload: Payload decodificado del token
        expected_type: Tipo esperado ("access" o "refresh")

    Returns:
        True si el tipo coincide, False en caso contrario
    """
    token_type = payload.get("type")
    return token_type == expected_type




def generate_verification_token() -> str:
    """
    Genera un token seguro para verificación de email.
    Usa secrets para generación criptográficamente segura.

    Returns:
        Token aleatorio de 32 caracteres hexadecimales
    """
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """
    Genera un token seguro para reset de contraseña.
    Usa secrets para generación criptográficamente segura.

    Returns:
        Token aleatorio de 32 caracteres hexadecimales
    """
    return secrets.token_urlsafe(32)


def generate_secure_random_string(length: int = 32) -> str:
    """
    Genera una cadena aleatoria segura de longitud específica.

    Args:
        length: Longitud deseada del token

    Returns:
        Cadena aleatoria segura
    """
    return secrets.token_urlsafe(length)




def get_token_subject(token: str) -> Optional[str]:
    """
    Extrae el subject (user_id) de un token JWT.

    Args:
        token: Token JWT

    Returns:
        User ID si el token es válido, None en caso contrario
    """
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


def is_token_expired(token: str) -> bool:
    """
    Verifica si un token JWT ha expirado.

    Args:
        token: Token JWT

    Returns:
        True si expiró o es inválido, False si aún es válido
    """
    payload = decode_token(token)
    if not payload:
        return True

    exp = payload.get("exp")
    if not exp:
        return True

    return datetime.fromtimestamp(exp) < datetime.utcnow()
