# 15 — Voice configuration backend (bonus)

**Requirements:** VX-1, VX-3, NF-5
**Depends on:** 07

## Goal

Support four concierge voices and switch between them without restarting.

## Scope

- Map the four PRD voices (James, Sofia, Marcus, Elena) to concrete voices of the chosen TTS provider; store id, name, description, provider voice id.
- Persist the active voice (settings table).
- Endpoints:
  - `GET /api/voices` — list with `active` flag.
  - `PUT /api/voices/active` with `{ "voice_id": ... }`.
  - `GET /api/voices/{id}/preview` — returns a short audio sample (generated once and cached).
- Agent fetches the active voice when a new session starts and configures TTS accordingly.

## Acceptance criteria

- [ ] Four distinct voices are available (VX-1).
- [ ] Changing the active voice applies to the next conversation without restarting any service (VX-3, NF-5).
- [ ] Preview endpoint returns playable audio for each voice.
