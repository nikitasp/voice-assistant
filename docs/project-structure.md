# Project structure

Guideline for where code and configuration live. Keep this document in sync with the repository.

```text
voice-assistant/
├── .cursor/rules/             # Cursor rules (project, backend, agent, web)
├── backend/                   # FastAPI — the only service with database access
│   ├── .dockerignore          # excludes .venv from image builds
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── alembic.ini
│   ├── migrations/
│   ├── app/
│   │   ├── main.py            # app factory, lifespan (migrate + seed)
│   │   ├── config.py          # pydantic-settings
│   │   ├── db.py              # async engine, session dependency
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── faq.py          # search (core) + CRUD (bonus)
│   │   │       ├── unanswered.py   # record (core) + queue (bonus)
│   │   │       ├── livekit.py      # room token for the playground
│   │   │       ├── property.py     # full property information sheet
│   │   │       └── voices.py       # bonus
│   │   ├── models/            # SQLAlchemy 2.0 models
│   │   ├── schemas/           # Pydantic v2 request/response models
│   │   ├── services/
│   │   │   ├── faq_search.py
│   │   │   ├── embeddings.py
│   │   │   ├── unanswered.py
│   │   │   ├── property.py
│   │   │   └── voices.py
│   │   └── seed/
│   │       ├── faq.yaml       # FAQ items (searchable knowledge base)
│   │       ├── property.yaml  # property information sheet from the PRD
│   │       └── loader.py
│   └── tests/                 # acceptance tests, see docs/testing.md
│       ├── data/              # seed_slugs.yaml, search_cases.yaml
│       └── support.py
├── agent/                     # LiveKit Agents worker
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── concierge/
│   │   ├── main.py            # worker entrypoint (LiveKit Agents CLI)
│   │   ├── ask.py             # text-mode CLI: python -m concierge.ask "question"
│   │   ├── config.py
│   │   ├── models.py          # build_llm / STT / TTS from settings
│   │   ├── assistant.py       # Concierge agent + search_faq / record_unanswered tools
│   │   ├── backend_client.py  # httpx client with timeouts
│   │   └── prompts/
│   │       └── concierge.md
│   └── tests/                 # text-mode behaviour + e2e scenarios, see docs/testing.md
│       ├── data/              # scenarios.yaml
│       └── support.py
├── web/                       # React + Vite + TypeScript
│   ├── package.json
│   └── src/
│       └── features/
│           ├── playground/    # core (task 09)
│           ├── faq/           # bonus
│           ├── unanswered/    # bonus
│           ├── voices/        # bonus
│           └── health/        # service probes + mic/speaker tests
├── deploy/
│   └── local/                 # Dockerfiles for local run
│       ├── backend.Dockerfile
│       ├── agent.Dockerfile
│       ├── web.Dockerfile
│       └── web.nginx.conf
├── docs/
│   ├── requirements.md
│   ├── project-structure.md
│   ├── testing.md
│   ├── technical-decisions.md
│   └── tasks/
├── docker-compose.yml         # local evaluation stack (run from repo root)
├── .env.example               # copy to .env
└── README.md
```

## Principles

- **Service boundaries.** Only `backend/` touches the database. The agent and the web app use the backend's HTTP API. There is no shared Python package between `backend/` and `agent/`.
- **One frontend.** `web/` ships the playground as part of the core deliverable; admin pages are added to the same app for the bonus, and the integrated playground (task 17) is a route there.
- **Deployment assets vs Compose entrypoint.** Dockerfiles live in `deploy/<environment>/`. `docker-compose.yml` and `.env.example` live at the repository root so `docker compose up` works without a `-f` flag. Service folders contain only code, dependency manifests and tests. `deploy/local/` is the only environment for now.
- **Each service has its own environment.** Python services each have their own `pyproject.toml` and `uv.lock`; there is no root virtualenv.

## Running locally

```bash
cp .env.example .env   # fill in credentials
docker compose up --build
```



| Service | URL |
| --- | --- |
| Web (playground, admin) | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| Local LiveKit server (optional) | ws://localhost:7880 |

By default the stack uses the provided LiveKit Cloud credentials. To run a LiveKit server locally instead, see the comments in `.env.example` and start with `docker compose --profile local-livekit up --build`.
