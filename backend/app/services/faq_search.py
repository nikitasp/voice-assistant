from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, delete, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faq import FaqItem
from app.schemas.faq import (
    FaqCreate,
    FaqItemOut,
    FaqSearchResponse,
    FaqSearchResult,
    FaqUpdate,
)
from app.services.embeddings import EmbeddingService


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:120] or str(uuid.uuid4())


class FaqService:
    def __init__(self, embeddings: EmbeddingService, threshold: float) -> None:
        self._embeddings = embeddings
        self._threshold = threshold

    async def search(self, session: AsyncSession, query: str) -> FaqSearchResponse:
        query_vector = await self._embeddings.embed_query(query.strip())
        distance = FaqItem.embedding.cosine_distance(query_vector)
        score_expr = (1 - distance).label("score")
        stmt = (
            select(FaqItem, score_expr)
            .where(FaqItem.embedding.is_not(None))
            .where(distance < (1 - self._threshold))
            .order_by(distance.asc())
            .limit(10)
        )
        rows = (await session.execute(stmt)).all()
        results = [
            FaqSearchResult(
                id=item.id,
                slug=item.slug,
                question=item.question,
                answer=item.answer,
                score=float(score),
            )
            for item, score in rows
        ]
        return FaqSearchResponse(found=bool(results), results=results)

    async def list_items(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        q: str | None = None,
    ) -> list[FaqItemOut]:
        stmt: Select[tuple[FaqItem]] = select(FaqItem).order_by(FaqItem.category, FaqItem.slug)
        if category:
            stmt = stmt.where(FaqItem.category == category)
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(FaqItem.question.ilike(pattern), FaqItem.answer.ilike(pattern), FaqItem.slug.ilike(pattern))
            )
        items = (await session.execute(stmt)).scalars().all()
        return [FaqItemOut.model_validate(item) for item in items]

    async def create(self, session: AsyncSession, payload: FaqCreate) -> FaqItemOut:
        embedding = await self._embeddings.embed_query(f"{payload.question}\n{payload.answer}")
        item = FaqItem(
            slug=payload.slug,
            category=payload.category,
            question=payload.question,
            answer=payload.answer,
            embedding=embedding,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return FaqItemOut.model_validate(item)

    async def update(self, session: AsyncSession, item_id: str, payload: FaqUpdate) -> FaqItemOut:
        item = await session.get(FaqItem, item_id)
        if item is None:
            raise LookupError("FAQ item not found")

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(item, key, value)

        if "question" in data or "answer" in data:
            item.embedding = await self._embeddings.embed_query(f"{item.question}\n{item.answer}")
        item.updated_at = datetime.now(UTC)

        await session.commit()
        await session.refresh(item)
        return FaqItemOut.model_validate(item)

    async def delete(self, session: AsyncSession, item_id: str) -> None:
        result = await session.execute(delete(FaqItem).where(FaqItem.id == item_id))
        if result.rowcount == 0:
            raise LookupError("FAQ item not found")
        await session.commit()

    async def create_from_unanswered(
        self,
        session: AsyncSession,
        *,
        category: str,
        question: str,
        answer: str,
        slug: str | None = None,
    ) -> FaqItem:
        final_slug = slug or _slugify(question)
        existing = await session.scalar(select(FaqItem).where(FaqItem.slug == final_slug))
        if existing is not None:
            final_slug = f"{final_slug}-{uuid.uuid4().hex[:8]}"

        embedding = await self._embeddings.embed_query(f"{question}\n{answer}")
        item = FaqItem(
            slug=final_slug,
            category=category,
            question=question,
            answer=answer,
            embedding=embedding,
        )
        session.add(item)
        await session.flush()
        return item

    async def count(self, session: AsyncSession) -> int:
        return int(await session.scalar(select(func.count()).select_from(FaqItem)) or 0)

    async def ensure_vector_extension(self, session: AsyncSession) -> None:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
