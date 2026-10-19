export default function LocationCard() {
  return (
    <section className="card location-card">
      <div className="location-info">
        <h3>
          Quezon City (Central Sector){" "}
          <span className="tag-blue">San Juan / Tullahan Basin</span>
        </h3>
        <p className="muted mono">
          14.6500°N, 121.0500°E • Pilot Jurisdiction Validated
        </p>
      </div>
      <span className="pill-green">● QC BOUNDS OK</span>
    </section>
  );
}