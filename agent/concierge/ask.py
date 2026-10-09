"""Text-mode CLI for the concierge (TC-5).

Usage:
  python -m concierge.ask "Is the poker room open right now?"
  python -m concierge.ask --file questions.txt
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from livekit.agents import AgentSession
from livekit.agents.voice.run_result import ChatMessageEvent, FunctionCallEvent, RunResult

from concierge.assistant import Concierge
from concierge.models import build_llm


def _assistant_text(result: RunResult) -> str:
    return "\n".join(
        event.item.text_content or ""
        for event in result.events
        if isinstance(event, ChatMessageEvent) and event.item.role == "assistant"
    ).strip()


def _tool_names(result: RunResult) -> list[str]:
    return [event.item.name for event in result.events if isinstance(event, FunctionCallEvent)]


def _load_questions(args: argparse.Namespace) -> list[str]:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines() if line.strip()]
    if args.question:
        return [args.question]
    raise SystemExit("Provide a question or --file")


async def _ask(question: str) -> None:
    async with build_llm() as model:
        async with AgentSession(llm=model) as session:
            await session.start(Concierge())
            result = await session.run(user_input=question)

    print(question)
    for name in _tool_names(result):
        print(name)
    reply = _assistant_text(result)
    if reply:
        print(reply)
    print()


async def _main(questions: list[str]) -> None:
    for question in questions:
        await _ask(question)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ask the Meridian concierge in text mode")
    parser.add_argument("question", nargs="?", help="A single guest question")
    parser.add_argument("--file", "-f", help="Path to a file with one question per line")
    args = parser.parse_args(argv)
    questions = _load_questions(args)
    asyncio.run(_main(questions))


if __name__ == "__main__":
    main(sys.argv[1:])
