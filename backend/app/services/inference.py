"""Cyclone category inference.

Mock for now: always status "demo", is_demo true, with a warning text (AGENTS.md safety rule 1).
Phase 3: load the ONNX model from settings.ONNX_MODEL_PATH (Luke + Kurt).
Do not invent model input names, normalization or class order; those come from Team A.
"""

from datetime import datetime

from app.config import MANILA_TZ
from app.schemas import CycloneAssessment


def get_cyclone_assessment() -> CycloneAssessment:
    """Return a fake Typhoon result, clearly marked as demo data."""
    return CycloneAssessment(
        status="demo",
        is_demo=True,
        category_code="TY",
        category_name="Typhoon",
        sustained_wind_kph=140.0,
        confidence=None,
        confidence_is_calibrated=False,
        model_version=None,
        observed_at=None,
        inferred_at=datetime.now(MANILA_TZ).isoformat(timespec="seconds"),
        warnings=["Mock result for development. Not a real prediction."],
    )
