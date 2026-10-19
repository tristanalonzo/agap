export default function LocationCard({ location }) {
  return (
    <section className="card location-card">
      <div className="location-info">
        <h3>{location.jurisdiction}</h3>
        <p className="muted mono">
          {location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E
        </p>
      </div>
      {location.in_bounds ? (
        <span className="pill-green">● QC BOUNDS OK</span>
      ) : (
        <span className="status-badge unavailable">OUTSIDE QC</span>
      )}
    </section>
  );
}
