import { useEffect, useState } from "react";
import { getHotlines } from "../api/client";
import StatusBadge from "./StatusBadge";

// The last list that loaded, so the numbers still show when the backend is down.
const CACHE_KEY = "agap.hotlines";

function saveToCache(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ data, savedAt: new Date().toISOString() }));
  } catch {
    // Storage blocked or full: the list still shows, it just won't work offline.
  }
}

function loadFromCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY));
  } catch {
    return null;
  }
}

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
  // status: "loading", "live" (from the backend), "stale" (from the cache) or "unavailable".
  const [state, setState] = useState({ status: "loading", data: null, time: null, error: null });

  useEffect(() => {
    let cancelled = false;
    getHotlines()
      .then((data) => {
        if (cancelled) return;
        saveToCache(data);
        setState({ status: "live", data, time: new Date().toISOString(), error: null });
      })
      .catch((err) => {
        if (cancelled) return;
        const cached = loadFromCache();
        if (cached?.data) {
          setState({ status: "stale", data: cached.data, time: cached.savedAt, error: err.message });
        } else {
          setState({ status: "unavailable", data: null, time: new Date().toISOString(), error: err.message });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.status === "loading") {
    return <p className="small muted">Loading hotlines…</p>;
  }

  if (state.status === "unavailable") {
    // Nothing loaded and nothing cached: still give one number to call.
    return (
      <>
        <div className="section-head">
          <p className="mono tiny muted">EMERGENCY HOTLINES:</p>
          <StatusBadge status="unavailable" time={state.time} />
        </div>
        <p className="small load-error">Could not load the hotline list ({state.error}).</p>
        <a className="hotline-row" href="tel:911">
          <span className="bold">Call 911</span>
          <span className="mono tiny muted">National emergency hotline</span>
        </a>
      </>
    );
  }

  // Priority numbers first; otherwise keep the file's order.
  const hotlines = [...state.data.hotlines].sort((a, b) => Number(b.priority) - Number(a.priority));

  return (
    <>
      <div className="section-head">
        <p className="mono tiny muted">EMERGENCY HOTLINES (TAP TO CALL):</p>
        <StatusBadge status={state.status} time={state.time} />
      </div>
      <p className="mono tiny green-text hotline-verified">
        List verified {formatDate(state.data.last_verified_date)}
      </p>
      {state.status === "stale" && (
        <p className="small load-error">
          Showing a cached list, may be outdated. Could not reach the server ({state.error}).
        </p>
      )}
      {hotlines.length === 0 && <p className="small muted">No hotlines in the list.</p>}
      <div className="hotline-list">
        {hotlines.map((h) => (
          <a className="hotline-row" key={h.id} href={`tel:${h.dial_string}`}>
            <span className="bold">{h.label}</span>
            <span className="mono small">
              {h.number}
              {h.extension ? ` ext. ${h.extension}` : ""}
            </span>
            <span className="tiny muted">{h.description}</span>
          </a>
        ))}
      </div>
    </>
  );
}
