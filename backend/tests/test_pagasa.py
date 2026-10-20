from datetime import datetime, timedelta
from pathlib import Path

import httpx
import pytest

from app.config import MANILA_TZ
from app.services import pagasa

FIXTURES = Path(__file__).parent / "fixtures"


def serve(monkeypatch: pytest.MonkeyPatch, fixture_name: str) -> None:
    """Make fetch_page return a saved page instead of calling PAGASA."""
    html = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    monkeypatch.setattr(pagasa, "fetch_page", lambda: html)


def test_no_warning_page_says_none(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, "pagasa_no_warning.html")
    result = pagasa.get_rainfall_warning()
    assert result.status == "fresh"
    assert result.alert_level == "none"
    assert "no Heavy Rainfall Warning" in result.raw_text
    assert result.retrieved_at is not None


def test_active_warning_picks_the_metro_manila_level(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, "pagasa_active_warning.html")
    result = pagasa.get_rainfall_warning()
    assert result.status == "fresh"
    assert result.alert_level == "orange"
    assert result.affected_area.startswith("Metro Manila")
    assert result.issued_at == "2026-10-21T14:00:00+08:00"
    assert "Heavy Rainfall Warning No. 3" in result.raw_text


def test_warning_without_metro_manila_says_so() -> None:
    html = '<div id="rainfalls">YELLOW WARNING LEVEL: Cavite and Laguna.</div>'
    result = pagasa.parse_rainfall(html, "2026-10-21T14:00:00+08:00")
    assert result.alert_level == "yellow"
    assert result.affected_area.startswith("Metro Manila not named")


def test_malformed_page_is_parse_error_and_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, "pagasa_malformed.html")
    result = pagasa.get_rainfall_warning()
    assert result.status == "parse_error"
    assert result.alert_level == "unknown"


def test_timeout_is_unavailable_and_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    def time_out() -> str:
        raise httpx.ReadTimeout("PAGASA took too long")

    monkeypatch.setattr(pagasa, "fetch_page", time_out)
    result = pagasa.get_rainfall_warning()
    assert result.status == "unavailable"
    assert result.alert_level == "unknown"


def test_timeout_after_a_good_result_is_stale(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, "pagasa_active_warning.html")
    pagasa.get_rainfall_warning()
    pagasa._cache_time = datetime.now(MANILA_TZ) - timedelta(hours=1)  # cache window over

    def time_out() -> str:
        raise httpx.ReadTimeout("PAGASA took too long")

    monkeypatch.setattr(pagasa, "fetch_page", time_out)
    result = pagasa.get_rainfall_warning()
    assert result.status == "stale"
    assert result.alert_level == "orange"
