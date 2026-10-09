import pytest

pytestmark = pytest.mark.asyncio


async def test_health_returns_ok(client):
    response = await client.get("/health")

    assert response.status_code == 200


async def test_openapi_documents_core_endpoints(client):
    response = await client.get("/openapi.json")

    paths = response.json()["paths"]
    assert "/api/faq/search" in paths
    assert "/api/unanswered" in paths
    assert "/api/livekit/token" in paths
