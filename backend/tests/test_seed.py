"""KB-1, KB-5, NF-2: the knowledge base is seeded automatically with all property information."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from .support import load_data

pytestmark = pytest.mark.asyncio

SEED = load_data("seed_slugs.yaml")
EXPECTED_SLUGS = {slug for slugs in SEED["topics"].values() for slug in slugs}


async def fetch_faq_rows(database_url: str) -> dict[str, tuple[str, str]]:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as conn:
            rows = (await conn.execute(text("SELECT slug, question, answer FROM faq_items"))).all()
    finally:
        await engine.dispose()
    return {row.slug: (row.question, row.answer) for row in rows}


async def test_every_property_topic_is_seeded(client, database_url):
    rows = await fetch_faq_rows(database_url)

    missing = EXPECTED_SLUGS - rows.keys()
    assert not missing, f"FAQ items missing from seed: {sorted(missing)}"


async def test_seeded_items_have_question_and_answer(client, database_url):
    rows = await fetch_faq_rows(database_url)

    empty = [slug for slug, (question, answer) in rows.items() if not question.strip() or not answer.strip()]
    assert not empty, f"FAQ items with empty question or answer: {empty}"


@pytest.mark.parametrize("slug,facts", SEED["facts"].items())
async def test_seeded_answers_keep_prd_facts(client, database_url, slug, facts):
    rows = await fetch_faq_rows(database_url)

    _, answer = rows[slug]
    for fact in facts:
        assert fact in answer, f"{slug}: expected '{fact}' in answer: {answer!r}"


async def test_seeding_is_idempotent(running_app, database_url):
    async with running_app():
        pass
    first = await fetch_faq_rows(database_url)

    async with running_app():
        pass
    second = await fetch_faq_rows(database_url)

    assert len(second) == len(first)
