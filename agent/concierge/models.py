from __future__ import annotations

from livekit.agents import llm, stt, tts
from livekit.plugins import cartesia, deepgram, openai

from concierge.config import get_settings

# Bias Deepgram toward Meridian proper nouns that STT often mangles (VC-2 / NF-1).
_STT_KEYTERMS = [
    "Meridian",
    "Aurelia",
    "Silk Road",
    "Eclipse Lounge",
    "Café Meridian",
    "NOVA",
    "Vegas",
    "baccarat",
    "concierge",
    "valet",
    "spa",
    "cabana",
    "Penthouse",
    "Chairman's Villa",
]


def build_llm() -> llm.LLM:
    settings = get_settings()
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is not set")
    kwargs: dict = {
        "model": settings.llm_model,
        "api_key": settings.llm_api_key,
        "temperature": 0.5,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return openai.LLM(**kwargs)


def build_stt() -> stt.STT:
    settings = get_settings()
    if not settings.stt_api_key:
        raise RuntimeError("STT_API_KEY is not set")
    return deepgram.STT(
        model="nova-3",
        language="en",
        api_key=settings.stt_api_key,
        keyterm=_STT_KEYTERMS,
    )


def build_tts(voice_id: str | None = None) -> tts.TTS:
    settings = get_settings()
    if not settings.tts_api_key:
        raise RuntimeError("TTS_API_KEY is not set")
    return cartesia.TTS(
        model="sonic-3",
        voice=voice_id or settings.default_tts_voice_id,
        api_key=settings.tts_api_key,
    )
