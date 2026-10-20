# AGAP Team B Playbook

Oct 17, 2026 · @Tristan Alonzo

The complete set list for Team B (Tristan, Kurt, Marcus), from installing tools to the final demo. Follow it top to bottom; when stuck, use the prompt library and troubleshooting table before asking anyone.

## Start here

The repo remembers the project so no AI chat has to. Every AI session starts by reading two files in the repo, and those files carry every decision.

1. **The starter kit** (`agap-starter-kit.zip`, sent in chat) is the first commit of the repo. It holds:
   - `AGENTS.md` — the rules every AI tool follows (stack, folders, API, safety rules, git rules). Claude Code, Gemini, Copilot and Cursor all read it.
   - `CLAUDE.md` — one line that makes Claude Code load `AGENTS.md` and `PROGRESS.md` automatically.
   - `docs/PROGRESS.md` — who owns what, decisions, open questions, and a one-line-per-task log.
   - `docs/contract/assess.sample.json` — the exact shape of the main API response. Backend builds it, frontend reads it.
   - `docs/reference/` — Feudo's architecture guide, the APIs doc and the task allocation, as background.
2. **This playbook** is the human set list. Work through it top to bottom, one task at a time.
3. **No Claude Project needed.** The repo replaces it. For a fresh claude.ai chat, drag in `AGENTS.md` + `PROGRESS.md` and use the context-setter prompt (Prompt library).
4. **Golden rule for long chats:** one task = one Claude Code session (`/clear` between tasks) and one claude.ai chat per problem. Long sessions forget and drift.
5. **When a decision changes**, change `AGENTS.md` or `PROGRESS.md` in a PR. Never only in a chat.

Share this doc with Kurt and Marcus (Share menu, top right) so they can follow their parts. Phase 0A, Phase 0C, the git loop, the set lists, the prompt library and troubleshooting are written for them too.

## Decisions already made

These are settled. Don't reopen them unless something is truly blocked, and then change `AGENTS.md` in a PR.

| Topic | Decision | Why |
| --- | --- | --- |
| Backend | Python 3.14 + FastAPI + uvicorn + pydantic + httpx + beautifulsoup4 | Matches Team A's Python model; auto-generated test page at `/docs` |
| Frontend | React + Vite, JavaScript (no TypeScript), plain CSS | Most common setup; every AI tool writes it well; less to learn |
| Map | MapLibre GL + pmtiles | What the APIs doc already specifies for the NOAH flood tiles |
| Database | None for now (JSON files + memory) | Nothing needs saving yet; SQLite is a stretch goal |
| Repo | One public GitHub repo `agap` on Tristan's account, folders `backend/`, `frontend/`, `docs/` | One place to clone; public allows free branch protection |
| Model file | `backend/app/weights/agap_tc_classifier.onnx` | Keeps "models" free for pydantic schemas; over 50 MB stays on Drive |
| API contract | `docs/contract/assess.sample.json` is the source of truth | Backend and frontend never guess each other's fields |
| Dev ports | Backend 8000, frontend 5173, Vite proxies `/api` and `/health` | No CORS errors in development |
| Out of scope (for now) | Historical replay, live Himawari download, SQLite, WebSockets, deployment, login | The guide is reference only (Feudo's comment); these come back only if time allows |
| Integration | Luke + Kurt; Tristan reviews | Confirmed by Team A |
| Who picks backend/frontend | Kurt = frontend, Marcus = backend; Tristan takes repo, contract, flood map, reviews | Already filled in the kit's `PROGRESS.md` |

Tell Feudo the model path today so Team A delivers to the right folder:

> Hi Feudo, for the ONNX file please put it in `backend/app/weights/agap_tc_classifier.onnx` instead of `/backend/models/` (that folder name clashes with our code). If it's over 50 MB, upload it to the Drive instead and we'll download it. Also please send `preprocessing.json` (input name, shape, normalization, class order) and 3–5 test frames with their expected outputs when the model is ready. Salamat!

## Timeline

&#91;embedded content: Team B roadmap · 5 phases, 5 gates\]

Only Phases 0 and 1 have fixed dates. Phase 3 starts when Team A delivers, and Phase 4 counts back from the final deadline (not known yet; add it to `PROGRESS.md`).

## Tools and models

Claude Code is the hands (it edits files and runs commands in the repo); claude.ai chat is the brain (explains, plans, reads screenshots). On Claude Pro both draw from one shared usage limit that resets every 5 hours, with a weekly cap on top.

| Who | Tool | Use it for | Model |
| --- | --- | --- | --- |
| Tristan | Claude Code (terminal, opened inside the `agap` folder) | Scaffolding, the flood map, building features, reviewing PRs, fixing a teammate's branch | `/model opusplan` as default (Opus plans, Sonnet writes). `/model sonnet` for small edits. `/model opus` for a nasty bug or a PR review |
| Tristan | claude.ai chat | Understanding a concept, reading a teammate's screenshot/error, writing GC messages, choosing between options, a fresh look when Code is looping | Opus for thinking and reviews; Sonnet for quick questions |
| Kurt / Marcus | Gemini app (Gemini 4 Argon) | Hard bugs, "review my code against AGENTS.md", explanations. Argon runs out fast, so save it for the hard stuff | Argon for hard problems; Flash for everyday questions |
| Kurt / Marcus | An agent that edits files: Antigravity, Gemini CLI, or Copilot agent mode in VS Code | Doing the tasks in this playbook inside the repo. First line of every session: "Read AGENTS.md and docs/PROGRESS.md first." | Whatever the tool offers; Argon only when stuck |
| Kurt / Marcus | GitHub Copilot (free for verified students through GitHub Education) | Autocomplete while typing, quick agent edits in VS Code | Default |

**The working loop (Tristan; teammates do the same with their tools):**

1. **Unclear what to build?** claude.ai chat, Opus: drag in `AGENTS.md`, paste the task from this playbook, ask for a plain-English plan.
2. **Build:** Claude Code. Press `Shift+Tab` until the footer says plan mode, paste the task prompt, read the plan, approve it.
3. **Test it yourself:** run the server, open the page, click around. Don't trust "done" until you've seen it work.
4. **Error?** Paste it into the same Code session first (it can see the files). After two failed fixes: `/clear` and use the Stuck prompt. Still stuck: claude.ai chat with a screenshot + the error for a fresh look, then bring the answer back to Code.
5. **Done:** run the End-of-session prompt (updates `PROGRESS.md`, commits). Then `/clear` before the next task.

**Saving usage:** Opus uses the limit faster than Sonnet, so plan with Opus and build with Sonnet. Use one task per session and `/compact` if a session gets long. Let Code read files itself instead of pasting them into chat. If you hit the limit, spend the wait reviewing PRs on GitHub or testing; it comes back within 5 hours.

## Phase 0A — Everyone installs the tools

All three of you do this (about 30 minutes). Commands go in **PowerShell**: press the Windows key, type `PowerShell`, open "Windows PowerShell". Paste with right-click. After each install, close PowerShell and open a new one so it sees the new program.

1. **Allow scripts once** (needed for Python environments and npm). Paste this, press Enter, type `Y`, Enter:
   - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
2. **Git.** Go to [git-scm.com/downloads/win](https://git-scm.com/downloads/win) and download "Git for Windows". Run it and click Next on every screen (keep the defaults, including Git Credential Manager). Check: `git --version` prints a version.
3. **Tell Git who you are** (use the same email as your GitHub account):
   - `git config --global user.name "Your Name"`
   - `git config --global user.email "you@example.com"`
   - `git config --global init.defaultBranch main`
4. **GitHub account.** Sign up at [github.com](https://github.com) if you don't have one. Send your username to Tristan. Optional: apply at [GitHub Education](https://education.github.com/benefits) with your TIP email for free Copilot.
5. **Python 3.14.** Go to [python.org/downloads/windows](https://www.python.org/downloads/windows/), download the latest **Python 3.14.x** "Windows installer (64-bit)". On the FIRST screen, tick **"Add python.exe to PATH"**, then Install Now. Check: `py --version` prints 3.14.x. Don't install 3.15 yet: onnxruntime (which runs Team A's model) has no Windows build for it.
6. **Node.js.** Go to [nodejs.org](https://nodejs.org), download the **LTS** installer, and click Next through it. Check: `node -v` and `npm -v` both print versions.
7. **VS Code.** Install from [code.visualstudio.com](https://code.visualstudio.com). In the installer, tick both "Add 'Open with Code' action" boxes. Then in VS Code → Extensions (left bar, four squares) install **Python** (by Microsoft).
8. **Tristan only — Claude Code.** In PowerShell: `irm https://claude.ai/install.ps1 | iex`. Close and reopen PowerShell. Run `claude --version`, then `claude`, and log in with your Claude Pro account in the browser that opens. If anything fails, run `claude doctor` and paste its output into claude.ai chat.

**Done when** `git --version`, `py --version`, `node -v` (and `claude --version` for Tristan) all print versions.

On a Mac: same downloads from the same sites, use the Terminal app, type `python3` instead of `py`, and skip step 1.

## Phase 0B — Tristan creates the repo

Do this today (Sat Oct 17), about 20 minutes. At the end, the repo is on GitHub, protected, and Kurt and Marcus are invited.

1. **Make a home for code.** In File Explorer create `C:\dev`. Don't put code on the Desktop or in Documents: if OneDrive syncs those, it chokes on `node_modules` (thousands of files).
2. **Unpack the kit.** Right-click `agap-starter-kit.zip` → Extract All. Rename the extracted `agap-starter-kit` folder to `agap` and move it to `C:\dev\agap`.
3. **Add the Drive data files.** Inside `C:\dev\agap` create the folders `backend\app\static`. From the Drive's `02_configs_and_resources`, download `qc_hotlines.json`, `debris_matrix.json` and both `historical_tc_manifest…` files into `backend\app\static`. Do NOT copy `TCIR_filtered.h5.zip` (too big for GitHub; it's Team A's).
4. **Create the empty repo.** On [github.com](https://github.com): top-right **+** → **New repository**. Name: `agap`. Visibility: **Public**. Leave "Add a README", ".gitignore" and "license" all OFF (the kit has them). Click **Create repository**.
5. **Push the kit.** In PowerShell, one line at a time (replace `YOUR-USERNAME`):
   - `cd C:\dev\agap`
   - `git init`
   - `git add -A`
   - `git commit -m "Add starter kit"`
   - `git branch -M main`
   - `git remote add origin https://github.com/YOUR-USERNAME/agap.git`
   - `git push -u origin main`
   - The first push opens a browser to sign in to GitHub. Approve it. Refresh the repo page; the files should be there.
6. **Invite Kurt and Marcus.** Repo page → **Settings** → **Collaborators** (left menu) → **Add people** → type each username → **Add to repository**. They must accept the email/notification (it expires after 7 days).
7. **Protect `main`.** Settings → **Branches** → **Add classic branch protection rule**. Branch name pattern: `main`. Tick **Require a pull request before merging**, and UNtick **Require approvals** (so you can merge your own PRs). Click **Create**. Leave "Do not allow bypassing" off so you can still fix emergencies. If GitHub shows "Rulesets" instead, screenshot the page and ask claude.ai chat: "Walk me through requiring a pull request on main with 0 approvals."
8. **Auto-clean branches.** Settings → **General** → scroll to Pull Requests → tick **Automatically delete head branches**.
9. **Check Claude Code sees the rules.** In PowerShell: `cd C:\dev\agap`, then `claude`. Approve the "trust this folder" prompt. Ask: `Summarize this project's rules in 5 bullets.` If it mentions FastAPI, React, the demo badge and the PAGASA "unknown" rule, it has loaded `AGENTS.md`. Type `/exit`.
10. **Tell the team.** Post in the GC: the repo link, "accept the invite", and this doc (Share → copy link, set to anyone with the link).

## Phase 0C — Kurt and Marcus join and run the project

Steps 1–3 can happen as soon as the invite arrives. Steps 4–6 wait until Tristan posts "skeleton is on main" (Phase 1, task L1).

1. **Accept the invite.** Open the GitHub email, or [github.com/notifications](https://github.com/notifications), and click **Accept invitation**.
2. **Get the code.** In PowerShell (replace `TRISTAN-USERNAME`):
   - `mkdir C:\dev` (skip if it exists)
   - `cd C:\dev`
   - `git clone https://github.com/TRISTAN-USERNAME/agap.git`
   - `cd agap`
   - `code .` (opens the folder in VS Code)
3. **Read `AGENTS.md`** in VS Code (10 minutes). It is the rulebook your AI tool will follow too.
4. **Update and run the backend.** In VS Code: **Terminal → New Terminal** (it opens in the `agap` folder):
   - `git pull`
   - `cd backend`
   - `py -m venv .venv` (first time only; makes a private Python for this project)
   - `.\.venv\Scripts\Activate.ps1` (the prompt now starts with `(.venv)`)
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`
   - Open <http://127.0.0.1:8000/docs> → click `POST /api/v1/telemetry/assess` → **Try it out** → **Execute**. You should see the demo JSON. Until B1 is merged only GET /health/live exists, so try that one instead.
5. **Run the frontend.** Click **+** in the terminal panel for a second terminal (leave the backend running):
   - `cd frontend`
   - `npm install` (first time, and whenever `package.json` changes)
   - `npm run dev`
   - Open <http://localhost:5173>. You should see the app with a DEMO cyclone card.
6. **Set up your AI agent** in the same folder. Copilot: VS Code → sign in with GitHub → open Copilot Chat → switch to Agent. Gemini: open `C:\dev\agap` in Antigravity, or run Gemini CLI inside it. Start every session with: `Read AGENTS.md and docs/PROGRESS.md first.`

**Every day after this,** you only need: activate (`.\.venv\Scripts\Activate.ps1`) + `uvicorn …` in one terminal, and `npm run dev` in the other. Re-run `pip install -r requirements.txt` or `npm install` when a teammate adds a library.

**Done when** both pages load on your laptop. Post a screenshot in the GC.

## The daily git loop

Every task follows this cycle: fresh `main` → your own branch → commits → Pull Request → Tristan merges. Run the commands in the `agap` folder (in VS Code's terminal, `cd ..` first if you're inside `backend` or `frontend`).

1. **Start a new task** (branch names come from the set lists below):
   - `git switch main`
   - `git pull`
   - `git switch -c feat/backend-assess-mock`
2. **Work, then save a checkpoint** after every piece that works (at least once an hour):
   - `git status` (lists what changed; check nothing weird like `.env` shows up)
   - `git add -A`
   - `git commit -m "Add mock assess endpoint"`
3. **Upload your branch:**
   - first time: `git push -u origin feat/backend-assess-mock`
   - after that: `git push`
4. **Open the Pull Request.** On the repo page a yellow bar says **Compare & pull request**; click it. Title = what it does. In the description paste the PR template below, then **Create pull request**. On the right, click the gear next to **Reviewers** and pick Tristan. Post the PR link in the GC.
5. **Continuing the next day** on the same branch, pull in everyone else's merged work first:
   - `git switch main`
   - `git pull`
   - `git switch feat/backend-assess-mock`
   - `git merge main` (if it says CONFLICT, see Troubleshooting)
6. **Tristan merges:** PR page → **Squash and merge** → **Confirm**. Then post "merged, pull main" in the GC.
7. **After your PR is merged:**
   - `git switch main`
   - `git pull`
   - `git branch -d feat/backend-assess-mock`

**PR template** (paste into every PR description):

```markdown
## What this does
- 

## How to test
1. 

## Screenshot / output

## Checklist
- [ ] I ran it and it works on my laptop
- [ ] Follows AGENTS.md (demo labels, "unknown" on failure, no secrets)
- [ ] Added a line to docs/PROGRESS.md
```

**Never:** commit straight to `main`, run `git push --force`, or commit `.env`, `.venv`, `node_modules` (the `.gitignore` blocks these, but check `git status`).

## Phase 1 set list — until the Oct 20 progress update

Goal for Tuesday: the backend returns a demo result, the app shows it with a DEMO badge, and the map shows one NOAH flood layer over QC. Each task below has a branch name, the prompt to paste into your AI agent, and a "done when" check. Paste prompts in plan mode (Claude Code: `Shift+Tab`) and approve the plan before it builds.

**Update Oct 19:** Kurt already built a standalone React + Vite app from the mockup. It becomes the frontend base: Kurt pushes it to `frontend/` on branch `feat/frontend-kurt`, then Tristan adapts it (proxy, `client.js`, contract mock data) before merging. L1 then only needs the backend half.

| When | Who | Task |
| --- | --- | --- |
| Sun Oct 18, by noon | Tristan | L1 skeleton merged → post "skeleton is on main" |
| Sun Oct 18 | Kurt, Marcus | Phase 0C, then Marcus starts B1 and Kurt starts F1 |
| Sun–Mon | Tristan | L2 flood map |
| Mon Oct 19, 6 PM | Everyone | PRs open |
| Mon Oct 19, 10 PM | Tristan | Reviews + merges, F2-lite switch, screenshots for Tuesday |

### L1 — Skeleton (Tristan) · branch `feat/skeleton`

Everyone else is blocked until this is on `main`, so keep it small.

```text
Read AGENTS.md, docs/PROGRESS.md and docs/contract/assess.sample.json.
Create only the empty project skeleton from AGENTS.md section 4. Teammates build the features.

Backend (backend/):
- app/main.py: FastAPI app, CORS allowing http://localhost:5173, includes the health router.
- app/config.py: settings from environment variables with defaults: QC_LAT_MIN=14.58, QC_LAT_MAX=14.77, QC_LON_MIN=120.98, QC_LON_MAX=121.14, PAGASA_URL, MOCK_INFERENCE=true, ONNX_MODEL_PATH=app/weights/agap_tc_classifier.onnx.
- app/api/health.py: GET /health/live -> {"status": "ok"}.
- Empty placeholder files (a docstring only) for api/hotlines.py, api/telemetry.py, api/shelters.py, services/inference.py, services/pagasa.py, services/shelters.py, schemas.py.
- requirements.txt with pinned versions (fastapi, uvicorn[standard], pydantic, pydantic-settings, httpx, beautifulsoup4, pytest), .env.example, tests/test_health.py.

Frontend (frontend/):
- Vite + React with JavaScript (no TypeScript). Use non-interactive flags so nothing waits for input.
- vite.config.js proxies /api and /health to http://127.0.0.1:8000.
- src/mocks/assess.sample.json = copy of docs/contract/assess.sample.json.
- src/api/client.js: export const USE_MOCK = true; getAssessment(lat, lon, years) returns the mock when USE_MOCK is true, else POSTs to /api/v1/telemetry/assess; getHotlines() GETs /api/v1/hotlines.
- App.jsx: shows "AGAP" and the cyclone category_name from getAssessment(14.65, 121.05, 25) with a DEMO badge.
- npm install maplibre-gl pmtiles (don't use them yet).

Show me the plan first. After I approve: build it, run pytest, start both servers to confirm they work, then stop them and tell me the exact run commands for Windows PowerShell. Add a line to docs/PROGRESS.md. Do not git push.
```

**Done when:** `/health/live` shows `{"status":"ok"}` and `localhost:5173` shows "Typhoon" + DEMO. Commit, push, open the PR, merge it yourself, and post "skeleton is on main, do Phase 0C now" in the GC.

### L2 — Flood map (Tristan) · branch `feat/flood-map`

1. Find the real layer name first. Open [pmtiles.io](https://pmtiles.io) and paste `https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/layers/flood_25yr.pmtiles`. Note the vector layer name it lists. If the viewer can't open it, Claude Code's plan should include a small script that prints the metadata (prompt below covers this).
2. Prompt:

```text
Read AGENTS.md and section 2 of docs/reference/apis_and_endpoints.md.
Build frontend/src/components/FloodMap.jsx with maplibre-gl + pmtiles:
- Esri World Light Gray basemap (URL in the doc), center [121.05, 14.65], zoom 12, minZoom 10, maxZoom 17.
- NOAH flood layer from the smaller per-scenario files under PMTiles/layers/ (flood_5yr, flood_25yr, flood_100yr). First write a tiny Node script in frontend/scripts/ that prints each file's vector layer names using the pmtiles library, run it, and use the real names. Tell me what it printed.
- Fill colored by the numeric Var attribute: 1 #fde047, 2 #fb923c, 3 #ef4444, opacity 0.55.
- A 5 / 25 / 100-year toggle (default 25) that is independent of the cyclone category.
- Legend (Low / Medium / High), attribution (Esri, Project NOAH via BetterGovPH, ODbL), and the label "Static flood hazard scenario - not a live flood forecast".
- Show a friendly error message if tiles fail to load.
- Put the map in App.jsx under the existing content for now.
Plan first. After I approve, build it and tell me what to check in the browser DevTools Network tab to confirm the tiles load.
```

**Done when:** the map shows colored flood areas over QC and the toggle switches scenarios. If it's blank, see Troubleshooting → "Map is blank".

### B1 — Mock assess API (Marcus) · branch `feat/backend-assess-mock`

```text
Read AGENTS.md, docs/PROGRESS.md and docs/contract/assess.sample.json first.
Task: build the mock assess API in backend/.
1. app/schemas.py: pydantic v2 models that match docs/contract/assess.sample.json exactly (same field names, types and nulls), plus AssessRequest {latitude: float, longitude: float, flood_return_period_years: 5|25|100 = 25}.
2. app/services/inference.py: get_cyclone_assessment() returns the demo cyclone object (status "demo", is_demo true, TY / Typhoon / 140.0, confidence null, warning "Mock result for development. Not a real prediction.").
3. app/api/telemetry.py: POST /api/v1/telemetry/assess. Reject coordinates outside the QC box from config.py with HTTP 422 and a clear message. Build the full response: cyclone = mock; rainfall_warning = status "unavailable", alert_level "unknown" (the scraper comes later); flood_scenario = chosen years, hazard_level null, lookup_status "not_implemented"; nearest_shelter = status "unavailable"; data_status lists the unavailable parts. New uuid per call; timestamps ISO 8601 in Asia/Manila time.
4. app/api/hotlines.py: GET /api/v1/hotlines returns app/static/qc_hotlines.json. Open that file first and describe its structure to me before writing code.
5. app/api/shelters.py: GET /api/v1/shelters returns app/static/qc_shelters.geojson, or an empty GeoJSON FeatureCollection if the file doesn't exist yet.
6. Register all routers in app/main.py.
7. backend/tests/test_api.py with pytest: assess OK; outside QC -> 422; years=10 -> 422; hotlines OK; shelters OK.
Explain your plan and wait for my OK. After building: run pytest, start the server, and tell me what to click in http://127.0.0.1:8000/docs to check it. Add a line to docs/PROGRESS.md. Don't push.
```

**Done when:** `pytest` passes and Execute on `/assess` in `/docs` returns JSON shaped like the contract.

### F1 — App shell from the mockup (Kurt) · branch `feat/frontend-shell`

First: open the CS++ link in `project_mockup.md` (Drive), copy its HTML, CSS and JS into `docs/reference/mockup/mockup.html`, `mockup.css`, `mockup.js`, and include them in this branch.

```text
Read AGENTS.md, docs/PROGRESS.md, docs/contract/assess.sample.json and the mockup in docs/reference/mockup/.
Task: turn the mockup into the React app shell in frontend/.
- Keep the mockup's look (colors, fonts, spacing, layout) but split it into components in src/components/: Header, CycloneCard, RainfallCard, FloodSection (an empty box where Tristan's FloodMap goes), ShelterCard, HotlinesScreen (placeholder), StatusBadge. If the mockup has sections I didn't list, tell me and suggest where they go.
- All data comes from getAssessment() in src/api/client.js (it returns the mock JSON for now). Components read only fields that exist in the contract. No fake data hard-coded in components, no direct fetch calls outside client.js.
- StatusBadge shows LIVE / DEMO / STALE / UNAVAILABLE. CycloneCard shows a very visible DEMO badge when is_demo is true and never calls the category an official signal.
- Mobile first: must look right at 390px wide. Plain CSS, no UI library.
Show the plan and wait for my OK. After building, run npm run dev and tell me what I should see. Add a line to docs/PROGRESS.md. Don't push.
```

**Done when:** the app at `localhost:5173` looks like the mockup, shows the demo data, and has the DEMO badge.

### Monday night (Tristan)

1. Review and merge B1, F1, L2 (see Prompt library → Review a PR).
2. On `main`, set `USE_MOCK = false` in `client.js` (branch `feat/use-real-api`), check the app now shows data from the real backend, merge.
3. Take 3 screenshots (app, `/docs`, map) and write the update: done / next / blockers. Use the Progress update prompt.

## Phase 2 set list — real features (from Oct 21)

Goal: every card shows real data or an honest "unavailable", except the cyclone card (still DEMO until Phase 3). Order inside each role matters; across roles, work in parallel.

### B2 — PAGASA rainfall-warning scraper (Marcus) · `feat/pagasa-scraper`

Step 0, no code (15 min). Open the [PAGASA rainfall warning page](https://bagong.pagasa.dost.gov.ph/weather/rainfall-warning) in Chrome.

1. Right-click → **View page source** → `Ctrl+F` for a word you can see on the page (e.g. "Metro Manila" or "Rainfall"). Found it = the text is in the HTML. Not found = the page loads it with JavaScript.
2. If not found: press `F12` → **Network** → **Fetch/XHR** → reload. Click each request and look in **Response** for the warning text. That request's URL is what you scrape instead.
3. Save a copy of what you found (HTML or JSON) to `backend/tests/fixtures/pagasa_sample.html` (or `.json`). Tell your AI which case it is.

```text
Read AGENTS.md (especially safety rule 2), docs/PROGRESS.md and section 3 of docs/reference/apis_and_endpoints.md.
Task: app/services/pagasa.py, a replaceable adapter that fetches the PAGASA rainfall warning and returns the rainfall_warning object from docs/contract/assess.sample.json.
- Source: [HTML page / JSON endpoint I found: PASTE URL]. A saved sample is in backend/tests/fixtures/.
- httpx with a 10 s timeout and a normal browser User-Agent. Cache the last good result for 10 minutes (configurable in config.py) so we don't hit PAGASA on every request.
- Extract: alert level exactly as published (Yellow/Orange/Red), affected area text, issued time, valid-until if present, and the full original text in raw_text.
- status: "fresh" when parsed now; "stale" when serving a cached result older than the cache window because the fetch failed; "unavailable" when it can't be reached and there is no cache; "parse_error" when the page changed. In all failure cases alert_level is "unknown". Only return alert_level "None" if the page explicitly says there is no warning.
- Mark whether the warning covers Metro Manila / NCR; never claim QC is affected unless the text says so.
- Wire it into POST /api/v1/telemetry/assess.
- Tests with saved fixtures: active warning, no warning, malformed page, timeout. No live network in tests.
Plan first and wait for my OK.
```

**Done when:** tests pass and `/assess` shows `"status":"fresh"` with real text (or an honest "unavailable" with the page down).

### B3 — Shelters + nearest shelter (Marcus) · `feat/shelters`

Step 0, no code (10 min): open [overpass-turbo.eu](https://overpass-turbo.eu), paste the query from section 4 of `apis_and_endpoints.md`, click **Run**, then **Export → GeoJSON → download**. Save it as `backend/app/static/qc_shelters.geojson`. If it returns 0 results, see Troubleshooting.

```text
Read AGENTS.md (safety rule 5), docs/PROGRESS.md and section 4 of docs/reference/apis_and_endpoints.md.
Task: app/services/shelters.py.
- Load backend/app/static/qc_shelters.geojson once at startup. Points stay points; polygons (ways/relations) become one point at their center (simple average of coordinates is fine). Keep the OSM id, name (or "Unnamed shelter"), and tags.
- nearest_shelter(lat, lon): Haversine straight-line distance in meters; return the nearest_shelter object from docs/contract/assess.sample.json with is_verified false. Return status "no_shelter_data" if the file is missing or empty.
- Wire it into POST /api/v1/telemetry/assess, and make GET /api/v1/shelters return the cleaned points with is_verified false.
- Tests: Haversine between two known points (+-1%), nearest of 3 fake shelters, missing file.
Plan first and wait for my OK.
```

**Done when:** `/assess` returns a real nearby shelter name and distance.

### F2 — Live data + refresh (Kurt) · `feat/frontend-live`

```text
Read AGENTS.md, docs/PROGRESS.md and docs/contract/assess.sample.json.
Task: src/hooks/useAssessment.js and wiring in App.jsx.
- Location: ask for the browser's location with a short explanation first ("to find your nearest shelter"). If denied or unavailable, use a manual fallback: a small "Set location" input (lat/lon) defaulting to Quezon Memorial Circle (14.6516, 121.0493).
- Call getAssessment(lat, lon, years) on load, then every 60 seconds. Pause polling when the tab is hidden (document.visibilityState). Don't start a new request while one is running.
- Refresh: a Refresh button plus pull-to-refresh on mobile (simple touch handler, no library).
- States: loading skeleton, error message with a Retry button, and "Updated X min ago". If the last success is older than 5 minutes, show STALE on every card.
- Show the backend's 422 message when the location is outside QC.
- The flood toggle value (5/25/100) is shared between the map and the request.
Plan first and wait for my OK.
```

**Done when:** the cards update by themselves every minute (watch the Network tab) and the Refresh button works on your phone.

### F3 — Status wording + hotlines screen (Kurt) · `feat/frontend-hotlines`

```text
Read AGENTS.md (safety rules 1-7) and docs/PROGRESS.md. Look at GET /api/v1/hotlines in http://127.0.0.1:8000/docs to see the real hotline fields.
Task:
- HotlinesScreen: list every hotline with its name, displayed number and description. Tapping calls it with href="tel:" + dial_string. Show the catalog's verification date. Cache the last good list in localStorage (wrapped in try/catch) so it shows offline with a "cached, may be outdated" note.
- RainfallCard wording: when alert_level is "unknown", say "Couldn't check PAGASA right now. This does NOT mean there is no warning." and link to the PAGASA page. Show raw_text in a "Full advisory" expandable section.
- ShelterCard: name, distance (m or km), and an "Unverified" tag, with a note to confirm with the barangay.
- Every card: StatusBadge plus the relevant time (issued, retrieved, or generated).
Plan first and wait for my OK.
```

**Done when:** tapping a hotline on your phone opens the dialer, and every card shows a status and a time.

### L3 — Map extras + layout (Tristan) · `feat/map-shelters`

```text
Read AGENTS.md and docs/PROGRESS.md.
Task: in FloodMap.jsx, add (1) shelter markers from GET /api/v1/shelters with a popup (name, "Unverified"), (2) the user's location marker, (3) the nearest shelter from the assessment highlighted. Then place FloodMap inside the frontend's FloodSection so it fits the mockup layout on a 390px-wide screen.
Plan first and wait for my OK.
```

**Done when:** the map shows you, nearby shelters, and the nearest one stands out.

## Phase 3 — Model integration (Luke + Kurt, Tristan reviews)

Starts only when Team A hands over everything in the checklist below. Until then the cyclone card stays DEMO, and that's fine.

**Handoff checklist (send to Feudo when they say the model is ready):**

- [ ] `agap_tc_classifier.onnx` (in `backend/app/weights/`, or on Drive if over 50 MB)
- [ ] `preprocessing.json`: input name, shape, dtype, normalization steps, channel handling, class order (TD, TS, STS, TY, STY?), whether there is a wind output and its unit
- [ ] 3–5 test frames as `.npy` files, already preprocessed, plus the expected class and probabilities for each
- [ ] `test_inference.py` that produces those expected outputs
- [ ] Which storms were used in training (so we don't call a training storm a "test")

**Demo input decision:** live Himawari download is out of scope. The model runs on Team A's archived test frames. The UI says so honestly: "Model result on archived frame: \<storm>, \<date>". This matches the guide's "historical replay" idea in its simplest form.

Before I1 starts, Tristan updates `AGENTS.md` section 5 in a small PR: move "historical replay endpoints" from out of scope into the API table, and add a Decisions line to `PROGRESS.md`. Otherwise the agents will refuse or skip it.

### I1 — Real inference (Kurt + Luke) · `feat/onnx-inference`

```text
Read AGENTS.md, docs/PROGRESS.md, section 7 of docs/reference/architecture_implementation_guide.md, backend/app/static/preprocessing.json, and Team A's test_inference.py.
Task: replace the mock with real ONNX inference, keeping mock mode as an explicit switch.
- app/services/inference.py: an InferenceService that loads backend/app/weights/agap_tc_classifier.onnx with onnxruntime when MOCK_INFERENCE=false. Check input/output names and shapes against preprocessing.json at startup and fail with a clear error if they don't match or the file is missing. Never fall back to mock silently.
- Use ONLY the preprocessing, class order and output names from preprocessing.json. Don't assume normalization or channel repetition.
- Softmax the logits; confidence_is_calibrated stays false. If there is a wind output, add a warning when it disagrees with the class's wind range.
- Demo frames: backend/app/static/demo_frames/ with the .npy files and frames.json (frame_id, storm name, UTC time, reference category + source). New endpoints: GET /api/v1/replay/frames and POST /api/v1/replay/assess {frame_id}. Response = the same contract with run_context.mode "historical_replay", observation_id = frame_id, and a separate evaluation_reference object. The reference label must never be fed to the model or copied into cyclone_assessment.
- Tests: for each test frame, our output class matches Team A's expected class, and probabilities match within 1e-4.
Plan first and wait for my OK.
```

**Done when:** `pytest` reproduces Team A's expected outputs and `MOCK_INFERENCE=false` serves real predictions.

### I2 — Replay UI (Kurt) · `feat/replay-ui`

```text
Read AGENTS.md and docs/PROGRESS.md. Look at GET /api/v1/replay/frames and POST /api/v1/replay/assess in http://127.0.0.1:8000/docs.
Task: a "Past storms" view: a picker of demo frames (storm + date). On select, call replay/assess and show the CycloneCard labeled "Model result on archived frame" with storm and time, model confidence (labeled "uncalibrated model score"), and, in a separate box, the reference category with its source, plus a match / no-match tag. All calls go through client.js.
Plan first and wait for my OK.
```

**Tristan's review of I1** uses Opus (`/model opus`) and the Review a PR prompt, plus this extra line: `Check especially that no reference label can reach the model and mock mode can't turn on by accident.`

## Phase 4 — Polish, freeze, demo

The last stretch is about not breaking what works. Put the final deadline in `PROGRESS.md` as soon as it's known and count back from it.

1. **Feature freeze 3 days before the deadline.** After that, only bug fixes and wording get merged.
2. **Everyone can explain their own files.** Each person runs this on every file they own: `Explain backend/app/services/pagasa.py to me like I have to defend it to my professor: what it does, why it's built this way, and 3 questions he might ask with answers.`
3. **README:** run steps, screenshots, data sources and the disclaimer "prototype, not an official warning service". Use the Claude Code prompt `Update README.md so a classmate can run the project from zero on Windows. Check every command actually works.`
4. **Final checks** (one PR per fix):
   - [ ] DEMO badge appears whenever mock data shows
   - [ ] PAGASA failure shows "unknown", never "no warning" (test by pulling the Wi-Fi)
   - [ ] Flood toggle never changes when the cyclone category changes
   - [ ] Shelters say "Unverified"
   - [ ] Every card shows a status and a time
   - [ ] `pytest` passes; app has no red errors in the browser console
   - [ ] No secrets, `.env` or big data files in the repo
5. **Demo script (about 3 minutes), rehearse twice on the demo laptop:** open the app → location → walk through the 4 cards → switch flood scenario 5/25/100 → nearest shelter on the map → tap a hotline → Past storms: model result vs reference → turn Wi-Fi off and show the STALE/unknown states (the honesty feature).
6. **Backups:** record a screen video of the full demo the night before, and keep screenshots. The map needs internet, so the video is the fallback if campus Wi-Fi dies.
7. **Stretch goals, only if everything above is done:** offline app install (PWA via `vite-plugin-pwa`); online deployment (backend on a free host such as Render, frontend on Vercel or Netlify). After deploying, re-test the flood map: PMTiles loading can fail from a new web address (CORS).

## Prompt library

Copy, fill the \[brackets\], paste. Claude Code loads `AGENTS.md` and `PROGRESS.md` by itself; every other tool (claude.ai chat, Gemini, Copilot) needs them attached or the line "Read AGENTS.md and docs/PROGRESS.md first."

### Context setter — brand-new claude.ai chat (or Gemini)

Drag `AGENTS.md` and `docs/PROGRESS.md` into the chat first.

```text
I'm [Tristan / Kurt / Marcus], on Team B of Project AGAP, a CS 403 school project. The attached AGENTS.md has all our rules and decisions; PROGRESS.md has the current status. Treat them as the truth. If I say something that contradicts them, point it out.
I'm on task [ID and name from our playbook, e.g. "B2 PAGASA scraper"].
What I'm doing: [one or two sentences].
Problem or question: [paste the exact error or describe it].
What I've tried: [list].
Give me the shortest path to fix it, with exact Windows PowerShell commands. Ask at most 2 questions if you really need more info.
```

### Stuck — Claude Code after `/clear` (or any agent)

```text
I'm stuck on [task]. Goal: [what should happen].
What happens instead: [exact error text or what I see].
Already tried: [list].
Don't change any code yet. First investigate: read the relevant files and run commands to reproduce it. Then tell me the root cause in plain words and how sure you are. Then propose the smallest fix and wait for my OK.
```

### Looping — when the AI keeps trying the same fix

```text
Stop. That's the second failed attempt. Summarize what we know for sure, list 3 different possible causes, and give a quick test to confirm or rule out each one. Don't edit files until I choose.
```

### Review a PR (Tristan, Claude Code, `/model opus`)

First in PowerShell: `git fetch origin`, then `git switch BRANCH-NAME`, then start `claude`.

```text
Review this branch against main (use git diff main...HEAD). Check:
1. Follows AGENTS.md: safety rules, folder structure, stack, git rules.
2. Matches docs/contract/assess.sample.json exactly.
3. No secrets, .env, or big files.
4. Tests exist and pass. Run them, and start the app if needed.
5. Code a student could explain in a defense.
Reply with MUST FIX / SHOULD FIX / OK, each with file and line, plus a short, friendly comment I can paste on GitHub. Don't edit anything.
```

Paste the comments into the PR (**Files changed** → click a line, or **Conversation** tab). When it's fixed: **Squash and merge**. Afterwards: `git switch main` and `git pull`.

### Fix a teammate's branch (Tristan)

`git fetch origin` → `git switch THEIR-BRANCH` → `git pull` → `claude`, then:

```text
This is [Kurt/Marcus]'s branch for task [ID]. Their problem: [paste their GC message]. Investigate first, then fix it with the smallest change, and explain the fix in 3 sentences I can send them so they learn from it.
```

Then commit, `git push`, and tell them to run `git pull` on their branch.

### Git emergency ("I don't know what state I'm in")

Run `git status` and `git log --oneline -10`, then paste both outputs:

```text
I'm lost in git. Here are git status and git log --oneline -10: [paste]. Explain in plain words what state I'm in, and give me the safest commands to get back to a clean state without losing my work. Nothing destructive (no reset --hard, no force push) unless you explain exactly what I'd lose.
```

### End of session (every task, Claude Code)

```text
We're done with this task. 1) Run the tests and confirm the app starts. 2) Add one line to the Log in docs/PROGRESS.md and update the status in the owner table. 3) Show me git status and suggest a commit message. Don't push.
```

### Progress update (claude.ai chat; attach PROGRESS.md + screenshots)

```text
Write Team B's progress update from the attached PROGRESS.md and screenshots: Done / In progress / Next / Blockers. Max 120 words, plain English, ready to paste into our group chat.
```

### Explain something to a teammate (claude.ai chat, Sonnet)

```text
Explain [e.g. what a Pull Request is / what the Vite proxy does] to a classmate who has never used it, in 5 sentences, with one example from our project (AGENTS.md attached).
```

## Troubleshooting

Find your symptom, try the fix, and if it's still broken after 15 minutes use the Stuck prompt, then the unblock ladder in the next section.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `py` / `python` / `git` / `node` "is not recognized" | Not installed, not on PATH, or PowerShell opened before the install | Close and reopen PowerShell. Still failing: rerun the installer (Python: tick "Add python.exe to PATH") |
| "running scripts is disabled on this system" | Windows script policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y` |
| `No module named 'fastapi'` or `uvicorn` not recognized | Virtual environment not active | In `backend`: `.\.venv\Scripts\Activate.ps1` (look for `(.venv)`), then `pip install -r requirements.txt` |
| `pip install onnxruntime` fails | Python too new | Install Python 3.14 (not 3.15), delete `backend\.venv`, recreate it |
| "Address already in use" (8000 or 5173) | An old server is still running | Find the old terminal and press `Ctrl+C`, or close VS Code terminals and start again |
| App shows "Failed to fetch" or 404 on `/api/...` | Backend not running, or the proxy isn't loaded | Start the backend; restart `npm run dev` after editing `vite.config.js` |
| CORS error in the browser console | Frontend calls `http://127.0.0.1:8000` directly | Use relative URLs (`/api/...`) through `client.js` |
| `npm install` errors | Broken install | Delete the `frontend\node_modules` folder and run `npm install` again; still failing → paste the error to your AI |
| `git push` rejected: "fetch first" / non-fast-forward | The branch on GitHub has commits you don't | `git pull`, then `git push` |
| `git push` rejected: protected branch | You're on `main` | `git switch -c feat/your-task`, then `git push -u origin feat/your-task` |
| Committed on `main` by mistake (not pushed) | Forgot to branch | `git switch -c feat/your-task` (your commits come along). Then ask Tristan to clean up local `main` with you |
| `git push` 403 / permission denied | Invite not accepted, or logged in as another account | Accept the invite. Windows: Credential Manager → Windows Credentials → remove `git:https://github.com` → push again and log in |
| "CONFLICT" after `git merge main` | Two people edited the same lines | Open the file in VS Code, click Accept Current / Incoming / Both, save, `git add -A`, `git commit`. Unsure → Git emergency prompt or Tristan |
| Push fails: file over 100 MB | Model or dataset committed | `git rm --cached PATH-TO-FILE`, add it to `.gitignore`, commit, push. Big files live on Drive |
| Map is blank | Wrong URL or layer name, tiles blocked, or wrong zoom | `F12` → Network → filter `pmtiles`: red rows = URL/CORS problem; check the `source-layer` name with [pmtiles.io](https://pmtiles.io); check the Console for errors; zoom in on QC |
| Map has no color in some places | No mapped hazard polygon there | Correct behavior. Never label it "safe" |
| PAGASA scraper finds nothing | Page is built by JavaScript, or the site changed or is down | Redo B2 step 0 (Network tab). Down = `unavailable` is the correct output |
| Overpass returns 0 shelters or times out | The area-name lookup failed | In the query, replace each `(area.qc)` with the box `(14.58,120.98,14.77,121.14)` and run again |
| Phone can't open the app | Dev server only listens on the laptop | `npm run dev -- --host`, phone on the same Wi-Fi, open the "Network" URL it prints; allow Node in the Windows Firewall prompt |
| Location doesn't work on the phone | Browsers allow location only on https or localhost | Use the manual location input on the phone; test GPS on the laptop |
| Claude Code: usage limit reached | Shared Pro limit used up | Wait for the reset time it shows; meanwhile review PRs or test. Use Sonnet for routine work |
| AI ignores the rules or drifts | Session too long, or rules not loaded | `/clear` and restart the task; ask "Which AGENTS.md rules apply here?" to check |
| AI wants to run `rm`, `reset --hard` or `push --force` | Risky shortcut | Say no; ask what it's trying to do and for a safe way |
| AI invents model details (input name, normalization, classes) | No info from Team A | Stop it. Only `preprocessing.json` from Team A counts; ask Feudo |

## Leading Kurt and Marcus

Your job as lead is to keep both of them unblocked and working on the next task, not to write their code. Fast reviews and clear next steps matter more than anything else.

**The unblock ladder** (tell them this on day one):

1. **0–15 min:** the Troubleshooting table, then their AI with the Stuck prompt.
2. **15–60 min:** post in the GC using the Stuck template below. Don't stay stuck alone past an hour.
3. **Tristan answers:** a quick one → paste their message + screenshot into claude.ai chat with the context setter. A code one → pull their branch and use the Fix a teammate's branch prompt, then send them the 3-sentence explanation.
4. **Still stuck:** a 15-minute call with screen share (Messenger or Google Meet). Have them drive while you guide.

**Habits that keep a 3-person team moving:**

- Do Phase 0C together on a 30-minute call on Sunday. Setup problems are the worst to fix by text.
- Review every PR within 12 hours. A PR that waits blocks the next task.
- Hand out the next task before they finish the current one (the set lists give the order).
- If someone is a day behind, split their task: take a piece yourself (e.g. the hotlines screen from F3) instead of waiting.
- When you fix their code, explain it. They have to defend it too.
- Decisions go in `PROGRESS.md`, never only in the GC. If it's not in the repo, the AI tools don't know it.
- Thank people publicly when a PR lands.

**Stuck template** (pin this in the GC):

```text
STUCK — [task ID, e.g. B2]
Goal: [what should happen]
What happens: [exact error, screenshot]
Tried: [what you and your AI tried]
Branch: [feat/...] (pushed? yes/no)
```

**Daily check-in** (each person posts by 9 PM on working days):

```text
[Name] — Done: ... | Next: ... | Blocked: none / ...
```

**Nudge** (when someone is quiet for a day):

```text
Hi [name], kumusta yung [task]? Kung stuck ka, send mo lang yung error or i-push mo yung branch, titingnan ko. No pressure, gusto ko lang ma-unblock ka before [date].
```

**Giving the next task:**

```text
[Name], nice work on [task]! Merged na. Next mo: [task ID + name] — nasa playbook yung prompt, branch name and "done when". Target: [date].
```

## Sources

- [Claude Code setup (install on Windows, login)](https://code.claude.com/docs/en/setup)
- [Claude Code memory: CLAUDE.md, AGENTS.md, @imports](https://code.claude.com/docs/en/memory)
- [Claude Code model configuration: /model, opusplan](https://code.claude.com/docs/en/model-config)
- [Using Claude Code with Pro or Max: shared limits, 5-hour reset](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Gemini 4 Argon availability (Gemini app, API, Antigravity)](https://letsdatascience.com/news/google-releases-gemini-4-argon-for-scientific-computing-644a49ff)
- Team Drive: `architecture_implementation_guide.md`, `apis_and_endpoints.md`, `tasks_allocation` (copied into `docs/reference/`)
