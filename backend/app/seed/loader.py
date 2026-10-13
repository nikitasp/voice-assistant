from __future__ import annotations

import json
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.faq import FaqItem
from app.models.settings import AppSetting
from app.models.voice import Voice
from app.services.embeddings import EmbeddingService
from app.services.voices import ACTIVE_VOICE_KEY, SEED_VOICES

SEED_PATH = Path(__file__).with_name("faq.yaml")
# Tracks which seed slugs have been applied. Missing DB rows for an applied slug
# mean the admin deleted them — do not recreate (AP-4). New YAML slugs still insert.
FAQ_SEED_SLUGS_KEY = "faq_seed_slugs"


def load_faq_seed() -> list[dict[str, str]]:
    with SEED_PATH.open() as handle:
        data = yaml.safe_load(handle)
    return list(data["items"])


async def seed_database(
    session_factory: async_sessionmaker[AsyncSession],
    embeddings: EmbeddingService,
) -> None:
    items = load_faq_seed()
    async with session_factory() as session:
        await _upsert_faq_items(session, embeddings, items)
        await _upsert_voices(session)
        await session.commit()


def _load_applied_slugs(setting: AppSetting | None) -> set[str]:
    if setting is None or not setting.value.strip():
        return set()
    try:
        raw = json.loads(setting.value)
        if isinstance(raw, list):
            return {str(item) for item in raw}
    except json.JSONDecodeError:
        pass
    return {part.strip() for part in setting.value.split(",") if part.strip()}


async def _upsert_faq_items(
    session: AsyncSession,
    embeddings: EmbeddingService,
    items: list[dict[str, str]],
) -> None:
    existing_rows = (await session.execute(select(FaqItem))).scalars().all()
    by_slug = {row.slug: row for row in existing_rows}
    seed_setting = await session.get(AppSetting, FAQ_SEED_SLUGS_KEY)
    applied = _load_applied_slugs(seed_setting)
    # Empty DB + no tracking row: first bootstrap. Existing DBs without the tracking
    # row keep current content and only fill missing seed slugs / embeddings.
    bootstrap = seed_setting is None and not by_slug
    if seed_setting is None and by_slug:
        applied = set(by_slug.keys())

    pending: list[tuple[dict[str, str], FaqItem | None]] = []
    for item in items:
        slug = item["slug"]
        current = by_slug.get(slug)
        if current is None:
            # Insert on first bootstrap, or when the seed file gains a brand-new slug.
            # Skip when the slug was applied before and the admin deleted the row.
            if bootstrap or slug not in applied:
                pending.append((item, None))
            continue

        if current.embedding is None:
            pending.append((item, current))
            continue

        # First bootstrap only: sync seed YAML into the empty database.
        # Later startups leave admin question/answer/category edits alone (AP-3).
        if bootstrap:
            changed = (
                current.category != item["category"]
                or current.question != item["question"]
                or current.answer != item["answer"]
            )
            if changed:
                pending.append((item, current))

    if pending:
        texts = [f"{item['question']}\n{item['answer']}" for item, _ in pending]
        vectors = await embeddings.embed_texts(texts)
        for (item, current), vector in zip(pending, vectors, strict=True):
            if current is None:
                session.add(
                    FaqItem(
                        slug=item["slug"],
                        category=item["category"],
                        question=item["question"],
                        answer=item["answer"],
                        embedding=vector,
                    )
                )
            elif not bootstrap and current.embedding is None:
                current.embedding = vector
            else:
                current.category = item["category"]
                current.question = item["question"]
                current.answer = item["answer"]
                current.embedding = vector

    # Remember every slug from the seed file so future deletes are not recreated,
    # while brand-new seed entries (not yet in this set) still get inserted.
    next_applied = sorted(applied | {item["slug"] for item in items})
    payload = json.dumps(next_applied)
    if seed_setting is None:
        session.add(AppSetting(key=FAQ_SEED_SLUGS_KEY, value=payload))
    elif seed_setting.value != payload:
        seed_setting.value = payload


async def _upsert_voices(session: AsyncSession) -> None:
    existing = (await session.execute(select(Voice))).scalars().all()
    by_name = {voice.name: voice for voice in existing}

    for seed in SEED_VOICES:
        voice = by_name.get(seed["name"])
        if voice is None:
            voice = Voice(
                name=seed["name"],
                description=seed["description"],
                provider_voice_id=seed["provider_voice_id"],
            )
            session.add(voice)
            await session.flush()
            by_name[seed["name"]] = voice
        else:
            voice.description = seed["description"]
            voice.provider_voice_id = seed["provider_voice_id"]

    active = await session.get(AppSetting, ACTIVE_VOICE_KEY)
    if active is None:
        default_voice = by_name["James"]
        session.add(AppSetting(key=ACTIVE_VOICE_KEY, value=default_voice.id))
