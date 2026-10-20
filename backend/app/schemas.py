"""Pydantic models for every request and response.

The assess response must match docs/contract/assess.sample.json exactly.
To change the shape, change that file first (AGENTS.md section 5).
"""

from typing import Literal

from pydantic import BaseModel


class AssessRequest(BaseModel):
    latitude: float
    longitude: float
    # The user picks the flood scenario. It is never chosen from the cyclone category.
    flood_return_period_years: Literal[5, 25, 100] = 25


class RunContext(BaseModel):
    mode: str
    storm_id: str | None
    observation_id: str | None


class Location(BaseModel):
    latitude: float
    longitude: float
    jurisdiction: str
    in_bounds: bool


class CycloneAssessment(BaseModel):
    status: str
    is_demo: bool
    category_code: str
    category_name: str
    sustained_wind_kph: float | None
    confidence: float | None
    confidence_is_calibrated: bool
    model_version: str | None
    observed_at: str | None
    inferred_at: str
    warnings: list[str]


class RainfallWarning(BaseModel):
    status: str
    alert_level: str
    affected_area: str | None
    issued_at: str | None
    valid_until: str | None
    source_url: str
    retrieved_at: str | None
    raw_text: str | None


class FloodScenario(BaseModel):
    source: str
    selected_return_period_years: Literal[5, 25, 100]
    hazard_level: str | None
    is_live_forecast: bool
    lookup_status: str


class NearestShelter(BaseModel):
    # When status is "unavailable", every other field is null.
    status: str
    facility_id: str | None
    name: str | None
    latitude: float | None
    longitude: float | None
    distance_m: int | None
    is_verified: bool | None


class DataStatus(BaseModel):
    overall: str
    stale_components: list[str]
    unavailable_components: list[str]


class AssessResponse(BaseModel):
    assessment_id: str
    generated_at: str
    run_context: RunContext
    location: Location
    cyclone_assessment: CycloneAssessment
    rainfall_warning: RainfallWarning
    flood_scenario: FloodScenario
    nearest_shelter: NearestShelter
    data_status: DataStatus
