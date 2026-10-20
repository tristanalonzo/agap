import { useState } from "react";

// Lets the user pick the point we assess: their GPS position, or a typed latitude/longitude.
export default function LocationControls({ location, onChange }) {
  const [message, setMessage] = useState(null);
  const [showManual, setShowManual] = useState(false);
  const [latText, setLatText] = useState(String(location.lat));
  const [lonText, setLonText] = useState(String(location.lon));

  function useGps() {
    if (!navigator.geolocation) {
      setMessage("This browser can't share your location. Set it by hand below.");
      setShowManual(true);
      return;
    }
    setMessage("Asking for your location…");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setMessage(null);
        onChange({
          lat: Number(position.coords.latitude.toFixed(5)),
          lon: Number(position.coords.longitude.toFixed(5)),
          source: "Your GPS location",
        });
      },
      () => {
        setMessage("Location not available (permission denied or no signal). Set it by hand below.");
        setShowManual(true);
      },
      { timeout: 10000 }
    );
  }

  function setManual(event) {
    event.preventDefault();
    const lat = Number(latText);
    const lon = Number(lonText);
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || latText === "" || lonText === "") {
      setMessage("Enter numbers, for example 14.6516 and 121.0493.");
      return;
    }
    setMessage(null);
    onChange({ lat, lon, source: "Set by hand" });
  }

  return (
    <section className="card location-controls">
      <p className="small muted">Showing: {location.source}</p>
      <div className="location-buttons">
        <button className="btn" onClick={useGps}>
          Use my location
        </button>
        <button className="btn secondary" onClick={() => setShowManual(!showManual)}>
          Set location
        </button>
      </div>
      <p className="tiny muted">We use your location only to find your nearest shelter.</p>
      {message && <p className="small load-error">{message}</p>}

      {showManual && (
        <form className="manual-location" onSubmit={setManual}>
          <label className="small">
            Latitude
            <input value={latText} onChange={(e) => setLatText(e.target.value)} inputMode="decimal" />
          </label>
          <label className="small">
            Longitude
            <input value={lonText} onChange={(e) => setLonText(e.target.value)} inputMode="decimal" />
          </label>
          <button className="btn" type="submit">
            Set
          </button>
        </form>
      )}
    </section>
  );
}
