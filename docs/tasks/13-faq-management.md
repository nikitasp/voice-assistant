# 13 — FAQ management (bonus)

**Requirements:** AP-1, AP-2, AP-3, AP-4
**Depends on:** 12

## Goal

Staff can manage FAQ content.

## Scope

Backend:

- `GET /api/faq` (list, with optional category filter and text search)
- `POST /api/faq`
- `PUT /api/faq/{id}`
- `DELETE /api/faq/{id}`
- Recompute search data (e.g. embeddings) on create and update.

Admin UI:

- FAQ table grouped or filterable by category.
- Create and edit form (category, question, answer).
- Delete with confirmation.

## Acceptance criteria

- [ ] Admin can view, add, edit, and delete FAQ items.
- [ ] A newly added FAQ is returned by the search API right away and answered by the agent in the next conversation.
