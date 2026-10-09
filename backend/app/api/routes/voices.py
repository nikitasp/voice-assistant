from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import SessionDep, VoiceServiceDep
from app.schemas.voices import ActiveVoiceRequest, VoiceOut

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("", response_model=list[VoiceOut])
async def list_voices(session: SessionDep, voice_service: VoiceServiceDep) -> list[VoiceOut]:
    return await voice_service.list_voices(session)


@router.put("/active", response_model=list[VoiceOut])
async def set_active_voice(
    payload: ActiveVoiceRequest,
    session: SessionDep,
    voice_service: VoiceServiceDep,
) -> list[VoiceOut]:
    try:
        return await voice_service.set_active_voice(session, payload.voice_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{voice_id}/preview")
async def preview_voice(
    voice_id: str,
    session: SessionDep,
    voice_service: VoiceServiceDep,
) -> Response:
    try:
        audio, media_type = await voice_service.get_preview_audio(session, voice_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(content=audio, media_type=media_type)
