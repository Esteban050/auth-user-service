"""
Pruebas unitarias para AuthService (app/services/auth_service.py)
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.models.user import User, UserRole
from app.crud import user as user_crud
from app.core.security import verify_password


class TestAuthService:
    """Test suite para AuthService"""

    def test_register_user_success(self, db: Session):
        """Prueba registro exitoso de usuario"""
        service = AuthService()

        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            password="Test123!Pass",
            role=UserRole.USUARIO
        )

        user = service.register_user(db, user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_verified is False
        assert user.is_active is True
        assert verify_password("Test123!Pass", user.password)

    def test_register_user_duplicate_email(self, db: Session, created_user: User):
        """Prueba registro con email duplicado"""
        service = AuthService()

        user_data = UserCreate(
            name="Another User",
            email=created_user.email,  # Email ya existe
            password="Test123!Pass",
            role=UserRole.USUARIO
        )

        with pytest.raises(HTTPException) as exc:
            service.register_user(db, user_data)

        assert exc.value.status_code == 400
        assert "ya está registrado" in exc.value.detail

    def test_login_success(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba login exitoso"""
        service = AuthService()

        access_token, refresh_token, user = service.login(
            db,
            email=test_user_data["email"],
            password=test_user_data["password"]
        )

        assert access_token is not None
        assert refresh_token is not None
        assert user.id == verified_user.id

    def test_login_wrong_password(self, db: Session, verified_user: User):
        """Prueba login con contraseña incorrecta"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.login(db, email=verified_user.email, password="WrongPassword123!")

        assert exc.value.status_code == 401
        assert "incorrectos" in exc.value.detail

    def test_login_wrong_email(self, db: Session):
        """Prueba login con email inexistente"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.login(db, email="noexiste@example.com", password="Test123!Pass")

        assert exc.value.status_code == 401
        assert "incorrectos" in exc.value.detail

    def test_login_unverified_user(self, db: Session, created_user: User, test_user_data: dict):
        """Prueba login con usuario no verificado"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.login(
                db,
                email=created_user.email,
                password=test_user_data["password"]
            )

        assert exc.value.status_code == 403
        assert "no verificado" in exc.value.detail

    def test_login_inactive_user(self, db: Session, inactive_user: User, test_user_data: dict):
        """Prueba login con usuario inactivo"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.login(
                db,
                email=inactive_user.email,
                password=test_user_data["password"]
            )

        assert exc.value.status_code == 403
        assert "inactivo" in exc.value.detail

    def test_refresh_access_token_success(self, db: Session, verified_user: User):
        """Prueba refresh token exitoso"""
        service = AuthService()

        new_access_token = service.refresh_access_token(verified_user)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)

    def test_refresh_access_token_inactive_user(self, db: Session, inactive_user: User):
        """Prueba refresh token con usuario inactivo"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.refresh_access_token(inactive_user)

        assert exc.value.status_code == 403
        assert "inactivo" in exc.value.detail

    def test_verify_email_success(self, db: Session, created_user: User):
        """Prueba verificación de email exitosa"""
        service = AuthService()

        # Establecer token de verificación
        from app.services.token_service import token_service
        token = token_service.create_verification_token(db, created_user)

        # Verificar email
        user = service.verify_email(db, token)

        assert user.id == created_user.id
        assert user.is_verified is True
        assert user.verification_token is None

    def test_verify_email_invalid_token(self, db: Session):
        """Prueba verificación con token inválido"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.verify_email(db, "invalid_token_123")

        assert exc.value.status_code == 400

    def test_verify_email_already_verified(self, db: Session, verified_user: User):
        """Prueba verificación de email ya verificado"""
        service = AuthService()

        # Crear token para usuario ya verificado
        from app.services.token_service import token_service
        token = token_service.create_verification_token(db, verified_user)

        with pytest.raises(HTTPException) as exc:
            service.verify_email(db, token)

        assert exc.value.status_code == 400
        assert "ya ha sido verificado" in exc.value.detail

    def test_resend_verification_email_success(self, db: Session, created_user: User):
        """Prueba reenvío de email de verificación"""
        service = AuthService()

        # No debe lanzar excepción
        service.resend_verification_email(db, created_user.email)

        # Verificar que se regeneró el token
        db.refresh(created_user)
        assert created_user.verification_token is not None

    def test_resend_verification_email_not_found(self, db: Session):
        """Prueba reenvío de verificación con email inexistente"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.resend_verification_email(db, "noexiste@example.com")

        assert exc.value.status_code == 404
        assert "no encontrado" in exc.value.detail

    def test_resend_verification_email_already_verified(self, db: Session, verified_user: User):
        """Prueba reenvío de verificación a usuario ya verificado"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.resend_verification_email(db, verified_user.email)

        assert exc.value.status_code == 400
        assert "ya ha sido verificado" in exc.value.detail

    def test_request_password_reset_success(self, db: Session, verified_user: User):
        """Prueba solicitud de reset de contraseña exitosa"""
        service = AuthService()

        # No debe lanzar excepción
        service.request_password_reset(db, verified_user.email)

        # Verificar que se generó el token
        db.refresh(verified_user)
        assert verified_user.reset_token is not None

    def test_request_password_reset_nonexistent_email(self, db: Session):
        """Prueba solicitud de reset con email inexistente (no revela info)"""
        service = AuthService()

        # No debe lanzar excepción por seguridad
        service.request_password_reset(db, "noexiste@example.com")

    def test_reset_password_success(self, db: Session, verified_user: User):
        """Prueba reset de contraseña exitoso"""
        service = AuthService()

        # Crear token de reset
        from app.services.token_service import token_service
        token = token_service.create_reset_token(db, verified_user)

        new_password = "NewPassword123!"

        # Resetear contraseña
        service.reset_password(db, token, new_password)

        # Verificar que la contraseña cambió
        db.refresh(verified_user)
        assert verify_password(new_password, verified_user.password)
        assert verified_user.reset_token is None

    def test_reset_password_invalid_token(self, db: Session):
        """Prueba reset de contraseña con token inválido"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc:
            service.reset_password(db, "invalid_token_123", "NewPassword123!")

        assert exc.value.status_code == 400

    def test_reset_password_expired_token(self, db: Session, verified_user: User):
        """Prueba reset de contraseña con token expirado"""
        service = AuthService()
        from datetime import datetime, timedelta

        # Crear token que ya expiró
        verified_user.reset_token = "expired_token"
        verified_user.reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.commit()

        with pytest.raises(HTTPException) as exc:
            service.reset_password(db, "expired_token", "NewPassword123!")

        assert exc.value.status_code == 400


class TestAuthServiceTokenGeneration:
    """Tests específicos para generación de tokens"""

    def test_register_generates_verification_token(self, db: Session):
        """Prueba que el registro genera token de verificación"""
        service = AuthService()

        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            password="Test123!Pass",
            role=UserRole.USUARIO
        )

        user = service.register_user(db, user_data)

        # Verificar que se generó el token
        assert user.verification_token is not None
        assert user.verification_token_expires is not None

    def test_resend_verification_regenerates_token(self, db: Session, created_user: User):
        """Prueba que reenviar verificación regenera el token"""
        service = AuthService()

        # Token inicial
        old_token = created_user.verification_token

        # Reenviar verificación
        service.resend_verification_email(db, created_user.email)

        # Verificar que el token cambió
        db.refresh(created_user)
        assert created_user.verification_token != old_token
        assert created_user.verification_token is not None

    def test_request_password_reset_generates_token(self, db: Session, verified_user: User):
        """Prueba que solicitar reset genera token"""
        service = AuthService()

        # Inicialmente no tiene token
        assert verified_user.reset_token is None

        # Solicitar reset
        service.request_password_reset(db, verified_user.email)

        # Verificar que se generó el token
        db.refresh(verified_user)
        assert verified_user.reset_token is not None
        assert verified_user.reset_token_expires is not None


class TestAuthServiceEdgeCases:
    """Tests de casos extremos y edge cases"""

    def test_verify_email_clears_token_after_verification(self, db: Session, created_user: User):
        """Prueba que verificar email limpia el token"""
        service = AuthService()
        from app.services.token_service import token_service

        token = token_service.create_verification_token(db, created_user)

        # Verificar
        service.verify_email(db, token)

        # El token debe haberse limpiado
        db.refresh(created_user)
        assert created_user.verification_token is None
        assert created_user.verification_token_expires is None

    def test_reset_password_clears_token_after_reset(self, db: Session, verified_user: User):
        """Prueba que reset de contraseña limpia el token"""
        service = AuthService()
        from app.services.token_service import token_service

        token = token_service.create_reset_token(db, verified_user)

        # Resetear
        service.reset_password(db, token, "NewPassword123!")

        # El token debe haberse limpiado
        db.refresh(verified_user)
        assert verified_user.reset_token is None
        assert verified_user.reset_token_expires is None

    def test_multiple_password_reset_requests_update_token(self, db: Session, verified_user: User):
        """Prueba que múltiples solicitudes de reset actualizan el token"""
        service = AuthService()

        # Primera solicitud
        service.request_password_reset(db, verified_user.email)
        db.refresh(verified_user)
        first_token = verified_user.reset_token

        # Segunda solicitud
        service.request_password_reset(db, verified_user.email)
        db.refresh(verified_user)
        second_token = verified_user.reset_token

        # Los tokens deben ser diferentes
        assert first_token != second_token
