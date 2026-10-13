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
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.backend_url).rstrip("/")
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def search_faq(self, query: str) -> dict[str, Any]:
        try:
            response = await self._get_client().post(
                f"{self._base_url}/api/faq/search",
                json={"query": query},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            return {
                "found": False,
                "results": [],
                "error": f"Knowledge base unavailable: {exc}",
            }

    async def record_unanswered(self, question: str) -> dict[str, Any]:
        try:
            response = await self._get_client().post(
                f"{self._base_url}/api/unanswered",
                json={"question": question},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            return {"error": f"Could not record unanswered question: {exc}"}

    async def get_property_info(self) -> str:
        """The property information sheet as plain text, one `Name: details` line per item."""
        response = await self._get_client().get(f"{self._base_url}/api/property")
        response.raise_for_status()
        sections: list[dict[str, Any]] = response.json()["sections"]
        blocks = []
        for section in sections:
            lines = [f"{section['title']}:"]
            lines += [f"- {item['name']}: {item['details']}" for item in section["items"]]
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    async def get_active_provider_voice_id(self) -> str | None:
        response = await self._get_client().get(f"{self._base_url}/api/voices")
        response.raise_for_status()
        voices: list[dict[str, Any]] = response.json()
        for voice in voices:
            if voice.get("active"):
                return str(voice["provider_voice_id"])
        return None
