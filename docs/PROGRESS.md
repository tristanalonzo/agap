# PROGRESS.md — Project AGAP, Team B

Keep this file short and current. AI tools read it at the start of every session.

## Who owns what

| Area | Owner | Status |
|---|---|---|
| Repo, skeleton, API contract, reviews | Tristan | skeleton done (#1); reviews ongoing |
| Flood map (MapLibre + NOAH PMTiles) | Tristan | done (#2); shelters + you + nearest markers (`feat/map-shelters`) |
| Backend: mock assess, hotlines, health, shelters endpoint | Marcus | done (#1 health, #4 mock `/assess`, hotlines, shelters) |
| Backend: PAGASA rainfall-warning scraper | Marcus | done by Tristan (Claude Code), `feat/pagasa-scraper` |
| Backend: qc_shelters.geojson + nearest shelter | Marcus | done by Tristan (Claude Code), `feat/shelters` |
| Frontend: app shell from mockup | Kurt | done (#3: Kurt's app, wired to the contract mock by Tristan) |
| Frontend: connect to /assess, refresh + 60 s polling | Kurt | done by Tristan: real API (#6), polling + location + refresh (`feat/frontend-live`); pull-to-refresh not built |
| Frontend: status badges + hotlines screen | Kurt | in progress: `StatusBadge` done (#3); hotlines screen done (Tristan, #7); shelter card done (Tristan, #9); rainfall card wording done (Tristan, `feat/frontend-rainfall-wording`) |
| Model integration (Phase 3) | Luke + Kurt | backend seam ready (`feat/inference-seam`): drop in the `.onnx` + `preprocessing.json`, pick a frame source, unskip `test_inference.py`. Still waiting on Team A |

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
- 2026-10-20: PAGASA source = NCR regional page `https://bagong.pagasa.dost.gov.ph/regional-forecast/ncrprsd` ("Rainfall Warning" tab). The old `/weather/rainfall-warning` URL returned 404. Results cached 10 min (`PAGASA_CACHE_MINUTES`).

## Open questions (for Team A / Feudo)

- [ ] Exact model input/output names, shapes, class order, and preprocessing (send `preprocessing.json` + test frames).
      The file goes in `backend/app/static/preprocessing.json`; `services/inference.py` already reads it and
      names the missing key if anything is absent. Required keys: `input_name`, `input_shape`, `dtype`,
      `class_order`, `normalization` (plus optional `model_version`).
- [ ] For the demo, which satellite images do we feed the model? (Proposal: a handful of TCIR test frames saved as `.npy`.)
      This now blocks I1 on our side too: `/assess` only receives a latitude and longitude, so even with the
      model loaded there is no frame to classify. `inference.classify()` takes an already-preprocessed frame
      and is ready; what is missing is whatever supplies one.
- [ ] Does the model also predict sustained wind? If yes, what unit? (`sustained_wind_kph` is left null without it.)

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
- 2026-10-20 — Tristan (Claude Code) — B2 on `feat/pagasa-scraper`: `services/pagasa.py` reads the NCR page's rainfall tab (fresh / stale / unavailable / parse_error; "none" only when PAGASA says so), 10-min cache, wired into `/assess`; fixtures + 6 tests, tests never use the network; 19 pytest tests pass. Live check: "no Heavy Rainfall Warning" → fresh / none.
- 2026-10-20 — Tristan (Claude Code) — F3 rainfall wording on `feat/frontend-rainfall-wording`: `fresh` shows LIVE, "none" shows NO HEAVY RAINFALL WARNING, "unknown" says it does NOT mean no warning + PAGASA link, stale note, issued time, "Full advisory" expandable; checked live + with a dead PAGASA URL.
- 2026-10-20 — Tristan (Claude Code) — F2 on `feat/frontend-live`: location (GPS button + manual lat/lon, default Quezon Memorial Circle), 60 s polling (paused when hidden / busy), Refresh, "Updated X min ago", STALE after 5 min, keeps last result on error + Retry, 422 message shown, flood years shared by map + request; "Live API" chip + honest mode bar. Pull-to-refresh cut.
- 2026-10-20 — Tristan (Claude Code) — L3 on `feat/map-shelters`: map shows all 239 shelters (popup: name + "Unverified"), a "You" marker at the assessed point (map moves there), nearest shelter as a green marker, legend + OSM credit; checked at 390 px.
- 2026-10-29 — Tristan (Claude Code) — I1 prep on `feat/inference-seam`: `MOCK_INFERENCE` is honoured for the first time (it was a dead setting), `services/inference.py` gains `load_preprocessing()`, `load_session()` (lazy onnxruntime import) and `classify(frame)`, all errors raise `ModelNotReady` naming what is missing; with the flag off and no model, `/assess` returns an honest `"unavailable"` + reason, never the mock. No model details invented — class order and input name come from Team A's `preprocessing.json`. 9 new tests, 27 pass + 1 skipped (unskips itself when the `.onnx` lands). Found: `/assess` has no satellite frame to feed the model, so that open question now blocks I1.
- 2026-10-29 — Tristan (Claude Code) — `fix/mode-bar-cyclone-status`: the mode bar and the MODEL VERSION line no longer hard-code "DEMO" / "(mock)" — both read `cyclone_assessment`, so they stay true once a real model runs or when there is no estimate. Checked all three states in the browser (demo / live / unavailable); lint + build pass.
- 2026-10-29 — Tristan (Claude Code) — Self-review of #15 fixed 5 bugs before merge: the class-count guard let a 3-class model pass against a 5-class list (wrong category served as "live"); `data_status` ignored the cyclone, so "complete" was reported while it was unavailable; a default argument made a safety test pass by accident (it would have failed on the day Team A delivers `preprocessing.json`); an unknown output layout crashed instead of saying so; the model path depended on the folder you ran from. Second pass: a model file that exists but cannot be opened (corrupt, opset too new, or Google Drive's HTML page) crashed all of `/assess` with HTTP 500, losing rainfall and shelter too — now "unavailable"; also onnxruntime errors on a rejected frame, NaN scores and a repeated class name now fail with a clear message. Each new test was checked by putting its bug back and watching it fail. 40 pass + 1 skipped.
