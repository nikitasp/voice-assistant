from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.health import ProvidersHealthResponse
from app.services.providers import check_llm_token, check_stt_token, check_tts_token

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/health/providers", response_model=ProvidersHealthResponse)
async def providers_health(settings: SettingsDep) -> ProvidersHealthResponse:
    """Validate LLM/STT/TTS API keys without exposing secrets (used by the Health page)."""
    return ProvidersHealthResponse(
        llm=await check_llm_token(settings.llm_api_key),
        stt=await check_stt_token(settings.stt_api_key),
        tts=await check_tts_token(settings.tts_api_key),
    )
