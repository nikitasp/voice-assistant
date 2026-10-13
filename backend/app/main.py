from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import faq, health, livekit, property, unanswered, voices
from app.config import Settings, clear_settings_cache
from app.db import create_engine, create_session_factory
from app.seed.loader import seed_database
from app.services.embeddings import EmbeddingService
from app.services.faq_search import FaqService
from app.services.unanswered import UnansweredService
from app.services.voices import VoiceService

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def run_migrations(database_url: str) -> None:
    alembic_cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")


def create_app() -> FastAPI:
    clear_settings_cache()
    settings = Settings()

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    embedding_service = EmbeddingService(settings.embedding_model)
    faq_service = FaqService(embedding_service, settings.faq_search_threshold)
    unanswered_service = UnansweredService(
        faq_service,
        embedding_service,
        settings.unanswered_similarity_threshold,
    )
    voice_service = VoiceService(settings.tts_api_key, settings.tts_model)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Alembic's async env uses asyncio.run; run it off the request loop.
        await asyncio.to_thread(run_migrations, settings.database_url)
        await asyncio.to_thread(embedding_service.warm_up)
        await seed_database(session_factory, embedding_service)
        yield
        await engine.dispose()

    app = FastAPI(title="Meridian Voice Concierge API", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.embedding_service = embedding_service
    app.state.faq_service = faq_service
    app.state.unanswered_service = unanswered_service
    app.state.voice_service = voice_service

    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(faq.router)
    app.include_router(unanswered.router)
    app.include_router(livekit.router)
    app.include_router(voices.router)
    app.include_router(property.router)
    return app


app = create_app()
