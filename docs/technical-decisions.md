# Technical decisions

## Architecture

```text
Browser (web/) ──HTTP──► Backend (FastAPI) ──SQL──► Postgres + pgvector
       │                      ▲
       └──LiveKit WebRTC──► Agent worker ──HTTP──┘
```

- **Backend** owns the database, FAQ search, unanswered queue, voice settings, and LiveKit token minting.
- **Agent** is a LiveKit Agents worker. It never talks to Postgres; knowledge-base access is only via backend HTTP tools (`search_faq`, `record_unanswered`).
- **Web** is one React app: guest playground plus admin pages (FAQ, unanswered queue, voices, integrated test playground). Nginx proxies `/api/` to the backend so the browser stays same-origin.

## Database and search

- **Postgres + pgvector** stores FAQ embeddings next to the rows (NF-1: search stays a single DB query).
- Embeddings use **`sentence-transformers/all-MiniLM-L6-v2`** (384-d). Cosine distance is computed in SQL; a result counts as a match when similarity `1 - distance` is at least `FAQ_SEARCH_THRESHOLD` (default `0.42`).
- Seed data lives in `backend/app/seed/faq.yaml` and is upserted by slug on every startup (idempotent).

## Unanswered question grouping

- Incoming questions are normalized: trim, lowercase, strip trailing punctuation/whitespace.
- An open row with the same normalized text is incremented; otherwise a new open row is created.
- Status values `open` / `converted` / `dismissed` support the admin convert/dismiss flow without schema changes.

## Voice stack

- **LiveKit** for realtime rooms (Cloud by default; optional local server via Compose profile `local-livekit`).
- **LLM**: OpenAI-compatible chat model via LiveKit's OpenAI plugin (`LLM_API_KEY`).
- **STT**: Deepgram (`STT_API_KEY`).
- **TTS**: Cartesia (`TTS_API_KEY`), with four PRD voices mapped to Cartesia voice IDs. The active voice is stored in `app_settings` and read by the agent at session start (NF-5).

## Text mode

- The same `Concierge` agent runs in a text-only `AgentSession` (LLM only) for automated tests and `python -m concierge.ask`.
- The playground sends typed messages on the LiveKit `lk.chat` text stream so typed and spoken turns share tools and prompt.

## Trade-offs / with more time

- Hybrid lexical + vector search for rare proper nouns.
- Cached embedding model in a shared volume to speed cold starts.
- Stronger admin UX (optimistic updates, undo dismiss) and richer conversation transcripts from agent data channels.
- Auth for the admin panel (explicitly out of scope for this assessment).
