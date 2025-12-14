"""Fetch prime rate data from the Bank of Canada Valet API."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Final

from .models import PrimeRate
from .errors import NetworkError, ParseError

SERIES_CODE: Final = "V80691311"
OBSERVATION_URL: Final = (
    f"https://www.bankofcanada.ca/valet/observations/{SERIES_CODE}/json?recent=1"
)

logger = logging.getLogger(__name__)


def fetch_latest_prime(timeout: float = 20.0) -> PrimeRate:
    """Fetch the latest prime rate observation."""
    try:
        request = urllib.request.Request(
            OBSERVATION_URL, headers={"User-Agent": "prime-rate-tracker/0.1"}
        )
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            if resp.status != 200:
                raise NetworkError(f"HTTP {resp.status} from Bank of Canada Valet API")
            try:
                payload = json.loads(resp.read())
            except json.JSONDecodeError as exc:
                raise ParseError("Response was not valid JSON") from exc
    except urllib.error.URLError as exc:
        raise NetworkError(f"Network error: {exc}") from exc

    observations = payload.get("observations")
    if not observations:
        raise ParseError("No observations found in response")

    latest = observations[-1]
    date = latest.get("d")
    if not isinstance(date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ParseError("Invalid or missing observation date")

    series_entry = latest.get(SERIES_CODE)
    if not isinstance(series_entry, dict) or "v" not in series_entry:
        raise ParseError("Prime rate series missing from observation")

    try:
        rate = float(series_entry["v"])
    except (TypeError, ValueError) as exc:
        raise ParseError("Prime rate value was not numeric") from exc

    logger.debug("Fetched prime rate %s on %s", rate, date)
    return PrimeRate(date=date, rate=rate)

