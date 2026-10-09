"""PG-1, PG-5, NF-5: the playground gets a token for a fresh room per conversation."""

import jwt
import pytest

from .support import TEST_LIVEKIT_ENV

pytestmark = pytest.mark.asyncio


async def request_token(client) -> dict:
    response = await client.post("/api/livekit/token", json={})
    assert response.status_code == 200, response.text
    return response.json()


async def test_token_allows_joining_the_returned_room(client):
    body = await request_token(client)

    assert body["url"] == TEST_LIVEKIT_ENV["LIVEKIT_PUBLIC_URL"]
    claims = jwt.decode(
        body["token"],
        TEST_LIVEKIT_ENV["LIVEKIT_API_SECRET"],
        algorithms=["HS256"],
        options={"verify_aud": False},
    )
    assert claims["iss"] == TEST_LIVEKIT_ENV["LIVEKIT_API_KEY"]
    assert claims["video"]["roomJoin"] is True
    assert claims["video"]["room"] == body["room"]


async def test_each_conversation_gets_a_new_room(client):
    first = await request_token(client)
    second = await request_token(client)

    assert first["room"] != second["room"]
