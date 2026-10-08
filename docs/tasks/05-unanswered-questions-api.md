# 05 — Unanswered questions API

**Requirements:** API-2, KB-3, KB-4
**Depends on:** 02

## Goal

Let the voice agent record questions it could not answer.

## Scope

- `POST /api/unanswered` with body `{ "question": "..." }`.
- If an equivalent open question already exists (same normalized text, or semantically near-identical), increment its frequency and update `last_asked_at`; otherwise create a new record.
- Response returns the stored record (id, frequency).

## Acceptance criteria

- [ ] New question creates a record with timestamp and frequency `1`.
- [ ] Asking the same question again increments frequency instead of duplicating.
- [ ] Endpoint is documented in OpenAPI.
- [ ] Tests cover create and increment paths.
