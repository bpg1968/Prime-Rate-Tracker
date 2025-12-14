"""Fetch prime rate data from the Bank of Canada Valet API."""

from __future__ import annotations

from typing import Final

from .models import PrimeRate

SERIES_CODE: Final = "V80691311"


def fetch_latest_prime(timeout: float = 20.0) -> PrimeRate:
    """Fetch the latest prime rate observation."""
    raise NotImplementedError("Fetcher implementation pending.")

