# Meridian Voice Concierge

Voice concierge for The Meridian Casino & Resort. Guests ask about the property by voice or text; the agent searches a seeded FAQ knowledge base and records questions it cannot answer.

| Document | Purpose |
| --- | --- |
| [`docs/requirements.md`](docs/requirements.md) | Product requirements (PRD) |
| [`docs/tasks/`](docs/tasks/) | Implementation work items |
| [`docs/project-structure.md`](docs/project-structure.md) | Repository layout |
| [`docs/technical-decisions.md`](docs/technical-decisions.md) | Architecture and implementer choices |
| [`docs/testing.md`](docs/testing.md) | Acceptance tests and contracts |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2
- Provider credentials (see `.env.example`):
  - LiveKit (`LIVEKIT_URL`, `LIVEKIT_PUBLIC_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`)
  - LLM (`LLM_API_KEY`)
  - Deepgram STT (`STT_API_KEY`)
  - Cartesia TTS (`TTS_API_KEY`)
- For running tests locally: [`uv`](https://docs.astral.sh/uv/) and a Postgres + pgvector database (the Compose `db` service is enough)

## Environment variables

Copy the example file and fill in secrets:

```bash
cp .env.example .env
```

| Variable | Used by | Notes |
| --- | --- | --- |
| `LIVEKIT_URL` | Agent | LiveKit WebSocket URL the worker joins |
| `LIVEKIT_PUBLIC_URL` | Backend → browser | URL returned in the playground token response |
| `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` | Backend, agent | Token minting and worker auth |
| `BACKEND_URL` | Agent (local / tests) | Compose sets `http://backend:8000` for the agent container |
| `LLM_API_KEY` | Agent, backend (optional) | OpenAI-compatible chat model |
| `LLM_BASE_URL` | Agent | Optional; omit for OpenAI. Use Groq / Ollama / other OpenAI-compatible APIs |
| `LLM_MODEL` | Agent | Chat model id (default `gpt-4.1-mini`; set a Groq/Ollama model when using those) |
| `STT_API_KEY` | Agent | Deepgram |
| `TTS_API_KEY` | Agent, backend previews | Cartesia |
| `DATABASE_URL` | Backend | Compose overrides host to `db` inside the stack |
| `POSTGRES_*` / `*_PORT` | Compose | Local ports and DB credentials |
| `FAQ_SEARCH_THRESHOLD` | Backend | Optional; default `0.42` (Compose passes through) |
| `UNANSWERED_SIMILARITY_THRESHOLD` | Backend | Optional; default `0.82` (Compose passes through) |
| `EMBEDDING_MODEL` | Backend | Optional; MiniLM by default (Compose passes through) |
| `CORS_ORIGINS` | Backend | Optional; for Vite dev (`localhost:5173`) |
| `VITE_API_BASE_URL` | Web | Optional API origin; empty = same-origin `/api` |

To use a local LiveKit server instead of Cloud, follow the comments in `.env.example` and start with:

```bash
docker compose --profile local-livekit up --build
```

## Run the stack

```bash
cp .env.example .env   # fill in credentials
docker compose up --build
```

Migrations and FAQ/voice seeding run automatically when the backend starts (NF-2).

| Service | URL |
| --- | --- |
| Web (playground + admin) | http://localhost:3000 |
| Backend OpenAPI docs | http://localhost:8000/docs |
| Backend health | http://localhost:8000/health |

## Try the playground

1. Open http://localhost:3000 and click **Start conversation** (allow the microphone).
2. Speak, or type in the text field and press **Send**.
3. End the session with **End conversation**.

Example questions from the PRD:

| Try asking… | Expected behaviour |
| --- | --- |
| “Is the poker room open right now?” | Answers from FAQ (24/7 poker room) |
| “What's your best restaurant?” | Recommends Aurelia |
| “Can I bring my dog to the hotel?” | Apologizes, notes the question, offers front desk |
| “Are there any good restaurants nearby?” | Mentions Carbone + room-key discount |

Admin routes (no auth — assessment scope):

| Path | Feature |
| --- | --- |
| `/admin/faqs` | FAQ CRUD |
| `/admin/unanswered` | Unanswered queue (convert / dismiss) |
| `/admin/voices` | Select and preview James / Sofia / Marcus / Elena |
| `/admin/health` | Service probes (env) + microphone / speaker tests |
| `/admin/playground` | Integrated **Test Mode** playground |

Changing a voice or FAQ applies to the **next** conversation without restarting services (NF-5).

### Text-only CLI (no microphone)

With the stack running:

```bash
cd agent
BACKEND_URL=http://localhost:8000 LLM_API_KEY=... \
  uv run python -m concierge.ask "Is the poker room open right now?"
```

Prints the question, each tool call (name + arguments), and the reply. Use `--file questions.txt` for a batch.

## API overview

Interactive docs: http://localhost:8000/docs

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness |
| `GET` | `/api/health/providers` | LLM/STT/TTS API key checks (no secrets returned) |
| `POST` | `/api/faq/search` | Semantic FAQ search (`{ "query": "..." }`) |
| `GET` | `/api/faq` | List FAQs (`?category=&q=`) |
| `POST` / `PUT` / `DELETE` | `/api/faq`, `/api/faq/{id}` | FAQ management |
| `POST` | `/api/unanswered` | Record an unanswered question |
| `GET` | `/api/unanswered?status=open` | Admin queue |
| `POST` | `/api/unanswered/{id}/convert` | Convert to FAQ |
| `POST` | `/api/unanswered/{id}/dismiss` | Dismiss |
| `POST` | `/api/livekit/token` | Playground room token |
| `GET` / `PUT` | `/api/voices`, `/api/voices/active` | List / set active voice |
| `GET` | `/api/voices/{id}/preview` | Short WAV sample |

The agent is the only knowledge-base client in production; the web app talks to the same HTTP API (proxied same-origin via nginx under `/api/`).

## Architecture (short)

```text
Browser (web/) ──HTTP──► Backend (FastAPI) ──SQL──► Postgres + pgvector
       │                      ▲
       └──LiveKit WebRTC──► Agent worker ──HTTP──┘
```

Details and trade-offs: [`docs/technical-decisions.md`](docs/technical-decisions.md).

## Run the tests

Full notes: [`docs/testing.md`](docs/testing.md).

### Backend

```bash
docker compose up -d db
docker compose exec db createdb -U meridian meridian_test   # once

cd backend
uv sync --group dev
TEST_DATABASE_URL=postgresql+asyncpg://meridian:meridian@localhost:5432/meridian_test \
  uv run pytest

# Skip the latency check (NF-1)
TEST_DATABASE_URL=postgresql+asyncpg://meridian:meridian@localhost:5432/meridian_test \
  uv run pytest -m "not perf"
```

### Agent

```bash
cd agent
uv sync --group dev

# Behaviour tests — LLM only, tools mocked (no backend)
LLM_API_KEY=... uv run pytest -m "not e2e"

# All agent tests, including PRD scenarios and the text CLI
# (stack must already be up: docker compose up)
LLM_API_KEY=... BACKEND_URL=http://localhost:8000 uv run pytest
```

### Pinning a new question

| What you want to pin | File |
| --- | --- |
| Search should return a given FAQ | `backend/tests/data/search_cases.yaml` (`match`) |
| Search should return no match | `backend/tests/data/search_cases.yaml` (`no_match`) |
| Full reply + tool calls | `agent/tests/data/scenarios.yaml` |
