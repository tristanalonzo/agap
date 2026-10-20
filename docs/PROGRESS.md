# PROGRESS.md — Project AGAP, Team B

Keep this file short and current. AI tools read it at the start of every session.

## Who owns what

| Area | Owner | Status |
|---|---|---|
| Repo, skeleton, API contract, reviews | Tristan | skeleton done (#1); reviews ongoing |
| Flood map (MapLibre + NOAH PMTiles) | Tristan | done (#2) |
| Backend: mock assess, hotlines, health, shelters endpoint | Marcus | done (#1 health, #4 mock `/assess`, hotlines, shelters) |
| Backend: PAGASA rainfall-warning scraper | Marcus | not started |
| Backend: qc_shelters.geojson + nearest shelter | Marcus | done by Tristan (Claude Code), `feat/shelters` |
| Frontend: app shell from mockup | Kurt | done (#3: Kurt's app, wired to the contract mock by Tristan) |
| Frontend: connect to /assess, refresh + 60 s polling | Kurt | in progress: `USE_MOCK = false`, app calls the real `/assess` (Tristan, #6); refresh + polling (F2) not started |
| Frontend: status badges + hotlines screen | Kurt | in progress: `StatusBadge` done (#3); hotlines screen done (Tristan, #7); shelter card done (Tristan, `feat/frontend-shelter-card`); rainfall card wording not started |
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
- 2026-10-20: Tristan takes the rest of Phase 2 (B2, B3, F2, F3, L3) for the progress check; owners in the table stay as the original plan.
- 2026-10-20: Shelters use our own Overpass query (evacuation centres, barangay halls, community centres, covered courts), not the reference one, which returns mostly bus stops. Query is in `backend/app/services/shelters.py`.

## Open questions (for Team A / Feudo)

- [ ] Exact model input/output names, shapes, class order, and preprocessing (send `preprocessing.json` + test frames).
- [ ] For the demo, which satellite images do we feed the model? (Proposal: a handful of TCIR test frames saved as `.npy`.)

## Log (newest at the bottom, one line each: date — who — what)

- 2026-10-17 — Tristan — Starter kit pushed (AGENTS.md, contract, reference docs).
- 2026-10-19 — Tristan (Claude Code) — Backend skeleton on `feat/backend-skeleton`: config, CORS, `/health/live` + test, pinned requirements, empty placeholders for Marcus.
- 2026-10-19 — Tristan (Claude Code) — L2 flood map on `feat/flood-map` (from Kurt's branch): `FloodMap.jsx` with MapLibre + NOAH PMTiles (layers flood_5yr/25yr/100yr, `Var` 1–3), 5/25/100 toggle default 25.
- 2026-10-20 — Tristan (Claude Code) — Covered F1 on `feat/frontend-base` (from Kurt's branch): proxy, `client.js` + contract mock, cards read the contract, StatusBadge, scenario chips labelled DEMO.
- 2026-10-20 — Tristan (Claude Code) — L2 moved onto main: `FloodMap` replaces Kurt's Leaflet map on the Hazard Map tab (`QcMap.jsx`, `hazard.js`, `leaflet` now unused).
- 2026-10-20 — Tristan (Claude Code) — #2 + #3 merged: `main` runs the app on mock data (DEMO labels, NOAH flood map); pytest, lint, build pass; waiting on Marcus's B1 `/assess`.
- 2026-10-20 — Marcus (Claude Code) — B1 on `feat/backend-assess-mock`: schemas match the contract, mock `/assess` (DEMO cyclone, rainfall + shelter "unavailable", QC-box 422), `/hotlines`, `/shelters` (empty FeatureCollection until B3); 7 pytest tests pass.
- 2026-10-20 — Tristan (Claude Code) — `feat/use-real-api`: `USE_MOCK = false`, the app now calls the real backend `/assess` (cyclone DEMO, rainfall + shelter honestly "unavailable"); all tabs checked in the browser.
- 2026-10-20 — Tristan (Claude Code) — F3 hotlines part on `feat/frontend-hotlines`: Action / SOS tab lists all 6 numbers from `/api/v1/hotlines` (name, number, description, tap to call, verified date, LIVE badge); last good list cached in localStorage and shown as STALE offline; nothing cached = UNAVAILABLE + a 911 button; lint, build, pytest pass. Rainfall/shelter wording of F3 still open (Kurt).
- 2026-10-20 — Tristan (Claude Code) — B3 on `feat/shelters`: `qc_shelters.geojson` (239 named OSM facilities in QC), Haversine nearest shelter in `/assess` (is_verified false), `/shelters` returns clean points, `data_status` built from real statuses; 13 pytest tests pass.
- 2026-10-20 — Tristan (Claude Code) — F3 shelter card on `feat/frontend-shelter-card`: own LIVE/UNAVAILABLE badge (no longer copies the cyclone DEMO), distance in m/km "straight line", UNVERIFIED tag + "confirm with your barangay"; lint, build pass.
