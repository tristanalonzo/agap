"""Load static/qc_shelters.geojson and find the nearest shelter by Haversine distance.

OpenStreetMap shelters are is_verified false (AGENTS.md safety rule 5): OSM tags do not prove
a place is an official, open evacuation centre.

How qc_shelters.geojson was made (rerun at https://overpass-turbo.eu, then Export -> GeoJSON).
The query in docs/reference/apis_and_endpoints.md mostly returns bus stops and gazebos, so this
one asks for evacuation centres, barangay halls, community centres and covered courts instead:

    [out:json][timeout:120];
    area["name"="Quezon City"]["boundary"="administrative"]["admin_level"="6"]->.qc;
    (
      nwr["emergency"="evacuation_centre"](area.qc);
      nwr["amenity"="townhall"](area.qc);
      nwr["amenity"="community_centre"](area.qc);
      nwr["leisure"~"sports_hall|sports_centre"]["name"~"covered court|multi.?purpose",i](area.qc);
      nwr["amenity"="shelter"]["name"~"covered court|multi.?purpose|evacuation",i](area.qc);
    );
    out center tags;

Only places with a name were kept.
"""

import json
import math
from pathlib import Path
from typing import Any

from app.schemas import NearestShelter

SHELTERS_FILE = Path(__file__).parent.parent / "static" / "qc_shelters.geojson"
EARTH_RADIUS_M = 6_371_000

# Loaded once, the first time it is needed.
_shelters: list[dict[str, Any]] | None = None


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance in meters between two points on Earth."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def feature_center(geometry: dict[str, Any]) -> tuple[float, float] | None:
    """(latitude, longitude) of a GeoJSON geometry. Polygons become the average of their corners."""
    if geometry["type"] == "Point":
        lon, lat = geometry["coordinates"]
        return lat, lon
    if geometry["type"] == "Polygon":
        ring = geometry["coordinates"][0]
        return sum(p[1] for p in ring) / len(ring), sum(p[0] for p in ring) / len(ring)
    return None


def load_shelters(path: Path = SHELTERS_FILE) -> list[dict[str, Any]]:
    """Read the GeoJSON file into simple dicts: facility_id, name, latitude, longitude, tags."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    shelters = []
    for feature in data.get("features", []):
        center = feature_center(feature["geometry"])
        if center is None:
            continue
        properties = feature.get("properties", {})
        shelters.append(
            {
                "facility_id": feature.get("id") or properties.get("@id", "unknown"),
                "name": properties.get("name") or "Unnamed shelter",
                "latitude": center[0],
                "longitude": center[1],
                "tags": properties.get("tags", {}),
            }
        )
    return shelters


def get_shelters() -> list[dict[str, Any]]:
    global _shelters
    if _shelters is None:
        _shelters = load_shelters()
    return _shelters


def nearest_shelter(
    latitude: float, longitude: float, shelters: list[dict[str, Any]] | None = None
) -> NearestShelter:
    """The closest shelter to a point, by straight-line distance (not walking distance)."""
    if shelters is None:
        shelters = get_shelters()
    if not shelters:
        return NearestShelter(
            status="no_shelter_data",
            facility_id=None,
            name=None,
            latitude=None,
            longitude=None,
            distance_m=None,
            is_verified=None,
        )

    closest = min(
        shelters, key=lambda s: haversine_m(latitude, longitude, s["latitude"], s["longitude"])
    )
    return NearestShelter(
        status="available",
        facility_id=closest["facility_id"],
        name=closest["name"],
        latitude=closest["latitude"],
        longitude=closest["longitude"],
        distance_m=round(haversine_m(latitude, longitude, closest["latitude"], closest["longitude"])),
        is_verified=False,
    )
