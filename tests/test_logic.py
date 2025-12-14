import sqlite3

from prime_rate_tracker.db import PrimeRateDatabase
from prime_rate_tracker.models import PrimeRate


def test_rate_change_updates_current_and_history(tmp_path) -> None:
    db_path = tmp_path / "prime.sqlite3"
    db = PrimeRateDatabase(db_path)
    db.ensure_schema()

    first = PrimeRate(date="2024-01-01", rate=7.2)
    db.apply_update(first)

    updated = PrimeRate(date="2024-03-01", rate=7.45)
    db.apply_update(updated)

    with sqlite3.connect(db_path) as conn:
        current = conn.execute(
            "SELECT as_of_date, rate FROM current_prime WHERE id = 1"
        ).fetchone()
        history_rows = conn.execute(
            "SELECT effective_date, rate FROM prime_history ORDER BY id"
        ).fetchall()

    assert current == ("2024-03-01", 7.45)
    assert history_rows == [("2024-01-01", 7.2), ("2024-03-01", 7.45)]


def test_date_only_change_updates_current_only(tmp_path) -> None:
    db_path = tmp_path / "prime.sqlite3"
    db = PrimeRateDatabase(db_path)
    db.ensure_schema()

    first = PrimeRate(date="2024-01-01", rate=7.2)
    db.apply_update(first)

    date_only = PrimeRate(date="2024-02-01", rate=7.2)
    db.apply_update(date_only)

    with sqlite3.connect(db_path) as conn:
        current = conn.execute(
            "SELECT as_of_date, rate FROM current_prime WHERE id = 1"
        ).fetchone()
        history_rows = conn.execute("SELECT COUNT(*) FROM prime_history").fetchone()[0]

    assert current == ("2024-02-01", 7.2)
    assert history_rows == 1

