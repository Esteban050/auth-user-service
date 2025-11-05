from app.core.config import settings


def get_verification_email_template(user_name: str, verification_token: str) -> dict:
    """
    Genera el template de email para verificación de correo electrónico.

    Args:
        user_name: Nombre del usuario
        verification_token: Token de verificación

    Returns:
        Dict con subject y html_content
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

    subject = f"Verifica tu cuenta en {settings.APP_NAME}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verificación de Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50; text-align: center;">{settings.APP_NAME}</h1>

            <div style="background-color: white; padding: 30px; border-radius: 5px; margin-top: 20px;">
                <h2 style="color: #333;">Hola {user_name},</h2>

                <p>Gracias por registrarte en {settings.APP_NAME}. Para completar tu registro, por favor verifica tu dirección de correo electrónico.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Verificar Email
                    </a>
                </div>

                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {verification_url}
                </p>

                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Este enlace expirará en {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} horas.
                </p>

                <p style="color: #666; font-size: 14px;">
                    Si no creaste esta cuenta, puedes ignorar este correo de forma segura.
                </p>
            </div>

            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                © 2024 {settings.APP_NAME}. Todos los derechos reservados.
            </p>
        </div>
    </body>
    </html>
    """

    return {
        "subject": subject,
        "html_content": html_content
    }


def get_password_reset_email_template(user_name: str, reset_token: str) -> dict:
    """
    Genera el template de email para recuperación de contraseña.

    Args:
        user_name: Nombre del usuario
        reset_token: Token de reset de contraseña

    Returns:
        Dict con subject y html_content
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    subject = f"Recuperación de contraseña - {settings.APP_NAME}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recuperación de Contraseña</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
            <h1 style="color: #FF9800; text-align: center;">{settings.APP_NAME}</h1>

            <div style="background-color: white; padding: 30px; border-radius: 5px; margin-top: 20px;">
                <h2 style="color: #333;">Hola {user_name},</h2>

                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background-color: #FF9800; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Restablecer Contraseña
                    </a>
                </div>

                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {reset_url}
                </p>

                <p style="color: #d32f2f; font-weight: bold; margin-top: 30px;">
                    ⚠️ Este enlace expirará en {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hora(s).
                </p>

                <p style="color: #666; font-size: 14px;">
                    Si no solicitaste restablecer tu contraseña, puedes ignorar este correo de forma segura. Tu contraseña no será cambiada.
                </p>
            </div>

            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                © 2024 {settings.APP_NAME}. Todos los derechos reservados.
            </p>
        </div>
    </body>
    </html>
    """

    return {
        "subject": subject,
        "html_content": html_content
    }


def get_password_changed_email_template(user_name: str) -> dict:
    """
    Genera el template de email para confirmar cambio de contraseña exitoso.

    Args:
        user_name: Nombre del usuario

    Returns:
        Dict con subject y html_content
    """
    subject = f"Tu contraseña ha sido cambiada - {settings.APP_NAME}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contraseña Cambiada</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50; text-align: center;">{settings.APP_NAME}</h1>

            <div style="background-color: white; padding: 30px; border-radius: 5px; margin-top: 20px;">
                <h2 style="color: #333;">Hola {user_name},</h2>

                <p>Tu contraseña ha sido cambiada exitosamente.</p>

                <div style="background-color: #e8f5e9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                    <p style="margin: 0; color: #2e7d32;">
                        ✓ Tu cuenta ahora está protegida con tu nueva contraseña.
                    </p>
                </div>

                <p style="color: #d32f2f; font-weight: bold; margin-top: 30px;">
                    ⚠️ ¿No realizaste este cambio?
                </p>

                <p style="color: #666; font-size: 14px;">
                    Si no cambiaste tu contraseña, tu cuenta puede estar comprometida. Por favor, contacta con soporte inmediatamente.
                </p>
            </div>

            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                © 2024 {settings.APP_NAME}. Todos los derechos reservados.
            </p>
        </div>
    </body>
    </html>
    """

    return {
        "subject": subject,
        "html_content": html_content
    }


def get_welcome_email_template(user_name: str) -> dict:
    """
    Genera el template de email de bienvenida después de verificar el email.

    Args:
        user_name: Nombre del usuario

    Returns:
        Dict con subject y html_content
    """
    subject = f"¡Bienvenido a {settings.APP_NAME}!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenido</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50; text-align: center;">{settings.APP_NAME}</h1>

            <div style="background-color: white; padding: 30px; border-radius: 5px; margin-top: 20px;">
                <h2 style="color: #333;">¡Bienvenido, {user_name}!</h2>

                <p>Tu email ha sido verificado exitosamente. Ahora puedes disfrutar de todas las funcionalidades de {settings.APP_NAME}.</p>

                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #1976d2; margin-top: 0;">¿Qué puedes hacer ahora?</h3>
                    <ul style="color: #666;">
                        <li>Gestionar tu perfil de usuario</li>
                        <li>Acceder a todas las funcionalidades del sistema</li>
                        <li>Cambiar tu contraseña en cualquier momento</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/login"
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Iniciar Sesión
                    </a>
                </div>

                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Si tienes alguna pregunta, no dudes en contactarnos.
                </p>
            </div>

            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                © 2024 {settings.APP_NAME}. Todos los derechos reservados.
            </p>
        </div>
    </body>
    </html>
    """

    return {
        "subject": subject,
        "html_content": html_content
    }
