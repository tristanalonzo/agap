from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.shelters import haversine_m, load_shelters, nearest_shelter

client = TestClient(app)


def fake_shelter(name: str, latitude: float, longitude: float) -> dict:
    return {
        "facility_id": f"test-{name}",
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "tags": {},
    }


def test_haversine_paris_to_london_is_about_344_km() -> None:
    distance = haversine_m(48.8566, 2.3522, 51.5074, -0.1278)
    assert abs(distance - 343_560) < 343_560 * 0.01


def test_nearest_of_three_fake_shelters() -> None:
    shelters = [
        fake_shelter("far", 14.70, 121.10),
        fake_shelter("near", 14.651, 121.050),
        fake_shelter("middle", 14.66, 121.06),
    ]
    result = nearest_shelter(14.65, 121.05, shelters)
    assert result.status == "available"
    assert result.name == "near"
    assert result.is_verified is False
    assert 100 < result.distance_m < 120  # 0.001 degree of latitude is about 111 m


def test_no_shelters_gives_no_shelter_data() -> None:
    result = nearest_shelter(14.65, 121.05, [])
    assert result.status == "no_shelter_data"
    assert result.name is None


def test_missing_file_loads_nothing() -> None:
    assert load_shelters(Path("does-not-exist.geojson")) == []


def test_assess_returns_a_real_unverified_shelter() -> None:
    body = client.post(
        "/api/v1/telemetry/assess", json={"latitude": 14.6516, "longitude": 121.0493}
    ).json()
    shelter = body["nearest_shelter"]
    assert shelter["status"] == "available"
    assert shelter["name"]
    assert shelter["is_verified"] is False
    assert "nearest_shelter" not in body["data_status"]["unavailable_components"]


def test_shelters_endpoint_marks_every_point_unverified() -> None:
    features = client.get("/api/v1/shelters").json()["features"]
    assert len(features) > 0
    assert all(f["geometry"]["type"] == "Point" for f in features)
    assert all(f["properties"]["is_verified"] is False for f in features)
