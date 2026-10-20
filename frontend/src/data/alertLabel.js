// Text for a PAGASA alert level ("red", "orange", "yellow", "none" or "unknown").
// "none" only comes from PAGASA saying there is no warning; a failed check is "unknown".
export function alertLabel(level) {
  if (level === "unknown") return "UNKNOWN — not loaded";
  if (level === "none") return "NO HEAVY RAINFALL WARNING";
  return `${level.toUpperCase()} WARNING`;
}
