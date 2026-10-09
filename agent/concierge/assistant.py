from __future__ import annotations

from pathlib import Path
from typing import Any

from livekit.agents import Agent, RunContext, function_tool

from concierge.backend_client import BackendClient

_PROMPT = Path(__file__).parent.joinpath("prompts/concierge.md").read_text(encoding="utf-8")


class Concierge(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=_PROMPT)
        self._backend = BackendClient()

    @function_tool
    async def search_faq(self, context: RunContext, query: str) -> dict[str, Any]:
        """Search the Meridian property knowledge base for an answer.

        Always call this before answering questions about the property, amenities,
        dining, gaming, rooms, events, or partner offers.

        Args:
            query: The guest's question or a concise search phrase.
        """
        return await self._backend.search_faq(query)

    @function_tool
    async def record_unanswered(self, context: RunContext, question: str) -> str:
        """Record a guest question that the knowledge base could not answer.

        Call this after search_faq returns no useful match.

        Args:
            question: The guest's original question.
        """
        await self._backend.record_unanswered(question)
        return "The question has been recorded for the concierge team."
