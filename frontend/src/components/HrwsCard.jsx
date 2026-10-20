import StatusBadge from "./StatusBadge";
import { alertLabel } from "../data/alertLabel";

function formatTime(isoText) {
  return new Date(isoText).toLocaleString("en-PH", {
    timeZone: "Asia/Manila",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function HrwsCard({ rainfall }) {
  const level = rainfall.alert_level;

  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h3>Official Heavy Rainfall Warning (HRWS)</h3>
          <p className="muted small">PAGASA NCR-PRSD Advisory Snapshot</p>
        </div>
        <StatusBadge status={rainfall.status} time={rainfall.retrieved_at} />
      </div>

      <div className={`alert-box ${level}`}>
        <div className="alert-row">
          <span className="alert-chip">{alertLabel(level)}</span>
          {rainfall.issued_at && <span className="mono tiny">Issued {formatTime(rainfall.issued_at)}</span>}
        </div>

        {level === "unknown" && (
          <p>
            Couldn't check PAGASA right now. This does NOT mean there is no warning.{" "}
            <a href={rainfall.source_url} target="_blank" rel="noreferrer">
              Check PAGASA directly
            </a>
            .
          </p>
        )}
        {level === "none" && (
          <p>
            PAGASA's NCR page says there is no heavy rainfall warning right now. Keep watching for
            updates; this can change quickly.
          </p>
        )}
        {rainfall.status === "stale" && (
          <p className="warning-text">
            Could not reach PAGASA just now. Showing the last result we got; it may be outdated.
          </p>
        )}

        {rainfall.raw_text && (
          <details className="advisory">
            <summary>Full advisory</summary>
            <p>{rainfall.raw_text}</p>
          </details>
        )}
      </div>

      <div className="two-col">
        <div className="box">
          <p className="box-label">AFFECTED AREA</p>
          <p className="mono bold">{rainfall.affected_area ?? "Not given"}</p>
        </div>
        <div className="box">
          <p className="box-label">SOURCE</p>
          <a className="mono green-text" href={rainfall.source_url} target="_blank" rel="noreferrer">
            PAGASA NCR-PRSD
          </a>
        </div>
      </div>
    </section>
  );
}
