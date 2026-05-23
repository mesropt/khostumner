from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Khostumner",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
)

fm = FastMail(mail_config)


async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    await fm.send_message(
        MessageSchema(
            subject="Verify your account",
            recipients=[email],
            body=(
                f"<html><body>"
                f"<p>Follow this link to verify your email:</p>"
                f"<p><a href='{verify_url}'>{verify_url}</a></p>"
                f"</body></html>"
            ),
            subtype=MessageType.html,
        )
    )


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    await fm.send_message(
        MessageSchema(
            subject="Password reset",
            recipients=[email],
            body=(
                f"<html><body>"
                f"<p>Follow this link to reset your password:</p>"
                f"<p><a href='{reset_url}'>{reset_url}</a></p>"
                f"</body></html>"
            ),
            subtype=MessageType.html,
        )
    )
