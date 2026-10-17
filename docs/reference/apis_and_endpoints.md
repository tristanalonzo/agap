# Project AGAP — External APIs, Data Feeds & Geospatial Endpoints

**Document version:** 1.2.0  
**Target pilot:** Quezon City, Metro Manila  
**Last source review:** 2026-10-13  
**Purpose:** Catalog external data sources, describe their intended use, and record the limitations that the backend and PWA must handle.

> **Operational disclaimer:** A listed endpoint is a data source, not a guarantee of real-time availability, completeness, official status, or suitability for life-safety decisions. Preserve source timestamps and provenance. Do not represent a static hazard layer or a machine-learning estimate as an official warning.

---

## 1. Satellite observations — NOAA/JMA Himawari-9 open data

- **Provider:** Japan Meteorological Agency (JMA); disseminated through the NOAA Open Data Dissemination program.
- **Satellite/instrument:** Himawari-9 / Advanced Himawari Imager (AHI).
- **Candidate band:** Band 13, clean infrared near 10.4 μm.
- **Product family:** Full-disk AHI L1b products. The registry describes archive access to `AHI-L1b-FLDK` products.
- **Public S3 bucket:** `s3://noaa-himawari9/`
- **Official registry:** <https://registry.opendata.aws/noaa-himawari/>
- **Example listing command:**

```bash
aws s3 ls --no-sign-request s3://noaa-himawari9/AHI-L1b-FLDK/
```

### Integration contract

1. Treat the S3 bucket as a collection of observation products, not as a ready-to-use image tensor. Implement product discovery, download, parsing, calibration, and quality checks.
2. Store the selected object's URI, observation time, retrieval time, band, product version, and processing status with every derived frame.
3. Verify actual key naming, object format, permissions, available timestamps, and request limits at implementation time. The listing command above is a connectivity check, not a complete ingestion implementation.
4. Do not assume that the offline training dataset (`TCIR`/HDF5 in the development guide) is identical to the live Himawari product. Team A must provide a preprocessing manifest demonstrating that the live observations can be transformed into the same input distribution expected by the trained model.
5. Keep the system in `data_unavailable` or demo state when a current, valid observation cannot be obtained. Do not silently substitute random data or a stale observation.
6. The same preprocessing/inference adapter is used by Live Monitoring and Historical TC Replay. Replay selects a dated archive frame from `historical_tc_manifest.json`; it does not use a separate mock classifier.

#### Historical TC Replay — satellite and reference resources

The historical mode uses archived satellite frames plus independent reference records. Verify exact frame availability and product consistency for every selected date; do not assume all storms or timestamps are present in the same bucket or format.

- **NOAA/JMA Himawari-8/9 open data:** <https://registry.opendata.aws/noaa-himawari/>. Use this as the first archive to investigate, then verify the exact object keys, times, and decoding requirements. If the required frame is not available, document the alternative archive or exclude that observation.
- **PAGASA Tropical Cyclone Preliminary Reports:** <https://www.pagasa.dost.gov.ph/tropical-cyclone/publications/preliminary-report>. These summarize near-real-time initial analysis and publicly issued bulletins/warnings. They are preliminary and may be removed from the page once the corresponding Annual Report is available.
- **PAGASA Annual Report on Philippine Tropical Cyclones (ARTC):** <https://www.pagasa.dost.gov.ph/tropical-cyclone/publications/annual-report>. Prefer the corresponding annual report for post-season best-track analysis where available; PAGASA states that ARTC supersedes corresponding preliminary reports.
- **NOAA/NCEI IBTrACS:** <https://www.ncei.noaa.gov/products/international-best-track-archive>. Use for supplementary track/intensity history and record the dataset version and source agency. IBTrACS merges records from multiple agencies; wind estimates may use different averaging periods, so do not compare them as equivalent unless harmonized.

The manifest file `historical_tc_manifest.json` is a new resource catalog. Populate it with 3–4 chosen storms, UTC observation times, archive URIs, locally cached asset paths/checksums where used, reference source URLs, and dataset role/training overlap. Keep reference labels separate from predictions. Split evaluation by whole storm, never by randomly distributing frames from the same storm across train and test sets.

**Source note:** The AWS Open Data Registry identifies JMA Himawari-8/9 as an open satellite-data source and links to the JMA product specification.  
Source: <https://registry.opendata.aws/noaa-himawari/>

---

## 2. Flood hazard maps — BetterGovPH Project NOAH dataset (PMTiles)

- **Dataset page and schema documentation:** <https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps>
- **Combined archive path:** `PMTiles/noah_hazard_maps.pmtiles`
- **Direct HTTP URL:**

```text
https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/noah_hazard_maps.pmtiles
```

- **Format:** PMTiles vector-tile archive.
- **Dataset owner/host shown by source:** BetterGovPH on Hugging Face; the dataset describes Project NOAH-derived hazard maps and provides its own source/provenance information.
- **Dataset license shown by the hosting page:** ODbL. Review the current license, attribution, and source lineage before redistribution or public production use.

### Combined archive — relevant vector layers

| Vector source-layer | Scenario | Classification attribute | Values |
|---|---|---|---|
| `flood_5yr` | 5-year rainfall return-period flood map | `Var` | `1` low, `2` medium, `3` high |
| `flood_25yr` | 25-year rainfall return-period flood map | `Var` | `1` low, `2` medium, `3` high |
| `flood_100yr` | 100-year rainfall return-period flood map | `Var` | `1` low, `2` medium, `3` high |

The dataset also documents layers for landslide, debris flow, and storm-surge scenarios. They are not part of the flood-only view unless separately implemented and tested.

### Integration contract

- Use the actual path `PMTiles/noah_hazard_maps.pmtiles`, not a guessed root-level filename.
- Use the exact flood source-layer names above and the numeric `Var` attribute. Do not use `flood_hazard` or `HAZARD_LVL` for these published flood layers.
- The combined archive is very large (the dataset page currently reports approximately 5.17 GB). PMTiles enables range-based access, but that does not guarantee that the hosting/CDN, browser CORS policy, and current archive serve every range request as the app needs. Test from the actual client deployment origin.
- The repository also provides individual files under `PMTiles/layers/` such as `flood_5yr.pmtiles`, `flood_25yr.pmtiles`, and `flood_100yr.pmtiles`. Evaluate the smaller per-layer archives if the UI only needs one scenario at a time; confirm the vector-layer name with the archive metadata before using them.
- Display the chosen return-period scenario as a **static modeled hazard layer**, not as a current flood forecast. Cyclone classification must not automatically select a return period.
- Show source/provenance and static-map status in the UI. A static return-period map does not report current water depth, road passability, or live inundation.

### Minimal MapLibre/PMTiles configuration

```javascript
import * as pmtiles from "pmtiles";
import maplibregl from "maplibre-gl";

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const NOAH_URL =
  "pmtiles://https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/noah_hazard_maps.pmtiles";

const map = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    sources: {
      "esri-light": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        ],
        tileSize: 256,
        attribution: "Tiles © Esri"
      },
      "noah-hazards": {
        type: "vector",
        url: NOAH_URL
      }
    },
    layers: [
      { id: "base-tiles", type: "raster", source: "esri-light" },
      {
        id: "flood-5yr",
        type: "fill",
        source: "noah-hazards",
        "source-layer": "flood_5yr",
        layout: { visibility: "visible" },
        paint: {
          "fill-color": ["match", ["get", "Var"], 1, "#fde047", 2, "#fb923c", 3, "#ef4444", "#cbd5e1"],
          "fill-opacity": 0.55,
          "fill-outline-color": "#ffffff"
        }
      },
      {
        id: "flood-25yr",
        type: "fill",
        source: "noah-hazards",
        "source-layer": "flood_25yr",
        layout: { visibility: "none" },
        paint: {
          "fill-color": ["match", ["get", "Var"], 1, "#fde047", 2, "#fb923c", 3, "#ef4444", "#cbd5e1"],
          "fill-opacity": 0.55,
          "fill-outline-color": "#ffffff"
        }
      },
      {
        id: "flood-100yr",
        type: "fill",
        source: "noah-hazards",
        "source-layer": "flood_100yr",
        layout: { visibility: "none" },
        paint: {
          "fill-color": ["match", ["get", "Var"], 1, "#fde047", 2, "#fb923c", 3, "#ef4444", "#cbd5e1"],
          "fill-opacity": 0.55,
          "fill-outline-color": "#ffffff"
        }
      }
    ]
  },
  center: [121.05, 14.65],
  zoom: 12,
  minZoom: 10,
  maxZoom: 17
});

// Select a static scenario independently of live cyclone classification.
export function showFloodScenario(years) {
  const selected = { 5: "flood-5yr", 25: "flood-25yr", 100: "flood-100yr" }[years];
  if (!selected) throw new Error("Scenario must be 5, 25, or 100 years");
  for (const id of ["flood-5yr", "flood-25yr", "flood-100yr"]) {
    map.setLayoutProperty(id, "visibility", id === selected ? "visible" : "none");
  }
}
```

**Before adopting this snippet:** confirm browser support, archive range responses, the exact layer metadata, attribution requirements, and current URLs in the deployed environment. The snippet is an integration starting point, not proof that remote rendering has been end-to-end tested.

---

## 3. Official rainfall warnings — DOST-PAGASA

- **Provider:** Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA), including relevant NCR public advisories.
- **Public rainfall-warning portal:** <https://bagong.pagasa.dost.gov.ph/weather/rainfall-warning>
- **General PAGASA site:** <https://www.pagasa.dost.gov.ph/>

### Integration contract

- The public portal is a website, not a documented stable JSON API in this specification. Before scraping, check for an official structured feed or obtain permission/guidance for automated access. Site markup may change and access may be rate-limited.
- If a scraper is used, isolate it behind an adapter and test against captured examples for active, expired, absent, changed, malformed, and unavailable advisories.
- Preserve the official alert label, exact advisory text, source URL, affected area, issuance time, expiry/validity if published, and ingestion timestamp. Do not label a Quezon City location affected unless the advisory's geographic scope supports it.
- Do not infer the official Yellow/Orange/Red warning label solely from a numeric rain-rate field. Hourly rainfall-intensity descriptions and official warning labels are related but are not interchangeable data contracts.
- If the source cannot be reached or parsing fails, report `unknown`/`stale` with the last successful retrieval time. Do not replace a failed fetch with `None` or imply there is no warning.
- Do not claim a guaranteed polling cadence based only on this document. Choose an interval that respects source guidance and access controls, and make it configurable.

PAGASA's published hourly rainfall-intensity descriptions include heavy rainfall at 7.5–15 mm/hour, intense at 15–30 mm/hour, and torrential rainfall above 30 mm/hour. These intensity descriptions must not be treated as a substitute for the actual area-specific warning bulletin.  
Reference: <https://bagong.pagasa.dost.gov.ph/index.php/article/38>

---

## 4. Candidate evacuation facilities — OpenStreetMap / Overpass API

- **Data contributors:** OpenStreetMap contributors.
- **Overpass API:** <https://overpass-api.de/api/interpreter>
- **OSM tagging reference:** <https://wiki.openstreetmap.org/wiki/Tag:emergency%3Devacuation_centre>

Example query for candidate facilities in Quezon City:

```overpass
[out:json][timeout:25];
area["name"="Quezon City"]["boundary"="administrative"]->.qc;
(
  node["amenity"="shelter"](area.qc);
  way["amenity"="shelter"](area.qc);
  relation["amenity"="shelter"](area.qc);
  node["emergency"="evacuation_centre"](area.qc);
  way["emergency"="evacuation_centre"](area.qc);
  relation["emergency"="evacuation_centre"](area.qc);
);
out center tags;
```

### Data-quality limits

- This is a tag-based discovery query. It does not establish that an entry is an officially designated evacuation center, open right now, accessible, staffed, safe under the current hazard, or able to accept additional people.
- Do not include every school as an approved shelter by default. Schools may be shown in a separate **candidate facilities requiring verification** layer if there is a clear need.
- Record the OSM element ID, retrieval time, source tags, coordinates, and validation status. Verify designated facilities, accessibility, opening status, capacity, and official contact details with Quezon City or barangay authorities before presenting them as active evacuation destinations.
- Provide a report/correction mechanism and never claim live occupancy unless the system has a trustworthy live occupancy feed.

---

## 5. Basemap tiles — Esri Canvas

- **Provider:** Esri.
- **Light Gray base:**

```text
https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}
```

- **Light Gray reference labels:**

```text
https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}
```

- **Dark Gray base:**

```text
https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}
```

- **Dark Gray reference labels:**

```text
https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}
```

Replace `{z}`, `{y}`, and `{x}` with the zoom level, tile row, and tile column. Review Esri's current attribution, usage, and availability terms before public deployment. Do not treat a third-party basemap as an emergency-critical guaranteed service.

---

## 6. Emergency hotlines

Use `qc_hotlines.json` as the local structured catalog. The official Quezon City contact page lists QC Helpline 122, QCDRRMO landlines 8927-5914 and 8928-4396, and City Hall trunkline 8988-4242.  
Source: <https://quezoncity.gov.ph/contact-us/>

The national Unified 911 hotline is supported by current government announcements.  
Source: <https://pia.gov.ph/press-release/dilg-unified-911-hits-96-15-efficiency-handles-12-7-million-calls/>

The Philippine Red Cross publishes 143 as its national emergency hotline.  
Source: <https://redcross.org.ph/contact-us/>

App requirements:

- Prefer the national and local emergency contacts appropriate to the user's location and emergency, while keeping direct calling available.
- Use `dial_string` for the `tel:` action and `number` for display. Test landline formats and extensions on actual Android and iOS devices.
- Do not assume every number is toll-free or 24/7 unless the linked official source establishes that fact.
- Cache the catalog for offline display, show its verification date, and advise users that cached contact information may need confirmation.

---

## 7. Historical replay dataset manifest and evaluation rules

`historical_tc_manifest.json` is a local project manifest, not an external API. It begins with an empty `storms` array so the team does not accidentally imply that particular storms or frame timestamps have already been verified. Fill it only after the archive objects and source reports are checked. The project target is 3–4 selected cases once data verification is complete; the empty template itself is not ready for replay. A companion `historical_tc_manifest.schema.json` validates its structure.

For each selected storm, record at least:

- a stable internal `storm_id`, storm name, season/year, selection status, and dataset role (`train`, `validation`, `test`, `demo_only`, or `not_assigned`);
- whether the storm overlaps Team A's training or model-selection data;
- PAGASA and/or IBTrACS reference source URLs, version/access date, and notes about provisional versus post-season records;
- observation IDs, UTC timestamps, satellite/product/band, source object URI, optional local asset path, and SHA-256 checksum where practical;
- reference category/wind values only when sourced, along with source agency, unit, averaging period, and reference URL;
- frame/image quality and retrieval status.

A frame can be used for deterministic replay even if there is no trustworthy reference intensity label, but it cannot contribute to a labeled accuracy metric. Never invent missing labels. For the prototype's 3–4 storms, use replay as a repeatable functional test and case study; do not claim broad model generalization from that small case set. Any independent test must hold out the entire storm from training and model selection.

## 8. Source validation checklist

Before release, record a dated pass/fail result for each check:

| Check | Required evidence |
|---|---|
| Himawari S3 discovery | A current object can be listed and a representative object retrieved without credentials, subject to current provider conditions. |
| Satellite processing | Frame time, product metadata, calibrated values, missing-data handling, and preprocessing match the Team A training manifest. |
| PAGASA ingestion | Tests for active, expired, unavailable, malformed, and geographically irrelevant bulletins; original text retained. |
| NOAH PMTiles | `pmtiles show` or equivalent metadata inspection confirms the expected layer names; browser devtools show successful byte-range requests. |
| Map visualization | Flood scenario layers render from the real hosting origin and use `Var` with values 1/2/3. |
| Shelter catalog | Every displayed operational evacuation center is confirmed with the responsible local authority; unverified OSM points are labeled candidates. |
| Hotlines | Current official number, dialing format, service description, and verification date are recorded per entry. |
| Failure states | UI clearly identifies stale, unavailable, static, cached, mock, and live data states. |

**Source review note (2026-10-13):** The linked source pages and their published metadata were reviewed while preparing this document. This is not a continuous uptime guarantee or proof that every network request will succeed from the eventual hosting environment. Re-run runtime checks during integration and before deployments.


### Historical mode acceptance checks

- [ ] Each selected storm has at least one verified source frame and a UTC observation timestamp.
- [ ] Source object, downloaded asset, and checksum agree where a local asset is used.
- [ ] PAGASA/IBTrACS reference labels include source provenance and wind units/averaging period where applicable.
- [ ] Inference always runs before the reference label is compared or scored.
- [ ] A historical replay response carries `run_context.mode: historical_replay`, `storm_id`, and `observation_id`; the live response carries `run_context.mode: live`. Execution status (`success`, `demo`, `unavailable`, `error`) is a separate field.
- [ ] An unavailable archive frame results in an explicit unavailable status, not a substitute random frame or an unmarked mock.
- [ ] Evaluation splits by storm, and training overlap is disclosed.
