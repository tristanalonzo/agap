// Shows where a card's data comes from (LIVE / DEMO / STALE / UNAVAILABLE) and when.
// "fresh" is what the PAGASA service calls data it read just now.
const LABELS = { live: "LIVE", fresh: "LIVE", demo: "DEMO", stale: "STALE" };

function formatTime(isoText) {
  if (!isoText) return "no time";
  return new Date(isoText).toLocaleString("en-PH", {
    timeZone: "Asia/Manila",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function StatusBadge({ status, time }) {
  // Anything we don't recognise (unavailable, parse_error, ...) is shown as UNAVAILABLE.
  const label = LABELS[status] ?? "UNAVAILABLE";
  return (
    <span className={`status-badge ${label.toLowerCase()}`}>
      {label} · {formatTime(time)}
    </span>
  );
}
