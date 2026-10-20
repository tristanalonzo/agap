"""Shared test setup: no test ever calls the real PAGASA website."""

import httpx
import pytest

from app.services import pagasa


def offline_fetch() -> str:
    raise httpx.ConnectError("Tests never use the network")


@pytest.fixture(autouse=True)
def no_pagasa_network(monkeypatch: pytest.MonkeyPatch) -> None:
    # Tests that need a page replace fetch_page again with their own fixture.
    monkeypatch.setattr(pagasa, "fetch_page", offline_fetch)
    pagasa.clear_cache()
