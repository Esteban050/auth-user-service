"""
Fixtures y configuración compartida para todas las pruebas.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.core.security import get_password_hash


# Database de prueba en memoria (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Crea una base de datos de prueba limpia para cada test.
    """
    # Crear tablas
    Base.metadata.create_all(bind=engine)

    # Crear sesión
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Limpiar tablas después de cada test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Crea un cliente de prueba con la base de datos de prueba.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """
    Datos de usuario válidos para pruebas.
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test123!Pass",
        "role": UserRole.USUARIO
    }


@pytest.fixture
def test_admin_data() -> dict:
    """
    Datos de administrador válidos para pruebas.
    """
    return {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin123!Pass",
        "role": UserRole.ADMIN_PARQUEADERO
    }


@pytest.fixture
def created_user(db: Session, test_user_data: dict) -> User:
    """
    Crea un usuario en la base de datos para pruebas.
    Usuario NO verificado por defecto.
    """
    user = User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        password=get_password_hash(test_user_data["password"]),
        role=test_user_data["role"],
        is_verified=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def verified_user(db: Session, test_user_data: dict) -> User:
    """
    Crea un usuario verificado en la base de datos para pruebas.
    """
    user = User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        password=get_password_hash(test_user_data["password"]),
        role=test_user_data["role"],
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def inactive_user(db: Session, test_user_data: dict) -> User:
    """
    Crea un usuario inactivo en la base de datos para pruebas.
    """
    user = User(
        name="Inactive User",
        email="inactive@example.com",
        password=get_password_hash(test_user_data["password"]),
        role=test_user_data["role"],
        is_verified=True,
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session, test_admin_data: dict) -> User:
    """
    Crea un usuario administrador verificado para pruebas.
    """
    user = User(
        name=test_admin_data["name"],
        email=test_admin_data["email"],
        password=get_password_hash(test_admin_data["password"]),
        role=test_admin_data["role"],
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def access_token_headers(verified_user: User) -> dict:
    """
    Headers con access token válido para pruebas de endpoints protegidos.
    """
    from app.core.security import create_access_token

    token = create_access_token(subject=str(verified_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def refresh_token_headers(verified_user: User) -> dict:
    """
    Headers con refresh token válido para pruebas.
    """
    from app.core.security import create_refresh_token

    token = create_refresh_token(subject=str(verified_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_rabbitmq(monkeypatch):
    """
    Mock automático de RabbitMQ para todas las pruebas.
    Evita que se intente conectar a RabbitMQ durante las pruebas.
    """
    def mock_publish(*args, **kwargs):
        # No hacer nada, simular publicación exitosa
        pass

    from app.services import message_service

    monkeypatch.setattr(
        message_service.message_service,
        "publish_verification_email",
        mock_publish
    )
    monkeypatch.setattr(
        message_service.message_service,
        "publish_welcome_email",
        mock_publish
    )
    monkeypatch.setattr(
        message_service.message_service,
        "publish_password_reset_email",
        mock_publish
    )
    monkeypatch.setattr(
        message_service.message_service,
        "publish_password_changed_email",
        mock_publish
    )
