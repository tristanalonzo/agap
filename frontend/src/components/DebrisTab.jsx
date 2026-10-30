import { useEffect, useState } from "react";
import { getDebrisMatrix } from "../api/client";
import StatusBadge from "./StatusBadge";

// Cache the reference matrix so precautionary guidance still displays offline.
const CACHE_KEY = "agap.debrisMatrix";

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

function formatWindRange(range) {
  if (!Array.isArray(range) || range.length < 2) return null;
  const [min, max] = range;
  return max === null ? `≥ ${min} km/h` : `${min}–${max} km/h`;
}

function matchCategoryEntry(matrixList, cyclone) {
  if (!Array.isArray(matrixList) || !cyclone) return null;
  const code = cyclone.category_code?.trim().toUpperCase();
  const name = cyclone.category_name?.trim().toLowerCase();
  if (!code && (!name || name === "unknown")) return null;

  return (
    matrixList.find(
      (entry) =>
        (code && entry.code?.toUpperCase() === code) ||
        (name && entry.category?.toLowerCase() === name)
    ) ?? null
  );
}

export default function DebrisTab({ cyclone }) {
  // status: "loading", "live" (from backend), "stale" (from cache) or "unavailable".
  const [state, setState] = useState({ status: "loading", data: null, time: null, error: null });

  useEffect(() => {
    let cancelled = false;
    getDebrisMatrix()
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

  const matrixList = state.data?.wind_hazard_matrix ?? [];
  const activeTier = matchCategoryEntry(matrixList, cyclone);
  const tierLabel = activeTier
    ? `${activeTier.code} · ${activeTier.category.toUpperCase()}`
    : "UNKNOWN";
  const windRangeText = activeTier ? formatWindRange(activeTier.sustained_wind_kph_range) : null;

  return (
    <>
      <section className="card">
        <div className="card-head">
          <div>
            <h3>Debris &amp; Wind Hazards</h3>
            <p className="muted small">
              Precautionary wind-hazard reference (not an official PAGASA TCWS)
            </p>
          </div>
          <StatusBadge
            status={activeTier ? state.status : "unavailable"}
            time={state.time ?? cyclone?.inferred_at}
          />
        </div>

        <div className="two-col">
          <div className="box">
            <p className="box-label">
              REFERENCE TIER <span className="unofficial">NON-OFFICIAL</span>
            </p>
            <p className="class-name">
              {tierLabel}
              {cyclone?.is_demo ? " · DEMO" : ""}
            </p>
            <p className="small mono">
              {windRangeText ? `Band: ${windRangeText}` : "No active tier band"}
            </p>
          </div>
          <div className="box">
            <p className="box-label">RELATIVE THREAT LEVEL</p>
            <p className="small bold">
              {activeTier?.relative_threat_level ?? "Requires active cyclone classification"}
            </p>
          </div>
        </div>

        {state.status === "loading" && (
          <p className="small muted">Loading wind and debris hazard reference…</p>
        )}

        {state.status === "stale" && (
          <p className="small load-error">
            Showing cached reference matrix, may be outdated. Could not reach the server ({state.error}).
          </p>
        )}

        {state.status === "unavailable" && (
          <p className="small load-error">
            Could not load the wind and debris hazard reference matrix ({state.error}). Follow
            official PAGASA and QCDRRMO advisories directly.
          </p>
        )}

        {state.status !== "loading" && state.status !== "unavailable" && !activeTier && (
          <p className="small load-error">
            Tier-specific wind and debris guidance is unavailable because there is no active or
            recognized cyclone category classification. Do not assume safe conditions; check PAGASA
            and QCDRRMO advisories directly.
          </p>
        )}

        {activeTier?.structural_vulnerabilities?.map((vuln) => (
          <div className="hazard-row" key={vuln.element}>
            <div className="hazard-top">
              <p className="bold">{vuln.element}</p>
              <span className="danger-tag">{activeTier.code} HAZARD</span>
            </div>
            <p className="muted small">
              <strong>Vulnerability:</strong> {vuln.risk}
            </p>
            <p className="small" style={{ marginTop: "6px" }}>
              <strong>Precautionary Action:</strong> {vuln.action}
            </p>
          </div>
        ))}
      </section>

      <section className="guidance">
        <p className="bold">
          {state.data?.title ?? "Safety & Precautionary Guidance"}
        </p>
        {state.data?.notes ? (
          state.data.notes.map((note) => (
            <p key={note} className="small" style={{ marginBottom: "6px" }}>
              • {note}
            </p>
          ))
        ) : (
          <p className="small">
            This general preparedness reference is not an engineering damage model, official
            warning, or evacuation order. Do not convert a cyclone category directly into an
            official PAGASA Tropical Cyclone Wind Signal (TCWS).
          </p>
        )}
        {state.data?.classification_source_url && (
          <p className="small mono" style={{ marginTop: "8px" }}>
            Source:{" "}
            <a
              className="green-text"
              href={state.data.classification_source_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {state.data.classification_source ?? "DOST-PAGASA TCWS Reference"}
            </a>
          </p>
        )}
      </section>
    </>
  );
}
