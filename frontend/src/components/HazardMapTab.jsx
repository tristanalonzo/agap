import FloodMap from "./FloodMap";
import StatusBadge from "./StatusBadge";

// 350 -> "350 m", 1234 -> "1.2 km"
function formatDistance(meters) {
  return meters < 1000 ? `${meters} m` : `${(meters / 1000).toFixed(1)} km`;
}

export default function HazardMapTab({ shelter, location, time, isStale, years, onYearsChange }) {
  const available = shelter.status === "available";
  const badgeStatus = !available ? "unavailable" : isStale ? "stale" : "live";

  return (
    <>
      <FloodMap
        years={years}
        onYearsChange={onYearsChange}
        location={location}
        nearest={available ? shelter : null}
      />

      <div className="section-head">
        <h3>Nearest Evacuation Shelter</h3>
        <StatusBadge status={badgeStatus} time={time} />
      </div>

      {available ? (
        <section className="card facility">
          <div>
            <p className="bold">{shelter.name}</p>
            <p className="muted small mono">{formatDistance(shelter.distance_m)} away (straight line, not walking route)</p>
            {!shelter.is_verified && (
              <p className="small">
                <span className="unverified-tag">UNVERIFIED</span> From OpenStreetMap. Confirm with your
                barangay that it is open as an evacuation center.
              </p>
            )}
          </div>
        </section>
      ) : (
        <section className="card">
          <p className="muted small">
            Shelter data is not available right now. Ask your barangay hall for the nearest
            evacuation center.
          </p>
        </section>
      )}
    </>
  );
}
