from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    livekit_public_url: str
    livekit_api_key: str
    livekit_api_secret: str
    llm_api_key: str | None = None
    tts_api_key: str | None = None
    faq_search_threshold: float = 0.42
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
