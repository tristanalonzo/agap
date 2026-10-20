"""POST /api/v1/telemetry/assess — returns the object in docs/contract/assess.sample.json.

Rejects coordinates outside the QC box (see config.py) with HTTP 422.
Rainfall warning and nearest shelter are "unavailable" until their services are built.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.config import MANILA_TZ, settings
from app.schemas import (
    AssessRequest,
    AssessResponse,
    DataStatus,
    FloodScenario,
    Location,
    NearestShelter,
    RainfallWarning,
    RunContext,
)
from app.services.inference import get_cyclone_assessment

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


def is_inside_qc(latitude: float, longitude: float) -> bool:
    return (
        settings.QC_LAT_MIN <= latitude <= settings.QC_LAT_MAX
        and settings.QC_LON_MIN <= longitude <= settings.QC_LON_MAX
    )


@router.post("/assess")
def assess(request: AssessRequest) -> AssessResponse:
    if not is_inside_qc(request.latitude, request.longitude):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Location ({request.latitude}, {request.longitude}) is outside Quezon City. "
                f"Latitude must be {settings.QC_LAT_MIN}–{settings.QC_LAT_MAX} and "
                f"longitude {settings.QC_LON_MIN}–{settings.QC_LON_MAX}."
            ),
        )

    # Not built yet, so honestly "unavailable" / "unknown" (AGENTS.md safety rule 2).
    rainfall_warning = RainfallWarning(
        status="unavailable",
        alert_level="unknown",
        affected_area=None,
        issued_at=None,
        valid_until=None,
        source_url=settings.PAGASA_URL,
        retrieved_at=None,
        raw_text=None,
    )
    flood_scenario = FloodScenario(
        source="Project NOAH hazard maps (BetterGovPH dataset)",
        selected_return_period_years=request.flood_return_period_years,
        hazard_level=None,
        is_live_forecast=False,
        lookup_status="not_implemented",
    )
    nearest_shelter = NearestShelter(
        status="unavailable",
        facility_id=None,
        name=None,
        latitude=None,
        longitude=None,
        distance_m=None,
        is_verified=None,
    )

    return AssessResponse(
        assessment_id=str(uuid.uuid4()),
        generated_at=datetime.now(MANILA_TZ).isoformat(timespec="seconds"),
        run_context=RunContext(mode="demo", storm_id=None, observation_id=None),
        location=Location(
            latitude=request.latitude,
            longitude=request.longitude,
            jurisdiction="Quezon City",
            in_bounds=True,
        ),
        cyclone_assessment=get_cyclone_assessment(),
        rainfall_warning=rainfall_warning,
        flood_scenario=flood_scenario,
        nearest_shelter=nearest_shelter,
        data_status=DataStatus(
            overall="partial",
            stale_components=[],
            unavailable_components=["rainfall_warning", "nearest_shelter"],
        ),
    )
