# 10 — Single-command Docker run

**Requirements:** NF-2
**Depends on:** 04, 05, 07, 09

## Goal

The whole core system starts with one Docker Compose command.

## Scope

- Root `docker-compose.yml` (already present; adjust as services are implemented) with: database (Postgres + pgvector), backend, agent, web, and an optional local LiveKit server (`--profile local-livekit`); LiveKit Cloud credentials are the default.
- Dockerfiles in `deploy/local/`: `backend.Dockerfile`, `agent.Dockerfile`, `web.Dockerfile` (+ `web.nginx.conf`).
- Health checks and `depends_on` so services start in the right order.
- Migrations and seeding run automatically.
- All configuration from `./.env` at the repo root (template: `deploy/local/.env.example`).

## Acceptance criteria

- [ ] On a clean machine with Docker: `cp deploy/local/.env.example .env`, fill credentials, `docker compose up --build` → working voice conversation in the browser.
- [ ] Restarting the stack keeps data (named volume for the database).
