import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml
from livekit.agents.voice.run_result import ChatMessageEvent, FunctionCallEvent, RunResult

DATA_DIR = Path(__file__).parent / "data"

MARKDOWN = re.compile(r"\*\*|__|`|^\s*#|^\s*[-*•]\s|^\s*\d+\.\s", re.MULTILINE)
EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f]")


def load_data(name: str) -> Any:
    with (DATA_DIR / name).open() as f:
        return yaml.safe_load(f)


def assistant_text(result: RunResult) -> str:
    return "\n".join(
        event.item.text_content or ""
        for event in result.events
        if isinstance(event, ChatMessageEvent) and event.item.role == "assistant"
    )


def tool_calls(result: RunResult) -> list[str]:
    return [event.item.name for event in result.events if isinstance(event, FunctionCallEvent)]


def assert_speakable(result: RunResult) -> None:
    """NF-4: spoken output has no markdown or emoji."""
    text = assistant_text(result)
    assert text.strip(), "concierge gave no reply"
    assert not MARKDOWN.search(text), f"markdown in reply: {text!r}"
    assert not EMOJI.search(text), f"emoji in reply: {text!r}"


def faq(slug: str, question: str, answer: str, score: float = 0.9) -> dict:
    return {"slug": slug, "question": question, "answer": answer, "score": score}


def search_returning(*items: dict) -> Callable[[str], dict]:
    """Mock for the search_faq tool; mirrors the POST /api/faq/search response."""

    def search_faq(query: str) -> dict:
        return {"found": bool(items), "results": list(items)}

    return search_faq


class UnansweredRecorder:
    """Mock for the record_unanswered tool that remembers what was recorded.

    Signature must match the real tool (context, question) so livekit's mock_tools
    bind can pass the question through — a single `question` param would swallow
    RunContext instead.
    """

    def __init__(self) -> None:
        self.questions: list[str] = []

    def __call__(self, context: Any = None, question: str = "") -> str:
        self.questions.append(question)
        return "The question has been recorded for the concierge team."


def backend_down(*_args: Any, **_kwargs: Any) -> Any:
    raise RuntimeError("backend unavailable")
