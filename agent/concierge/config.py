from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    livekit_url: str | None = None
    livekit_api_key: str | None = None
    livekit_api_secret: str | None = None
    llm_api_key: str | None = None
    # OpenAI-compatible endpoint (omit for api.openai.com). Examples:
    #   Groq:   https://api.groq.com/openai/v1
    #   Ollama: http://host.docker.internal:11434/v1  (agent in Docker)
    llm_base_url: str | None = None
    stt_api_key: str | None = None
    tts_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"
    # Fallback Cartesia voice (James) when the backend is unreachable at session start.
    default_tts_voice_id: str = "95856005-0332-41b0-935f-352e296aa0df"

    # Interruption tuning. Default off: open-speaker echo was cutting TTS mid-utterance
    # and STT was transcribing the agent's own words as the guest. Re-enable with
    # headphones via ALLOW_INTERRUPTIONS=true.
    allow_interruptions: bool = False
    min_interruption_duration: float = 0.8
    min_interruption_words: int = 2
    resume_false_interruption: bool = True
    false_interruption_timeout: float = 1.5


def get_settings() -> Settings:
    # Fresh instance so test monkeypatches of env vars are picked up.
    return Settings()
