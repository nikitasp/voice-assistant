from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import FaqServiceDep, SessionDep
from app.schemas.faq import (
    FaqCreate,
    FaqItemOut,
    FaqSearchRequest,
    FaqSearchResponse,
    FaqUpdate,
)

router = APIRouter(prefix="/api/faq", tags=["faq"])


@router.post("/search", response_model=FaqSearchResponse)
async def search_faq(
    payload: FaqSearchRequest,
    session: SessionDep,
    faq_service: FaqServiceDep,
) -> FaqSearchResponse:
    return await faq_service.search(session, payload.query)


@router.get("", response_model=list[FaqItemOut])
async def list_faq(
    session: SessionDep,
    faq_service: FaqServiceDep,
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[FaqItemOut]:
    return await faq_service.list_items(session, category=category, q=q)


@router.post("", response_model=FaqItemOut, status_code=status.HTTP_201_CREATED)
async def create_faq(
    payload: FaqCreate,
    session: SessionDep,
    faq_service: FaqServiceDep,
) -> FaqItemOut:
    try:
        return await faq_service.create(session, payload)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="FAQ slug already exists",
        ) from exc


@router.put("/{item_id}", response_model=FaqItemOut)
async def update_faq(
    item_id: str,
    payload: FaqUpdate,
    session: SessionDep,
    faq_service: FaqServiceDep,
) -> FaqItemOut:
    try:
        return await faq_service.update(session, item_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="FAQ slug already exists",
        ) from exc


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    item_id: str,
    session: SessionDep,
    faq_service: FaqServiceDep,
) -> None:
    try:
        await faq_service.delete(session, item_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
