import os
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from livekit.agents import AgentSession, llm


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: needs a running, seeded backend at BACKEND_URL")


@pytest_asyncio.fixture
async def model() -> AsyncIterator[llm.LLM]:
    """The concierge's LLM; also used as the judge for reply intent."""
    if not os.environ.get("LLM_API_KEY"):
        pytest.fail("LLM_API_KEY is not set — see docs/testing.md")
    from concierge.models import build_llm

    async with build_llm() as instance:
        yield instance


@pytest_asyncio.fixture
async def session(model: llm.LLM) -> AsyncIterator[AgentSession]:
    """TC-4: text-only session — LLM only, no STT, TTS or VAD."""
    from concierge.assistant import Concierge

    async with AgentSession(llm=model) as agent_session:
        await agent_session.start(Concierge())
        yield agent_session


@pytest.fixture
def backend_url(monkeypatch: pytest.MonkeyPatch) -> str:
    """Request before `session` so the agent and `concierge.ask` subprocesses use the same backend."""
    url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    try:
        httpx.get(f"{url}/health", timeout=2).raise_for_status()
    except httpx.HTTPError as exc:
        pytest.fail(f"backend not reachable at {url}: {exc}")
    monkeypatch.setenv("BACKEND_URL", url)
    return url
