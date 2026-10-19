export default function SatelliteCard({ scenario }) {
  const { obs, badge, unevenScore, coreTemp, classification, windKmh, reference } = scenario;

  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h3>Himawari-9 Clean IR (Band 13)</h3>
          <p className="muted small">Experimental ResNet-18 Classifier (Model estimate)</p>
        </div>
        <span className="tag-blue">{badge}</span>
      </div>

      <div className={`sat-view ${scenario.id}`}>
        <span className="sat-label top-left">{obs}</span>
        <span className="sat-label top-right">UNEVEN SCORE: {unevenScore}</span>
        <div className="eye" />
        <div className="sat-legend">
          <span className="red-text">{coreTemp}</span>
          <span className="blue-text">-30°C Edge</span>
        </div>
      </div>

      <div className="two-col">
        <div className="box">
          <p className="box-label">
            MODEL CLASSIFICATION <span className="unofficial">NON-OFFICIAL</span>
          </p>
          <p className="class-name">{classification}</p>
          <p className="small mono">{windKmh} km/h est. sustained</p>
        </div>
        <div className="box">
          <p className="box-label">EVALUATION REFERENCE</p>
          <p className="ref-name mono">{reference.label}</p>
          <p className="small mono">{reference.note}</p>
        </div>
      </div>

      <p className="notice">
        <strong>Notice:</strong> Model classification estimates meteorological storm
        intensity and is <em>not</em> an official PAGASA Tropical Cyclone Wind Signal
        (TCWS). TCWS incorporates municipal terrain and lead times.
      </p>
    </section>
  );
}