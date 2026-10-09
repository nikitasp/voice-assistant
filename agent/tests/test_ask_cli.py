"""TC-5: command-line tool that runs questions through the agent in text mode."""

import subprocess
import sys

import pytest

pytestmark = pytest.mark.e2e


def run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "concierge.ask", *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_single_question_prints_reply_and_tool_calls(backend_url):
    completed = run_ask("Is the poker room open right now?")

    assert completed.returncode == 0, completed.stderr
    assert "search_faq" in completed.stdout
    assert "24" in completed.stdout


def test_questions_file_runs_each_question(backend_url, tmp_path):
    questions = tmp_path / "questions.txt"
    questions.write_text("What time is checkout?\nCan I bring my dog to the hotel?\n")

    completed = run_ask("--file", str(questions))

    assert completed.returncode == 0, completed.stderr
    assert "What time is checkout?" in completed.stdout
    assert "Can I bring my dog to the hotel?" in completed.stdout
    assert "record_unanswered" in completed.stdout
