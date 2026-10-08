# 14 — Unanswered questions queue (bonus)

**Requirements:** AP-5, AP-6, AP-7, AP-8
**Depends on:** 12, 13

## Goal

Staff can review unanswered questions and turn them into FAQs.

## Scope

Backend:

- `GET /api/unanswered?status=open` sorted by frequency, then recency.
- `POST /api/unanswered/{id}/convert` with `{ category, question, answer }` → creates FAQ item, sets status `converted`.
- `POST /api/unanswered/{id}/dismiss` → sets status `dismissed`.

Admin UI:

- Queue list showing question, frequency, first/last asked.
- "Convert to FAQ" form prefilled with the question text.
- "Dismiss" action.

## Acceptance criteria

- [ ] Queue shows open questions with frequency counts.
- [ ] Converting creates a searchable FAQ and removes the item from the open queue.
- [ ] Dismissed questions no longer appear in the open queue.
