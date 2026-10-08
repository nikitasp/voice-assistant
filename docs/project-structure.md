# Project structure

Guideline for where code and configuration live. Keep this document in sync with the repository.

```text
voice-assistant/
├── .cursor/rules/             # Cursor rules (project, backend, agent, web)
├── backend/                   # FastAPI — the only service with database access
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
│   │   │       └── voices.py       # bonus
│   │   ├── models/            # SQLAlchemy 2.0 models
│   │   ├── schemas/           # Pydantic v2 request/response models
│   │   ├── services/
│   │   │   ├── faq_search.py
│   │   │   ├── embeddings.py
│   │   │   ├── unanswered.py
│   │   │   └── voices.py
│   │   └── seed/
│   │       ├── faq.yaml       # Meridian property data
│   │       └── loader.py
│   └── tests/
├── agent/                     # LiveKit Agents worker
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── concierge/
│   │   ├── main.py            # worker entrypoint (LiveKit Agents CLI)
│   │   ├── config.py
│   │   ├── assistant.py       # Agent class + search_faq / record_unanswered tools
│   │   ├── backend_client.py  # httpx client with timeouts
│   │   └── prompts/
│   │       └── concierge.md
│   └── tests/
├── web/                       # React + Vite + TypeScript
│   ├── package.json
│   └── src/
│       └── features/
│           ├── playground/    # core (task 09)
│           ├── faq/           # bonus
│           ├── unanswered/    # bonus
│           └── voices/        # bonus
├── deploy/
│   └── local/                 # Dockerfiles and env template for local run
│       ├── .env.example
│       ├── backend.Dockerfile
│       ├── agent.Dockerfile
│       ├── web.Dockerfile
│       └── web.nginx.conf
├── docs/
│   ├── requirements.md
│   ├── project-structure.md
│   ├── technical-decisions.md
│   └── tasks/
├── docker-compose.yml         # local evaluation stack (run from repo root)
└── README.md
```

## Principles

- **Service boundaries.** Only `backend/` touches the database. The agent and the web app use the backend's HTTP API. There is no shared Python package between `backend/` and `agent/`.
- **One frontend.** `web/` ships the playground as part of the core deliverable; admin pages are added to the same app for the bonus, and the integrated playground (task 17) is a route there.
- **Deployment assets vs Compose entrypoint.** Dockerfiles and `.env.example` live in `deploy/<environment>/`. `docker-compose.yml` lives at the repository root so `docker compose up` works without a `-f` flag. Service folders contain only code, dependency manifests and tests. `deploy/local/` is the only environment for now.
- **Each service has its own environment.** Python services each have their own `pyproject.toml` and `uv.lock`; there is no root virtualenv.

## Running locally

```bash
cp deploy/local/.env.example .env   # fill in credentials
docker compose up --build
```


| Service | URL |
| --- | --- |
| Web (playground, admin) | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| Local LiveKit server (optional) | ws://localhost:7880 |

By default the stack uses the provided LiveKit Cloud credentials. To run a LiveKit server locally instead, see the comments in `deploy/local/.env.example` and start with `docker compose --profile local-livekit up --build`.
