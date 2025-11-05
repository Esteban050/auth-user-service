import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings
from app.utils.email_templates import (
    get_verification_email_template,
    get_password_reset_email_template,
    get_password_changed_email_template,
    get_welcome_email_template,
)


class EmailService:
    """
    Servicio para envío de emails usando SMTP (Gmail).
    """

    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Función auxiliar para enviar emails via SMTP.

        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        try:
            print(f"[EMAIL] Attempting to send email to {to_email}")
            print(f"[EMAIL] SMTP Config: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            print(f"[EMAIL] SMTP User: {settings.SMTP_USER}")
            print(f"[EMAIL] Subject: {subject}")

            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject

            # Adjuntar contenido HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Conectar al servidor SMTP
            print(f"[EMAIL] Connecting to SMTP server...")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                print(f"[EMAIL] Starting TLS...")
                server.starttls()  # Habilitar seguridad
                print(f"[EMAIL] Logging in...")
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                print(f"[EMAIL] Sending message...")
                server.send_message(msg)

            print(f"[EMAIL] ✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] ❌ Error sending email to {to_email}")
            print(f"[EMAIL] Error type: {type(e).__name__}")
            print(f"[EMAIL] Error message: {str(e)}")
            import traceback
            print(f"[EMAIL] Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_verification_email(email: str, user_name: str, verification_token: str) -> bool:
        """
        Envía email de verificación de cuenta.

        Args:
            email: Email del destinatario
            user_name: Nombre del usuario
            verification_token: Token de verificación

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        template = get_verification_email_template(user_name, verification_token)
        return EmailService._send_email(email, template["subject"], template["html_content"])

    @staticmethod
    def send_password_reset_email(email: str, user_name: str, reset_token: str) -> bool:
        """
        Envía email de recuperación de contraseña.

        Args:
            email: Email del destinatario
            user_name: Nombre del usuario
            reset_token: Token de reset de contraseña

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        template = get_password_reset_email_template(user_name, reset_token)
        return EmailService._send_email(email, template["subject"], template["html_content"])

    @staticmethod
    def send_password_changed_email(email: str, user_name: str) -> bool:
        """
        Envía email de confirmación de cambio de contraseña.

        Args:
            email: Email del destinatario
            user_name: Nombre del usuario

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        template = get_password_changed_email_template(user_name)
        return EmailService._send_email(email, template["subject"], template["html_content"])

    @staticmethod
    def send_welcome_email(email: str, user_name: str) -> bool:
        """
        Envía email de bienvenida después de verificar la cuenta.

        Args:
            email: Email del destinatario
            user_name: Nombre del usuario

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        template = get_welcome_email_template(user_name)
        return EmailService._send_email(email, template["subject"], template["html_content"])

    @staticmethod
    def send_custom_email(
        email: str,
        subject: str,
        html_content: str,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Envía un email personalizado.

        Args:
            email: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email
            reply_to: Email de respuesta (opcional)

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        # Note: reply_to is not implemented in this simple SMTP version
        return EmailService._send_email(email, subject, html_content)


# Instancia única del servicio
email_service = EmailService()
