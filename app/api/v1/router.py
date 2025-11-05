from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, password


# Router principal para API v1
api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    password.router,
    prefix="/password",
    tags=["Password"]
)
