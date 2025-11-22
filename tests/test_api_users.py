"""
Pruebas de integración para endpoints de usuarios (app/api/v1/endpoints/users.py)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestGetCurrentUserProfile:
    """Tests para el endpoint GET /me"""

    def test_get_profile_success(self, client: TestClient, verified_user: User, access_token_headers: dict):
        """Prueba obtener perfil con usuario autenticado"""
        response = client.get(
            "/api/v1/users/me",
            headers=access_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == verified_user.email
        assert data["name"] == verified_user.name
        assert data["is_verified"] is True
        assert data["is_active"] is True

    def test_get_profile_without_auth(self, client: TestClient):
        """Prueba obtener perfil sin autenticación"""
        response = client.get("/api/v1/users/me")

        assert response.status_code in [401, 403]  # Puede variar según implementación

    def test_get_profile_invalid_token(self, client: TestClient):
        """Prueba obtener perfil con token inválido"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_get_profile_expired_token(self, client: TestClient, verified_user: User):
        """Prueba obtener perfil con token expirado"""
        from datetime import timedelta
        from app.core.security import create_access_token

        # Crear token que ya expiró
        expired_token = create_access_token(
            subject=str(verified_user.id),
            expires_delta=timedelta(minutes=-10)
        )

        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401


class TestUpdateProfile:
    """Tests para el endpoint PUT /me"""

    def test_update_name_success(self, client: TestClient, verified_user: User, access_token_headers: dict):
        """Prueba actualizar nombre exitosamente"""
        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == verified_user.email
        assert data["is_verified"] is True

    def test_update_email_success(self, client: TestClient, verified_user: User, access_token_headers: dict):
        """Prueba actualizar email exitosamente"""
        new_email = "newemail@example.com"

        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"email": new_email}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == new_email
        # Al cambiar email, debe marcar como no verificado
        assert data["is_verified"] is False

    def test_update_multiple_fields(self, client: TestClient, verified_user: User, access_token_headers: dict):
        """Prueba actualizar múltiples campos"""
        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={
                "name": "New Name",
                "email": "newemail@example.com"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["email"] == "newemail@example.com"
        assert data["is_verified"] is False

    def test_update_duplicate_email(
        self,
        client: TestClient,
        verified_user: User,
        admin_user: User,
        access_token_headers: dict
    ):
        """Prueba actualizar a un email que ya existe"""
        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"email": admin_user.email}
        )

        assert response.status_code == 400
        assert "ya está en uso" in response.json()["detail"]

    def test_update_without_auth(self, client: TestClient):
        """Prueba actualizar perfil sin autenticación"""
        response = client.put(
            "/api/v1/users/me",
            json={"name": "New Name"}
        )

        assert response.status_code in [401, 403]  # Puede variar según implementación

    def test_update_invalid_email_format(self, client: TestClient, access_token_headers: dict):
        """Prueba actualizar con email inválido"""
        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"email": "invalid-email"}
        )

        assert response.status_code == 422  # Validation error

    def test_update_empty_body(self, client: TestClient, verified_user: User, access_token_headers: dict):
        """Prueba actualizar sin cambios"""
        response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        # No debe cambiar nada
        assert data["name"] == verified_user.name
        assert data["email"] == verified_user.email


class TestChangePassword:
    """Tests para el endpoint POST /change-password"""

    def test_change_password_success(
        self,
        client: TestClient,
        verified_user: User,
        test_user_data: dict,
        access_token_headers: dict
    ):
        """Prueba cambiar contraseña exitosamente"""
        response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "exitosamente" in data["message"]

    def test_change_password_wrong_current(
        self,
        client: TestClient,
        access_token_headers: dict
    ):
        """Prueba cambiar contraseña con contraseña actual incorrecta"""
        response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 400
        assert "incorrecta" in response.json()["detail"]

    def test_change_password_same_as_current(
        self,
        client: TestClient,
        test_user_data: dict,
        access_token_headers: dict
    ):
        """Prueba cambiar a la misma contraseña actual"""
        response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": test_user_data["password"]
            }
        )

        assert response.status_code == 400
        assert "diferente" in response.json()["detail"]

    def test_change_password_weak_new_password(
        self,
        client: TestClient,
        test_user_data: dict,
        access_token_headers: dict
    ):
        """Prueba cambiar a una contraseña débil"""
        response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": "weak"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_change_password_without_auth(self, client: TestClient):
        """Prueba cambiar contraseña sin autenticación"""
        response = client.post(
            "/api/v1/users/change-password",
            json={
                "current_password": "Test123!Pass",
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code in [401, 403]  # Puede variar según implementación

    def test_change_password_missing_fields(self, client: TestClient, access_token_headers: dict):
        """Prueba cambiar contraseña con campos faltantes"""
        response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={"current_password": "Test123!Pass"}
        )

        assert response.status_code == 422  # Validation error


class TestDeactivateAccount:
    """Tests para el endpoint DELETE /me"""

    def test_deactivate_account_success(
        self,
        client: TestClient,
        db: Session,
        verified_user: User,
        access_token_headers: dict
    ):
        """Prueba desactivar cuenta exitosamente"""
        response = client.delete(
            "/api/v1/users/me",
            headers=access_token_headers
        )

        assert response.status_code == 204

        # Verificar que el usuario fue desactivado
        db.refresh(verified_user)
        assert verified_user.is_active is False

    def test_deactivate_account_without_auth(self, client: TestClient):
        """Prueba desactivar cuenta sin autenticación"""
        response = client.delete("/api/v1/users/me")

        assert response.status_code in [401, 403]  # Puede variar según implementación

    def test_deactivate_account_cannot_login_after(
        self,
        client: TestClient,
        db: Session,
        verified_user: User,
        test_user_data: dict,
        access_token_headers: dict
    ):
        """Prueba que no se puede hacer login después de desactivar"""
        # Desactivar cuenta
        response = client.delete(
            "/api/v1/users/me",
            headers=access_token_headers
        )
        assert response.status_code == 204

        # Intentar hacer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": verified_user.email,
                "password": test_user_data["password"]
            }
        )

        assert login_response.status_code == 403
        assert "inactivo" in login_response.json()["detail"]


class TestUserEndpointsIntegration:
    """Tests de integración entre múltiples endpoints"""

    def test_update_profile_then_get_profile(
        self,
        client: TestClient,
        verified_user: User,
        access_token_headers: dict
    ):
        """Prueba actualizar perfil y luego obtenerlo"""
        # Actualizar
        update_response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"name": "Updated Name"}
        )
        assert update_response.status_code == 200

        # Obtener perfil actualizado
        get_response = client.get(
            "/api/v1/users/me",
            headers=access_token_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Updated Name"

    def test_change_password_then_login_with_new(
        self,
        client: TestClient,
        verified_user: User,
        test_user_data: dict,
        access_token_headers: dict
    ):
        """Prueba cambiar contraseña y luego hacer login con la nueva"""
        new_password = "NewPassword123!"

        # Cambiar contraseña
        change_response = client.post(
            "/api/v1/users/change-password",
            headers=access_token_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": new_password
            }
        )
        assert change_response.status_code == 200

        # Login con contraseña anterior debe fallar
        old_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": verified_user.email,
                "password": test_user_data["password"]
            }
        )
        assert old_login_response.status_code == 401

        # Login con nueva contraseña debe funcionar
        new_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": verified_user.email,
                "password": new_password
            }
        )
        assert new_login_response.status_code == 200
        assert "access_token" in new_login_response.json()

    def test_update_email_requires_reverification(
        self,
        client: TestClient,
        verified_user: User,
        access_token_headers: dict
    ):
        """Prueba que actualizar email requiere reverificación"""
        # Actualizar email
        update_response = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"email": "newemail@example.com"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["is_verified"] is False

        # Intentar hacer login debe fallar por no estar verificado
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "newemail@example.com",
                "password": "Test123!Pass"
            }
        )
        assert login_response.status_code == 403
        assert "no verificado" in login_response.json()["detail"]

    def test_multiple_profile_updates(
        self,
        client: TestClient,
        verified_user: User,
        access_token_headers: dict
    ):
        """Prueba múltiples actualizaciones de perfil"""
        # Primera actualización
        response1 = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"name": "Name 1"}
        )
        assert response1.status_code == 200
        assert response1.json()["name"] == "Name 1"

        # Segunda actualización
        response2 = client.put(
            "/api/v1/users/me",
            headers=access_token_headers,
            json={"name": "Name 2"}
        )
        assert response2.status_code == 200
        assert response2.json()["name"] == "Name 2"

        # Verificar que el perfil actual tiene el último valor
        get_response = client.get(
            "/api/v1/users/me",
            headers=access_token_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Name 2"


class TestUserEndpointsWithUnverifiedUser:
    """Tests con usuario no verificado"""

    def test_unverified_user_cannot_access_profile(
        self,
        client: TestClient,
        created_user: User
    ):
        """Prueba que usuario no verificado no puede acceder a su perfil"""
        from app.core.security import create_access_token

        # Crear token para usuario no verificado
        token = create_access_token(subject=str(created_user.id))

        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Debe fallar porque el endpoint requiere usuario verificado
        assert response.status_code == 403

    def test_unverified_user_cannot_update_profile(
        self,
        client: TestClient,
        created_user: User
    ):
        """Prueba que usuario no verificado no puede actualizar su perfil"""
        from app.core.security import create_access_token

        token = create_access_token(subject=str(created_user.id))

        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "New Name"}
        )

        assert response.status_code == 403
