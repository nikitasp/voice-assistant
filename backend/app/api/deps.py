from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.services.embeddings import EmbeddingService
from app.services.faq_search import FaqService
from app.services.unanswered import UnansweredService
from app.services.voices import VoiceService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


async def get_session(
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service


def get_faq_service(request: Request) -> FaqService:
    return request.app.state.faq_service


def get_unanswered_service(request: Request) -> UnansweredService:
    return request.app.state.unanswered_service


def get_voice_service(request: Request) -> VoiceService:
    return request.app.state.voice_service


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
FaqServiceDep = Annotated[FaqService, Depends(get_faq_service)]
UnansweredServiceDep = Annotated[UnansweredService, Depends(get_unanswered_service)]
VoiceServiceDep = Annotated[VoiceService, Depends(get_voice_service)]
