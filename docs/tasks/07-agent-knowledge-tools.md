# 07 — Agent knowledge base tools

**Requirements:** VC-3, VC-5
**Depends on:** 04, 05, 06

## Goal

Make the agent answer from the knowledge base and record what it cannot answer.

## Scope

- LLM function tools in the agent:
  - `search_faq(query)` → calls `POST /api/faq/search`.
  - `record_unanswered(question)` → calls `POST /api/unanswered`.
- Instructions: always search before answering property questions; answer only from returned facts; when nothing is found, call `record_unanswered`, apologize, and confirm the question has been noted (PRD Scenario 3).
- Handle backend errors and timeouts gracefully (spoken fallback, no crash).
- Backend URL configurable via environment.

## Acceptance criteria

- [ ] PRD Scenarios 1, 2, 4 and 5 are answered using knowledge base facts.
- [ ] Scenario 3 ("Can I bring my dog?") produces a graceful apology and a new or incremented unanswered record.
- [ ] Agent does not invent property facts that are not in the knowledge base.
- [ ] Backend outage results in a polite spoken fallback.
