# Easy Parking - Authentication Microservice

FastAPI-based authentication microservice with email verification, JWT authentication, and password management.

## Features

- User registration with email verification
- JWT-based authentication (access & refresh tokens)
- Password reset via email
- User profile management
- PostgreSQL database
- Email delivery via Resend

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Resend API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd FastAPIProject1

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Create a `.env` file with:

```env
DATABASE_URL=postgresql://user:password@localhost/easy_parking
SECRET_KEY=your-secret-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=usario de email
SMTP_PASSWORD=contraseña de la app de email (no es del correo)
FROM_EMAIL=Email
FRONTEND_URL=http://localhost:3000
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Setup

```bash
python -m app.db.init_db
```

### Run Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API documentation available at: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/verify-email` - Verify email with token
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with token

### User Profile
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/change-password` - Change password

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/
```

## Architecture

```
API Layer (app/api/) → Services (app/services/) → CRUD (app/crud/) → Models (app/models/)
```

- **Clean architecture** with separation of concerns
- **Dependency injection** for database sessions and authentication
- **Service pattern** for business logic isolation

## Security

- bcrypt password hashing
- JWT with HS256 algorithm
- Email verification required for login
- Token type validation (access/refresh)
- Single-use password reset tokens
- CORS protection

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **JWT** - Token authentication
- **Resend** - Email delivery
- **pytest** - Testing


