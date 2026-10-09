# 01 — Project setup

**Requirements:** NF-2
**Depends on:** —

## Goal

Create the repository layout and tooling so that each service can be developed and run in Docker.

## Scope

- Directory layout as described in [`../project-structure.md`](../project-structure.md): `backend/`, `agent/`, `web/`, `deploy/local/`, `docs/`.
- Python dependency management for `backend/` and `agent/` with `uv` (`pyproject.toml` + committed `uv.lock`).
- Root `.env.example` listing every required variable (copy to `./.env`): LiveKit URL/API key/secret, LLM API key, STT/TTS credentials, database settings.
- `.gitignore` covering `.env`, virtualenvs, build output.
- Minimal FastAPI app with `GET /health`.
- Remove the placeholder `main.py`.

## Acceptance criteria

- [ ] `backend` starts locally and `GET /health` returns `200`.
- [ ] `.env.example` documents every variable the system needs.
- [ ] No secrets are committed.
