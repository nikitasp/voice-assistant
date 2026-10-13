from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unanswered import UnansweredQuestion
from app.schemas.unanswered import UnansweredConvertRequest, UnansweredOut
from app.services.embeddings import EmbeddingService
from app.services.faq_search import FaqService

_TRAILING_PUNCT = re.compile(r"[\s\?\.\!\,\;\:]+$")
_TOKEN = re.compile(r"[a-z0-9]+")
# Hex/UUID-like markers that must match when present (keeps laundry-floor-UUID rows distinct).
_IDENTIFIER = re.compile(r"[a-f0-9]{6,}")
NORMALIZED_MAX_LEN = 512
# Lexical overlap required in addition to embedding similarity for paraphrase merges.
DEFAULT_TOKEN_OVERLAP = 0.45


def normalize_question(question: str) -> str:
    normalized = question.strip().lower()
    normalized = _TRAILING_PUNCT.sub("", normalized).strip()
    return normalized[:NORMALIZED_MAX_LEN]


def _content_tokens(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text.lower()) if len(token) >= 3}


def _identifiers(text: str) -> set[str]:
    return set(_IDENTIFIER.findall(text.lower()))


def is_near_paraphrase(
    left: str,
    right: str,
    *,
    min_token_overlap: float = DEFAULT_TOKEN_OVERLAP,
) -> bool:
    """True when texts are paraphrases of the same question, not merely the same topic."""
    left_tokens = _content_tokens(left)
    right_tokens = _content_tokens(right)
    if not left_tokens or not right_tokens:
        return False

    overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    if overlap < min_token_overlap:
        return False

    left_ids = _identifiers(left)
    right_ids = _identifiers(right)
    if left_ids or right_ids:
        return left_ids == right_ids
    return True


class UnansweredService:
    def __init__(
        self,
        faq_service: FaqService,
        embeddings: EmbeddingService,
        similarity_threshold: float,
        *,
        min_token_overlap: float = DEFAULT_TOKEN_OVERLAP,
    ) -> None:
        self._faq_service = faq_service
        self._embeddings = embeddings
        self._similarity_threshold = similarity_threshold
        self._min_token_overlap = min_token_overlap

    async def record(self, session: AsyncSession, question: str) -> tuple[UnansweredOut, bool]:
        normalized = normalize_question(question)
        if not normalized:
            raise ValueError("question must not be empty")

        now = datetime.now(UTC)
        existing = await self._find_open_by_normalized(session, normalized)
        if existing is not None:
            vector = None
            if existing.embedding is None:
                vector = await self._embeddings.embed_query(question.strip())
            return await self._increment(session, existing.id, now, vector=vector), False

        vector = await self._embeddings.embed_query(question.strip())
        near = await self._find_open_near(session, vector, question.strip())
        if near is not None:
            return await self._increment(session, near.id, now, vector=vector), False

        row = UnansweredQuestion(
            question=question.strip(),
            normalized_text=normalized,
            frequency=1,
            first_asked_at=now,
            last_asked_at=now,
            status="open",
            embedding=vector,
        )
        session.add(row)
        try:
            await session.commit()
        except IntegrityError:
            # Another request inserted the same open question concurrently.
            await session.rollback()
            existing = await self._find_open_by_normalized(session, normalized)
            if existing is None:
                raise
            return await self._increment(session, existing.id, datetime.now(UTC), vector=vector), False

        await session.refresh(row)
        return UnansweredOut.model_validate(row), True

    async def _find_open_by_normalized(
        self,
        session: AsyncSession,
        normalized: str,
    ) -> UnansweredQuestion | None:
        stmt = select(UnansweredQuestion).where(
            UnansweredQuestion.normalized_text == normalized,
            UnansweredQuestion.status == "open",
        )
        return await session.scalar(stmt)

    async def _find_open_near(
        self,
        session: AsyncSession,
        vector: list[float],
        question: str,
    ) -> UnansweredQuestion | None:
        distance = UnansweredQuestion.embedding.cosine_distance(vector)
        stmt = (
            select(UnansweredQuestion)
            .where(UnansweredQuestion.status == "open")
            .where(UnansweredQuestion.embedding.is_not(None))
            .where(distance < (1 - self._similarity_threshold))
            .order_by(distance.asc())
            .limit(5)
        )
        candidates = (await session.execute(stmt)).scalars().all()
        for candidate in candidates:
            if is_near_paraphrase(
                question,
                candidate.question,
                min_token_overlap=self._min_token_overlap,
            ):
                return candidate
        return None

    async def _increment(
        self,
        session: AsyncSession,
        row_id: str,
        now: datetime,
        *,
        vector: list[float] | None = None,
    ) -> UnansweredOut:
        # Atomic frequency bump so concurrent records cannot overwrite each other.
        stmt = (
            update(UnansweredQuestion)
            .where(UnansweredQuestion.id == row_id)
            .values(
                frequency=UnansweredQuestion.frequency + 1,
                last_asked_at=now,
            )
            .returning(UnansweredQuestion)
        )
        row = (await session.execute(stmt)).scalar_one()
        if vector is not None and row.embedding is None:
            row.embedding = vector
        await session.commit()
        await session.refresh(row)
        return UnansweredOut.model_validate(row)

    async def list_by_status(self, session: AsyncSession, status: str) -> list[UnansweredOut]:
        stmt = (
            select(UnansweredQuestion)
            .where(UnansweredQuestion.status == status)
            .order_by(
                UnansweredQuestion.frequency.desc(),
                UnansweredQuestion.last_asked_at.desc(),
            )
        )
        rows = (await session.execute(stmt)).scalars().all()
        return [UnansweredOut.model_validate(row) for row in rows]

    async def convert(
        self,
        session: AsyncSession,
        item_id: str,
        payload: UnansweredConvertRequest,
    ) -> UnansweredOut:
        row = await session.get(UnansweredQuestion, item_id)
        if row is None:
            raise LookupError("Unanswered question not found")
        if row.status != "open":
            raise ValueError("Only open questions can be converted")

        await self._faq_service.create_from_unanswered(
            session,
            category=payload.category,
            question=payload.question,
            answer=payload.answer,
            slug=payload.slug,
        )
        row.status = "converted"
        await session.commit()
        await session.refresh(row)
        return UnansweredOut.model_validate(row)

    async def dismiss(self, session: AsyncSession, item_id: str) -> UnansweredOut:
        row = await session.get(UnansweredQuestion, item_id)
        if row is None:
            raise LookupError("Unanswered question not found")
        if row.status != "open":
            raise ValueError("Only open questions can be dismissed")

        row.status = "dismissed"
        await session.commit()
        await session.refresh(row)
        return UnansweredOut.model_validate(row)
