from __future__ import annotations

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


async def _upsert_faq_items(
    session: AsyncSession,
    embeddings: EmbeddingService,
    items: list[dict[str, str]],
) -> None:
    existing_rows = (await session.execute(select(FaqItem))).scalars().all()
    by_slug = {row.slug: row for row in existing_rows}

    pending: list[tuple[dict[str, str], FaqItem | None]] = []
    for item in items:
        current = by_slug.get(item["slug"])
        if current is None:
            pending.append((item, None))
            continue
        changed = (
            current.category != item["category"]
            or current.question != item["question"]
            or current.answer != item["answer"]
            or current.embedding is None
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
            else:
                current.category = item["category"]
                current.question = item["question"]
                current.answer = item["answer"]
                current.embedding = vector


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
