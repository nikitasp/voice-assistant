# 09 — Playground interface

**Requirements:** PG-1, PG-2, PG-3, PG-4, PG-5
**Depends on:** 06

## Goal

A browser interface to talk to the concierge.

## Scope

Choose one:

- **Option A:** LiveKit Agents Playground (hosted or self-hosted), with instructions for connecting it to the local LiveKit server.
- **Option B:** Custom page using the LiveKit client SDK, plus a backend endpoint `POST /api/livekit/token` that issues room access tokens.

Option B is reusable for the integrated admin playground (task 17).

## Acceptance criteria

- [ ] Accessible in a desktop browser (PG-1).
- [ ] Uses the microphone for input (PG-2).
- [ ] Plays the concierge's audio (PG-3).
- [ ] Shows connection and conversation state, e.g. connecting / listening / speaking (PG-4).
- [ ] Start and end conversation controls (PG-5).
