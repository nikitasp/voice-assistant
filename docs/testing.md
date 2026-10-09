# Testing

Acceptance tests are written before the implementation. They fail until the code exists; a task is done when the tests for its requirements pass.

## Test suites

| Suite | Location | Needs | What it checks |
| --- | --- | --- | --- |
| Backend API | `backend/tests/` | Postgres + pgvector (`TEST_DATABASE_URL`) | Seeding, FAQ search/CRUD, unanswered record/queue, voices, LiveKit tokens |
| Agent behaviour | `agent/tests/test_concierge_behaviour.py` | `LLM_API_KEY` | Concierge replies in text mode with mocked knowledge-base tools |
| Agent end-to-end (`e2e`) | `agent/tests/test_scenarios_e2e.py`, `test_ask_cli.py` | `LLM_API_KEY` + running, seeded backend (`BACKEND_URL`) | PRD example conversations and the `concierge.ask` CLI |

Agent tests run the concierge in a text-only `AgentSession` (no STT, TTS or VAD) and use LiveKit's test helpers: `session.run(user_input=...)`, `result.expect...`, `mock_tools`, and `judge(llm, intent=...)` — an LLM checks that the reply has the intended meaning.

## Adding a question to check

- Search should find a specific FAQ: add it to `backend/tests/data/search_cases.yaml` under `match`.
- Search should find nothing: add it under `no_match`.
- Full conversation (tool calls + meaning of the reply): add a scenario to `agent/tests/data/scenarios.yaml`.
- Quick manual check: `python -m concierge.ask "your question"` (TC-5).

## Running

```bash
# Database for backend tests (separate from the dev database)
docker compose up -d db
docker compose exec db createdb -U meridian meridian_test

cd backend
TEST_DATABASE_URL=postgresql+asyncpg://meridian:meridian@localhost:5432/meridian_test uv run pytest
uv run pytest -m "not perf"            # skip latency checks

cd ../agent
LLM_API_KEY=... uv run pytest -m "not e2e"                     # mocked tools only
LLM_API_KEY=... BACKEND_URL=http://localhost:8000 uv run pytest  # all, with docker compose up
```

Test dependencies (dev group in each `pyproject.toml`):

- backend: `pytest`, `pytest-asyncio`, `httpx`, `asgi-lifespan`, `pyyaml`, `pyjwt`
- agent: `pytest`, `pytest-asyncio`, `httpx`, `pyyaml`

## Contracts the implementation must satisfy

These are the names and shapes the tests rely on.

### Backend

- `app.main.create_app()` builds a new FastAPI app, reading settings from the environment on each call. Its lifespan runs migrations and seeding.
- Table `faq_items` with a unique `slug`, `question`, `answer`. Seed slugs: `backend/tests/data/seed_slugs.yaml`.
- `GET /health` → `200`.
- `POST /api/faq/search` `{ "query": str }` → `{ "found": bool, "results": [{ "id", "slug", "question", "answer", "score": float }] }`, sorted by score descending; `results` is `[]` when `found` is false. Empty query → `422`.
- `POST /api/unanswered` `{ "question": str }` → `200`/`201` with `{ "id", "question", "frequency", "first_asked_at", "last_asked_at", "status" }`. Timestamps are ISO 8601 with time zone. Questions differing only in case, surrounding whitespace or trailing punctuation are the same record. Semantically near-identical paraphrases of an open question also increment that record. Empty question → `422`.
- `GET /api/faq` → list of FAQ items; optional `category` and `q` filters.
- `POST /api/faq` / `PUT /api/faq/{id}` / `DELETE /api/faq/{id}` → CRUD; create/update recompute embeddings so search reflects changes immediately.
- `GET /api/unanswered?status=open` → open queue sorted by frequency desc, then `last_asked_at` desc.
- `POST /api/unanswered/{id}/convert` `{ category, question, answer, slug? }` → creates FAQ, status `converted`.
- `POST /api/unanswered/{id}/dismiss` → status `dismissed`.
- `GET /api/voices` → four seeded voices with `active` flag; `PUT /api/voices/active` `{ "voice_id" }`; `GET /api/voices/{id}/preview` → WAV audio on success (cached only after a successful TTS generate); `503` when TTS is unavailable (failure is not cached).
- `POST /api/livekit/token` `{}` → `{ "token", "url", "room" }`; a new room per call; `url` is `LIVEKIT_PUBLIC_URL`.

### Agent

- `concierge.assistant.Concierge` — `Agent` subclass, constructed with no arguments, with function tools `search_faq(query)` and `record_unanswered(question)`. It does not speak in `on_enter`; the greeting is triggered by the worker entrypoint.
- `concierge.models.build_llm()` returns the configured `llm.LLM`.
- The backend URL comes from the `BACKEND_URL` environment variable.
- `python -m concierge.ask "question"` and `python -m concierge.ask --file path` print, for each question, the question, the tool calls (name and arguments) and the reply; exit code `0`.

## Requirement coverage

| Requirement | Tests |
| --- | --- |
| VC-2 natural language | `test_scenarios_e2e`, `test_concierge_behaviour` |
| VC-3 searches knowledge base | `test_property_question_searches_knowledge_base`, scenario `tools` |
| VC-4 answers when found | `test_answer_uses_facts_from_search_result`, `test_answer_includes_relevant_details`, scenarios |
| VC-5 graceful no-answer | `test_unknown_question_is_recorded_and_apologized`, scenario `prd-3-pets` |
| VC-6, NF-4 tone | `test_tone_is_warm_and_professional`, `assert_speakable` in every agent test |
| KB-1, KB-5 seeded content | `test_seed.py` |
| KB-2 semantic matching | `test_faq_search.py::test_question_finds_expected_faq` |
| KB-3, KB-4 timestamp, frequency | `test_unanswered.py` |
| API-1, API-3 search endpoint | `test_faq_search.py` |
| API-2 record endpoint | `test_unanswered.py` |
| PG-1, PG-5 playground session | `test_livekit_token.py` |
| NF-1 prompt responses | `test_search_is_fast` (`perf`) |
| NF-2 automatic seeding | `test_seeding_is_idempotent` |
| NF-5 new session per conversation | `test_each_conversation_gets_a_new_room` |
| TC-4 text-only session | every agent test (`session` fixture) |
| TC-5 CLI | `test_ask_cli.py` |
| Agent robustness (task 07) | `test_backend_failure_gives_polite_fallback` |
| AP-1–AP-4 FAQ management | `test_faq_crud.py` |
| AP-5–AP-8 unanswered queue | `test_unanswered_queue.py` |
| VX-1, VX-3, NF-5 voices | `test_voices.py` |

Not covered by automated tests yet: PG-2–PG-4 and TC-1–TC-2 (browser UI), and admin UI wiring (AP-9–AP-16) beyond the HTTP contracts above.
