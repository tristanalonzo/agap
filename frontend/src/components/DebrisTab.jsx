import { debrisHazards } from "../data/safety";

export default function DebrisTab({ cyclone }) {
  const tier = (cyclone.category_name ?? "Unknown").toUpperCase();

  return (
    <>
      <section className="card">
        <div className="card-head">
          <div>
            <h3>Debris &amp; Wind Hazards</h3>
            <p className="muted small">Material vulnerabilities calibrated to wind speeds</p>
          </div>
          <span className="static-tag">{tier} TIER{cyclone.is_demo && " · DEMO"}</span>
        </div>

        {debrisHazards.map((h) => (
          <div className="hazard-row" key={h.title}>
            <div className="hazard-top">
              <p className="bold">{h.title}</p>
              <span className="danger-tag">{h.tag}</span>
            </div>
            <p className="muted small">{h.text}</p>
          </div>
        ))}
      </section>

      <section className="guidance">
        <p className="bold">Safety Guidance (Guideline §8.4)</p>
        <p>
          Corrugated iron (G.I.) sheets and broken tree branches represent severe
          projectile hazards during elevated gusts. This general guidance does not
          replace official evacuation instructions from the Quezon City Disaster Risk
          Reduction and Management Office (QCDRRMO).
        </p>
      </section>
    </>
  );
}