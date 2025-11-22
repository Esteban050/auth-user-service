"""
Servicio de mensajería para publicar eventos a RabbitMQ (CloudAMQP).
"""
import json
import logging
from typing import Optional
import pika
from pika.exceptions import AMQPError

from app.core.config import settings
from app.schemas.events import (
    EmailVerificationEvent,
    WelcomeEmailEvent,
    PasswordResetEvent,
    PasswordChangedEvent
)

logger = logging.getLogger(__name__)


class MessageService:
    """
    Servicio para publicar eventos a RabbitMQ CloudAMQP.
    Implementa patrón publish/subscribe usando exchange tipo topic.
    """

    def __init__(self):
        """
        Inicializa el servicio de mensajería.
        La conexión se establece bajo demanda (lazy initialization).
        """
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None

    def _get_connection(self) -> pika.BlockingConnection:
        """
        Obtiene o crea una conexión a RabbitMQ.

        Returns:
            Conexión activa a RabbitMQ

        Raises:
            AMQPError: Si no se puede establecer conexión
        """
        if self._connection is None or self._connection.is_closed:
            try:
                # Parsear URL de CloudAMQP
                params = pika.URLParameters(settings.RABBITMQ_URL)
                params.socket_timeout = 5  # Timeout de 5 segundos

                # Crear conexión
                self._connection = pika.BlockingConnection(params)
                logger.info("Conexión a RabbitMQ establecida exitosamente")
            except AMQPError as e:
                logger.error(f"Error al conectar con RabbitMQ: {str(e)}")
                raise

        return self._connection

    def _get_channel(self) -> pika.channel.Channel:
        """
        Obtiene o crea un canal de comunicación.

        Returns:
            Canal activo de RabbitMQ
        """
        if self._channel is None or self._channel.is_closed:
            connection = self._get_connection()
            self._channel = connection.channel()

            # Declarar exchange tipo topic (idempotente)
            self._channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type=settings.RABBITMQ_EXCHANGE_TYPE,
                durable=True  # Persistente entre reinicios
            )
            logger.info(f"Exchange '{settings.RABBITMQ_EXCHANGE}' declarado")

        return self._channel

    def publish_event(self, routing_key: str, event_data: dict) -> bool:
        """
        Publica un evento al exchange de RabbitMQ.

        Args:
            routing_key: Routing key para dirigir el mensaje (ej: email.verification)
            event_data: Datos del evento en formato dict

        Returns:
            True si se publicó exitosamente, False en caso de error
        """
        try:
            channel = self._get_channel()

            # Serializar a JSON (convertir UUID a string)
            message_body = json.dumps(event_data, default=str)

            # Publicar mensaje
            channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                    content_type='application/json'
                )
            )

            logger.info(f"Evento publicado: {routing_key}")
            return True

        except AMQPError as e:
            logger.error(f"Error al publicar evento {routing_key}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al publicar evento {routing_key}: {str(e)}")
            return False

    def publish_verification_email(self, event: EmailVerificationEvent) -> bool:
        """
        Publica evento de email de verificación.

        Args:
            event: Datos del evento de verificación

        Returns:
            True si se publicó exitosamente
        """
        return self.publish_event(
            routing_key="email.verification",
            event_data=event.model_dump()
        )

    def publish_welcome_email(self, event: WelcomeEmailEvent) -> bool:
        """
        Publica evento de email de bienvenida.

        Args:
            event: Datos del evento de bienvenida

        Returns:
            True si se publicó exitosamente
        """
        return self.publish_event(
            routing_key="email.welcome",
            event_data=event.model_dump()
        )

    def publish_password_reset_email(self, event: PasswordResetEvent) -> bool:
        """
        Publica evento de email de reset de contraseña.

        Args:
            event: Datos del evento de reset

        Returns:
            True si se publicó exitosamente
        """
        return self.publish_event(
            routing_key="email.password_reset",
            event_data=event.model_dump()
        )

    def publish_password_changed_email(self, event: PasswordChangedEvent) -> bool:
        """
        Publica evento de email de confirmación de cambio de contraseña.

        Args:
            event: Datos del evento de cambio de contraseña

        Returns:
            True si se publicó exitosamente
        """
        return self.publish_event(
            routing_key="email.password_changed",
            event_data=event.model_dump()
        )

    def close(self):
        """
        Cierra la conexión a RabbitMQ de forma segura.
        Debe llamarse al finalizar la aplicación.
        """
        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
                logger.info("Canal de RabbitMQ cerrado")

            if self._connection and not self._connection.is_closed:
                self._connection.close()
                logger.info("Conexión a RabbitMQ cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión a RabbitMQ: {str(e)}")

    def __del__(self):
        """Destructor: cierra conexión automáticamente."""
        self.close()


# Instancia única del servicio
message_service = MessageService()
