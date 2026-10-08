# Tasks

Tasks derived from [`../requirements.md`](../requirements.md). Requirement IDs (VC-*, KB-*, API-*, PG-*, AP-*, VX-*, NF-*) refer to the PRD.

Complete core tasks before starting bonus tasks.

## Core

| # | Task | Requirements | Depends on |
| --- | --- | --- | --- |
| 01 | [Project setup](01-project-setup.md) | NF-2 | — |
| 02 | [Database schema](02-database-schema.md) | KB-1, KB-3, KB-4 | 01 |
| 03 | [Seed property data](03-seed-property-data.md) | KB-5 | 02 |
| 04 | [FAQ search API](04-faq-search-api.md) | API-1, API-3, KB-2 | 03 |
| 05 | [Unanswered questions API](05-unanswered-questions-api.md) | API-2, KB-3, KB-4 | 02 |
| 06 | [Voice agent foundation](06-voice-agent-foundation.md) | VC-1, VC-2, VC-4, NF-1 | 01 |
| 07 | [Agent knowledge base tools](07-agent-knowledge-tools.md) | VC-3, VC-5 | 04, 05, 06 |
| 08 | [Concierge persona and prompt](08-concierge-persona.md) | VC-6, NF-4 | 07 |
| 09 | [Playground interface](09-playground.md) | PG-1 – PG-5 | 06 |
| 10 | [Single-command Docker run](10-docker-compose.md) | NF-2 | 04, 05, 07, 09 |
| 11 | [Documentation](11-documentation.md) | Deliverables | 10 |

## Bonus

| # | Task | Requirements | Depends on |
| --- | --- | --- | --- |
| 12 | [Admin panel scaffold](12-admin-panel-scaffold.md) | NF-3 | 10 |
| 13 | [FAQ management](13-faq-management.md) | AP-1 – AP-4 | 12 |
| 14 | [Unanswered questions queue](14-unanswered-queue.md) | AP-5 – AP-8 | 12, 13 |
| 15 | [Voice configuration backend](15-voice-config-backend.md) | VX-1, VX-3, NF-5 | 07 |
| 16 | [Voice configuration UI](16-voice-config-ui.md) | VX-2, VX-4, AP-9 – AP-12 | 12, 15 |
| 17 | [Integrated playground](17-integrated-playground.md) | AP-13 – AP-16 | 09, 12, 15 |
