"""Dataclasses used across the prime rate tracker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PrimeRate:
    """Prime rate observation with effective date."""

    date: str
    rate: float


@dataclass(slots=True)
class CurrentPrime:
    """Persisted current prime record."""

    as_of_date: str
    rate: float
    updated_at: str


@dataclass(slots=True)
class UpdateResult:
    """Outcome flags from applying a fetched prime rate."""

    current_created: bool = False
    current_updated: bool = False
    history_inserted: bool = False
