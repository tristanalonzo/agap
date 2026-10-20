import { useState } from "react";
import { scenarios } from "./data/scenarios";
import { toDemoReplay } from "./data/demoReplay";
import useAssessment from "./hooks/useAssessment";
import StatusBadge from "./components/StatusBadge";
import LocationCard from "./components/LocationCard";
import LocationControls from "./components/LocationControls";
import SatelliteCard from "./components/SatelliteCard";
import HrwsCard from "./components/HrwsCard";
import { alertLabel } from "./data/alertLabel";
import HazardMapTab from "./components/HazardMapTab";
import DebrisTab from "./components/DebrisTab";
import ActionTab from "./components/ActionTab";

const TABS = ["Overview", "Hazard Map", "Debris", "Action / SOS"];

// Until the user shares or sets a location: Quezon Memorial Circle.
const DEFAULT_LOCATION = { lat: 14.6516, lon: 121.0493, source: "Default: Quezon Memorial Circle" };

// When the last good update is over 5 minutes old, every live card says STALE.
function markStale(data) {
  return { ...data, rainfall_warning: { ...data.rainfall_warning, status: "stale" } };
}

export default function App() {
  const [scenarioId, setScenarioId] = useState("live");
  const [tab, setTab] = useState("Overview");
  const [location, setLocation] = useState(DEFAULT_LOCATION);
  // The user picks the flood scenario (map + request). It is never picked from the cyclone category.
  const [years, setYears] = useState(25);
  const { assessment, error, loading, isStale, minutesAgo, refresh } = useAssessment(
    location.lat,
    location.lon,
    years
  );

  if (loading) {
    return <div className="app"><p className="content muted">Loading…</p></div>;
  }
  if (!assessment) {
    return (
      <div className="app">
        <div className="content">
          <p className="load-error">Could not load data: {error}</p>
          <button className="btn" onClick={refresh}>Retry</button>
          <LocationControls location={location} onChange={setLocation} />
        </div>
      </div>
    );
  }

  const scenario = scenarios.find((s) => s.id === scenarioId);
  const isLive = scenario.id === "live";
  // "Live API" chip = the assessment as loaded. Other chips = mockup example values.
  let data = isLive ? assessment : toDemoReplay(assessment, scenario);
  if (isLive && isStale) data = markStale(data);
  const rainfall = data.rainfall_warning;

  return (
    <div className="app">
      {/* Scenario switcher */}
      <div className="chips">
        {scenarios.map((s) => (
          <button
            key={s.id}
            className={`chip ${s.id === scenarioId ? "active" : ""}`}
            onClick={() => setScenarioId(s.id)}
          >
            {s.id !== "live" && <span className="chip-demo">DEMO</span>} {s.chip}
          </button>
        ))}
      </div>

      <div className="mode-bar">
        {isLive ? (
          <>
            <strong>MODE: LIVE API</strong> · Rainfall + shelter are real · Cyclone card is DEMO (no model yet)
          </>
        ) : (
          <>
            <strong>MODE: DEMO</strong> · {scenario.mode} · Not real data
          </>
        )}
      </div>

      <div className="refresh-bar">
        <span className={`small ${isStale ? "load-error" : "muted"}`}>
          {isStale && "STALE · "}Updated {minutesAgo === 0 ? "just now" : `${minutesAgo} min ago`}
        </span>
        <button className="btn small-btn" onClick={refresh}>Refresh</button>
      </div>
      {error && (
        <p className="refresh-error small load-error">
          Couldn't update: {error} Showing the last result. <button className="link-btn" onClick={refresh}>Retry</button>
        </p>
      )}

      <div className={`banner ${rainfall.alert_level}`}>
        <span>
          <strong>PAGASA WARNING:</strong> {alertLabel(rainfall.alert_level)}
        </span>
        <StatusBadge status={rainfall.status} time={rainfall.retrieved_at} />
      </div>

      <main className="content">
        {tab === "Overview" && (
          <>
            <LocationCard location={data.location} />
            <LocationControls location={location} onChange={setLocation} />
            <SatelliteCard cyclone={data.cyclone_assessment} visual={scenario.id} />
            <HrwsCard rainfall={rainfall} />
          </>
        )}
        {tab === "Hazard Map" && (
          <HazardMapTab
            shelter={data.nearest_shelter}
            location={data.location}
            time={data.generated_at}
            isStale={isLive && isStale}
            years={years}
            onYearsChange={setYears}
          />
        )}
        {tab === "Debris" && <DebrisTab cyclone={data.cyclone_assessment} />}
        {tab === "Action / SOS" && <ActionTab rainfall={rainfall} />}
      </main>

      {/* Bottom navigation */}
      <nav className="tabbar">
        {TABS.map((t) => (
          <button
            key={t}
            className={t === tab ? "active" : ""}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </nav>
    </div>
  );
}
