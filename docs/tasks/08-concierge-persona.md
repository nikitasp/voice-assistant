# 08 — Concierge persona and prompt

**Requirements:** VC-6, NF-4
**Depends on:** 07

## Goal

Make the concierge sound like a luxury hospitality professional.

## Scope

- System prompt defining the Meridian concierge persona: warm, professional, concise, personalized.
- Rules for voice output: short sentences, no markdown or lists, numbers and prices phrased for speech.
- Offer relevant alternatives or follow-ups where useful (e.g. suggest casual dining after Aurelia).
- Mention front desk (extension 0) or concierge desk when a question cannot be answered or needs a human.
- Keep the prompt in a separate file so it is easy to edit.

## Acceptance criteria

- [ ] Responses to the five PRD example scenarios match their tone and content.
- [ ] No slang, emojis, or formatting artifacts in spoken output.
