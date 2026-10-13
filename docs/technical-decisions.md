# Technical decisions

## Architecture

```text
Browser (web/) ──HTTP──► Backend (FastAPI) ──SQL──► Postgres + pgvector
       │                      ▲
       └──LiveKit WebRTC──► Agent worker ──HTTP──┘
```

- **Backend** (FastAPI / Python 3.12) owns the database, FAQ search, unanswered queue, voice settings, and LiveKit token minting. Communication with the agent and web app is JSON over HTTP.
- **Agent** is a LiveKit Agents worker. It never talks to Postgres; knowledge-base access is only via backend HTTP tools (`search_faq`, `record_unanswered`).
- **Web** is one React app (Vite + TypeScript): guest playground plus admin pages (FAQ, unanswered queue, voices, integrated test playground). Nginx proxies `/api/` to the backend so the browser stays same-origin. There is no separate `admin/` package — bonus UI lives under `web/src/features/`.

## Database and search

- **Postgres + pgvector** stores FAQ embeddings next to the rows (NF-1: search stays a single DB query).
- Embeddings use **`sentence-transformers/all-MiniLM-L6-v2`** (384-d). Cosine distance is computed in SQL; a result counts as a match when similarity `1 - distance` is at least `FAQ_SEARCH_THRESHOLD` (default `0.42`).
- Seed data lives in `backend/app/seed/faq.yaml` and is upserted by slug on every startup (idempotent).
- **Property information sheet.** FAQ search returns individual Q&A items, which cannot answer questions that span topics ("what discounts do you have?", "help me plan a proposal"). The full PRD property information lives in `backend/app/seed/property.yaml` and is served by `GET /api/property`. The agent fetches it at session start (in parallel with the active voice, NF-5) and appends it to its instructions, so the LLM can combine facts across sections. It is still called `search_faq` first; when FAQ facts differ from the sheet, the prompt prefers FAQ (admin-maintained). A question is recorded as unanswered only when neither source covers it. Trade-off: about 2.5k extra prompt tokens per turn, and edits to the sheet need a backend restart; FAQ edits apply immediately.

## Unanswered question grouping

- Incoming questions are normalized: trim, lowercase, strip trailing punctuation/whitespace.
- An open row with the same normalized text is incremented first.
- Otherwise the question is embedded (same MiniLM model as FAQ search). An open row whose cosine similarity is at least `UNANSWERED_SIMILARITY_THRESHOLD` (default `0.82`) is treated as a near-duplicate and incremented; else a new open row is created with its embedding stored.
- Status values `open` / `converted` / `dismissed` support the admin convert/dismiss flow without schema changes.
- The concierge prompt requires `search_faq` then `record_unanswered` for every informational guest question, including off-topic ones. Declining without recording left odd asks (e.g. "can I turn to the dark side") out of the admin queue while ordinary unknowns (e.g. "do you have cookies") were captured.

## Voice stack

- **LiveKit** for realtime rooms (Cloud by default; optional local server via Compose profile `local-livekit`).
- **LLM**: OpenAI-compatible chat model via LiveKit's OpenAI plugin (`LLM_API_KEY`, optional `LLM_BASE_URL` / `LLM_MODEL`). Defaults to OpenAI; for unpaid local/dev use point `LLM_BASE_URL` at Groq or Ollama.
- **STT**: Deepgram (`STT_API_KEY`).
- **TTS**: Cartesia (`TTS_API_KEY`), with four PRD voices mapped to Cartesia voice IDs. The active voice is stored in `app_settings` and read by the agent at session start (NF-5). Backend voice previews use `TTS_MODEL` (default `sonic-3`); Cartesia has no TTS model-list API, so the model is configured explicitly.
- **Health probes**: `GET /api/health/providers` validates OpenAI/Deepgram/Cartesia API keys (token-only) for the admin Health page. Speech generation is checked separately via voice preview. `STT_API_KEY` / `LLM_API_KEY` are available to the backend for those probes; the agent remains the runtime LLM/STT consumer.

## Echo / false interruptions

- Open-speaker setups pick up TTS as guest speech (browser AEC alone was not enough: STT transcribed the agent's own greeting). Two defenses:
  1. **Playground half-duplex**: mic stays off during agent speech (and briefly after) so echo never reaches STT. Voice barge-in is unavailable in the playground; typed `lk.chat` turns still work.
  2. **Agent** `ALLOW_INTERRUPTIONS=false` by default so leftover audio cannot cut TTS mid-utterance (`discard_audio_if_uninterruptible`). Thresholds (`MIN_INTERRUPTION_DURATION` / `MIN_INTERRUPTION_WORDS` / false-interruption resume) remain available when interruptions are re-enabled (headphones).

## Text mode

- The same `Concierge` agent runs in a text-only `AgentSession` (LLM only) for automated tests and `python -m concierge.ask`.
- The playground sends typed messages on the LiveKit `lk.chat` text stream so typed and spoken turns share tools and prompt.

## Trade-offs / with more time

- Hybrid lexical + vector search for rare proper nouns.
- Cached embedding model in a shared volume to speed cold starts.
- Stronger admin UX (optimistic updates, undo dismiss) and richer conversation transcripts from agent data channels.
- Auth for the admin panel (explicitly out of scope for this assessment).
