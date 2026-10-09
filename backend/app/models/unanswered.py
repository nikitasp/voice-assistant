from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.faq import EMBEDDING_DIM


class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"
    __table_args__ = (
        Index(
            "uq_unanswered_open_normalized_text",
            "normalized_text",
            unique=True,
            postgresql_where=text("status = 'open'"),
        ),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    first_asked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_asked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open", index=True)
    embedding = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
