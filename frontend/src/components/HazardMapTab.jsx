import { useState } from "react";
import { noahScenarios, varLevels, facilities } from "../data/hazard";
import QcMap from "./QcMap";

export default function HazardMapTab() {
  const [periodId, setPeriodId] = useState("5yr");
  const [recenterKey, setRecenterKey] = useState(0);
  const period = noahScenarios.find((p) => p.id === periodId);

  return (
    <>
      <section className="card">
        <p className="info-note">
          <strong>Static Modeled Scenarios:</strong> Project NOAH return-period layers
          represent independent hydrological models, <em>not</em> live water depth
          forecasts or road traffic status.
        </p>

        <div className="card-head">
          <div>
            <h3>Project NOAH Hazard Scenarios</h3>
            <p className="muted small">Independent Return-Period Selector (Var 1–3)</p>
          </div>
          <button className="recenter" onClick={() => setRecenterKey((k) => k + 1)}>
            Recenter QC
          </button>
        </div>

        <div className="segmented">
          {noahScenarios.map((p) => (
            <button
              key={p.id}
              className={p.id === periodId ? "active" : ""}
              onClick={() => setPeriodId(p.id)}
            >
              {p.label}
            </button>
          ))}
        </div>

        <div className="map-box">
          <QcMap color={period.color} recenterKey={recenterKey} />

          <div className="map-callout">
            <div>
              <p className="tiny muted mono">STATIC MODEL INTERSECT</p>
              <p className="bold">
                <span className="dot" style={{ background: period.color }} />
                {period.zone} (Var: {period.varLevel}, {period.depth})
              </p>
            </div>
            <span className="static-tag">STATIC NOAH</span>
          </div>

          <div className="map-legend">
            <p className="tiny muted mono">NOAH VAR LEVELS</p>
            {varLevels.map((v) => (
              <p key={v.label} className="tiny">
                <span className="dot" style={{ background: v.color }} />
                {v.label}
              </p>
            ))}
          </div>
        </div>
      </section>

      <div className="section-head">
        <h3>Nearby Evacuation Facilities</h3>
        <span className="mono tiny muted">UNVERIFIED</span>
      </div>

      {facilities.map((f) => (
        <section className="card facility" key={f.name}>
          <div>
            <p className="bold">{f.name}</p>
            <p className="muted small mono">
              District {f.district} • Unverified, confirm with your barangay
            </p>
          </div>
          <div className="facility-right">
            <span className="pill-green">CAPACITY: {f.capacity.toLocaleString()}</span>
            <a href="#" onClick={(e) => e.preventDefault()}>View Pin</a>
          </div>
        </section>
      ))}
    </>
  );
}