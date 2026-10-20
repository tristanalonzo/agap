import { useEffect, useState } from "react";
import { getHotlines } from "../api/client";
import StatusBadge from "./StatusBadge";

// "2026-10-13" -> "Oct 13, 2026"
function formatDate(dateText) {
  return new Date(`${dateText}T00:00:00+08:00`).toLocaleDateString("en-PH", {
    timeZone: "Asia/Manila",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// Emergency hotlines from backend static/qc_hotlines.json. Tap a row to call.
export default function HotlinesSection() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getHotlines()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    // Even if the list fails to load, still give one number to call.
    return (
      <>
        <div className="section-head">
          <p className="mono tiny muted">EMERGENCY HOTLINES:</p>
          <StatusBadge status="unavailable" time={new Date().toISOString()} />
        </div>
        <p className="small load-error">Could not load the hotline list ({error}).</p>
        <a className="hotline-row" href="tel:911">
          <span className="bold">Call 911</span>
          <span className="mono tiny muted">National emergency hotline</span>
        </a>
      </>
    );
  }

  if (!data) {
    return <p className="small muted">Loading hotlines…</p>;
  }

  // Priority numbers first; otherwise keep the file's order.
  const hotlines = [...data.hotlines].sort((a, b) => Number(b.priority) - Number(a.priority));

  return (
    <>
      <div className="section-head">
        <p className="mono tiny muted">EMERGENCY HOTLINES (TAP TO CALL):</p>
        <span className="green-text mono tiny">VERIFIED {formatDate(data.last_verified_date)}</span>
      </div>
      {hotlines.length === 0 && <p className="small muted">No hotlines in the list.</p>}
      <div className="hotline-list">
        {hotlines.map((h) => (
          <a className="hotline-row" key={h.id} href={`tel:${h.dial_string}`}>
            <span className="bold">{h.label}</span>
            <span className="mono small">
              {h.number}
              {h.extension ? ` ext. ${h.extension}` : ""}
            </span>
            <span className="tiny muted">{h.service_type}</span>
          </a>
        ))}
      </div>
    </>
  );
}
