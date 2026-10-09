# Meridian Voice Concierge

Voice concierge for The Meridian Casino & Resort. Spec: [`docs/requirements.md`](docs/requirements.md). Tasks: [`docs/tasks/`](docs/tasks/). Layout: [`docs/project-structure.md`](docs/project-structure.md). Testing details: [`docs/testing.md`](docs/testing.md).

## Run the stack

```bash
cp .env.example .env   # fill in credentials
docker compose up --build
```

| Service | URL |
| --- | --- |
| Web (playground) | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |

## Run the tests

Acceptance tests live in `backend/tests/` and `agent/tests/`. They fail until the corresponding code exists. Full notes: [`docs/testing.md`](docs/testing.md).

### Prerequisites

- Docker (for Postgres)
- [`uv`](https://docs.astral.sh/uv/) for Python deps
- Backend: `TEST_DATABASE_URL` pointing at a Postgres + pgvector database
- Agent: `LLM_API_KEY`; end-to-end tests also need a running, seeded backend (`BACKEND_URL`)

### Backend

```bash
# Start Postgres and create a dedicated test database (once)
docker compose up -d db
docker compose exec db createdb -U meridian meridian_test

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

# Behaviour tests — LLM only, knowledge-base tools mocked (no backend needed)
LLM_API_KEY=... uv run pytest -m "not e2e"

# All agent tests, including PRD scenarios and the text CLI
# (stack must already be up: docker compose up)
LLM_API_KEY=... BACKEND_URL=http://localhost:8000 uv run pytest
```

### Manual text check (TC-5)

With the stack running:

```bash
cd agent
BACKEND_URL=http://localhost:8000 LLM_API_KEY=... \
  uv run python -m concierge.ask "Is the poker room open right now?"
```

### Adding a question to check

| What you want to pin | File |
| --- | --- |
| Search should return a given FAQ | `backend/tests/data/search_cases.yaml` (`match`) |
| Search should return no match | `backend/tests/data/search_cases.yaml` (`no_match`) |
| Full reply + tool calls | `agent/tests/data/scenarios.yaml` |
