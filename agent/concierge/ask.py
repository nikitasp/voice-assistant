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
from concierge.backend_client import BackendClient
from concierge.models import build_llm


def _assistant_text(result: RunResult) -> str:
    return "\n".join(
        event.item.text_content or ""
        for event in result.events
        if isinstance(event, ChatMessageEvent) and event.item.role == "assistant"
    ).strip()


def _format_tool_calls(result: RunResult) -> list[str]:
    lines: list[str] = []
    for event in result.events:
        if not isinstance(event, FunctionCallEvent):
            continue
        name = event.item.name
        arguments = event.item.arguments or ""
        lines.append(f"{name}({arguments})" if arguments else name)
    return lines


def _load_questions(args: argparse.Namespace) -> list[str]:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines() if line.strip()]
    if args.question:
        return [args.question]
    raise SystemExit("Provide a question or --file")


async def _ask(question: str, property_info: str | None) -> None:
    async with build_llm() as model:
        async with AgentSession(llm=model) as session:
            await session.start(Concierge(property_info=property_info))
            result = await session.run(user_input=question)

    print(question)
    for line in _format_tool_calls(result):
        print(line)
    reply = _assistant_text(result)
    if reply:
        print(reply)
    print()


async def _main(questions: list[str]) -> None:
    try:
        property_info: str | None = await BackendClient().get_property_info()
    except Exception as exc:
        print(f"warning: could not fetch property information: {exc}", file=sys.stderr)
        property_info = None
    for question in questions:
        await _ask(question, property_info)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ask the Meridian concierge in text mode")
    parser.add_argument("question", nargs="?", help="A single guest question")
    parser.add_argument("--file", "-f", help="Path to a file with one question per line")
    args = parser.parse_args(argv)
    questions = _load_questions(args)
    asyncio.run(_main(questions))


if __name__ == "__main__":
    main(sys.argv[1:])
