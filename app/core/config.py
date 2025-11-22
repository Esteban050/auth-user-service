from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Lee las variables de entorno desde .env
    """

    # Application Settings
    APP_NAME: str = "Auth Microservice"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database - Supabase
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # RabbitMQ - CloudAMQP
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE: str = "notifications"
    RABBITMQ_EXCHANGE_TYPE: str = "topic"

    # Security - JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security - Email Verification & Password Reset
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Email Service - SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins(self) -> List[str]:
        """
        Convierte ALLOWED_ORIGINS (string separado por comas) en lista.

        Returns:
            Lista de orígenes permitidos para CORS
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variables de entorno no definidas
    )


# Instancia única de configuración
settings = Settings()
