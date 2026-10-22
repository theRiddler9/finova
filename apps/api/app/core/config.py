from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings shared by API and workers."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Finova API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://finova:finova-dev-only@localhost:5432/finova"
    redis_url: str = "redis://localhost:6379/0"
    paypal_env: str = Field(default="sandbox", pattern="^(sandbox|live)$")
    paypal_webhook_id: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_api_key: str = ""
    llm_model: str = ""
    vision_model: str = ""
    auth_jwt_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
