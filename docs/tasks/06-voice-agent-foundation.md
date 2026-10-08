# 06 — Voice agent foundation

**Requirements:** VC-1, VC-2, VC-4, NF-1
**Depends on:** 01

## Goal

A LiveKit agent that joins a room, listens to the guest, and replies with speech.

## Scope

- Python agent using the LiveKit Agents SDK.
- Pipeline: STT → LLM → TTS using the provided credentials, with voice activity detection and turn detection.
- Agent connects to the LiveKit server from `.env` and joins rooms created by the playground.
- Agent greets the guest when the session starts.
- Latency (NF-1): use streaming STT/TTS, keep the LLM response short, allow interruptions.

## Acceptance criteria

- [ ] Speaking a question in a LiveKit room produces a spoken reply.
- [ ] Guest can interrupt the agent mid-sentence.
- [ ] Response start latency feels conversational (target: roughly under 2 seconds after the guest stops speaking).
