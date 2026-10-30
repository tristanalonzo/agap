// Every call to the backend lives in this file.
import mockAssessment from "../mocks/assess.sample.json";

// true = use the sample response from docs/contract (no backend needed).
// false = call the real FastAPI backend.
export const USE_MOCK = false;

export async function getAssessment(lat, lon, years) {
  if (USE_MOCK) {
    return structuredClone(mockAssessment);
  }
  const response = await fetch("/api/v1/telemetry/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitude: lat, longitude: lon, flood_return_period_years: years }),
  });
  if (response.status === 422) {
    // The backend explains what is wrong, e.g. "Location (...) is outside Quezon City."
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : "Invalid location or flood scenario.";
    throw new Error(detail);
  }
  if (!response.ok) {
    throw new Error(`Assessment request failed (HTTP ${response.status})`);
  }
  return response.json();
}

export async function getHotlines() {
  const response = await fetch("/api/v1/hotlines");
  if (!response.ok) {
    throw new Error(`Hotlines request failed (HTTP ${response.status})`);
  }
  return response.json();
}

export async function getShelters() {
  const response = await fetch("/api/v1/shelters");
  if (!response.ok) {
    throw new Error(`Shelters request failed (HTTP ${response.status})`);
  }
  return response.json();
}

export async function getDebrisMatrix() {
  const response = await fetch("/api/v1/debris-matrix");
  if (!response.ok) {
    throw new Error(`Debris matrix request failed (HTTP ${response.status})`);
  }
  return response.json();
}
