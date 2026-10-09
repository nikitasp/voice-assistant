"""Initial schema for FAQ, unanswered questions, voices, and settings.

Revision ID: 001_initial
Revises:
Create Date: 2026-10-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "faq_items",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_faq_items_slug", "faq_items", ["slug"])
    op.create_index("ix_faq_items_category", "faq_items", ["category"])

    op.create_table(
        "unanswered_questions",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.String(length=512), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("first_asked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_asked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
    )
    op.create_index("ix_unanswered_questions_normalized_text", "unanswered_questions", ["normalized_text"])
    op.create_index("ix_unanswered_questions_status", "unanswered_questions", ["status"])
    op.create_index(
        "uq_unanswered_open_normalized_text",
        "unanswered_questions",
        ["normalized_text"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
    )

    op.create_table(
        "voices",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("provider_voice_id", sa.String(length=128), nullable=False),
        sa.Column("preview_audio", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_table("voices")
    op.drop_index(
        "uq_unanswered_open_normalized_text",
        table_name="unanswered_questions",
        postgresql_where=sa.text("status = 'open'"),
    )
    op.drop_index("ix_unanswered_questions_status", table_name="unanswered_questions")
    op.drop_index("ix_unanswered_questions_normalized_text", table_name="unanswered_questions")
    op.drop_table("unanswered_questions")
    op.drop_index("ix_faq_items_category", table_name="faq_items")
    op.drop_index("ix_faq_items_slug", table_name="faq_items")
    op.drop_table("faq_items")
