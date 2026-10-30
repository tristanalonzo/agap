import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import inference

client = TestClient(app)

CONTRACT_FILE = Path(__file__).parents[2] / "docs" / "contract" / "assess.sample.json"
INSIDE_QC = {"latitude": 14.65, "longitude": 121.05}


def same_keys(actual: dict, expected: dict) -> bool:
    """True if both dicts have the same keys, checked at every nesting level."""
    if actual.keys() != expected.keys():
        return False
    return all(
        same_keys(actual[key], expected[key])
        for key in expected
        if isinstance(expected[key], dict)
    )


def test_assess_returns_demo_result_shaped_like_contract() -> None:
    response = client.post("/api/v1/telemetry/assess", json=INSIDE_QC)
    assert response.status_code == 200
    body = response.json()

    contract = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
    assert same_keys(body, contract)

    cyclone = body["cyclone_assessment"]
    assert cyclone["status"] == "demo"
    assert cyclone["is_demo"] is True
    assert cyclone["warnings"]
    assert body["rainfall_warning"]["alert_level"] == "unknown"
    assert body["flood_scenario"]["selected_return_period_years"] == 25
    assert body["generated_at"].endswith("+08:00")


def test_assess_gives_a_new_id_each_call() -> None:
    first = client.post("/api/v1/telemetry/assess", json=INSIDE_QC).json()
    second = client.post("/api/v1/telemetry/assess", json=INSIDE_QC).json()
    assert first["assessment_id"] != second["assessment_id"]


def test_assess_outside_qc_returns_422() -> None:
    response = client.post(
        "/api/v1/telemetry/assess", json={"latitude": 10.31, "longitude": 123.89}
    )
    assert response.status_code == 422
    assert "outside Quezon City" in response.json()["detail"]


def test_assess_invalid_return_period_returns_422() -> None:
    response = client.post(
        "/api/v1/telemetry/assess", json={**INSIDE_QC, "flood_return_period_years": 10}
    )
    assert response.status_code == 422


def test_hotlines_returns_the_list() -> None:
    response = client.get("/api/v1/hotlines")
    assert response.status_code == 200
    hotlines = response.json()["hotlines"]
    assert len(hotlines) > 0
    assert all("dial_string" in hotline for hotline in hotlines)


def test_shelters_returns_a_feature_collection() -> None:
    response = client.get("/api/v1/shelters")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert isinstance(body["features"], list)


def test_data_status_lists_the_cyclone_when_it_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # MOCK_INFERENCE off with no model: the cyclone has no estimate, so the summary must not
    # call the response complete.
    monkeypatch.setattr(settings, "MOCK_INFERENCE", False)
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", Path("does/not/exist.json"))
    inference.clear_cache()

    status = client.post("/api/v1/telemetry/assess", json=INSIDE_QC).json()["data_status"]
    assert "cyclone_assessment" in status["unavailable_components"]
    assert status["overall"] == "partial"


def test_data_status_does_not_count_the_demo_cyclone_as_missing() -> None:
    # The DEMO card flags itself; listing it as missing would change today's summary.
    status = client.post("/api/v1/telemetry/assess", json=INSIDE_QC).json()["data_status"]
    assert "cyclone_assessment" not in status["unavailable_components"]


def test_debris_matrix_returns_all_five_categories() -> None:
    response = client.get("/api/v1/debris-matrix")
    assert response.status_code == 200
    body = response.json()
    assert body.get("classification_source_url")
    matrix = body.get("wind_hazard_matrix", [])
    assert [item["code"] for item in matrix] == ["TD", "TS", "STS", "TY", "STY"]
    for item in matrix:
        vulnerabilities = item.get("structural_vulnerabilities", [])
        assert len(vulnerabilities) > 0
        for vuln in vulnerabilities:
            assert vuln.get("element")
            assert vuln.get("risk")
            assert vuln.get("action")
