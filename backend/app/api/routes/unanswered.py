from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.deps import SessionDep, UnansweredServiceDep
from app.schemas.unanswered import (
    UnansweredConvertRequest,
    UnansweredCreate,
    UnansweredOut,
)

router = APIRouter(prefix="/api/unanswered", tags=["unanswered"])


@router.post("", response_model=UnansweredOut)
async def record_unanswered(
    payload: UnansweredCreate,
    session: SessionDep,
    unanswered_service: UnansweredServiceDep,
    response: Response,
) -> UnansweredOut:
    try:
        body, created = await unanswered_service.record(session, payload.question)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return body


@router.get("", response_model=list[UnansweredOut])
async def list_unanswered(
    session: SessionDep,
    unanswered_service: UnansweredServiceDep,
    status_filter: str = Query(default="open", alias="status"),
) -> list[UnansweredOut]:
    if status_filter not in {"open", "converted", "dismissed"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")
    return await unanswered_service.list_by_status(session, status_filter)


@router.post("/{item_id}/convert", response_model=UnansweredOut)
async def convert_unanswered(
    item_id: str,
    payload: UnansweredConvertRequest,
    session: SessionDep,
    unanswered_service: UnansweredServiceDep,
) -> UnansweredOut:
    try:
        return await unanswered_service.convert(session, item_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/{item_id}/dismiss", response_model=UnansweredOut)
async def dismiss_unanswered(
    item_id: str,
    session: SessionDep,
    unanswered_service: UnansweredServiceDep,
) -> UnansweredOut:
    try:
        return await unanswered_service.dismiss(session, item_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
