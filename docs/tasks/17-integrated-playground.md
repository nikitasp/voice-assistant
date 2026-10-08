# 17 — Integrated playground (bonus)

**Requirements:** AP-13, AP-14, AP-15, AP-16
**Depends on:** 09, 12, 15

## Goal

Staff can test the concierge from inside the admin panel.

## Scope

- Playground page in the admin panel, reusing the LiveKit client logic from task 09 (token endpoint, mic, audio, status, start/end).
- Each session uses the current active voice and the current FAQ content.
- Prominent "Test Mode" / "Playground" label.
- Optional: live transcript of the conversation.

## Acceptance criteria

- [ ] Admin can hold a full voice conversation from the admin panel (AP-13, AP-15).
- [ ] Changing the voice or adding an FAQ is reflected in the next playground session (AP-14).
- [ ] Page is clearly labeled as test mode (AP-16).
