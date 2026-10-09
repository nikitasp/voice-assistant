import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager

from .support import TEST_LIVEKIT_ENV

# Startup runs migrations and seeding, which may download an embedding model.
STARTUP_TIMEOUT_S = 180


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "perf: latency checks (NF-1)")


@pytest.fixture
def database_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail("TEST_DATABASE_URL is not set — see docs/testing.md")
    return url


@pytest.fixture
def app_env(database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    for key, value in TEST_LIVEKIT_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def running_app(app_env: None):
    """Factory: start a fresh app instance (lifespan included) and yield an HTTP client."""

    @asynccontextmanager
    async def _start() -> AsyncIterator[httpx.AsyncClient]:
        from app.main import create_app

        app = create_app()
        async with LifespanManager(app, startup_timeout=STARTUP_TIMEOUT_S):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    return _start


@pytest_asyncio.fixture
async def client(running_app) -> AsyncIterator[httpx.AsyncClient]:
    async with running_app() as c:
        yield c
