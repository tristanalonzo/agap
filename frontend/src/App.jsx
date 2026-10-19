import { useState } from "react";
import { scenarios } from "./data/scenarios";
import LocationCard from "./components/LocationCard";
import SatelliteCard from "./components/SatelliteCard";
import HrwsCard from "./components/HrwsCard";
import HazardMapTab from "./components/HazardMapTab";
import DebrisTab from "./components/DebrisTab";
import ActionTab from "./components/ActionTab";

const TABS = ["Overview", "Hazard Map", "Debris", "Action / SOS"];

export default function App() {
  const [scenarioId, setScenarioId] = useState("live");
  const [tab, setTab] = useState("Overview");

  const scenario = scenarios.find((s) => s.id === scenarioId);

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
            {s.chip}
          </button>
        ))}
      </div>

      <div className="mode-bar">
        <strong>MODE:</strong> {scenario.mode}
      </div>

      <div className={`banner ${scenario.alert.level}`}>
        <span>
          <strong>PAGASA WARNING:</strong> {scenario.alert.label}
        </span>
        <span>FRESH (12m ago)</span>
      </div>

      <main className="content">
        {tab === "Overview" && (
          <>
            <LocationCard />
            <SatelliteCard scenario={scenario} />
            <HrwsCard scenario={scenario} />
          </>
        )}
        {tab === "Hazard Map" && <HazardMapTab />}
        {tab === "Debris" && <DebrisTab scenario={scenario} />}
        {tab === "Action / SOS" && <ActionTab scenario={scenario} />}
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