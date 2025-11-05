from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    generate_verification_token,
    generate_reset_token,
    generate_secure_random_string,
    get_token_subject,
    is_token_expired,
)

# Lazy import to avoid circular dependency
def _get_dependencies():
    from app.core.dependencies import (
        get_current_user,
        get_current_active_user,
        get_current_verified_user,
        get_current_admin_user,
        get_current_user_optional,
        validate_refresh_token,
    )
    return {
        "get_current_user": get_current_user,
        "get_current_active_user": get_current_active_user,
        "get_current_verified_user": get_current_verified_user,
        "get_current_admin_user": get_current_admin_user,
        "get_current_user_optional": get_current_user_optional,
        "validate_refresh_token": validate_refresh_token,
    }

_deps = None

def __getattr__(name):
    global _deps
    if _deps is None:
        _deps = _get_dependencies()
    if name in _deps:
        return _deps[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Config
    "settings",
    # Security
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token_type",
    "generate_verification_token",
    "generate_reset_token",
    "generate_secure_random_string",
    "get_token_subject",
    "is_token_expired",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_admin_user",
    "get_current_user_optional",
    "validate_refresh_token",
]
