from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner"
    DB_ECHO: bool = False
    ENVIRONMENT: str = "development"

    # Phase 4: Auth
    JWT_SECRET: str = "change-me-in-production"
    RESET_PASSWORD_SECRET: str = "change-me-reset-in-production"
    VERIFICATION_SECRET: str = "change-me-verify-in-production"
    CSRF_SECRET: str = "change-me-in-production-csrf"
    # Set to False only for local dev via .env; defaults to True for security
    COOKIE_SECURE: bool = True
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@khostumner.am"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
