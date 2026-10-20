"""All app settings, read from environment variables (or a .env file).

Change a value by setting the env var or adding it to backend/.env.
Every setting has a safe default so the app runs with no .env at all.
"""

from datetime import timedelta, timezone

from pydantic_settings import BaseSettings, SettingsConfigDict

# Philippine time (UTC+8). Manila has no daylight saving, so a fixed offset is exact
# and avoids the extra tzdata package that ZoneInfo needs on Windows.
MANILA_TZ = timezone(timedelta(hours=8), "Asia/Manila")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Quezon City bounding box (approximate). Requests outside it get HTTP 422.
    QC_LAT_MIN: float = 14.58
    QC_LAT_MAX: float = 14.77
    QC_LON_MIN: float = 120.98
    QC_LON_MAX: float = 121.14

    # PAGASA NCR regional page that services/pagasa.py scrapes (its "Rainfall Warning" tab).
    # The old /weather/rainfall-warning page returned 404 when checked on 2026-10-20.
    PAGASA_URL: str = "https://bagong.pagasa.dost.gov.ph/regional-forecast/ncrprsd"
    # Ask PAGASA at most once per this many minutes; reuse the last good result in between.
    PAGASA_CACHE_MINUTES: int = 10

    # True = return a fake cyclone result marked as demo. False = run the ONNX model.
    MOCK_INFERENCE: bool = True
    ONNX_MODEL_PATH: str = "app/weights/agap_tc_classifier.onnx"

    # The React dev server. CORS only allows this origin.
    FRONTEND_ORIGIN: str = "http://localhost:5173"


settings = Settings()
