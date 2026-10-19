import FloodMap from "./FloodMap";
import StatusBadge from "./StatusBadge";

export default function HazardMapTab({ shelter, dataStatus, time }) {
  return (
    <>
      <FloodMap />

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
