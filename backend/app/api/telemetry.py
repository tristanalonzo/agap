"""POST /api/v1/telemetry/assess — returns the object in docs/contract/assess.sample.json.

Rejects coordinates outside the QC box (see config.py) with HTTP 422.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.config import MANILA_TZ, settings
from app.schemas import (
    AssessRequest,
    AssessResponse,
    CycloneAssessment,
    DataStatus,
    FloodScenario,
    Location,
    NearestShelter,
    RainfallWarning,
    RunContext,
)
from app.services.inference import get_cyclone_assessment
from app.services.pagasa import get_rainfall_warning
from app.services.shelters import nearest_shelter

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


# Component statuses that count as "we have no usable data for this".
NOT_AVAILABLE = {"unavailable", "parse_error", "no_shelter_data"}


def build_data_status(
    cyclone: CycloneAssessment, rainfall: RainfallWarning, shelter: NearestShelter
) -> DataStatus:
    """Summarise which parts of the response are stale or missing.

    The cyclone counts too: with MOCK_INFERENCE off and no model it is "unavailable", and the
    summary must not call the response "complete" then. Its "demo" status is not counted as
    missing -- the card flags it as DEMO itself.
    """
    statuses = {
        "cyclone_assessment": cyclone.status,
        "rainfall_warning": rainfall.status,
        "nearest_shelter": shelter.status,
    }
    unavailable = [name for name, status in statuses.items() if status in NOT_AVAILABLE]
    stale = [name for name, status in statuses.items() if status == "stale"]
    return DataStatus(
        overall="partial" if unavailable or stale else "complete",
        stale_components=stale,
        unavailable_components=unavailable,
    )


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

    cyclone = get_cyclone_assessment()
    rainfall_warning = get_rainfall_warning()
    flood_scenario = FloodScenario(
        source="Project NOAH hazard maps (BetterGovPH dataset)",
        selected_return_period_years=request.flood_return_period_years,
        hazard_level=None,
        is_live_forecast=False,
        lookup_status="not_implemented",
    )
    shelter = nearest_shelter(request.latitude, request.longitude)

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
        cyclone_assessment=cyclone,
        rainfall_warning=rainfall_warning,
        flood_scenario=flood_scenario,
        nearest_shelter=shelter,
        data_status=build_data_status(cyclone, rainfall_warning, shelter),
    )
