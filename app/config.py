import secrets
from typing import Annotated, Any, Literal
import app.config
from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROJECT_NAME: str = "myHome"
    FRONTEND_URL: AnyUrl = "http://localhost:8001/api/v1/"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    ALGORITHM: str = "HS256"
    EMAIL_RESET_PASSWORD_EXPIRE_MINUTES: int = 10
    EMAIL_VERIFY_EMAIL_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAILS_FROM_NAME: str = "myHome"
    EMAILS_FROM_EMAIL: str = ""

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 2525
    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_USER: str = "8194b3b06d50b2"
    SMTP_PASSWORD: str = "def1e61ddd646c"


settings = Settings()  # type: ignore