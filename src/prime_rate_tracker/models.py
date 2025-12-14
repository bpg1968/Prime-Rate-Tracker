"""Dataclasses used across the prime rate tracker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PrimeRate:
    """Prime rate observation with effective date."""

    date: str
    rate: float

