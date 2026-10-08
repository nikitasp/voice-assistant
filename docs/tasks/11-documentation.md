# 11 — Documentation

**Requirements:** Deliverables (README, technical decisions document)
**Depends on:** 10

## Goal

Evaluators can run and understand the system without asking questions.

## Scope

- `README.md`:
  - Prerequisites
  - Environment variables
  - `docker compose up` instructions
  - How to open the playground and try the example scenarios
  - API overview and link to `/docs`
- `docs/technical-decisions.md`:
  - Architecture diagram or description
  - Choice of database, search approach, LLM/STT/TTS providers
  - How unanswered questions are grouped
  - Trade-offs and what would be done with more time

## Acceptance criteria

- [ ] Following only the README results in a working system.
- [ ] Each implementer-discretion decision from the PRD is explained.
