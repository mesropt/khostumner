import html as html_module

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Խոստումներ",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
)

fm = FastMail(mail_config)


async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    safe_url = html_module.escape(verify_url)
    await fm.send_message(
        MessageSchema(
            subject="Հաստատեք Ձեր հաշիվը — Խոստումներ",
            recipients=[email],
            body=(
                f"<html><body>"
                f"<p>Բարև, Ձեր հաշիվը Խոստումներ կայքում գրանցված է։</p>"
                f"<p>Հաստատելու համար հետևեք հղմանը՝</p>"
                f'<p><a href="{safe_url}">{safe_url}</a></p>'
                f"<p>Եթե Դուք չեք գրանցվել, անտեսեք այս նամակը։</p>"
                f"</body></html>"
            ),
            subtype=MessageType.html,
        )
    )


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    safe_url = html_module.escape(reset_url)
    await fm.send_message(
        MessageSchema(
            subject="Գաղտնաբառի վերականգնում — Խոստումներ",
            recipients=[email],
            body=(
                f"<html><body>"
                f"<p>Ձեր գաղտնաբառը վերականգնելու համար հետևեք հղմանը՝</p>"
                f'<p><a href="{safe_url}">{safe_url}</a></p>'
                f"<p>Հղումն ունի սահմանափակ ժամկետ։</p>"
                f"<p>Եթե Դուք չեք պահանջել գաղտնաբառի վերականգնում, անտեսեք այս նամակը։</p>"
                f"</body></html>"
            ),
            subtype=MessageType.html,
        )
    )
