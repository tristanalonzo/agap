"""GET /api/v1/hotlines — returns the contents of static/qc_hotlines.json.

The file is returned as-is: some entries have extra fields (source_urls,
alternate_extensions) that a strict model would drop.
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["hotlines"])

HOTLINES_FILE = Path(__file__).parent.parent / "static" / "qc_hotlines.json"


@router.get("/hotlines")
def get_hotlines() -> dict[str, Any]:
    with open(HOTLINES_FILE, encoding="utf-8") as file:
        return json.load(file)
