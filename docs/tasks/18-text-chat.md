# 18 — Text chat

**Requirements:** TC-1, TC-2, TC-3, TC-4, TC-5
**Depends on:** 07, 09

## Goal

Let people talk to the concierge by typing, so its reaction to each specific question is easy to check.

## Scope

- Agent: keep LiveKit's room text input enabled (default `lk.chat` text stream) so typed messages go through the same `AgentSession`, prompt and tools as speech.
- Agent: the `Concierge` agent class must work in an `AgentSession` created with only an LLM (no STT, TTS or VAD); this is what the automated tests use.
- Agent: `python -m concierge.ask "question"` and `python -m concierge.ask --file questions.txt` run each question in a text-only session against the configured backend and print the reply and the tool calls with their arguments.
- Playground (`web/`): text input next to the microphone controls, and a transcript showing guest and concierge messages for both typed and spoken turns.

## Acceptance criteria

- [ ] Typing "Is the poker room open right now?" in the playground produces a concierge reply in the transcript (TC-1, TC-2).
- [ ] Typed and spoken questions produce the same tool calls (TC-3).
- [ ] `agent/tests/` runs without audio providers configured (TC-4).
- [ ] `python -m concierge.ask` prints the reply and tool calls for a question (TC-5).
