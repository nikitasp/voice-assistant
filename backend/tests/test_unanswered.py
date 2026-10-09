"""API-2, KB-3, KB-4: recording unanswered questions with timestamp and frequency."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


def unique_question() -> str:
    # Unique per test run so results do not depend on rows left by earlier runs.
    return f"Is there a laundry service on floor {uuid4().hex[:8]}?"


async def record(client, question: str) -> dict:
    response = await client.post("/api/unanswered", json={"question": question})
    assert response.status_code in (200, 201), response.text
    return response.json()


async def test_new_question_is_stored_with_timestamp(client):
    question = unique_question()

    body = await record(client, question)

    assert body["question"] == question
    assert body["frequency"] == 1
    assert body["status"] == "open"
    asked_at = datetime.fromisoformat(body["first_asked_at"])
    assert asked_at.tzinfo is not None
    assert abs(datetime.now(UTC) - asked_at) < timedelta(minutes=1)
    assert body["last_asked_at"] == body["first_asked_at"]


async def test_repeated_question_increments_frequency(client):
    question = unique_question()

    first = await record(client, question)
    second = await record(client, question)

    assert second["id"] == first["id"]
    assert second["frequency"] == 2
    assert datetime.fromisoformat(second["last_asked_at"]) >= datetime.fromisoformat(first["last_asked_at"])
    assert second["first_asked_at"] == first["first_asked_at"]


async def test_case_whitespace_and_punctuation_variants_are_grouped(client):
    question = unique_question()
    variants = [question, question.upper(), f"  {question}  ", question.rstrip("?")]

    bodies = [await record(client, v) for v in variants]

    assert len({b["id"] for b in bodies}) == 1
    assert bodies[-1]["frequency"] == len(variants)


async def test_different_questions_are_separate(client):
    first = await record(client, unique_question())
    second = await record(client, unique_question())

    assert first["id"] != second["id"]
    assert second["frequency"] == 1


@pytest.mark.parametrize(
    "payload",
    [{}, {"question": ""}, {"question": "   "}, {"question": "???"}, {"question": "..."}],
)
async def test_empty_question_is_rejected(client, payload):
    response = await client.post("/api/unanswered", json=payload)

    assert response.status_code == 422
