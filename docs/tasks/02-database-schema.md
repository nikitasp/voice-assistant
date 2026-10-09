# 02 — Database schema

**Requirements:** KB-1, KB-3, KB-4
**Depends on:** 01

## Goal

Persist FAQ items and unanswered questions.

## Scope

- Choose a database (e.g. PostgreSQL, optionally with `pgvector` if semantic search is done in the DB) and document the choice.
- Tables / models:
  - `faq_items`: id, slug (unique, stable key such as `poker-room`), category, question, answer, created_at, updated_at, plus whatever the search approach needs (e.g. embedding vector).
  - `unanswered_questions`: id, question text, normalized text (for grouping), frequency count, first_asked_at, last_asked_at, status (`open`, `converted`, `dismissed`).
- Migrations (e.g. Alembic) applied automatically on startup or via a documented command.

## Acceptance criteria

- [ ] Schema is created from migrations on a fresh database.
- [ ] Unanswered questions store a timestamp (KB-3) and a frequency count (KB-4).
- [ ] The `status` field supports the bonus convert/dismiss flow without schema changes later.
