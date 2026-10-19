import { useState } from "react";
import { noahScenarios, varLevels } from "../data/hazard";
import QcMap from "./QcMap";
import StatusBadge from "./StatusBadge";

export default function HazardMapTab({ shelter, dataStatus, time }) {
  const [periodId, setPeriodId] = useState("25yr");
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
        <h3>Nearest Evacuation Shelter</h3>
        <StatusBadge status={dataStatus} time={time} />
      </div>

      {shelter.status === "available" ? (
        <section className="card facility">
          <div>
            <p className="bold">{shelter.name}</p>
            <p className="muted small mono">
              {shelter.distance_m} m away (straight line) •{" "}
              {shelter.is_verified ? "Verified" : "Unverified, confirm with your barangay"}
            </p>
          </div>
        </section>
      ) : (
        <section className="card">
          <p className="muted small">Shelter data is not available right now.</p>
        </section>
      )}
    </>
  );
}
