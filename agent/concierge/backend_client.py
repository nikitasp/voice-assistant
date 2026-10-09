from __future__ import annotations

from typing import Any

import httpx

from concierge.config import get_settings

DEFAULT_TIMEOUT_S = 2.0


class BackendClient:
    """HTTP client for the Meridian backend knowledge-base API."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.backend_url).rstrip("/")
        self._timeout = timeout

    async def search_faq(self, query: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/faq/search",
                json={"query": query},
            )
            response.raise_for_status()
            return response.json()

    async def record_unanswered(self, question: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/unanswered",
                json={"question": question},
            )
            response.raise_for_status()
            return response.json()

    async def get_active_provider_voice_id(self) -> str | None:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(f"{self._base_url}/api/voices")
            response.raise_for_status()
            voices: list[dict[str, Any]] = response.json()
        for voice in voices:
            if voice.get("active"):
                return str(voice["provider_voice_id"])
        if voices:
            return str(voices[0]["provider_voice_id"])
        return None
