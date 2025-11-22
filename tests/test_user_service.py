"""
Pruebas unitarias para UserService (app/services/user_service.py)
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.schemas.user import UserUpdate
from app.models.user import User
from app.core.security import verify_password


class TestUserService:
    """Test suite para UserService"""

    def test_get_user_profile(self, db: Session, verified_user: User):
        """Prueba obtener perfil de usuario"""
        service = UserService()

        profile = service.get_user_profile(verified_user)

        assert profile.id == verified_user.id
        assert profile.email == verified_user.email
        assert profile.name == verified_user.name

    def test_update_user_profile_name(self, db: Session, verified_user: User):
        """Prueba actualizar nombre de usuario"""
        service = UserService()

        update_data = UserUpdate(name="Updated Name")
        updated_user = service.update_user_profile(db, verified_user, update_data)

        assert updated_user.name == "Updated Name"
        assert updated_user.email == verified_user.email  # No cambió

    def test_update_user_profile_email(self, db: Session, verified_user: User):
        """Prueba actualizar email de usuario"""
        service = UserService()
        new_email = "newemail@example.com"

        update_data = UserUpdate(email=new_email)
        updated_user = service.update_user_profile(db, verified_user, update_data)

        assert updated_user.email == new_email
        # Al cambiar email, debe marcar como no verificado
        assert updated_user.is_verified is False

    def test_update_user_profile_duplicate_email(self, db: Session, verified_user: User, admin_user: User):
        """Prueba actualizar a un email que ya existe"""
        service = UserService()

        # Intentar cambiar al email del admin
        update_data = UserUpdate(email=admin_user.email)

        with pytest.raises(HTTPException) as exc:
            service.update_user_profile(db, verified_user, update_data)

        assert exc.value.status_code == 400
        assert "ya está en uso" in exc.value.detail

    def test_update_user_profile_same_email(self, db: Session, verified_user: User):
        """Prueba actualizar con el mismo email (no debe marcar como no verificado)"""
        service = UserService()

        # Actualizar con el mismo email
        update_data = UserUpdate(email=verified_user.email)
        updated_user = service.update_user_profile(db, verified_user, update_data)

        # No debe cambiar el estado de verificación
        assert updated_user.is_verified is True

    def test_update_user_profile_multiple_fields(self, db: Session, verified_user: User):
        """Prueba actualizar múltiples campos"""
        service = UserService()

        update_data = UserUpdate(
            name="New Name",
            email="newemail@example.com"
        )
        updated_user = service.update_user_profile(db, verified_user, update_data)

        assert updated_user.name == "New Name"
        assert updated_user.email == "newemail@example.com"
        assert updated_user.is_verified is False  # Email cambió

    def test_change_password_success(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba cambiar contraseña exitosamente"""
        service = UserService()

        new_password = "NewPassword123!"

        service.change_password(
            db,
            verified_user,
            current_password=test_user_data["password"],
            new_password=new_password
        )

        # Verificar que la contraseña cambió
        db.refresh(verified_user)
        assert verify_password(new_password, verified_user.password)

    def test_change_password_wrong_current_password(self, db: Session, verified_user: User):
        """Prueba cambiar contraseña con contraseña actual incorrecta"""
        service = UserService()

        with pytest.raises(HTTPException) as exc:
            service.change_password(
                db,
                verified_user,
                current_password="WrongPassword123!",
                new_password="NewPassword123!"
            )

        assert exc.value.status_code == 400
        assert "incorrecta" in exc.value.detail

    def test_change_password_same_as_current(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba cambiar a la misma contraseña actual"""
        service = UserService()

        with pytest.raises(HTTPException) as exc:
            service.change_password(
                db,
                verified_user,
                current_password=test_user_data["password"],
                new_password=test_user_data["password"]  # Misma contraseña
            )

        assert exc.value.status_code == 400
        assert "diferente" in exc.value.detail

    def test_deactivate_account(self, db: Session, verified_user: User):
        """Prueba desactivar cuenta de usuario"""
        service = UserService()

        service.deactivate_account(db, verified_user)

        db.refresh(verified_user)
        assert verified_user.is_active is False

    def test_delete_account_success(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba eliminar cuenta exitosamente"""
        service = UserService()
        user_id = verified_user.id

        service.delete_account(db, verified_user, password=test_user_data["password"])

        # Verificar que el usuario fue eliminado
        from app.crud import user as user_crud
        deleted_user = user_crud.get(db, user_id=user_id)
        assert deleted_user is None

    def test_delete_account_wrong_password(self, db: Session, verified_user: User):
        """Prueba eliminar cuenta con contraseña incorrecta"""
        service = UserService()

        with pytest.raises(HTTPException) as exc:
            service.delete_account(db, verified_user, password="WrongPassword123!")

        assert exc.value.status_code == 400
        assert "incorrecta" in exc.value.detail

        # Verificar que el usuario NO fue eliminado
        db.refresh(verified_user)
        assert verified_user is not None


class TestUserServiceEdgeCases:
    """Tests de casos extremos y edge cases"""

    def test_update_profile_empty_data(self, db: Session, verified_user: User):
        """Prueba actualizar perfil sin cambios"""
        service = UserService()

        update_data = UserUpdate()  # Sin datos
        updated_user = service.update_user_profile(db, verified_user, update_data)

        # No debe cambiar nada
        assert updated_user.name == verified_user.name
        assert updated_user.email == verified_user.email
        assert updated_user.is_verified == verified_user.is_verified

    def test_change_password_updates_hash(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba que cambiar contraseña actualiza el hash"""
        service = UserService()

        old_hash = verified_user.password
        new_password = "NewPassword123!"

        service.change_password(
            db,
            verified_user,
            current_password=test_user_data["password"],
            new_password=new_password
        )

        db.refresh(verified_user)
        # El hash debe ser diferente
        assert verified_user.password != old_hash
        # Pero la nueva contraseña debe ser válida
        assert verify_password(new_password, verified_user.password)

    def test_deactivate_already_inactive_user(self, db: Session, inactive_user: User):
        """Prueba desactivar usuario que ya está inactivo"""
        service = UserService()

        # No debe lanzar error
        service.deactivate_account(db, inactive_user)

        db.refresh(inactive_user)
        assert inactive_user.is_active is False

    def test_update_email_case_sensitivity(self, db: Session, verified_user: User):
        """Prueba actualización de email con diferente capitalización"""
        service = UserService()

        # Email con capitalización diferente pero mismo dominio
        new_email = verified_user.email.upper()

        update_data = UserUpdate(email=new_email)
        updated_user = service.update_user_profile(db, verified_user, update_data)

        # Verificar que el email se actualizó (puede normalizarse a lowercase)
        assert updated_user.email.lower() == verified_user.email.lower()
        # Como el email cambió (aunque sea capitalización), debe marcar como no verificado
        assert updated_user.is_verified is False


class TestUserServiceIntegration:
    """Tests de integración entre métodos del servicio"""

    def test_update_email_then_verify(self, db: Session, verified_user: User):
        """Prueba actualizar email y luego necesitar reverificar"""
        service = UserService()

        # Usuario verificado cambia su email
        update_data = UserUpdate(email="newemail@example.com")
        updated_user = service.update_user_profile(db, verified_user, update_data)

        # Debe estar marcado como no verificado
        assert updated_user.is_verified is False

        # Simular que verificó el nuevo email
        from app.crud import user as user_crud
        user_crud.verify_email(db, db_obj=updated_user)

        db.refresh(updated_user)
        assert updated_user.is_verified is True

    def test_change_password_multiple_times(self, db: Session, verified_user: User, test_user_data: dict):
        """Prueba cambiar contraseña múltiples veces"""
        service = UserService()

        # Primera cambio
        first_new_password = "NewPassword123!"
        service.change_password(
            db,
            verified_user,
            current_password=test_user_data["password"],
            new_password=first_new_password
        )

        db.refresh(verified_user)

        # Segundo cambio
        second_new_password = "AnotherPassword456!"
        service.change_password(
            db,
            verified_user,
            current_password=first_new_password,
            new_password=second_new_password
        )

        db.refresh(verified_user)
        assert verify_password(second_new_password, verified_user.password)

    def test_deactivate_then_try_to_update(self, db: Session, verified_user: User):
        """Prueba desactivar cuenta y luego intentar actualizar perfil"""
        service = UserService()

        # Desactivar
        service.deactivate_account(db, verified_user)

        db.refresh(verified_user)

        # Intentar actualizar (debería funcionar, solo está inactivo)
        update_data = UserUpdate(name="New Name")
        updated_user = service.update_user_profile(db, verified_user, update_data)

        assert updated_user.name == "New Name"
        assert updated_user.is_active is False  # Sigue inactivo
