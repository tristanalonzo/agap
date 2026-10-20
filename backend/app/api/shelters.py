"""GET /api/v1/shelters — every shelter point from static/qc_shelters.geojson, for map markers.

Polygons are already turned into one point each (services/shelters.py). Every shelter is
is_verified false (AGENTS.md safety rule 5). If the file is missing, the list is empty.
"""

from typing import Any

from fastapi import APIRouter

from app.services.shelters import get_shelters

router = APIRouter(prefix="/api/v1", tags=["shelters"])


@router.get("/shelters")
def list_shelters() -> dict[str, Any]:
    features = [
        {
            "type": "Feature",
            "id": shelter["facility_id"],
            "geometry": {"type": "Point", "coordinates": [shelter["longitude"], shelter["latitude"]]},
            "properties": {
                "facility_id": shelter["facility_id"],
                "name": shelter["name"],
                "is_verified": False,
            },
        }
        for shelter in get_shelters()
    ]
    return {"type": "FeatureCollection", "features": features}
