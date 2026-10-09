from __future__ import annotations

import struct
import wave
from io import BytesIO

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import AppSetting
from app.models.voice import Voice
from app.schemas.voices import VoiceOut

ACTIVE_VOICE_KEY = "active_voice_id"

# Distinct Cartesia Sonic voice IDs mapped to PRD personas.
SEED_VOICES: list[dict[str, str]] = [
    {
        "name": "James",
        "description": "Male, mature, warm British accent. Professional and refined.",
        "provider_voice_id": "95856005-0332-41b0-935f-352e296aa0df",
    },
    {
        "name": "Sofia",
        "description": "Female, friendly, subtle European accent. Welcoming and elegant.",
        "provider_voice_id": "79a125e8-cd45-4c13-8a67-188112f4dd22",
    },
    {
        "name": "Marcus",
        "description": "Male, American, confident and energetic. Modern and approachable.",
        "provider_voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
    },
    {
        "name": "Elena",
        "description": "Female, American, calm and reassuring. Sophisticated and clear.",
        "provider_voice_id": "694f9389-aac1-45b6-b726-9d9369183238",
    },
]

PREVIEW_TEXT = (
    "Good evening, and welcome to The Meridian Casino and Resort. "
    "How may I assist you today?"
)


def silent_wav(duration_ms: int = 300, sample_rate: int = 16000) -> bytes:
    frame_count = int(sample_rate * duration_ms / 1000)
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        silence = struct.pack("<h", 0) * frame_count
        wav.writeframes(silence)
    return buffer.getvalue()


class VoiceService:
    def __init__(self, tts_api_key: str | None) -> None:
        self._tts_api_key = tts_api_key

    async def list_voices(self, session: AsyncSession) -> list[VoiceOut]:
        voices = (await session.execute(select(Voice).order_by(Voice.name))).scalars().all()
        active_id = await self.get_active_voice_id(session)
        return [
            VoiceOut(
                id=voice.id,
                name=voice.name,
                description=voice.description,
                provider_voice_id=voice.provider_voice_id,
                active=voice.id == active_id,
            )
            for voice in voices
        ]

    async def get_active_voice_id(self, session: AsyncSession) -> str | None:
        setting = await session.get(AppSetting, ACTIVE_VOICE_KEY)
        return setting.value if setting else None

    async def set_active_voice(self, session: AsyncSession, voice_id: str) -> list[VoiceOut]:
        voice = await session.get(Voice, voice_id)
        if voice is None:
            raise LookupError("Voice not found")

        setting = await session.get(AppSetting, ACTIVE_VOICE_KEY)
        if setting is None:
            session.add(AppSetting(key=ACTIVE_VOICE_KEY, value=voice_id))
        else:
            setting.value = voice_id
        await session.commit()
        return await self.list_voices(session)

    async def get_preview_audio(self, session: AsyncSession, voice_id: str) -> tuple[bytes, str]:
        voice = await session.get(Voice, voice_id)
        if voice is None:
            raise LookupError("Voice not found")

        if voice.preview_audio:
            return voice.preview_audio, "audio/wav"

        audio, media_type = await self._generate_preview(voice.provider_voice_id)
        voice.preview_audio = audio
        await session.commit()
        return audio, media_type

    async def _generate_preview(self, provider_voice_id: str) -> tuple[bytes, str]:
        if not self._tts_api_key:
            return silent_wav(), "audio/wav"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={
                    "X-API-Key": self._tts_api_key,
                    "Cartesia-Version": "2024-06-10",
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": "sonic-english",
                    "transcript": PREVIEW_TEXT,
                    "voice": {
                        "mode": "id",
                        "id": provider_voice_id,
                    },
                    "output_format": {
                        "container": "wav",
                        "encoding": "pcm_s16le",
                        "sample_rate": 22050,
                    },
                },
            )
            if response.status_code >= 400:
                return silent_wav(), "audio/wav"
            return response.content, "audio/wav"
