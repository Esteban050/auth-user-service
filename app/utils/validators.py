import re
from typing import Optional


def validate_email_format(email: str) -> bool:
    """
    Valida el formato de un email usando regex.

    Args:
        email: Email a validar

    Returns:
        True si el formato es válido, False en caso contrario
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida la fortaleza de una contraseña.

    Args:
        password: Contraseña a validar

    Returns:
        Tupla (is_valid, error_message)
        - is_valid: True si la contraseña cumple los requisitos
        - error_message: Mensaje de error si no es válida, None si es válida
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if len(password) > 100:
        return False, "La contraseña no puede tener más de 100 caracteres"

    if not any(char.isupper() for char in password):
        return False, "La contraseña debe contener al menos una letra mayúscula"

    if not any(char.islower() for char in password):
        return False, "La contraseña debe contener al menos una letra minúscula"

    if not any(char.isdigit() for char in password):
        return False, "La contraseña debe contener al menos un número"

    # Opcional: validar caracteres especiales
    # special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # if not any(char in special_chars for char in password):
    #     return False, "La contraseña debe contener al menos un carácter especial"

    return True, None


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Valida que un nombre sea válido.

    Args:
        name: Nombre a validar

    Returns:
        Tupla (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "El nombre no puede estar vacío"

    if len(name.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"

    if len(name.strip()) > 255:
        return False, "El nombre no puede tener más de 255 caracteres"

    return True, None


def sanitize_string(text: str) -> str:
    """
    Sanitiza una cadena de texto removiendo espacios extras y caracteres no deseados.

    Args:
        text: Texto a sanitizar

    Returns:
        Texto sanitizado
    """
    # Remover espacios extras
    text = " ".join(text.split())
    # Remover caracteres de control
    text = "".join(char for char in text if ord(char) >= 32 or char == '\n')
    return text.strip()


def is_safe_url(url: str, allowed_hosts: Optional[list[str]] = None) -> bool:
    """
    Valida que una URL sea segura y pertenezca a hosts permitidos.

    Args:
        url: URL a validar
        allowed_hosts: Lista de hosts permitidos (opcional)

    Returns:
        True si la URL es segura, False en caso contrario
    """
    if not url:
        return False

    # Verificar que no contenga javascript:
    if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        return False

    # Si hay hosts permitidos, verificar
    if allowed_hosts:
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts or any(
                parsed.netloc.endswith(f".{host}") for host in allowed_hosts
            )
        except Exception:
            return False

    return True


def validate_uuid_format(uuid_string: str) -> bool:
    """
    Valida que una cadena tenga formato UUID válido.

    Args:
        uuid_string: Cadena a validar

    Returns:
        True si es un UUID válido, False en caso contrario
    """
    uuid_regex = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(uuid_regex, uuid_string.lower()) is not None
