"""VX-1, VX-3, NF-5: four voices, active selection, preview audio."""

import struct
import wave
from io import BytesIO

import pytest

pytestmark = pytest.mark.asyncio

EXPECTED_NAMES = {"James", "Sofia", "Marcus", "Elena"}


def non_silent_wav(duration_ms: int = 200, sample_rate: int = 16000) -> bytes:
    """Minimal WAV with non-zero PCM samples (not the silent fallback)."""
    frame_count = int(sample_rate * duration_ms / 1000)
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        # A short square-ish tone so content is clearly not silence.
        frames = b"".join(
            struct.pack("<h", 12000 if i % 2 == 0 else -12000) for i in range(frame_count)
        )
        wav.writeframes(frames)
    return buffer.getvalue()


async def test_four_voices_seeded_with_one_active(client):
    response = await client.get("/api/voices")
    assert response.status_code == 200, response.text
    voices = response.json()
    names = {voice["name"] for voice in voices}
    assert EXPECTED_NAMES <= names
    assert sum(1 for voice in voices if voice["active"]) == 1
    for voice in voices:
        assert voice["provider_voice_id"]
        assert voice["description"]


async def test_set_active_voice_updates_flag(client):
    voices = (await client.get("/api/voices")).json()
    inactive = next(voice for voice in voices if not voice["active"])

    response = await client.put("/api/voices/active", json={"voice_id": inactive["id"]})
    assert response.status_code == 200, response.text
    updated = response.json()
    assert next(voice for voice in updated if voice["id"] == inactive["id"])["active"] is True
    assert sum(1 for voice in updated if voice["active"]) == 1


async def _clear_voice_previews(database_url: str) -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("UPDATE voices SET preview_audio = NULL"))
    finally:
        await engine.dispose()


async def test_preview_returns_wav_audio(client, monkeypatch, database_url):
    await _clear_voice_previews(database_url)

    sample = non_silent_wav()
    calls = {"n": 0}

    async def fake_generate(self, provider_voice_id: str) -> tuple[bytes, str]:
        calls["n"] += 1
        assert provider_voice_id
        return sample, "audio/wav"

    monkeypatch.setattr(
        "app.services.voices.VoiceService._generate_preview",
        fake_generate,
    )

    voices = (await client.get("/api/voices")).json()
    voice_id = voices[0]["id"]

    response = await client.get(f"/api/voices/{voice_id}/preview")
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("audio/")
    assert response.content == sample
    assert response.content[:4] == b"RIFF"
    assert any(b != 0 for b in response.content[44:]), "preview must not be silence"
    assert calls["n"] == 1

    # Cached successful preview — generator must not run again.
    cached = await client.get(f"/api/voices/{voice_id}/preview")
    assert cached.status_code == 200
    assert cached.content == sample
    assert calls["n"] == 1


async def test_preview_failure_is_not_cached(client, monkeypatch, database_url):
    from app.services.voices import VoicePreviewError

    await _clear_voice_previews(database_url)

    calls = {"n": 0}

    async def failing_generate(self, provider_voice_id: str) -> tuple[bytes, str]:
        calls["n"] += 1
        raise VoicePreviewError("TTS preview failed with status 500")

    monkeypatch.setattr(
        "app.services.voices.VoiceService._generate_preview",
        failing_generate,
    )

    voices = (await client.get("/api/voices")).json()
    voice_id = voices[0]["id"]

    first = await client.get(f"/api/voices/{voice_id}/preview")
    assert first.status_code == 503, first.text
    assert calls["n"] == 1

    second = await client.get(f"/api/voices/{voice_id}/preview")
    assert second.status_code == 503, second.text
    assert calls["n"] == 2, "failed previews must not be cached"
