import { useCallback, useEffect, useRef, useState } from "react";
import { getAssessment } from "../api/client";

const POLL_MS = 60 * 1000; // ask the backend again every minute
const STALE_MS = 5 * 60 * 1000; // older than 5 minutes = STALE

// Loads the assessment, then every 60 s while the tab is visible.
// Keeps the last good result when a request fails, so the cards don't go blank.
export default function useAssessment(lat, lon, years) {
  const [assessment, setAssessment] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [now, setNow] = useState(() => Date.now());
  const inFlight = useRef(false);
  const latestRequest = useRef(0);

  const load = useCallback(() => {
    const requestId = ++latestRequest.current;
    const isLatest = () => requestId === latestRequest.current; // a newer request replaces older ones
    inFlight.current = true;
    getAssessment(lat, lon, years)
      .then((data) => {
        if (!isLatest()) return;
        setAssessment(data);
        setError(null);
        setLastUpdated(Date.now());
      })
      .catch((err) => {
        if (isLatest()) setError(err.message);
      })
      .finally(() => {
        if (isLatest()) inFlight.current = false;
      });
  }, [lat, lon, years]);

  // Load now (and again whenever location or flood scenario changes), then poll.
  useEffect(() => {
    load();
    const timer = setInterval(() => {
      // Skip while the tab is hidden or the last request is still running.
      if (document.visibilityState === "visible" && !inFlight.current) load();
    }, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

  // Tick every 15 s so "Updated X min ago" and STALE stay current.
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 15 * 1000);
    return () => clearInterval(timer);
  }, []);

  return {
    assessment,
    error,
    loading: !assessment && !error,
    lastUpdated,
    isStale: lastUpdated !== null && now - lastUpdated > STALE_MS,
    // max(0, …): "now" only ticks every 15 s, so it can be a little older than lastUpdated.
    minutesAgo: lastUpdated === null ? null : Math.max(0, Math.floor((now - lastUpdated) / 60000)),
    refresh: load,
  };
}
