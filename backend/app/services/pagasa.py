"""PAGASA heavy rainfall warning, read from the NCR regional page (settings.PAGASA_URL).

The warning is in the page's "Rainfall Warning" tab: <div id="rainfalls">.
Safety rule 2 (AGENTS.md): if the fetch or parsing fails, alert_level is "unknown", never "none".
"none" is only returned when PAGASA's own text says there is no warning.

Statuses: "fresh" (read just now, or within the cache window), "stale" (fetch failed, showing the
last good result), "unavailable" (fetch failed, nothing cached), "parse_error" (page layout changed).
"""

import re
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from app.config import MANILA_TZ, settings
from app.schemas import RainfallWarning

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)
NO_WARNING_TEXT = "no heavy rainfall warning"
LEVELS = ["red", "orange", "yellow"]  # most severe first
LEVEL_PATTERN = re.compile(r"\b(RED|ORANGE|YELLOW)\s+(?:RAINFALL\s+)?WARNING(?:\s+LEVEL)?\s*:?\s*", re.I)
ISSUED_PATTERN = re.compile(r"Issued at:\s*(\d{1,2}:\d{2}\s*[AP]M),?\s*(\d{1,2}\s+\w+\s+\d{4})", re.I)
METRO_MANILA_PATTERN = re.compile(r"metro manila|\bNCR\b|quezon city", re.I)

# Last good result, so we don't ask PAGASA on every request.
_cache: RainfallWarning | None = None
_cache_time: datetime | None = None


def now_text() -> str:
    return datetime.now(MANILA_TZ).isoformat(timespec="seconds")


def fetch_page() -> str:
    """Download the PAGASA page. Raises httpx.HTTPError on timeout or a bad HTTP status."""
    response = httpx.get(
        settings.PAGASA_URL, timeout=10, headers={"User-Agent": USER_AGENT}, follow_redirects=True
    )
    response.raise_for_status()
    return response.text


def parse_issued_at(text: str) -> str | None:
    """'Issued at: 2:00 PM, 21 October 2026' -> '2026-10-21T14:00:00+08:00'."""
    match = ISSUED_PATTERN.search(text)
    if not match:
        return None
    try:
        issued = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%I:%M %p %d %B %Y")
    except ValueError:
        return None
    return issued.replace(tzinfo=MANILA_TZ).isoformat(timespec="seconds")


def find_level_areas(text: str) -> dict[str, str]:
    """{'orange': 'Metro Manila, Bulacan and Rizal.', ...} from 'ORANGE WARNING LEVEL: ...' parts."""
    matches = list(LEVEL_PATTERN.finditer(text))
    areas = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        level = match.group(1).lower()
        areas.setdefault(level, text[match.end() : end].split(". ")[0].strip())
    return areas


def parse_rainfall(html: str, retrieved_at: str) -> RainfallWarning:
    """Turn the PAGASA page into the contract's rainfall_warning object."""
    tab = BeautifulSoup(html, "html.parser").find(id="rainfalls")
    text = " ".join(tab.get_text(" ").split()) if tab else ""

    result = RainfallWarning(
        status="parse_error",
        alert_level="unknown",
        affected_area=None,
        issued_at=parse_issued_at(text),
        valid_until=None,
        source_url=settings.PAGASA_URL,
        retrieved_at=retrieved_at,
        raw_text=text or None,
    )
    if not text:
        return result

    if NO_WARNING_TEXT in text.lower():
        result.status = "fresh"
        result.alert_level = "none"
        return result

    areas = find_level_areas(text)
    if not areas:
        return result  # a warning we can't read: stays parse_error / unknown

    # Prefer the level that names Metro Manila. Otherwise show the highest level and say
    # Metro Manila is not named, so we never claim QC is affected when the text doesn't say so.
    metro_levels = [level for level in LEVELS if level in areas and METRO_MANILA_PATTERN.search(areas[level])]
    if metro_levels:
        level = metro_levels[0]
        result.affected_area = areas[level]
    else:
        level = next(level for level in LEVELS if level in areas)
        result.affected_area = f"Metro Manila not named. Areas: {areas[level]}"
    result.status = "fresh"
    result.alert_level = level
    return result


def unavailable(retrieved_at: str) -> RainfallWarning:
    return RainfallWarning(
        status="unavailable",
        alert_level="unknown",
        affected_area=None,
        issued_at=None,
        valid_until=None,
        source_url=settings.PAGASA_URL,
        retrieved_at=retrieved_at,
        raw_text=None,
    )


def get_rainfall_warning() -> RainfallWarning:
    """Cached for settings.PAGASA_CACHE_MINUTES. Never raises: failures become a status."""
    global _cache, _cache_time
    now = datetime.now(MANILA_TZ)
    if _cache and _cache_time and now - _cache_time < timedelta(minutes=settings.PAGASA_CACHE_MINUTES):
        return _cache

    try:
        html = fetch_page()
    except httpx.HTTPError:
        if _cache:
            # Keep the alert level but say clearly it is old (retrieved_at is the old time).
            return _cache.model_copy(update={"status": "stale"})
        return unavailable(now_text())

    result = parse_rainfall(html, now_text())
    if result.status == "fresh":
        _cache, _cache_time = result, now
    return result


def clear_cache() -> None:
    """For tests."""
    global _cache, _cache_time
    _cache, _cache_time = None, None
