# AGENTS.md — Project AGAP (Team B: App Development)

Read this whole file before writing any code. It is the single source of truth for every
AI tool on this team (Claude Code, Claude chat, Gemini, Copilot, Cursor, Antigravity).
If something here conflicts with `docs/reference/`, THIS FILE WINS. The reference docs
are background only (Team A lead: "reference, not strict instructions").

## 1. What we are building

A web app for Quezon City (QC) that shows a user, for their location:
1. **Cyclone category** — from Team A's ONNX model (TD, TS, STS, TY, STY). FAKE (mock) until the model is delivered.
2. **PAGASA rainfall warning** — scraped from PAGASA's website.
3. **Flood hazard map** — Project NOAH static flood scenarios (5 / 25 / 100-year), shown on a map.
4. **Nearest evacuation shelter** — from `qc_shelters.geojson`, straight-line (Haversine) distance.
5. **Emergency hotlines** — from `qc_hotlines.json`, tap to call.

This is a school prototype (CS 403). Keep it simple. Working > perfect.

## 2. Team and ownership

- Team B lead + reviewer: Tristan Alonzo. Owns repo setup, the API contract, the flood map, PR reviews.
- Backend (FastAPI): Marcus Marcaida.
- Frontend (React): Kurt Raneses.
- Team A (model): Feudo (lead), Luke Manimtim.
- Final model integration: Luke Manimtim + Kurt Raneses.

## 3. Stack (decided — do not change without the lead)

| Part | Choice |
|---|---|
| Backend | Python 3.14 (not 3.15: no onnxruntime build yet), FastAPI, uvicorn, pydantic v2, httpx, beautifulsoup4 |
| Model runtime | onnxruntime, numpy (only in Phase 3) |
| Frontend | React + Vite, **JavaScript (not TypeScript)**, plain CSS |
| Map | maplibre-gl + pmtiles |
| Database | **None for now.** JSON files + in-memory cache. |
| Package managers | pip + `requirements.txt` (backend), npm (frontend) |

Ports: backend `http://127.0.0.1:8000`, frontend `http://localhost:5173`.
The Vite dev server proxies `/api` and `/health` to the backend, so the frontend always calls
relative URLs like `fetch("/api/v1/telemetry/assess")`. Never hard-code `http://127.0.0.1:8000` in frontend code.

## 4. Folder structure (create files only in these places)

```
agap/
├── AGENTS.md  CLAUDE.md  README.md  .gitignore
├── docs/
│   ├── PROGRESS.md                 # who is doing what + decision log. Update it.
│   ├── contract/assess.sample.json # THE response shape. Backend and frontend both follow it.
│   └── reference/                  # Team docs (background only) + mockup/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, routers
│   │   ├── config.py               # all settings from env vars (.env)
│   │   ├── schemas.py              # pydantic models matching assess.sample.json
│   │   ├── api/  health.py  hotlines.py  telemetry.py  shelters.py
│   │   ├── services/
│   │   │   ├── inference.py        # mock now, ONNX later
│   │   │   ├── pagasa.py           # rainfall-warning scraper
│   │   │   └── shelters.py         # load geojson + haversine nearest
│   │   ├── static/                 # qc_hotlines.json, debris_matrix.json, qc_shelters.geojson, preprocessing.json
│   │   └── weights/                # agap_tc_classifier.onnx (from Team A)
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── vite.config.js              # includes the /api + /health proxy
    └── src/
        ├── main.jsx  App.jsx  index.css
        ├── api/client.js           # every fetch to the backend lives here
        ├── mocks/assess.sample.json# copy of docs/contract/assess.sample.json
        ├── hooks/useAssessment.js  # polling + refresh logic
        └── components/             # one file per card/screen; FloodMap.jsx
```

The ONNX model goes in `backend/app/weights/agap_tc_classifier.onnx` (decided; NOT `/backend/models/`,
because "models" is confusing next to pydantic schemas). If the file is over 50 MB, do NOT commit it:
keep it in the team Drive and list the download step in README.

## 5. API (MVP)

| Method | Path | Returns |
|---|---|---|
| GET | `/health/live` | `{"status": "ok"}` |
| GET | `/api/v1/hotlines` | contents of `static/qc_hotlines.json` |
| GET | `/api/v1/shelters` | contents of `static/qc_shelters.geojson` (for map markers) |
| POST | `/api/v1/telemetry/assess` | the object in `docs/contract/assess.sample.json` |

Assess request body:
```json
{ "latitude": 14.65, "longitude": 121.05, "flood_return_period_years": 25 }
```
- `flood_return_period_years` is optional, one of 5 / 25 / 100, default 25.
- Reject coordinates outside the QC box with HTTP 422 and a clear message.
  QC box (approximate, keep it in `config.py` only): lat 14.58–14.77, lon 120.98–121.14.
- The response shape is `docs/contract/assess.sample.json`. **To change the shape, change that file
  first in its own PR, tell the lead, then update backend `schemas.py` and frontend together.**

Out of scope for now (do not build unless the lead says so): historical replay endpoints, live Himawari
satellite download, SQLite database, WebSockets, user accounts, deployment.

## 6. Safety rules (these matter — it's a disaster app)

1. A mock cyclone result must ALWAYS have `"status": "demo"`, `"is_demo": true`, and a warning text.
   The UI must show a visible "DEMO" badge on it. Never show fake data as real.
2. If the PAGASA fetch or parsing fails, return `"status": "unavailable"` or `"parse_error"` and
   `"alert_level": "unknown"`. NEVER return "None" / "no warning" because a fetch failed.
   Keep the original advisory text in `raw_text`.
3. The flood scenario (5/25/100-year) is chosen by the user. It is NOT picked from the cyclone category.
   Label it "Static flood hazard scenario — not a live flood forecast".
4. The model's cyclone category is NOT an official PAGASA wind signal. Never call it a "Signal No."
5. Shelters from OpenStreetMap are `"is_verified": false` and the UI labels them "Unverified".
6. Every card shows its data status (LIVE / DEMO / STALE / UNAVAILABLE) and a time.
7. Never say "safe" because a map layer has no flood polygon at a point.
8. No secrets in the repo. `.env` is git-ignored; `.env.example` lists the keys with dummy values.

## 7. Coding rules

- Small, readable code. Students must be able to explain every file in a defense. No clever tricks.
- Backend: type hints, pydantic models for every request/response, `httpx` with timeouts (10 s)
  for external calls, one function per job. Add a pytest test for each service.
- Frontend: function components + hooks, no Redux, no UI framework unless the lead approves.
  All backend calls go through `src/api/client.js`. Handle loading, error, and empty states.
- Add a dependency only if needed, and mention it in the PR description.
- Don't reformat or rewrite files you weren't asked to touch.

## 8. Git rules

- Never commit directly to `main`. Branch → Pull Request → lead reviews → "Squash and merge".
- Branch names: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
  Examples: `feat/backend-assess-mock`, `feat/frontend-shell`, `fix/pagasa-timeout`.
- Before starting work each day: `git switch main`, `git pull`, then `git switch <your-branch>` and `git merge main`.
- Commit messages: short, present tense: "Add mock assess endpoint".
- One task = one branch = one PR. Keep PRs small (ideally under ~400 changed lines).

## 9. How to run

Backend (Windows PowerShell, from `backend/`):
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Open http://127.0.0.1:8000/docs to test endpoints.

Frontend (from `frontend/`):
```
npm install
npm run dev
```
Open http://localhost:5173.

## 10. For AI agents specifically

- Before coding: read this file, `docs/PROGRESS.md`, and `docs/contract/assess.sample.json`.
- For anything bigger than one small change, propose a short plan and wait for approval.
- After finishing a task: run the tests / start the server to check it works, then add one line
  to the "Log" section of `docs/PROGRESS.md`.
- If you are unsure about a requirement, ASK instead of guessing. Do not invent model details
  (input names, normalization, class order) — those come from Team A only.
- Do not run `git push`, `git reset --hard`, or delete files without asking the human first.
