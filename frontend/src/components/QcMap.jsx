import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const QC_CENTER = [14.65, 121.05];
// QC bounding box from the playbook's config (lat min/max, lon min/max)
const QC_BOUNDS = [
  [14.58, 120.98],
  [14.77, 121.14],
];
const TILES =
  "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}";

export default function QcMap({ color, recenterKey }) {
  const holderRef = useRef(null);
  const mapRef = useRef(null);
  const boxRef = useRef(null);

  useEffect(() => {
    const map = L.map(holderRef.current, {
      zoomControl: false,
      minZoom: 10,
      maxZoom: 17,
    }).setView(QC_CENTER, 12);

    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer(TILES, { attribution: "Tiles © Esri" }).addTo(map);

    boxRef.current = L.rectangle(QC_BOUNDS, {
      weight: 2,
      fillOpacity: 0.08,
    }).addTo(map);

    L.circleMarker(QC_CENTER, {
      radius: 6,
      color: "#1b7fc4",
      fillColor: "#1b7fc4",
      fillOpacity: 1,
    }).addTo(map);

    mapRef.current = map;
    return () => map.remove();
  }, []);

  // Box color follows the selected return period
  useEffect(() => {
    boxRef.current?.setStyle({ color, fillColor: color });
  }, [color]);

  // Recenter QC button
  useEffect(() => {
    mapRef.current?.setView(QC_CENTER, 12);
  }, [recenterKey]);

  return <div ref={holderRef} className="leaflet-holder" />;
}