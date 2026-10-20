import { useState } from "react";
import { scenarios } from "./data/scenarios";
import { toDemoReplay } from "./data/demoReplay";
import useAssessment from "./hooks/useAssessment";
import StatusBadge from "./components/StatusBadge";
import LocationCard from "./components/LocationCard";
import SatelliteCard from "./components/SatelliteCard";
import HrwsCard from "./components/HrwsCard";
import { alertLabel } from "./data/alertLabel";
import HazardMapTab from "./components/HazardMapTab";
import DebrisTab from "./components/DebrisTab";
import ActionTab from "./components/ActionTab";

const TABS = ["Overview", "Hazard Map", "Debris", "Action / SOS"];

// Fixed point in central QC until location search exists.
const QC_LAT = 14.65;
const QC_LON = 121.05;
const FLOOD_YEARS = 25;

export default function App() {
  const [scenarioId, setScenarioId] = useState("live");
  const [tab, setTab] = useState("Overview");
  const { assessment, error, loading } = useAssessment(QC_LAT, QC_LON, FLOOD_YEARS);

  if (loading) {
    return <div className="app"><p className="content muted">Loading…</p></div>;
  }
  if (error) {
    return <div className="app"><p className="content load-error">Could not load data: {error}</p></div>;
  }

  const scenario = scenarios.find((s) => s.id === scenarioId);
  // "Mock API" chip = the assessment as loaded. Other chips = mockup example values.
  const data = scenario.id === "live" ? assessment : toDemoReplay(assessment, scenario);
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
            <span className="chip-demo">DEMO</span> {s.chip}
          </button>
        ))}
      </div>

      <div className="mode-bar">
        <strong>MODE: DEMO</strong> · {scenario.mode} · Not real data
      </div>

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
            <SatelliteCard cyclone={data.cyclone_assessment} visual={scenario.id} />
            <HrwsCard rainfall={rainfall} />
          </>
        )}
        {tab === "Hazard Map" && (
          <HazardMapTab shelter={data.nearest_shelter} time={data.generated_at} />
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
