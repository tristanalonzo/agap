import StatusBadge from "./StatusBadge";

export default function SatelliteCard({ cyclone, visual }) {
  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h3>Himawari-9 Clean IR (Band 13)</h3>
          <p className="muted small">Experimental ResNet-18 Classifier (Model estimate)</p>
        </div>
        <StatusBadge status={cyclone.status} time={cyclone.inferred_at} />
      </div>

      {cyclone.is_demo && <p className="demo-banner">DEMO — not a real prediction</p>}

      <div className={`sat-view ${visual}`}>
        <span className="sat-label top-left">ILLUSTRATION — not a real satellite image</span>
        <div className="eye" />
      </div>

      <div className="two-col">
        <div className="box">
          <p className="box-label">
            MODEL CLASSIFICATION <span className="unofficial">NON-OFFICIAL</span>
          </p>
          <p className="class-name">{cyclone.category_name ?? "Unknown"}</p>
          <p className="small mono">{cyclone.sustained_wind_kph ?? "?"} km/h est. sustained</p>
        </div>
        <div className="box">
          <p className="box-label">MODEL VERSION</p>
          <p className="ref-name mono">{cyclone.model_version ?? "None (mock)"}</p>
          <p className="small mono">Confidence: {cyclone.confidence ?? "n/a"}</p>
        </div>
      </div>

      {cyclone.warnings.map((warning) => (
        <p className="warning-text" key={warning}>⚠ {warning}</p>
      ))}

      <p className="notice">
        <strong>Notice:</strong> Model classification estimates meteorological storm
        intensity and is <em>not</em> an official PAGASA Tropical Cyclone Wind Signal
        (TCWS). TCWS incorporates municipal terrain and lead times.
      </p>
    </section>
  );
}
