# Project AGAP: System Architecture, ML Pipeline & Implementation Guide

**Document version:** 1.3.0  
**Target pilot:** Quezon City, Metro Manila  
**Audience:** Team B — Backend, Frontend, and System Integration Engineers  
**Status:** Corrected implementation blueprint for a prototype; not a production emergency-response certification  
**Last reviewed:** 2026-10-13

---

## 0\. Implementation status and non-negotiable rules

Project AGAP combines satellite-derived tropical-cyclone assessment, official weather bulletins, static geospatial hazard data, verified evacuation resources, and an offline-capable Progressive Web App (PWA). The prototype supports two first-class operating modes: **Historical TC Replay** for repeatable evaluation on 3–4 selected past storms, and **Live Monitoring** for current source ingestion. Both modes share the same preprocessing and inference adapter but retain separate provenance and status fields.

The architecture is suitable for a prototype if the components below are implemented and tested. The source files do **not** establish that the system can yet make validated live predictions. In particular:

1. A mock/demo result must never be presented as a live model prediction.  
2. A classifier output must not be converted directly into an official PAGASA Tropical Cyclone Wind Signal (TCWS).  
3. Cyclone category must not automatically select a 5-, 25-, or 100-year flood map. Those are independent static modeled scenarios.  
4. Static hazard maps must not be described as live inundation forecasts, current water depth, or real-time road conditions.  
5. Missing data, stale data, parsing errors, or missing model weights must be represented explicitly. Do not silently substitute random tensors, default alerts, or an unlabelled mock result.  
6. Only current official warnings and authorized local-government instructions can establish official warning status or evacuation orders.

Before operational/public use, the system requires validation by relevant disaster-management personnel, model evaluation against held-out data, security review, and field testing. The prototype should be described as a decision-support tool, not as a replacement for official sources.

## 1\. System topology

```
HISTORICAL TC REPLAY                         LIVE MONITORING
- historical source-frame index             - latest usable satellite observation
- PAGASA reports / best-track references    - current official PAGASA advisories
- selected storm + observation timestamp    - source freshness and availability
             |                                               |
             +--------------------+--------------------------+
                                  v
                     SHARED SATELLITE PREPROCESSOR
                  same versioned preprocessing contract
                                  |
                                  v
                       SHARED ONNX INFERENCE
                     no random input in live mode
                                  |
                                  v
                       UNIFIED ASSESSMENT API
           mode/provenance preserved; live and replay distinguished
                                  |
        +-------------------------+--------------------------+
        |                         |                          |
        v                         v                          v
OFFICIAL WARNING SNAPSHOT   STATIC FLOOD SCENARIOS   VERIFIED QC RESOURCES
        |                         |                          |
        +-------------------------+--------------------------+
                                  v
                        PWA / MAPLIBRE CLIENT
             - Historical Replay controls and reference comparison
             - Live Monitoring source-health and freshness indicators
             - separate official-warning and flood-scenario layers
             - offline cache with clear cached/stale/offline status
```

&nbsp;

Historical replay is not a different classifier: it selects archived observations and passes them through the same approved preprocessing and inference adapter. It must never substitute a reference label for a model prediction. Live Monitoring retrieves current observations and must report unavailable/stale states rather than silently replaying an old frame.

**MVP transport:** REST/HTTPS with client polling is sufficient. WebSockets may be added later if implemented, secured, and tested; they are not a required capability of the current blueprint.

### 1.1 Data categories must remain separate

| Data category | Examples | Meaning in the product |
| :---- | :---- | :---- |
| Observed/source data | Himawari observation timestamp, official PAGASA bulletin text | What the source published or observed, with source and time metadata |
| Model output | Predicted TC category, estimated wind, model confidence | A model estimate; never an official warning |
| Official warning | PAGASA wind signal or rainfall warning for an affected area | Official warning status, preserved from the official source |
| Static hazard scenario | Project NOAH 5-, 25-, or 100-year flood layer | A modeled return-period scenario, not current flooding |
| Operational resource data | Officially confirmed shelters and hotlines | A verified resource catalog with its own update/verification date |

&nbsp;

---

## 2\. External sources and ingestion contracts

Use [`apis_and_endpoints.md`](./apis_and_endpoints.md) as the canonical source inventory and [`qc_hotlines.json`](./qc_hotlines.json) as the structured hotline catalog.

### 2.1 Himawari-9 satellite observations

- Public bucket: `s3://noaa-himawari9/`  
- Registry: [https\://registry.opendata.aws/noaa-himawari/](https://registry.opendata.aws/noaa-himawari/)  
- Candidate product: AHI L1b Full Disk, Band 13 infrared.

The satellite loader must discover an actual current object, retrieve it, decode the specific product format, validate calibration and quality flags, and return a timestamped observation. The bucket does not supply a ready-made `[1, 3, 128, 128]` input tensor.

The training data described as raw TCIR/HDF5 may differ in format, spatial crop, calibration, resolution, and normalization from the live satellite feed. Team A must deliver a preprocessing manifest and a representative test frame. Team B must demonstrate that the live preprocessing reproduces the training input contract before any result can be called a live prediction.

#### 2.1.1 Historical satellite frames and storm references

Historical Replay should use timestamped archival satellite observations where the required products are actually available. Do not assume every selected storm has a usable Band 13 frame in the same archive or an identical file format. Before approving a storm for replay, verify that each selected observation can be retrieved, decoded, spatially cropped, and transformed with the same versioned preprocessing used by the model.

Reference resources:

- **PAGASA Tropical Cyclone Preliminary Reports:** [https\://www\.pagasa.dost.gov.ph/tropical-cyclone/publications/preliminary-report](https://www.pagasa.dost.gov.ph/tropical-cyclone/publications/preliminary-report). These reports summarize near-real-time analysis and warnings; treat them as preliminary when an Annual Report is available.  
- **PAGASA Annual Report on Philippine Tropical Cyclones (ARTC):** [https\://www\.pagasa.dost.gov.ph/tropical-cyclone/publications/annual-report](https://www.pagasa.dost.gov.ph/tropical-cyclone/publications/annual-report). PAGASA describes the annual reports as post-season best-track analyses that supersede preliminary reports for the corresponding storm/season.  
- **NOAA/NCEI IBTrACS:** [https\://www\.ncei.noaa.gov/products/international-best-track-archive](https://www.ncei.noaa.gov/products/international-best-track-archive). Use as a supplementary track/intensity reference; preserve the data provider/agency, original units, wind-averaging period when available, and dataset version. Do not assume all agencies' wind estimates are directly interchangeable.

Catalog the chosen 3–4 storms and their observation frames in `historical_tc_manifest.json`. The manifest must be populated with real storm names, UTC timestamps, source URIs, asset paths/checksums, and reference sources before the replay UI is considered data-ready. Do not invent an observation timestamp or expected label to complete a missing record.

### 2.2 PAGASA warning ingestion

The public rainfall-warning portal is a website; this blueprint does not assume a supported stable JSON API. Build a replaceable adapter, prefer an official structured feed if one is available, and verify automation/access requirements before scraping.

Store at minimum:

- source URL and original bulletin text;  
- official warning/alert label as published;  
- affected geographic area as published;  
- issuance time and validity/expiry time, when supplied;  
- retrieval/ingestion timestamp;  
- parser version and status (`fresh`, `stale`, `unavailable`, `parse_error`).

Do not infer an official Yellow/Orange/Red warning from the model or from a single numeric rainfall-rate estimate. If the source is unavailable, return an unknown/stale state with the last successful update time; never treat a failed fetch as evidence that no warning exists.

### 2.3 Project NOAH flood map

Use the current dataset documentation at [https\://huggingface.co/datasets/bettergovph/project-noah-hazard-maps](https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps). The combined archive is published under:

```
https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/noah_hazard_maps.pmtiles
```

&nbsp;

The documented flood source-layers are `flood_5yr`, `flood_25yr`, and `flood_100yr`; the flood hazard attribute is `Var` (`1` low, `2` medium, `3` high). Do not use `flood_hazard` or `HAZARD_LVL` for this source.

The archive is large. Test the actual HTTP Range and browser CORS behavior from the deployment origin. Consider separate per-scenario PMTiles files if that improves performance, but inspect their metadata before use. Review provenance and the dataset's current ODbL license/attribution obligations.

**Do not link model class to the scenario.** The user chooses or views a flood scenario independently. Store a scenario selection separately from cyclone inference.

### 2.4 Shelter data

`qc_shelters.geojson` is a required runtime asset but was not included in the four reviewed files. The project must create it from verified records and include per-facility source, verification date/status, coordinates, capacity if confirmed, accessibility details if known, and contact information where available.

OpenStreetMap/Overpass can identify candidate locations, but mapped schools or shelters are not automatically officially designated, open, staffed, safe, or capable of accommodating people. Show unverified facilities as candidates only. Verify operational shelters with Quezon City/barangay authorities before presenting them as destinations.

---

## 3\. ML workflow and model contract

### 3.1 Offline handoff — Team A

Team A must provide:

1. `agap_tc_classifier.onnx`;  
2. a versioned preprocessing manifest, such as `preprocessing.json`;  
3. class-index-to-code mapping (`TD`, `TS`, `STS`, `TY`, `STY`);  
4. named input/output tensors and their exact shapes/dtypes;  
5. a clear statement of whether the model has a wind-regression output and its unit/shape;  
6. normalization/calibration steps used during training;  
7. representative test inputs and expected outputs, including edge cases;  
8. evaluation metrics, dataset provenance, limitations, and the method used to assess/calibrate confidence.

The frontend/backend must not invent any of these details. If Team A's actual exported names differ from the names below, update this contract and its adapter in one reviewed change before integration.

### 3.2 Required integration contract (proposed; confirm with Team A)

The following is the **target contract for integration**, not a claim about an already-provided ONNX artifact:

| Item | Expected integration contract |
| :---- | :---- |
| Input name | `ir_image` |
| Input dtype/shape | `float32`, `[1, 3, 128, 128]` |
| Input semantic | One storm-centered Band 13 infrared patch, transformed exactly as defined by the versioned training manifest |
| Classification output | `class_logits`, shape `[1, 5]`, order `TD, TS, STS, TY, STY` |
| Wind output | `wind_kph`, shape `[1, 1]`, if the model includes the documented regression head |
| Preprocessing | Defined by the checked-in manifest and verified against training; do not hard-code assumed calibration/normalization values without Team A's confirmation |
| Missing model or invalid frame | Explicit unavailable/error state; no random-input fallback |

&nbsp;

Do not assume that repeating a single infrared channel into three channels or scaling brightness temperature to `[0, 1]` is correct unless Team A's training pipeline did exactly that. Any mismatch between live preprocessing and training preprocessing invalidates a live-inference claim.

### 3.3 Category thresholds

The class definitions used by the data contract are:

| Code | Category | Sustained wind range (km/h) |
| :---- | :---- | ----: |
| `TD` | Tropical Depression | 0–61 |
| `TS` | Tropical Storm | 62–88 |
| `STS` | Severe Tropical Storm | 89–117 |
| `TY` | Typhoon | 118–184 |
| `STY` | Super Typhoon | 185 and above |

&nbsp;

Reference: PAGASA's public TCWS learning page ([https\://pagasa.dost.gov.ph/learning-tools/tropical-cyclone-wind-signal](https://pagasa.dost.gov.ph/learning-tools/tropical-cyclone-wind-signal)). Wind category and official TCWS are not interchangeable: TCWS is issued for a particular land area and incorporates expected wind threat and warning lead time. Do not generate a TCWS label from the predicted class alone.

### 3.4 Separate cyclone output from flood return period

Remove `active_return_period` from cyclone inference records. A storm category alone does not determine which static flood return-period scenario applies. A validated dynamic flood forecast would require a separate hydrological/hydraulic model and appropriate rainfall, catchment, terrain, and calibration data; it is not implemented by this classifier.

### 3.5 Inference statuses

Each inference result should include at least:

```json
{
  "status": "success",
  "is_demo": false,
  "model_version": "<version from manifest>",
  "source_frame_id": "<provider object key or stable ID>",
  "observed_at": "<source timestamp>",
  "inferred_at": "<timestamp>",
  "category_code": "TY",
  "category_name": "Typhoon",
  "sustained_wind_kph": 140.0,
  "confidence": 0.82,
  "confidence_is_calibrated": false,
  "warnings": []
}
```

&nbsp;

The numbers are examples only, not an AGAP prediction. `status` describes execution state (`success`, `demo`, `unavailable`, or `error`); `run_context.mode` separately identifies whether the request is `live`, `historical_replay`, or `demo`. Do not report `status: success` unless real model inference completed using a valid preprocessed frame. If confidence has not been calibrated, label it as an uncalibrated model score rather than a probability of correctness. If classification and regression output disagree materially, preserve the outputs and add a validation warning; do not silently coerce one to the other.

### 3.6 Historical Replay and Live Monitoring contract

Both modes must call the same versioned image-preprocessing function and inference adapter. Keep their run context separate:

| Field | Historical TC Replay | Live Monitoring |
| :---- | :---- | :---- |
| `run_mode` | `historical_replay` | `live` |
| Frame selection | Explicit storm and observation ID from the manifest | Latest valid observation acquired by the live loader |
| Reference label | Kept in a separate evaluation/reference object | Not supplied as model input; may be added later for retrospective evaluation |
| Current official warning | Historical bulletin only if it has been archived and timestamp-aligned; otherwise `unavailable` | Latest source snapshot with freshness/validity status |
| UI status | “Historical replay” with storm and observation time | “Live” only after fresh acquisition, approved preprocessing, and real model inference all succeed |
| Permitted claim | Result for this specific archived case | Experimental model estimate until broader validation is completed |

&nbsp;

Never use a PAGASA/IBTrACS reference label as the input to inference or substitute it into the prediction field. Use it only after inference to compute evaluation metrics. A replay can be successful even when the model classifies a storm incorrectly; that is an evaluation result, not a replay-system failure.

For a prototype with 3–4 storms, use the cases for integration testing and qualitative case studies. This is not sufficient by itself to establish broad predictive generalization. Keep train/validation/test separation at the **storm level**, not the frame level. If a storm appeared in Team A's training or model-selection data, it must not be reported as an independent held-out test storm. Record `dataset_role` and training-overlap status in the manifest.

Suggested retrospective metrics include a confusion matrix and per-class precision/recall for classification. Evaluate wind error (for example, MAE) only if the model exposes a valid wind regression output and the reference wind units/averaging period have been harmonized. State the number of storms and usable frames; do not report frame-level scores as independent storm-level evidence.

---

## 4\. API design

### 4.1 MVP endpoints

| Method | Path | Purpose |
| :---- | :---- | :---- |
| `GET` | `/health/live` | Process liveness only |
| `GET` | `/health/ready` | Readiness check: assets, model mode, manifest, and configured dependencies |
| `GET` | `/api/v1/hotlines` | Return cached hotline catalog and verification metadata |
| `GET` | `/api/v1/replay/storms` | List selected historical cases available in the manifest |
| `GET` | `/api/v1/replay/{storm_id}/observations` | List available archived observations and their source/reference metadata |
| `POST` | `/api/v1/replay/{storm_id}/assess` | Run inference for one selected archived observation using the shared pipeline |
| `POST` | `/api/v1/telemetry/assess` | Live assessment using the latest usable live observation, location, official warning snapshot, static hazard lookup, and nearest verified facility |

&nbsp;

The replay endpoints must only expose manifest entries with `selection_status: "selected"` and available frame assets. Each replay request names an `observation_id`; do not accept arbitrary filesystem paths from a client. If `MOCK_INFERENCE=true`, the route may be exercised for UI/integration demonstration, but it must mark `cyclone_assessment.status: demo` and must not calculate or display accuracy metrics. A replay counts as a model evaluation only when the real model ran on the archived observation. A later WebSocket endpoint may be added if the application genuinely needs push updates. Do not document a WebSocket feature until it is implemented and tested.

### 4.2 Request contract

```json
{
  "latitude": 14.6500,
  "longitude": 121.0500
}
```

&nbsp;

Coordinates must be finite and fall within the verified Quezon City boundary polygon. A rectangular envelope may be used for an inexpensive first rejection, but it is not a substitute for a polygon/jurisdiction check. Do not hard-code bounds in multiple modules; configure them once and test boundary cases.

For a local demo, benchmark selection should use a separate development-only route or an explicit demo mode that is impossible to enable accidentally in production. Do not let public clients override live inference results through the production assessment endpoint.

#### Historical replay request

`GET /api/v1/replay/storms` returns manifest-backed cases. The client then calls `GET /api/v1/replay/{storm_id}/observations` and submits one selected observation to the replay assessment route:

```json
{
  "observation_id": "<manifest observation ID>"
}
```

&nbsp;

The server resolves the ID in `historical_tc_manifest.json`, checks that the case is selected and the observation asset exists, and runs the normal preprocessing/inference pipeline. The request must not include reference labels or arbitrary asset paths. Reference labels are loaded server-side after inference for a separate evaluation result. An unknown storm/observation should return `404`; a manifest entry with a missing/unusable asset should return a clear unavailable status and must not fall back to a random frame or mock result.

### 4.3 Response contract

The response should carry independent statuses rather than a single ambiguous `detected: true` value. Example shape:

```json
{
  "assessment_id": "<uuid>",
  "generated_at": "<timestamp>",
  "run_context": {
    "mode": "live",
    "storm_id": null,
    "observation_id": "<live source frame ID>"
  },
  "spatial_context": {
    "jurisdiction": "Quezon City",
    "latitude": 14.6500,
    "longitude": 121.0500,
    "in_bounds": true
  },
  "cyclone_assessment": {
    "status": "success",
    "is_demo": false,
    "category_code": "TY",
    "category_name": "Typhoon",
    "sustained_wind_kph": 140.0,
    "confidence": 0.82,
    "observed_at": "<timestamp>",
    "inferred_at": "<timestamp>",
    "source_frame_id": "<id>",
    "warnings": []
  },
  "official_rainfall_warning": {
    "status": "fresh",
    "alert_level": "unknown",
    "affected_area": null,
    "issued_at": null,
    "source_url": "<official source URL>",
    "retrieved_at": "<timestamp>",
    "raw_text": "<preserve original bulletin text>"
  },
  "static_flood_scenario": {
    "source": "Project NOAH hazard map dataset",
    "is_live_forecast": false,
    "selected_return_period_years": 25,
    "hazard_level": 2,
    "lookup_status": "available"
  },
  "nearest_verified_facility": {
    "status": "available",
    "facility_id": "<id>",
    "name": "<verified facility name>",
    "distance_m": 850,
    "verified_at": "<date>"
  },
  "overall_data_status": {
    "status": "partial",
    "stale_components": ["official_rainfall_warning"]
  }
}
```

&nbsp;

All data values above are examples. `run_context.mode` is `live` for the live endpoint and `historical_replay` for replay responses; include the `storm_id` and manifest `observation_id` for replay. Historical responses should add a separate `evaluation_reference` object containing the reference source, reference category/wind (when available), and comparison metrics/status; that object must never overwrite `cyclone_assessment` or be supplied as model input. `hazard_level` must come from the selected static map's `Var` attribute or be `null` if no trustworthy spatial lookup exists. An official warning must come from an official source snapshot and must never be synthesized from the ML result. Never label an overall assessment `safe` merely because a particular map layer has no intersecting feature.

### 4.4 Error and stale-data behavior

Use typed errors/statuses for at least:

- invalid coordinates or outside pilot jurisdiction;  
- missing/unavailable model weights;  
- no current satellite frame;  
- preprocessing or ONNX output-contract mismatch;  
- rainfall source unavailable or parser failure;  
- stale cached bulletin;  
- no verified shelter data;  
- static hazard data unavailable;  
- internal database/cache errors.

Return useful HTTP codes for request errors and service availability, but preserve component statuses in successful partial responses when reasonable. Never convert an ingestion exception into `alert_level: None` unless an authoritative fresh source explicitly indicates no active warning.

---

## 5\. Database design

Use SQLite for the two-week prototype. SpatiaLite is optional; application-level geometry operations using a verified GeoJSON polygon and a suitable geometry library can be used at small scale. Enable SQLite foreign-key checks for every connection. An in-memory cache may accelerate reads, but it must not be the only store of audit-relevant observations.

### 5.1 Logical data model

```
cyclone_inference_log  N ---- 1 source_frame (if stored separately)
pagasa_rainfall_bulletin: timestamped official source snapshots
 evacuation_facility: verified operational-resource catalog
spatial_assessment_cache: references the inference/bulletin/facility context
flood_scenario_choice: a user/UI-selected static scenario, not a model output
```

&nbsp;

### 5.2 SQLite DDL

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS historical_replay_case (
    storm_id TEXT PRIMARY KEY,
    storm_name TEXT NOT NULL,
    season_year INTEGER NOT NULL,
    selection_status TEXT NOT NULL CHECK(selection_status IN ('candidate', 'selected', 'excluded')),
    dataset_role TEXT NOT NULL DEFAULT 'not_assigned'
        CHECK(dataset_role IN ('not_assigned', 'train', 'validation', 'test', 'demo_only')),
    reference_sources_json TEXT NOT NULL DEFAULT '[]',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS historical_replay_observation (
    observation_id TEXT PRIMARY KEY,
    storm_id TEXT NOT NULL REFERENCES historical_replay_case(storm_id),
    observed_at TEXT NOT NULL,
    source_object_uri TEXT NOT NULL,
    local_asset_path TEXT,
    sha256 TEXT,
    reference_category_code TEXT CHECK(reference_category_code IN ('TD', 'TS', 'STS', 'TY', 'STY')),
    reference_wind_kph REAL,
    wind_averaging_period_minutes REAL,
    reference_source_url TEXT,
    asset_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK(asset_status IN ('unverified', 'available', 'unavailable', 'invalid'))
);

CREATE TABLE IF NOT EXISTS cyclone_inference_log (
    id TEXT PRIMARY KEY,
    run_mode TEXT NOT NULL CHECK(run_mode IN ('live', 'historical_replay', 'demo')),
    replay_observation_id TEXT REFERENCES historical_replay_observation(observation_id),
    inferred_at TEXT NOT NULL,
    observed_at TEXT,
    source_frame_id TEXT,
    model_version TEXT,
    preprocessing_version TEXT,
    category_code TEXT CHECK(category_code IN ('TD', 'TS', 'STS', 'TY', 'STY')),
    sustained_wind_kph REAL,
    confidence_score REAL,
    confidence_is_calibrated INTEGER NOT NULL DEFAULT 0,
    inference_status TEXT NOT NULL CHECK(inference_status IN ('success', 'demo', 'unavailable', 'error')),
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS pagasa_rainfall_bulletin (
    id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    issued_at TEXT,
    valid_until TEXT,
    ingested_at TEXT NOT NULL,
    alert_level TEXT CHECK(alert_level IN ('Yellow', 'Orange', 'Red', 'None', 'unknown')),
    affected_area TEXT,
    raw_advisory_text TEXT NOT NULL,
    source_status TEXT NOT NULL CHECK(source_status IN ('fresh', 'stale', 'unavailable', 'parse_error')),
    parser_version TEXT
);

CREATE TABLE IF NOT EXISTS evacuation_facility (
    facility_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    barangay TEXT,
    district TEXT,
    facility_type TEXT NOT NULL,
    capacity_persons INTEGER CHECK(capacity_persons IS NULL OR capacity_persons >= 0),
    current_occupancy INTEGER CHECK(current_occupancy IS NULL OR current_occupancy >= 0),
    contact_hotline TEXT,
    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
    is_officially_verified INTEGER NOT NULL DEFAULT 0,
    verification_source TEXT,
    verified_at TEXT,
    operational_status TEXT NOT NULL DEFAULT 'unknown'
        CHECK(operational_status IN ('open', 'closed', 'unknown', 'unverified'))
);

CREATE TABLE IF NOT EXISTS spatial_assessment_cache (
    cache_id TEXT PRIMARY KEY,
    inference_id TEXT REFERENCES cyclone_inference_log(id),
    bulletin_id TEXT REFERENCES pagasa_rainfall_bulletin(id),
    center_lat REAL NOT NULL,
    center_lon REAL NOT NULL,
    selected_flood_scenario_years INTEGER CHECK(selected_flood_scenario_years IN (5, 25, 100)),
    flood_hazard_level INTEGER CHECK(flood_hazard_level IN (1, 2, 3)),
    in_flood_hazard_polygon INTEGER CHECK(in_flood_hazard_polygon IN (0, 1)),
    nearest_shelter_id TEXT REFERENCES evacuation_facility(facility_id),
    distance_to_shelter_m REAL,
    computed_at TEXT NOT NULL,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_replay_observation_storm_time
    ON historical_replay_observation(storm_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_inference_run_mode_time
    ON cyclone_inference_log(run_mode, inferred_at);
CREATE INDEX IF NOT EXISTS idx_inference_inferred_at
    ON cyclone_inference_log(inferred_at);
CREATE INDEX IF NOT EXISTS idx_bulletin_ingested_at
    ON pagasa_rainfall_bulletin(ingested_at);
CREATE INDEX IF NOT EXISTS idx_facility_verified_status
    ON evacuation_facility(is_officially_verified, operational_status);
CREATE INDEX IF NOT EXISTS idx_spatial_cache_computed_at
    ON spatial_assessment_cache(computed_at);
```

&nbsp;

The DDL records static map scenario selection separately from cyclone classification. Do not restore an `active_return_period` derived from the predicted category.

---

## 6\. Suggested backend structure

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── health.py
│   │   ├── telemetry.py
│   │   ├── replay.py
│   │   └── hotlines.py
│   ├── services/
│   │   ├── onnx_inference.py
│   │   ├── satellite_loader.py
│   │   ├── historical_replay.py
│   │   ├── satellite_preprocess.py
│   │   ├── pagasa_adapter.py
│   │   ├── geospatial.py
│   │   ├── flood_map_lookup.py
│   │   └── assessment.py
│   ├── models/
│   │   ├── schemas.py
│   │   └── db.py
│   ├── static/
│   │   ├── debris_matrix.json
│   │   ├── qc_hotlines.json
│   │   ├── historical_tc_manifest.json
│   │   ├── historical_tc_manifest.schema.json
│   │   ├── qc_shelters.geojson
│   │   └── preprocessing.json
│   ├── data/
│   │   └── historical_tc/           # locally cached source frames; keep large files out of source control
│   └── weights/
│       └── agap_tc_classifier.onnx
├── tests/
│   ├── test_assets.py
│   ├── test_mock_inference.py
│   ├── test_onnx_contract.py
│   ├── test_rainfall_parser.py
│   ├── test_historical_manifest.py
│   ├── test_replay_api.py
│   ├── test_geospatial.py
│   └── test_api.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

&nbsp;

The corrected `debris_matrix.json` is a root JSON object with `wind_hazard_matrix`. The hotline file uses `hotlines`. Load each by key and validate its shape at startup. `qc_shelters.geojson` is a required asset that must be produced and verified separately; it is not included in the four corrected files.

### 6.1 Environment configuration

Use environment variables or a settings module; do not duplicate source URLs or jurisdiction bounds throughout the code.

```ini
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000

ONNX_MODEL_PATH=app/weights/agap_tc_classifier.onnx
MOCK_INFERENCE=true
HISTORICAL_TC_MANIFEST=app/static/historical_tc_manifest.json
HISTORICAL_ASSET_ROOT=app/data/historical_tc

PAGASA_SCRAPE_URL=https://bagong.pagasa.dost.gov.ph/weather/rainfall-warning
HIMAWARI_S3_BUCKET=noaa-himawari9
NOAH_PMTILES_URI=https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/noah_hazard_maps.pmtiles

# Comma-separated explicit origins. Do not use '*' with credentials in production.
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

&nbsp;

For real-model mode, `MOCK_INFERENCE=false` and a missing or invalid ONNX artifact must fail readiness/startup. Mock mode must be an explicit development/demo setting, not an automatic fallback.

---

## 7\. ONNX inference adapter contract

The adapter below enforces the **proposed** model contract. Team A must export matching named inputs/outputs or the team must make a reviewed coordinated change. It does not construct the satellite tensor; the actual satellite preprocessor is responsible for that.

```py
# app/services/onnx_inference.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np

CLASS_MAP = [
    ("TD", "Tropical Depression"),
    ("TS", "Tropical Storm"),
    ("STS", "Severe Tropical Storm"),
    ("TY", "Typhoon"),
    ("STY", "Super Typhoon"),
]
WIND_RANGES_KPH = [(0, 61), (62, 88), (89, 117), (118, 184), (185, None)]

DEMO_CASES = {
    "TD":  {"category_code": "TD",  "category_name": "Tropical Depression", "sustained_wind_kph": 50.0},
    "TS":  {"category_code": "TS",  "category_name": "Tropical Storm", "sustained_wind_kph": 75.0},
    "STS": {"category_code": "STS", "category_name": "Severe Tropical Storm", "sustained_wind_kph": 105.0},
    "TY":  {"category_code": "TY",  "category_name": "Typhoon", "sustained_wind_kph": 140.0},
    "STY": {"category_code": "STY", "category_name": "Super Typhoon", "sustained_wind_kph": 210.0},
}


class TCInferenceService:
    def __init__(self, model_path: str, mock: bool = False):
        self.mock = mock
        self.session = None
        self.input_name: str | None = None

        if mock:
            return

        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(
                f"ONNX model not found at {path}; set MOCK_INFERENCE=true only for an explicit demo."
            )

        import onnxruntime as ort
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(
            str(path), options, providers=["CPUExecutionProvider"]
        )

        inputs = self.session.get_inputs()
        if len(inputs) != 1 or inputs[0].name != "ir_image":
            raise RuntimeError("Model input contract mismatch: expected one input named 'ir_image'.")
        self.input_name = inputs[0].name
        output_names = {item.name for item in self.session.get_outputs()}
        if not {"class_logits", "wind_kph"}.issubset(output_names):
            raise RuntimeError(
                "Model output contract mismatch: expected 'class_logits' and 'wind_kph'."
            )

    def predict(
        self,
        input_tensor: np.ndarray | None = None,
        benchmark_override: str | None = None,
    ) -> dict[str, Any]:
        # Benchmark values are permitted only in explicit mock/demo mode.
        if benchmark_override is not None:
            if not self.mock:
                raise ValueError("Benchmark overrides are disabled outside mock/demo mode.")
            if benchmark_override not in DEMO_CASES:
                raise ValueError(f"Unsupported benchmark category: {benchmark_override}")
            result = DEMO_CASES[benchmark_override].copy()
            result.update({
                "status": "demo",
                "is_demo": True,
                "confidence": None,
                "confidence_is_calibrated": False,
                "model_version": None,
                "source_frame_id": None,
                "observed_at": None,
                "warnings": ["Predefined demonstration scenario; not a live prediction."],
            })
            return result

        if self.mock:
            result = DEMO_CASES["TY"].copy()
            result.update({
                "status": "demo",
                "is_demo": True,
                "confidence": None,
                "confidence_is_calibrated": False,
                "model_version": None,
                "source_frame_id": None,
                "observed_at": None,
                "warnings": ["Default mock scenario; not a live prediction."],
            })
            return result

        if self.session is None or self.input_name is None:
            raise RuntimeError("Inference session is not initialized.")
        if input_tensor is None:
            raise RuntimeError("Real inference requires a preprocessed satellite tensor.")

        tensor = np.asarray(input_tensor, dtype=np.float32)
        if tensor.shape != (1, 3, 128, 128):
            raise ValueError(f"Expected tensor shape (1, 3, 128, 128), got {tensor.shape}.")
        if not np.isfinite(tensor).all():
            raise ValueError("Input tensor contains NaN or infinite values.")

        output_names = [item.name for item in self.session.get_outputs()]
        raw_outputs = self.session.run(output_names, {self.input_name: tensor})
        outputs = dict(zip(output_names, raw_outputs))

        logits = np.asarray(outputs["class_logits"], dtype=np.float64).reshape(-1)
        wind = np.asarray(outputs["wind_kph"], dtype=np.float64).reshape(-1)
        if logits.size != 5 or wind.size != 1:
            raise RuntimeError("ONNX output shape mismatch with the documented model contract.")
        if not np.isfinite(logits).all() or not np.isfinite(wind).all():
            raise RuntimeError("ONNX model returned non-finite output values.")

        shifted = logits - np.max(logits)
        exp_logits = np.exp(shifted)
        probabilities = exp_logits / exp_logits.sum()
        class_index = int(np.argmax(probabilities))
        code, name = CLASS_MAP[class_index]
        wind_kph = float(wind[0])

        warnings = []
        lower, upper = WIND_RANGES_KPH[class_index]
        if wind_kph < 0:
            warnings.append("Wind-regression output was negative; treat the wind estimate as invalid.")
        elif wind_kph < lower or (upper is not None and wind_kph > upper):
            warnings.append(
                "Classification and wind-regression outputs disagree; preserve both outputs and review."
            )

        return {
            "status": "success",
            "is_demo": False,
            "category_code": code,
            "category_name": name,
            "sustained_wind_kph": wind_kph if wind_kph >= 0 else None,
            "confidence": float(probabilities[class_index]),
            "confidence_is_calibrated": False,
            "model_version": None,  # Populate from the deployed model manifest.
            "source_frame_id": None,  # Set by the caller from the actual source frame.
            "observed_at": None,      # Set by the caller from source metadata.
            "warnings": warnings,
        }
```

&nbsp;

**Important:** The code enforces the proposed tensor shape because that is the proposed integration contract, not because the model file has been inspected. The app/service layer must attach the actual `model_version`, `source_frame_id`, and observation timestamp, plus top-level `run_context.mode`. The adapter's `status: success` means the model call succeeded; the route may label the run as `live` only after fresh live source acquisition and preprocessing, or as `historical_replay` when it used a manifest-selected archived frame.

---

## 8\. Geospatial assessment and map behavior

### 8.1 Coordinate validation

- Use one configured, authoritative Quezon City boundary geometry for jurisdiction validation.  
- Validate numeric coordinate ranges first, then check whether the point lies inside the polygon.  
- Do not accept a bounding rectangle as proof that a coordinate is inside Quezon City.  
- Use a consistent coordinate order: API input is latitude/longitude; GeoJSON coordinates are longitude/latitude.

### 8.2 Static flood scenario lookup

The selected return period is one of `5`, `25`, or `100`, controlled independently by the user/UI. The selected map source-layer is respectively `flood_5yr`, `flood_25yr`, or `flood_100yr`. For the combined archive, use the `Var` field: `1` low, `2` medium, `3` high.

The result should report whether a point intersects a mapped feature only when the application has a valid geometry lookup implementation. An absent feature must be described as “no mapped feature returned for this query,” not as “safe” or “no flood risk.”

### 8.3 Nearest facility

Compute distance to the nearest **verified and operationally eligible** facility, not merely the nearest mapped feature. If no verified facility is found, return an explicit `no_verified_facility` status. Straight-line distance does not establish that a route is accessible or safe; route guidance requires separate routing data and hazard-aware validation.

### 8.4 Debris matrix

Load `debris_matrix.json` using its root object:

```py
with open(asset_path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)
DEBRIS_RULES = payload["wind_hazard_matrix"]
```

&nbsp;

Validate that the payload is a dictionary and the value of `wind_hazard_matrix` is a list. Match by `code`; if no valid match exists, return a validation error or an `unknown` state. **Do not use the second item as a default fallback**—that would arbitrarily assign Tropical Storm instructions to an unknown class.

The matrix is general preparedness content. Review recommendations with local disaster-management personnel and do not treat it as a structural engineering calculation or evacuation authority.

---

## 9\. PWA and offline behavior

The client should have three clearly separated map/status layers:

1. **Cyclone assessment:** execution status (`success`, `demo`, `unavailable`, `error`) plus a separate run-mode label (`live` or `historical_replay`), observation time, inference time, model version, and confidence caveat.  
2. **Official warnings:** source, affected area, issuance/validity, retrieval time, and a conspicuous stale/unavailable state.  
3. **Static flood scenario:** selected return period, source label, hazard-level legend, and an explicit “static modeled scenario — not a live flood forecast” description.

Offline cache should include only useful reference content, such as the last successful assessment, selected static-map metadata, hotlines, and verified shelter catalog. Each cached object must include its source timestamp and cache timestamp. In offline mode:

- make it visually obvious that information is cached and may be stale;  
- do not imply that an old official warning is currently active;  
- keep emergency dial actions available when the device supports them;  
- explain when live status cannot be checked;  
- do not claim cached map tiles or a cached hotline record are complete or current without evidence.

Direct-dial actions use `dial_string` from `qc_hotlines.json` and should be tested on real Android and iOS devices. The app may request the device's geolocation but must ask permission, explain the purpose, and support manual location entry.

---

## 10\. Security, deployment, and reliability

- Configure CORS with explicit development and production origins. Avoid `allow_origins=["*"]` together with credentials.  
- Do not expose filesystem paths, raw exception traces, API secrets, or stack traces in public API responses.  
- Keep source fetches asynchronous and bounded by timeouts; use retries/backoff and a stale-data policy.  
- Put source URLs, polling intervals, and feature flags in centralized configuration.  
- Limit requests to public endpoints and follow provider terms/rate limits.  
- Use HTTPS in deployed environments, secure admin/configuration paths, and minimize location retention. Do not persist precise user coordinates unless needed and justified.  
- Pin/test dependencies in a lock file before release.  
- Add structured logs and request IDs. Avoid logging unnecessary personal/location data.  
- Add readiness checks that distinguish app process health from required external data availability.  
- Monitor source freshness and parser failures, not only HTTP status codes.

### 10.1 Suggested Python dependencies

Pin known-compatible versions in `requirements.txt` after integration tests. Likely packages include:

```
fastapi
uvicorn[standard]
pydantic
numpy
onnxruntime
httpx
shapely
```

&nbsp;

Add a parser dependency only if needed by the verified source adapter. SQLite support is included in Python. Frontend dependencies (`maplibre-gl`, `pmtiles`) belong in the frontend package manifest, not the Python requirements.

---

## 11\. Two-week implementation plan (revised for Historical Replay \+ Live Monitoring)

| Days | Goal | Acceptance criterion |
| :---- | :---- | :---- |
| 1–2 | Asset/schema and common inference contract | Both JSON assets parse; manifest/schema checks pass; replay and live modes use the same inference result schema and explicit run-mode metadata. |
| 3–4 | Historical manifest and replay API | The manifest holds selected cases; list/observation endpoints work; missing assets are reported clearly; no client-supplied filesystem paths are accepted. |
| 5–6 | Map integration | Project NOAH URL, source-layer metadata, `Var` colors, range requests, attribution, and Quezon City rendering are verified. Flood scenario selection is independent of cyclone class. |
| 7–8 | Source ingestion | PAGASA parser tests active/expired/malformed/unavailable cases; live satellite discovery and decoding work for a real sample; archived frames for selected cases are verified. |
| 9–10 | Model handoff and historical evaluation | Team A provides ONNX artifact, preprocessing manifest, test vectors, and training-overlap information; one replay observation reaches the real model; reference labels remain separate from predictions. |
| 11–12 | Live mode, geospatial/resources/offline | Live source freshness/status, jurisdiction validation, verified facilities, hotline dialing, offline status, and stale-data behavior are tested. |
| 13–14 | End-to-end, held-out case, and demo | Replay several timestamps across 3–4 selected storms; report which storms overlap training; run at least one independent whole-storm test if one is available; test live mode and failure injection; lock dependencies and document limits. |

&nbsp;

## If the real model, historical frames, reference labels, or verified shelter catalog are not delivered in time, label those capabilities as mock/unavailable rather than claiming the full workflow is complete. Historical-case selection does not count as independent accuracy validation when those storms were used during training or model selection.

## 12\. Release checklist

- [ ] `debris_matrix.json` is valid JSON with an object root and a `wind_hazard_matrix` array.  
- [ ] `qc_hotlines.json` validates and each record has a source and verification status.  
- [ ] `qc_shelters.geojson` exists, has valid WGS84 coordinates, and separates verified operational facilities from candidates.  
- [ ] Mock API responses use the same schema as live responses, keep `run_context.mode` separate from `cyclone_assessment.status`, include `is_demo: true`, and cannot be scored as model evaluation.  
- [ ] Missing ONNX weights do not silently activate mock mode.  
- [ ] Model input/output names and shapes match Team A's signed-off manifest/test vectors.  
- [ ] `historical_tc_manifest.json` lists 3–4 selected storms, with real observation timestamps, source URIs, asset status, reference URLs, and dataset-role/training-overlap metadata.  
- [ ] Archived source frames can be retrieved/loaded, decoded, validated, and replayed through the same versioned preprocessing used by live inference.  
- [ ] Historical reference labels are kept separate from model predictions and used only for post-inference evaluation.  
- [ ] Training/validation/test separation is by entire storm, not randomly by frame; any overlapping storm is disclosed and not claimed as independent testing.  
- [ ] Live and historical API responses use a common schema and include `run_context.mode`, observation provenance, model version, and freshness/status fields.  
- [ ] Real inference is passed a real, correctly preprocessed satellite tensor; no random tensor is used.  
- [ ] PAGASA source failures are exposed as stale/unavailable/parse-error states, never as “no warning.”  
- [ ] The NOAH source URL and the `flood_5yr`, `flood_25yr`, `flood_100yr` / `Var` schema are verified against actual archive metadata.  
- [ ] Selecting a flood return period is independent of cyclone classification.  
- [ ] Official TCWS is sourced from an official bulletin, not inferred directly from model category.  
- [ ] CORS, logging, source polling, offline cache, and coordinate privacy have been reviewed.  
- [ ] Public-facing wording and protective actions have been reviewed by qualified local disaster-management personnel.  
- [ ] Reports state the count of storms and usable frames; any 3–4-storm result is described as prototype case-study evidence, not proof of broad generalization.

---
