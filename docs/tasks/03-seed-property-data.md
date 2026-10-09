# 03 — Seed property data

**Requirements:** KB-5, KB-1
**Depends on:** 02

## Goal

Load the Meridian property information from the PRD into the knowledge base.

## Scope

- Convert every section of "Property Information (Seed Data)" into FAQ items:
  - General information (hours, check-in/out, parking, dress code, age, Wi-Fi)
  - Casino gaming
  - Accommodations
  - On-property restaurants
  - Bars & lounges
  - Entertainment & amenities
  - Celebrations & special events
  - Partner discounts
- Store seed data in a versioned file (e.g. `backend/seed/faq.json` or `.yaml`).
- Each item has the slug listed in `backend/tests/data/seed_slugs.yaml`; the slug is the upsert key.
- Seeding is idempotent: re-running does not create duplicates.
- Seeding runs automatically on first start in Docker.
- If search uses embeddings, compute them during seeding.

## Acceptance criteria

- [ ] Every row of every seed table in the PRD is represented by at least one FAQ item.
- [ ] Running the seed twice leaves the same number of items.
- [ ] Fresh `docker compose up` results in a populated knowledge base.
