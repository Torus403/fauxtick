import secrets

from pydantic import PostgresDsn, computed_field, EmailStr, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # Project
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FauxTick"
    PROJECT_DESCRIPTION: str = "Welcome to FauxTick's API documentation. Here you will be able to explore all the ways you can interact with the FauxTick API."
    BACKEND_HOST: str = "http://localhost:8000"

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_NAME: str = ""
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    @property
    def DB_URI(self) -> PostgresDsn:
        uri = MultiHostUrl.build(
            # needed to use pyscopg3: https://stackoverflow.com/questions/73596058/creating-an-sqlalchemy-engine-based-on-psycopg3
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_NAME,
        )
        return PostgresDsn(str(uri))

    AWS_REGION: str
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.AWS_REGION and self.EMAILS_FROM_EMAIL)

    CONFIRMATION_TOKEN_EXPIRE_HOURS: int = 24
    RESET_TOKEN_EXPIRE_HOURS: int = 24


settings = Settings()
