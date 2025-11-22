from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Microservicio de autenticación y autorización de usuarios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de health check básico.
    Retorna el estado del servicio sin verificar dependencias.
    Útil para load balancers y orquestadores.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


# Readiness check endpoint
@app.get("/ready", tags=["Health"])
def readiness_check():
    """
    Endpoint de readiness check.
    Verifica que el servicio esté listo para recibir tráfico.
    Verifica conexión a base de datos.
    """
    from fastapi import status, HTTPException
    from sqlalchemy import text
    from app.db.session import SessionLocal

    try:
        # Verificar conexión a base de datos
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

        return {
            "status": "ready",
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not ready",
                "service": settings.APP_NAME,
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Endpoint raíz.
    Retorna información básica del servicio.
    """
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_PREFIX
    }


# Evento al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    """
    Evento ejecutado al iniciar la aplicación.
    Aquí se pueden inicializar conexiones, caché, etc.
    """
    print(f"Starting {settings.APP_NAME}...")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"API Base URL: http://localhost:8000{settings.API_V1_PREFIX}")


# Evento al detener la aplicación
@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento ejecutado al detener la aplicación.
    Aquí se pueden cerrar conexiones, limpiar recursos, etc.
    """
    print(f"Shutting down {settings.APP_NAME}...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
