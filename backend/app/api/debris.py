"""GET /api/v1/debris-matrix — returns the contents of static/debris_matrix.json.

Provides the DOST-PAGASA reference wind-hazard matrix (TD, TS, STS, TY, STY) with
precautionary structural vulnerabilities and protective actions.
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["debris"])

DEBRIS_MATRIX_FILE = Path(__file__).resolve().parent.parent / "static" / "debris_matrix.json"


@router.get("/debris-matrix")
def get_debris_matrix() -> dict[str, Any]:
    with open(DEBRIS_MATRIX_FILE, encoding="utf-8") as file:
        return json.load(file)
