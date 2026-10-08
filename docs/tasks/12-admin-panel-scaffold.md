# 12 — Admin panel scaffold (bonus)

**Requirements:** NF-3
**Depends on:** 10

## Goal

A React app that hosts all admin features.

## Scope

- React app (e.g. Vite + TypeScript) in `admin/`.
- Layout with navigation: FAQs, Unanswered Questions, Voice, Playground.
- API client configured via environment variable.
- CORS enabled on the backend for the admin origin.
- Added to `docker-compose.yml`.
- No authentication (out of scope per PRD).

## Acceptance criteria

- [ ] Admin panel opens from `docker compose up` in a desktop browser.
- [ ] Navigation between sections works.
