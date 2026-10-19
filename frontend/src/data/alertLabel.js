// Text for a PAGASA alert level ("red", "orange", "yellow" or "unknown").
export function alertLabel(level) {
  return level === "unknown" ? "UNKNOWN — not loaded" : `${level.toUpperCase()} ALERT`;
}
