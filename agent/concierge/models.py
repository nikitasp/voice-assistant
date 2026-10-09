from __future__ import annotations

from livekit.agents import llm, stt, tts
from livekit.plugins import cartesia, deepgram, openai

from concierge.config import get_settings


def build_llm() -> llm.LLM:
    settings = get_settings()
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is not set")
    return openai.LLM(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        temperature=0.5,
    )


def build_stt() -> stt.STT:
    settings = get_settings()
    if not settings.stt_api_key:
        raise RuntimeError("STT_API_KEY is not set")
    return deepgram.STT(
        model="nova-3",
        language="en-US",
        api_key=settings.stt_api_key,
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
