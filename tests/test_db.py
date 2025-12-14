import sqlite3

from prime_rate_tracker.db import PrimeRateDatabase
from prime_rate_tracker.models import PrimeRate


def test_schema_creation(tmp_path) -> None:
    db_path = tmp_path / "prime.sqlite3"
    db = PrimeRateDatabase(db_path)

    db.ensure_schema()

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert {"current_prime", "prime_history"} <= tables


def test_first_run_inserts_current_and_history(tmp_path) -> None:
    db_path = tmp_path / "prime.sqlite3"
    db = PrimeRateDatabase(db_path)
    db.ensure_schema()

    prime = PrimeRate(date="2024-01-01", rate=7.2)
    db.apply_update(prime)

    with sqlite3.connect(db_path) as conn:
        current = conn.execute(
            "SELECT as_of_date, rate FROM current_prime WHERE id = 1"
        ).fetchone()
        history_count = conn.execute("SELECT COUNT(*) FROM prime_history").fetchone()[0]

    assert current == ("2024-01-01", 7.2)
    assert history_count == 1


def test_repeat_run_does_not_duplicate_history(tmp_path) -> None:
    db_path = tmp_path / "prime.sqlite3"
    db = PrimeRateDatabase(db_path)
    db.ensure_schema()

    prime = PrimeRate(date="2024-01-01", rate=7.2)
    db.apply_update(prime)
    db.apply_update(prime)

    with sqlite3.connect(db_path) as conn:
        history_count = conn.execute("SELECT COUNT(*) FROM prime_history").fetchone()[0]

    assert history_count == 1
