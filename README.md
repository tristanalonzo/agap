# Project AGAP

Cyclone, rainfall-warning, flood-hazard, and shelter info for Quezon City. CS 403 Intelligent Agents final project.

- Team rules and setup for humans and AI tools: [AGENTS.md](AGENTS.md)
- Current status: [docs/PROGRESS.md](docs/PROGRESS.md)
- API response shape: [docs/contract/assess.sample.json](docs/contract/assess.sample.json)

## Run it

Backend (from `backend/`, Windows PowerShell):

```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (from `frontend/`):

```
npm install
npm run dev
```

Then open http://localhost:5173.

## Data sources

Project NOAH hazard maps (BetterGovPH, ODbL), DOST-PAGASA, OpenStreetMap contributors (ODbL), Esri basemap.
Prototype only — not an official warning service.
