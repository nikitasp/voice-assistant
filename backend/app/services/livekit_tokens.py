from __future__ import annotations

from uuid import uuid4

from livekit.api import AccessToken, VideoGrants


def create_room_token(*, api_key: str, api_secret: str, public_url: str) -> dict[str, str]:
    room = f"meridian-{uuid4().hex[:12]}"
    identity = f"guest-{uuid4().hex[:8]}"
    token = (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )
    return {"token": token, "url": public_url, "room": room}
