# 04 — FAQ search API

**Requirements:** API-1, API-3, KB-2
**Depends on:** 03

## Goal

Expose an endpoint that finds the best FAQ answer for a natural-language question.

## Scope

- `POST /api/faq/search` with body `{ "query": "..." }`.
- Response contains either the best match(es) with a relevance score, or an explicit no-match indicator, e.g.:
  - `{ "found": true, "results": [{ "id", "question", "answer", "score" }] }`
  - `{ "found": false, "results": [] }`
- Natural-language matching, not keyword-only (e.g. embeddings + cosine similarity, optionally hybrid with full-text search).
- Configurable relevance threshold that decides between match and no-match.

## Acceptance criteria

- [ ] "Is the poker room open right now?" returns the Poker Room item.
- [ ] Paraphrases with no shared keywords still match (e.g. "where can I get a massage" → Meridian Spa).
- [ ] "Can I bring my dog?" returns no match.
- [ ] Endpoint is documented in OpenAPI (`/docs`).
- [ ] Unit/integration tests cover match and no-match cases.
