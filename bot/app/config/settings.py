"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-based configuration.

    All values can be overridden by environment variables or a .env file.
    """

    BOT_TOKEN: str
    API_URL: str
    API_TOKEN: str

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "bot"

    LOG_LEVEL: str = "INFO"
    PARSE_MODE: Optional[str] = None

    REQUEST_TIMEOUT: float = 10.0
    RETRY_COUNT: int = 3
    RETRY_BACKOFF: float = 0.5

    RATE_LIMIT_SECONDS: float = 0.5
    USER_SYNC_TTL: int = 3600

    PARTNER_ID: Optional[str] = None
    PARTNER_ENDPOINT: str = "/api/bot/partner"

    START_ENDPOINT: str = "/api/bot/start"
    USER_SYNC_ENDPOINT: str = "/api/bot/user/sync"
    MENU_ENDPOINT: str = "/api/bot/menu"
    ACTION_ENDPOINT: str = "/api/bot/action"

    model_config = SettingsConfigDict(
        env_file=(".env", "bot/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
