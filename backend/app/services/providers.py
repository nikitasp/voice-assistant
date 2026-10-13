from __future__ import annotations

import httpx

from app.schemas.health import ProviderCheck


async def check_llm_token(
    api_key: str | None,
    *,
    base_url: str | None = None,
) -> ProviderCheck:
    """Validate an OpenAI-compatible API key without running a full chat completion."""
    if not api_key:
        return ProviderCheck(ok=False, detail="LLM_API_KEY is not configured")

    root = (base_url or "https://api.openai.com/v1").rstrip("/")
    label = "OpenAI-compatible" if base_url else "OpenAI"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{root}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
    if response.status_code == 200:
        return ProviderCheck(ok=True, detail=f"{label} token accepted")
    snippet = response.text.strip().replace("\n", " ")[:240]
    return ProviderCheck(
        ok=False,
        detail=f"{label} status {response.status_code}: {snippet or response.reason_phrase}",
    )


async def check_stt_token(api_key: str | None) -> ProviderCheck:
    """Validate Deepgram API key without running a full transcription."""
    if not api_key:
        return ProviderCheck(ok=False, detail="STT_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.deepgram.com/v1/projects",
            headers={"Authorization": f"Token {api_key}"},
        )
    if response.status_code == 200:
        return ProviderCheck(ok=True, detail="Deepgram token accepted")
    snippet = response.text.strip().replace("\n", " ")[:240]
    return ProviderCheck(
        ok=False,
        detail=f"Deepgram status {response.status_code}: {snippet or response.reason_phrase}",
    )


async def check_tts_token(api_key: str | None) -> ProviderCheck:
    """Validate Cartesia API key by listing voices (no speech generation)."""
    if not api_key:
        return ProviderCheck(ok=False, detail="TTS_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.cartesia.ai/voices",
            headers={
                "X-API-Key": api_key,
                "Cartesia-Version": "2024-06-10",
            },
            params={"limit": 1},
        )
    if response.status_code == 200:
        return ProviderCheck(ok=True, detail="Cartesia token accepted")
    snippet = response.text.strip().replace("\n", " ")[:240]
    return ProviderCheck(
        ok=False,
        detail=f"Cartesia status {response.status_code}: {snippet or response.reason_phrase}",
    )
