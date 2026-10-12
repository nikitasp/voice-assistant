from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.health import ProviderCheck

pytestmark = pytest.mark.asyncio


async def test_health_returns_ok(client):
    response = await client.get("/health")

    assert response.status_code == 200


async def test_providers_health_reports_llm_stt_and_tts(client):
    with (
        patch(
            "app.api.routes.health.check_llm_token",
            new=AsyncMock(return_value=ProviderCheck(ok=True, detail="OpenAI token accepted")),
        ),
        patch(
            "app.api.routes.health.check_stt_token",
            new=AsyncMock(return_value=ProviderCheck(ok=True, detail="Deepgram token accepted")),
        ),
        patch(
            "app.api.routes.health.check_tts_token",
            new=AsyncMock(return_value=ProviderCheck(ok=False, detail="TTS_API_KEY is not configured")),
        ),
    ):
        response = await client.get("/api/health/providers")

    assert response.status_code == 200
    body = response.json()
    assert body["llm"] == {"ok": True, "detail": "OpenAI token accepted"}
    assert body["stt"] == {"ok": True, "detail": "Deepgram token accepted"}
    assert body["tts"]["ok"] is False


async def test_openapi_documents_core_endpoints(client):
    response = await client.get("/openapi.json")

    paths = response.json()["paths"]
    assert "/api/faq/search" in paths
    assert "/api/unanswered" in paths
    assert "/api/livekit/token" in paths
    assert "/api/health/providers" in paths
