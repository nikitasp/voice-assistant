from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    livekit_url: str | None = None
    livekit_api_key: str | None = None
    livekit_api_secret: str | None = None
    llm_api_key: str | None = None
    stt_api_key: str | None = None
    tts_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"
    # Fallback Cartesia voice (James) when the backend is unreachable at session start.
    default_tts_voice_id: str = "95856005-0332-41b0-935f-352e296aa0df"


def get_settings() -> Settings:
    # Fresh instance so test monkeypatches of env vars are picked up.
    return Settings()
