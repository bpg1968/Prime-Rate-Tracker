"""Custom exceptions with associated exit codes."""

from __future__ import annotations


class PrimeRateError(Exception):
    """Base exception for prime rate tracker errors."""

    exit_code: int = 1


class AlreadyRunningError(PrimeRateError):
    """Raised when a process lock is already held."""

    exit_code = 2


class NetworkError(PrimeRateError):
    """Raised for network or HTTP issues."""

    exit_code = 10


class ParseError(PrimeRateError):
    """Raised when the API payload is invalid."""

    exit_code = 11


class DatabaseError(PrimeRateError):
    """Raised for SQLite-related failures."""

    exit_code = 20


class FilesystemError(PrimeRateError):
    """Raised when filesystem operations fail."""

    exit_code = 21

