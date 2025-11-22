# Dockerfile para Auth Microservice - FastAPI
# Multi-stage build para optimizar tamaño de imagen

# ============================================
# Stage 1: Builder - Instala dependencias
# ============================================
FROM python:3.13-slim as builder

# Metadata
LABEL maintainer="Auth Microservice Team"
LABEL description="Authentication Microservice for Easy Parking"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero (aprovecha cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python en un virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ============================================
# Stage 2: Runtime - Imagen final optimizada
# ============================================
FROM python:3.13-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Instalar solo dependencias runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=appuser:appuser app ./app

# Crear directorio para logs si es necesario
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto - Uvicorn con configuración de producción
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]


# ============================================
# Comandos útiles:
# ============================================
# Build:
#   docker build -t auth-microservice:latest .
#
# Run:
#   docker run -p 8000:8000 --env-file .env auth-microservice:latest
#
# Run con override de comando (development):
#   docker run -p 8000:8000 --env-file .env auth-microservice:latest \
#     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload