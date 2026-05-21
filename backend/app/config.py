from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner"
    DB_ECHO: bool = False
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
