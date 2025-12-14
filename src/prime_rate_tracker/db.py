"""SQLite persistence for prime rate tracking."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .errors import DatabaseError
from .models import CurrentPrime, PrimeRate, UpdateResult


class PrimeRateDatabase:
    """Manage the prime rate SQLite schema and updates."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def ensure_schema(self) -> None:
        """Create tables if they do not yet exist."""
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS current_prime (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        as_of_date TEXT NOT NULL,
                        rate REAL NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prime_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        effective_date TEXT NOT NULL UNIQUE,
                        rate REAL NOT NULL,
                        recorded_at TEXT NOT NULL
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to ensure schema: {exc}") from exc

    def get_current(self) -> Optional[CurrentPrime]:
        """Return the current prime rate row, if any."""
        try:
            with self._connect() as conn:
                row = self._fetch_current(conn)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to read current prime: {exc}") from exc

        if row is None:
            return None
        return CurrentPrime(as_of_date=row[0], rate=float(row[1]), updated_at=row[2])

    def apply_update(self, prime: PrimeRate, *, dry_run: bool = False) -> UpdateResult:
        """Apply fetched prime data to the database following update rules."""
        now = self._now()
        result = UpdateResult()

        try:
            with self._connect() as conn:
                current_row = self._fetch_current(conn)
                if current_row is None:
                    result.current_created = True
                    result.history_inserted = True
                    if not dry_run:
                        with conn:
                            conn.execute(
                                """
                                INSERT INTO current_prime (id, as_of_date, rate, updated_at)
                                VALUES (1, ?, ?, ?)
                                """,
                                (prime.date, prime.rate, now),
                            )
                            conn.execute(
                                """
                                INSERT INTO prime_history (effective_date, rate, recorded_at)
                                VALUES (?, ?, ?)
                                """,
                                (prime.date, prime.rate, now),
                            )
                    return result

                current = CurrentPrime(
                    as_of_date=current_row[0], rate=float(current_row[1]), updated_at=current_row[2]
                )

                if prime.rate != current.rate:
                    result.current_updated = True
                    result.history_inserted = True
                    if not dry_run:
                        with conn:
                            conn.execute(
                                """
                                UPDATE current_prime
                                SET as_of_date = ?, rate = ?, updated_at = ?
                                WHERE id = 1
                                """,
                                (prime.date, prime.rate, now),
                            )
                            conn.execute(
                                """
                                INSERT INTO prime_history (effective_date, rate, recorded_at)
                                VALUES (?, ?, ?)
                                """,
                                (prime.date, prime.rate, now),
                            )
                    return result

                if prime.date != current.as_of_date:
                    result.current_updated = True
                    if not dry_run:
                        with conn:
                            conn.execute(
                                """
                                UPDATE current_prime
                                SET as_of_date = ?, updated_at = ?
                                WHERE id = 1
                                """,
                                (prime.date, now),
                            )
                    return result

                result.current_updated = True
                if not dry_run:
                    with conn:
                        conn.execute(
                            """
                            UPDATE current_prime
                            SET updated_at = ?
                            WHERE id = 1
                            """,
                            (now,),
                        )
                return result
        except sqlite3.IntegrityError as exc:
            raise DatabaseError(f"Database constraint violated: {exc}") from exc
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to apply update: {exc}") from exc

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    @staticmethod
    def _fetch_current(conn: sqlite3.Connection):
        return conn.execute(
            "SELECT as_of_date, rate, updated_at FROM current_prime WHERE id = 1"
        ).fetchone()

    @staticmethod
    def _now() -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
