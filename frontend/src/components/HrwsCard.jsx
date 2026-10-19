import StatusBadge from "./StatusBadge";
import { alertLabel } from "../data/alertLabel";

export default function HrwsCard({ rainfall }) {
  const notLoaded = !["live", "demo", "stale"].includes(rainfall.status);

  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h3>Official Heavy Rainfall Warning (HRWS)</h3>
          <p className="muted small">PAGASA NCR-PRSD Advisory Snapshot</p>
        </div>
        <StatusBadge status={rainfall.status} time={rainfall.retrieved_at} />
      </div>

      <div className={`alert-box ${rainfall.alert_level}`}>
        <div className="alert-row">
          <span className="alert-chip">{alertLabel(rainfall.alert_level)}</span>
        </div>
        {notLoaded && (
          <p>
            The PAGASA rainfall warning could not be loaded. This does NOT mean there is no
            warning. Check PAGASA directly.
          </p>
        )}
        {rainfall.raw_text && <p>{rainfall.raw_text}</p>}
      </div>

      <div className="two-col">
        <div className="box">
          <p className="box-label">AFFECTED AREA</p>
          <p className="mono bold">{rainfall.affected_area ?? "Not given"}</p>
        </div>
        <div className="box">
          <p className="box-label">SOURCE</p>
          <a className="mono green-text" href={rainfall.source_url} target="_blank" rel="noreferrer">
            bagong.pagasa.dost.gov.ph
          </a>
        </div>
      </div>
    </section>
  );
}
