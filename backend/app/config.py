from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    livekit_public_url: str
    livekit_api_key: str
    livekit_api_secret: str
    llm_api_key: str | None = None
    # OpenAI-compatible base URL for health probes (omit for api.openai.com).
    llm_base_url: str | None = None
    stt_api_key: str | None = None
    tts_api_key: str | None = None
    # Cartesia TTS model for voice previews (stable family alias preferred).
    tts_model: str = "sonic-3"
    faq_search_threshold: float = 0.42
    # Near-duplicate unanswered questions (paraphrases) share a row above this score.
    unanswered_similarity_threshold: float = 0.82
    # Lexical Jaccard overlap also required before semantic near-dup merge.
    unanswered_token_overlap: float = 0.45
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
