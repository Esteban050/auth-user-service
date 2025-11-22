# Pruebas - Auth Microservice

Este directorio contiene todas las pruebas unitarias y de integración para el microservicio de autenticación.

## Estructura de Pruebas

```
tests/
├── conftest.py              # Fixtures compartidos y configuración
├── test_crud_user.py        # Pruebas unitarias CRUD de usuarios
├── test_auth_service.py     # Pruebas unitarias AuthService
├── test_user_service.py     # Pruebas unitarias UserService
├── test_api_auth.py         # Pruebas integración endpoints auth
└── test_api_users.py        # Pruebas integración endpoints users
```

## Tipos de Pruebas

### Pruebas Unitarias
- **test_crud_user.py**: Operaciones CRUD de la base de datos
- **test_auth_service.py**: Lógica de negocio de autenticación
- **test_user_service.py**: Lógica de negocio de gestión de usuarios

### Pruebas de Integración
- **test_api_auth.py**: Endpoints de registro, login, verificación
- **test_api_users.py**: Endpoints de perfil y gestión de usuario

## Ejecutar Pruebas

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar Todas las Pruebas

```bash
pytest
```

### Ejecutar con Reporte de Cobertura

```bash
pytest --cov=app --cov-report=html
```

El reporte HTML se generará en `htmlcov/index.html`

### Ejecutar Pruebas Específicas

```bash
# Por archivo
pytest tests/test_crud_user.py

# Por clase
pytest tests/test_auth_service.py::TestAuthService

# Por función
pytest tests/test_api_auth.py::TestLoginEndpoint::test_login_success

# Por marcador
pytest -m unit
pytest -m integration
```

### Opciones Útiles

```bash
# Modo verbose (más detalles)
pytest -v

# Mostrar print statements
pytest -s

# Detener en el primer fallo
pytest -x

# Ejecutar última prueba fallida
pytest --lf

# Ejecutar pruebas en paralelo (requiere pytest-xdist)
pytest -n auto

# Ver cobertura en terminal
pytest --cov=app --cov-report=term-missing
```

## Marcadores de Pruebas

Las pruebas están categorizadas con marcadores:

- `@pytest.mark.unit` - Pruebas unitarias
- `@pytest.mark.integration` - Pruebas de integración
- `@pytest.mark.auth` - Pruebas relacionadas con autenticación
- `@pytest.mark.user` - Pruebas de gestión de usuarios
- `@pytest.mark.crud` - Pruebas de operaciones CRUD
- `@pytest.mark.service` - Pruebas de capa de servicios

## Fixtures Disponibles

Definidos en `conftest.py`:

### Base de Datos
- `db` - Sesión de base de datos SQLite en memoria

### Cliente HTTP
- `client` - Cliente de prueba FastAPI

### Datos de Prueba
- `test_user_data` - Datos válidos de usuario
- `test_admin_data` - Datos válidos de administrador

### Usuarios Pre-creados
- `created_user` - Usuario creado, NO verificado
- `verified_user` - Usuario creado y verificado
- `inactive_user` - Usuario inactivo
- `admin_user` - Usuario administrador verificado

### Autenticación
- `access_token_headers` - Headers con access token válido
- `refresh_token_headers` - Headers con refresh token válido

## Cobertura de Código

El objetivo es mantener al menos **80% de cobertura** de código.

Para verificar la cobertura actual:

```bash
pytest --cov=app --cov-report=term-missing
```

## Buenas Prácticas

1. **Nombres Descriptivos**: Usa nombres claros que describan qué se está probando
   - ✅ `test_login_with_wrong_password`
   - ❌ `test_login_2`

2. **Arrange-Act-Assert**: Estructura tus pruebas en 3 secciones
   ```python
   def test_example():
       # Arrange - preparar datos
       user_data = {...}

       # Act - ejecutar acción
       result = service.create_user(user_data)

       # Assert - verificar resultado
       assert result.email == user_data["email"]
   ```

3. **Una Aserción por Test** (cuando sea posible)
   - Enfoca cada test en verificar un comportamiento específico

4. **Independencia**: Cada test debe poder ejecutarse solo
   - No depender del orden de ejecución
   - Usar fixtures para setup

5. **Mock de Servicios Externos**: RabbitMQ está mockeado automáticamente
   - Ver fixture `mock_rabbitmq` en conftest.py

## Tests Pendientes

Algunos tests marcados con `assert response.status_code in [200, 404]` indican endpoints que aún no están implementados:

- `POST /api/v1/auth/password/reset-request` - Solicitar reset de contraseña
- `POST /api/v1/auth/password/reset` - Resetear contraseña

Estos tests fallarán intencionalmente hasta que se implementen los endpoints.

## Debugging

Para debuggear una prueba específica:

```bash
# Con breakpoint en el código
pytest tests/test_auth_service.py::test_login_success --pdb

# Ver todos los logs
pytest tests/test_auth_service.py -v -s
```

## CI/CD

Las pruebas deben ejecutarse automáticamente en CI/CD antes de cada deploy.

Comando recomendado para CI:

```bash
pytest --cov=app --cov-fail-under=80 --cov-report=xml
```

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
