"""PAGASA rainfall-warning scraper (settings.PAGASA_URL).

On fetch or parse failure return status "unavailable" / "parse_error" and alert_level "unknown",
never "no warning" (AGENTS.md safety rule 2). Use httpx with a 10 s timeout.
Owner: Marcus. Not built yet.
"""
