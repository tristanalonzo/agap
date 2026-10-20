import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import "maplibre-gl/dist/maplibre-gl.css";
import { getShelters } from "../api/client";
import "./FloodMap.css";

// Tell MapLibre where its background worker file is (Vite can't find it on its own).
maplibregl.setWorkerUrl(maplibreWorkerUrl);

// Let MapLibre read "pmtiles://" URLs. Register only once, even if this file reloads.
if (!window.pmtilesProtocolAdded) {
  maplibregl.addProtocol("pmtiles", new Protocol().tile);
  window.pmtilesProtocolAdded = true;
}

const DEFAULT_YEARS = 25;
const QC_CENTER = [121.05, 14.65]; // [longitude, latitude]
const BASEMAP_URL =
  "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}";
const NOAH_LAYERS_URL =
  "https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/layers/";
const NOAH_ATTRIBUTION = "Flood hazard: Project NOAH via BetterGovPH (ODbL)";

// One PMTiles file per scenario. Layer names were checked with scripts/print-pmtiles-layers.mjs.
const SCENARIOS = [
  { years: 5, label: "5-year", layer: "flood_5yr" },
  { years: 25, label: "25-year", layer: "flood_25yr" },
  { years: 100, label: "100-year", layer: "flood_100yr" },
];

// NOAH "Var" attribute: 1 = low, 2 = medium, 3 = high hazard.
const LEGEND = [
  { label: "Low", color: "#fde047" },
  { label: "Medium", color: "#fb923c" },
  { label: "High", color: "#ef4444" },
];

const SHELTER_COLOR = "#2563eb";
const NEAREST_COLOR = "#16a34a";
const YOU_COLOR = "#111827";

// Run fn now if the map has finished loading, otherwise right after it does.
function whenReady(map, fn) {
  if (map.agapReady) fn();
  else map.once("load", fn);
}

// Popup text built with DOM nodes (not HTML strings), because shelter names come from OpenStreetMap.
function popupFor(title, note) {
  const box = document.createElement("div");
  const strong = document.createElement("strong");
  strong.textContent = title;
  const small = document.createElement("div");
  small.textContent = note;
  box.append(strong, small);
  return new maplibregl.Popup({ offset: 12 }).setDOMContent(box);
}

// All shelters from GET /api/v1/shelters as small blue dots; click one for its name.
function addShelterLayer(map, shelters) {
  map.addSource("shelters", { type: "geojson", data: shelters });
  map.addLayer({
    id: "shelters",
    type: "circle",
    source: "shelters",
    paint: {
      "circle-radius": 5,
      "circle-color": SHELTER_COLOR,
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 1.5,
    },
  });
  map.on("click", "shelters", (event) => {
    const feature = event.features[0];
    popupFor(feature.properties.name, "Unverified: confirm with your barangay")
      .setLngLat(feature.geometry.coordinates)
      .addTo(map);
  });
  map.on("mouseenter", "shelters", () => (map.getCanvas().style.cursor = "pointer"));
  map.on("mouseleave", "shelters", () => (map.getCanvas().style.cursor = ""));
}

function buildStyle(selectedYears) {
  const sources = {
    basemap: { type: "raster", tiles: [BASEMAP_URL], tileSize: 256, attribution: "Tiles © Esri" },
  };
  const layers = [
    // The Esri tiles are white with see-through parts, so they need a gray layer underneath.
    { id: "background", type: "background", paint: { "background-color": "#dddddd" } },
    { id: "basemap", type: "raster", source: "basemap" },
  ];

  for (const scenario of SCENARIOS) {
    sources[scenario.layer] = {
      type: "vector",
      url: `pmtiles://${NOAH_LAYERS_URL}${scenario.layer}.pmtiles`,
      attribution: NOAH_ATTRIBUTION,
    };
    layers.push({
      id: scenario.layer,
      type: "fill",
      source: scenario.layer,
      "source-layer": scenario.layer,
      layout: { visibility: scenario.years === selectedYears ? "visible" : "none" },
      paint: {
        "fill-color": ["match", ["get", "Var"], 1, "#fde047", 2, "#fb923c", 3, "#ef4444", "#cbd5e1"],
        "fill-opacity": 0.55,
      },
    });
  }

  return { version: 8, sources, layers };
}

// years / onYearsChange come from App, so the map and the /assess request use the same scenario.
// The user picks the scenario. It is never picked from the cyclone category.
// location = the point we assessed; nearest = the nearest shelter (or null).
export default function FloodMap({ years, onYearsChange, location, nearest }) {
  const [error, setError] = useState(null);
  const [shelterError, setShelterError] = useState(null);
  const holderRef = useRef(null);
  const mapRef = useRef(null);

  // Create the map once.
  useEffect(() => {
    const map = new maplibregl.Map({
      container: holderRef.current,
      style: buildStyle(DEFAULT_YEARS),
      center: QC_CENTER,
      zoom: 12,
      minZoom: 10,
      maxZoom: 17,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    map.on("error", (event) => {
      console.error("Flood map error:", event.error);
      setError("Some map tiles could not load. Check your internet connection and reload the page.");
    });
    map.once("load", () => (map.agapReady = true));
    mapRef.current = map;
    return () => map.remove();
  }, []);

  // Shelter dots, loaded once.
  useEffect(() => {
    let cancelled = false;
    getShelters()
      .then((shelters) => {
        if (!cancelled) whenReady(mapRef.current, () => addShelterLayer(mapRef.current, shelters));
      })
      .catch((err) => {
        if (!cancelled) setShelterError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // "You" marker at the assessed point; move the map there when it changes.
  const lat = location?.latitude;
  const lon = location?.longitude;
  useEffect(() => {
    const map = mapRef.current;
    if (!map || lat === undefined) return;
    const marker = new maplibregl.Marker({ color: YOU_COLOR })
      .setLngLat([lon, lat])
      .setPopup(popupFor("You", "The location we checked"))
      .addTo(map);
    map.easeTo({ center: [lon, lat] });
    return () => marker.remove();
  }, [lat, lon]);

  // The nearest shelter stands out as a bigger green marker.
  const nearestId = nearest?.facility_id;
  const nearestLat = nearest?.latitude;
  const nearestLon = nearest?.longitude;
  const nearestName = nearest?.name;
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !nearestId) return;
    const marker = new maplibregl.Marker({ color: NEAREST_COLOR, scale: 1.1 })
      .setLngLat([nearestLon, nearestLat])
      .setPopup(popupFor(`Nearest: ${nearestName}`, "Unverified: confirm with your barangay"))
      .addTo(map);
    return () => marker.remove();
  }, [nearestId, nearestLat, nearestLon, nearestName]);

  // Show only the selected scenario's layer.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const showSelected = () => {
      for (const scenario of SCENARIOS) {
        map.setLayoutProperty(scenario.layer, "visibility", scenario.years === years ? "visible" : "none");
      }
    };
    whenReady(map, showSelected);
  }, [years]);

  return (
    <section className="card flood-map">
      <div className="card-head">
        <div>
          <h3>Flood Hazard Map</h3>
          <p className="muted small">Static flood hazard scenario — not a live flood forecast</p>
        </div>
        <span className="static-tag">STATIC</span>
      </div>

      <div className="segmented">
        {SCENARIOS.map((scenario) => (
          <button
            key={scenario.years}
            className={scenario.years === years ? "active" : ""}
            onClick={() => onYearsChange(scenario.years)}
          >
            {scenario.label}
          </button>
        ))}
      </div>

      {shelterError && <p className="flood-map-error">Shelter markers could not load ({shelterError}).</p>}
      {error && <p className="flood-map-error">{error} No color on the map does NOT mean an area is safe.</p>}

      <div ref={holderRef} className="flood-map-holder" />

      <div className="flood-map-legend">
        {LEGEND.map((item) => (
          <span key={item.label} className="small">
            <span className="dot" style={{ background: item.color }} />
            {item.label}
          </span>
        ))}
      </div>

      <div className="flood-map-legend">
        <span className="small"><span className="dot" style={{ background: YOU_COLOR }} />You</span>
        <span className="small"><span className="dot" style={{ background: NEAREST_COLOR }} />Nearest shelter</span>
        <span className="small"><span className="dot" style={{ background: SHELTER_COLOR }} />Shelters (unverified, OSM)</span>
      </div>

      <p className="muted tiny">
        Areas with no color are not marked "safe". Basemap: Esri. Flood hazard: Project NOAH via
        BetterGovPH (ODbL). Shelters: OpenStreetMap contributors (ODbL).
      </p>
    </section>
  );
}
