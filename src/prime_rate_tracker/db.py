"""SQLite persistence for prime rate tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import PrimeRate


class PrimeRateDatabase:
    """Manage the prime rate SQLite schema and updates."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def ensure_schema(self) -> None:
        """Create tables if they do not yet exist."""
        raise NotImplementedError("Database schema creation pending.")

    def get_current(self) -> Optional[PrimeRate]:
        """Return the current prime rate row, if any."""
        raise NotImplementedError("Current prime retrieval pending.")

    def upsert_prime(self, prime: PrimeRate, *, effective_date: str) -> None:
        """Insert or update rows based on the fetched prime rate."""
        raise NotImplementedError("Prime update logic pending.")

