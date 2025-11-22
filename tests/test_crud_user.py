"""
Pruebas unitarias para CRUD de usuarios (app/crud/user.py)
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.crud.user import CRUDUser
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password


class TestCRUDUser:
    """Test suite para CRUD de usuarios"""

    def test_create_user(self, db: Session, test_user_data: dict):
        """Prueba crear un nuevo usuario"""
        crud = CRUDUser()
        user_in = UserCreate(**test_user_data)

        user = crud.create(db, obj_in=user_in)

        assert user.id is not None
        assert user.email == test_user_data["email"]
        assert user.name == test_user_data["name"]
        assert user.role == test_user_data["role"]
        assert user.is_verified is False  # Por defecto no verificado
        assert user.is_active is True  # Por defecto activo
        assert verify_password(test_user_data["password"], user.password)

    def test_get_user_by_id(self, db: Session, created_user: User):
        """Prueba obtener usuario por ID"""
        crud = CRUDUser()

        user = crud.get(db, user_id=created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_id_not_found(self, db: Session):
        """Prueba obtener usuario por ID inexistente"""
        crud = CRUDUser()
        from uuid import uuid4

        user = crud.get(db, user_id=uuid4())

        assert user is None

    def test_get_user_by_email(self, db: Session, created_user: User):
        """Prueba obtener usuario por email"""
        crud = CRUDUser()

        user = crud.get_by_email(db, email=created_user.email)

        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_email_not_found(self, db: Session):
        """Prueba obtener usuario por email inexistente"""
        crud = CRUDUser()

        user = crud.get_by_email(db, email="noexiste@example.com")

        assert user is None

    def test_get_multi_users(self, db: Session):
        """Prueba obtener múltiples usuarios"""
        crud = CRUDUser()

        # Crear varios usuarios
        for i in range(5):
            user_in = UserCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="Test123!Pass",
                role=UserRole.USUARIO
            )
            crud.create(db, obj_in=user_in)

        users = crud.get_multi(db, skip=0, limit=10)

        assert len(users) == 5

    def test_get_multi_users_with_pagination(self, db: Session):
        """Prueba paginación de usuarios"""
        crud = CRUDUser()

        # Crear varios usuarios
        for i in range(10):
            user_in = UserCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="Test123!Pass",
                role=UserRole.USUARIO
            )
            crud.create(db, obj_in=user_in)

        # Primera página
        users_page1 = crud.get_multi(db, skip=0, limit=5)
        assert len(users_page1) == 5

        # Segunda página
        users_page2 = crud.get_multi(db, skip=5, limit=5)
        assert len(users_page2) == 5

        # Verificar que son diferentes
        assert users_page1[0].id != users_page2[0].id

    def test_get_multi_users_filter_by_role(self, db: Session):
        """Prueba filtrar usuarios por rol"""
        crud = CRUDUser()

        # Crear usuarios con diferentes roles
        for i in range(3):
            user_in = UserCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="Test123!Pass",
                role=UserRole.USUARIO
            )
            crud.create(db, obj_in=user_in)

        for i in range(2):
            admin_in = UserCreate(
                name=f"Admin {i}",
                email=f"admin{i}@example.com",
                password="Test123!Pass",
                role=UserRole.ADMIN_PARQUEADERO
            )
            crud.create(db, obj_in=admin_in)

        # Filtrar por rol de usuario
        users = crud.get_multi(db, role=UserRole.USUARIO)
        assert len(users) == 3
        assert all(u.role == UserRole.USUARIO for u in users)

        # Filtrar por rol de admin
        admins = crud.get_multi(db, role=UserRole.ADMIN_PARQUEADERO)
        assert len(admins) == 2
        assert all(u.role == UserRole.ADMIN_PARQUEADERO for u in admins)

    def test_get_multi_users_filter_by_verified(self, db: Session):
        """Prueba filtrar usuarios por verificación"""
        crud = CRUDUser()

        # Crear usuarios verificados y no verificados
        for i in range(3):
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="hashed_password",
                role=UserRole.USUARIO,
                is_verified=i % 2 == 0,  # Alternar verificado/no verificado
                is_active=True
            )
            db.add(user)
        db.commit()

        # Filtrar verificados
        verified = crud.get_multi(db, is_verified=True)
        assert len(verified) == 2
        assert all(u.is_verified for u in verified)

        # Filtrar no verificados
        not_verified = crud.get_multi(db, is_verified=False)
        assert len(not_verified) == 1
        assert all(not u.is_verified for u in not_verified)

    def test_update_user(self, db: Session, created_user: User):
        """Prueba actualizar datos de usuario"""
        crud = CRUDUser()

        update_data = UserUpdate(name="Updated Name")
        updated_user = crud.update(db, db_obj=created_user, obj_in=update_data)

        assert updated_user.name == "Updated Name"
        assert updated_user.email == created_user.email  # No cambió

    def test_update_password(self, db: Session, created_user: User):
        """Prueba actualizar contraseña de usuario"""
        crud = CRUDUser()
        new_password = "NewPassword123!"

        updated_user = crud.update_password(
            db,
            db_obj=created_user,
            new_password=new_password
        )

        assert verify_password(new_password, updated_user.password)

    def test_authenticate_user_success(self, db: Session, created_user: User, test_user_data: dict):
        """Prueba autenticación exitosa"""
        crud = CRUDUser()

        user = crud.authenticate(
            db,
            email=test_user_data["email"],
            password=test_user_data["password"]
        )

        assert user is not None
        assert user.id == created_user.id

    def test_authenticate_user_wrong_password(self, db: Session, created_user: User):
        """Prueba autenticación con contraseña incorrecta"""
        crud = CRUDUser()

        user = crud.authenticate(
            db,
            email=created_user.email,
            password="WrongPassword123!"
        )

        assert user is None

    def test_authenticate_user_wrong_email(self, db: Session):
        """Prueba autenticación con email inexistente"""
        crud = CRUDUser()

        user = crud.authenticate(
            db,
            email="noexiste@example.com",
            password="Test123!Pass"
        )

        assert user is None

    def test_is_active(self, db: Session):
        """Prueba verificación de usuario activo"""
        crud = CRUDUser()
        from app.core.security import get_password_hash

        # Crear usuarios directamente para evitar conflictos de email
        active_user = User(
            name="Active User",
            email="active@test.com",
            password=get_password_hash("pass"),
            role=UserRole.USUARIO,
            is_active=True,
            is_verified=True
        )
        inactive_user = User(
            name="Inactive User",
            email="inactive@test.com",
            password=get_password_hash("pass"),
            role=UserRole.USUARIO,
            is_active=False,
            is_verified=True
        )
        db.add(active_user)
        db.add(inactive_user)
        db.commit()

        assert crud.is_active(active_user) is True
        assert crud.is_active(inactive_user) is False

    def test_is_verified(self, db: Session):
        """Prueba verificación de email"""
        crud = CRUDUser()
        from app.core.security import get_password_hash

        # Crear usuarios directamente para evitar conflictos de email
        verified = User(
            name="Verified User",
            email="verified@test.com",
            password=get_password_hash("pass"),
            role=UserRole.USUARIO,
            is_active=True,
            is_verified=True
        )
        unverified = User(
            name="Unverified User",
            email="unverified@test.com",
            password=get_password_hash("pass"),
            role=UserRole.USUARIO,
            is_active=True,
            is_verified=False
        )
        db.add(verified)
        db.add(unverified)
        db.commit()

        assert crud.is_verified(verified) is True
        assert crud.is_verified(unverified) is False

    def test_set_verification_token(self, db: Session, created_user: User):
        """Prueba establecer token de verificación"""
        crud = CRUDUser()
        token = "test_verification_token_123"

        user = crud.set_verification_token(
            db,
            db_obj=created_user,
            token=token,
            expires_hours=24
        )

        assert user.verification_token == token
        assert user.verification_token_expires is not None
        # Verificar que expira en ~24 horas (con margen de 1 minuto)
        expected_expiry = datetime.utcnow() + timedelta(hours=24)
        assert abs((user.verification_token_expires - expected_expiry).total_seconds()) < 60

    def test_get_by_verification_token_valid(self, db: Session, created_user: User):
        """Prueba obtener usuario por token de verificación válido"""
        crud = CRUDUser()
        token = "valid_token_123"

        # Establecer token
        crud.set_verification_token(db, db_obj=created_user, token=token)

        # Obtener por token
        user = crud.get_by_verification_token(db, token=token)

        assert user is not None
        assert user.id == created_user.id

    def test_get_by_verification_token_expired(self, db: Session, created_user: User):
        """Prueba obtener usuario por token de verificación expirado"""
        crud = CRUDUser()
        token = "expired_token_123"

        # Establecer token que ya expiró
        created_user.verification_token = token
        created_user.verification_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.commit()

        # Intentar obtener por token expirado
        user = crud.get_by_verification_token(db, token=token)

        assert user is None

    def test_verify_email(self, db: Session, created_user: User):
        """Prueba verificar email de usuario"""
        crud = CRUDUser()

        # Establecer token primero
        crud.set_verification_token(db, db_obj=created_user, token="token_123")

        # Verificar email
        user = crud.verify_email(db, db_obj=created_user)

        assert user.is_verified is True
        assert user.verification_token is None
        assert user.verification_token_expires is None

    def test_set_reset_token(self, db: Session, created_user: User):
        """Prueba establecer token de reset de contraseña"""
        crud = CRUDUser()
        token = "reset_token_123"

        user = crud.set_reset_token(
            db,
            db_obj=created_user,
            token=token,
            expires_hours=1
        )

        assert user.reset_token == token
        assert user.reset_token_expires is not None
        # Verificar que expira en ~1 hora
        expected_expiry = datetime.utcnow() + timedelta(hours=1)
        assert abs((user.reset_token_expires - expected_expiry).total_seconds()) < 60

    def test_get_by_reset_token_valid(self, db: Session, created_user: User):
        """Prueba obtener usuario por token de reset válido"""
        crud = CRUDUser()
        token = "valid_reset_token_123"

        # Establecer token
        crud.set_reset_token(db, db_obj=created_user, token=token)

        # Obtener por token
        user = crud.get_by_reset_token(db, token=token)

        assert user is not None
        assert user.id == created_user.id

    def test_get_by_reset_token_expired(self, db: Session, created_user: User):
        """Prueba obtener usuario por token de reset expirado"""
        crud = CRUDUser()
        token = "expired_reset_token_123"

        # Establecer token que ya expiró
        created_user.reset_token = token
        created_user.reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.commit()

        # Intentar obtener por token expirado
        user = crud.get_by_reset_token(db, token=token)

        assert user is None

    def test_clear_reset_token(self, db: Session, created_user: User):
        """Prueba limpiar token de reset"""
        crud = CRUDUser()

        # Establecer token primero
        crud.set_reset_token(db, db_obj=created_user, token="token_123")

        # Limpiar token
        user = crud.clear_reset_token(db, db_obj=created_user)

        assert user.reset_token is None
        assert user.reset_token_expires is None

    def test_deactivate_user(self, db: Session, verified_user: User):
        """Prueba desactivar usuario"""
        crud = CRUDUser()

        user = crud.deactivate(db, db_obj=verified_user)

        assert user.is_active is False

    def test_activate_user(self, db: Session, inactive_user: User):
        """Prueba activar usuario"""
        crud = CRUDUser()

        user = crud.activate(db, db_obj=inactive_user)

        assert user.is_active is True

    def test_delete_user(self, db: Session, created_user: User):
        """Prueba eliminar usuario (hard delete)"""
        crud = CRUDUser()
        user_id = created_user.id

        deleted_user = crud.delete(db, user_id=user_id)

        assert deleted_user is not None
        assert deleted_user.id == user_id

        # Verificar que ya no existe
        user = crud.get(db, user_id=user_id)
        assert user is None

    def test_delete_user_not_found(self, db: Session):
        """Prueba eliminar usuario inexistente"""
        crud = CRUDUser()
        from uuid import uuid4

        deleted_user = crud.delete(db, user_id=uuid4())

        assert deleted_user is None
