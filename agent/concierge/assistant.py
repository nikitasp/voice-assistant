from __future__ import annotations

from pathlib import Path
from typing import Any

from livekit.agents import Agent, RunContext, function_tool

from concierge.backend_client import BackendClient

_PROMPT = Path(__file__).parent.joinpath("prompts/concierge.md").read_text(encoding="utf-8")

_RECORD_FAILED = (
    "Recording failed. Do not tell the guest that the question was noted. "
    "Apologize that you cannot look that up right now and offer the front desk at extension 0."
)


class Concierge(Agent):
    def __init__(self, property_info: str | None = None) -> None:
        instructions = _PROMPT
        if property_info:
            instructions += f"\n\n## Property information\n\n{property_info}\n"
        super().__init__(instructions=instructions)
        self._backend = BackendClient()

    @function_tool
    async def search_faq(self, context: RunContext, query: str) -> dict[str, Any]:
        """Search the Meridian FAQ knowledge base for an answer.

        Call this before answering any guest question that seeks information or a
        yes/no answer, including odd or off-topic questions. Skip only for
        greetings, thanks, and small talk. An empty result does not mean the
        question is unanswered: also check the property information in your
        instructions. If the result includes an error field, the knowledge base
        is unavailable — apologize and offer the front desk; do not invent facts.

        Args:
            query: The guest's question or a concise search phrase.
        """
        return await self._backend.search_faq(query)

    @function_tool
    async def record_unanswered(self, context: RunContext, question: str) -> str:
        """Record a guest question that neither search_faq nor the property information answers.

        Do not call this when the property information in your instructions answers
        the question, even if search_faq found nothing. Otherwise — including for
        off-topic questions — call it before apologizing or declining. If this tool
        reports a failure, do not claim the question was noted.

        Args:
            question: The guest's original question.
        """
        result = await self._backend.record_unanswered(question)
        if result.get("error"):
            return _RECORD_FAILED
        return "The question has been recorded for the concierge team."
