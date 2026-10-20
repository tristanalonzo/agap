"""GET /api/v1/shelters — returns the contents of static/qc_shelters.geojson for map markers.

If the file doesn't exist yet (task B3 adds it), returns an empty FeatureCollection.
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["shelters"])

SHELTERS_FILE = Path(__file__).parent.parent / "static" / "qc_shelters.geojson"


@router.get("/shelters")
def get_shelters() -> dict[str, Any]:
    if not SHELTERS_FILE.exists():
        return {"type": "FeatureCollection", "features": []}
    with open(SHELTERS_FILE, encoding="utf-8") as file:
        return json.load(file)
