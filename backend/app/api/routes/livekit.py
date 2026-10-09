from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.livekit import LiveKitTokenResponse
from app.services.livekit_tokens import create_room_token

router = APIRouter(prefix="/api/livekit", tags=["livekit"])


@router.post("/token", response_model=LiveKitTokenResponse)
async def create_token(settings: SettingsDep) -> LiveKitTokenResponse:
    payload = create_room_token(
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
        public_url=settings.livekit_public_url,
    )
    return LiveKitTokenResponse(**payload)
