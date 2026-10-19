# PROGRESS.md — Project AGAP, Team B

Keep this file short and current. AI tools read it at the start of every session.

## Who owns what

| Area | Owner | Status |
|---|---|---|
| Repo, skeleton, API contract, reviews | Tristan | in progress |
| Flood map (MapLibre + NOAH PMTiles) | Tristan | not started |
| Backend: mock assess, hotlines, health, shelters endpoint | Marcus | not started |
| Backend: PAGASA rainfall-warning scraper | Marcus | not started |
| Backend: qc_shelters.geojson + nearest shelter | Marcus | not started |
| Frontend: app shell from mockup | Kurt | not started |
| Frontend: connect to /assess, refresh + 60 s polling | Kurt | not started |
| Frontend: status badges + hotlines screen | Kurt | not started |
| Model integration (Phase 3) | Luke + Kurt | waiting on Team A |

## Dates

- 2026-10-20 (Tue): progress update — target: mock /assess works, app shell shows it, map shows one flood layer.
- Final deadline: _(fill in)_

## Decisions

- 2026-10-17: Stack = FastAPI + React/Vite (JavaScript) + MapLibre/PMTiles. No database for now.
- 2026-10-17: ONNX model path = `backend/app/weights/agap_tc_classifier.onnx`.
- 2026-10-17: Final integration = Luke + Kurt. Tristan reviews.
- 2026-10-17: Kurt = frontend, Marcus = backend.
- 2026-10-17: Out of scope for now: historical replay, live Himawari download, SQLite, WebSockets, deployment.

## Open questions (for Team A / Feudo)

- [ ] Exact model input/output names, shapes, class order, and preprocessing (send `preprocessing.json` + test frames).
- [ ] For the demo, which satellite images do we feed the model? (Proposal: a handful of TCIR test frames saved as `.npy`.)

## Log (newest at the bottom, one line each: date — who — what)

- 2026-10-17 — Tristan — Starter kit pushed (AGENTS.md, contract, reference docs).
- 2026-10-19 — Tristan (Claude Code) — Backend skeleton on `feat/backend-skeleton`: config, CORS, `/health/live` + test, pinned requirements, empty placeholders for Marcus.
- 2026-10-20 — Tristan (Claude Code) — Covered F1 on `feat/frontend-base` (from Kurt's branch): proxy, `client.js` + contract mock, cards read the contract, StatusBadge, scenario chips labelled DEMO.
