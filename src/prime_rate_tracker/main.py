"""Main CLI entrypoint and orchestration."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from .db import PrimeRateDatabase
from .errors import (
    AlreadyRunningError,
    DatabaseError,
    FilesystemError,
    NetworkError,
    ParseError,
    PrimeRateError,
)
from .fetcher import fetch_latest_prime
from .lock import process_lock

logger = logging.getLogger("prime_rate_tracker")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the prime rate tracker CLI."""
    args = _parse_args(argv)
    _configure_logging(verbose=args.verbose)
    db_path = Path(args.db)

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = Path(str(db_path) + ".lock")
    except OSError as exc:
        logger.error("Filesystem error: %s", exc)
        return FilesystemError.exit_code

    try:
        with process_lock(lock_path):
            return _run_once(
                db_path=db_path,
                timeout=args.timeout,
                dry_run=args.dry_run,
            )
    except AlreadyRunningError:
        if args.verbose:
            logger.info("Another instance is already running; exiting")
        return AlreadyRunningError.exit_code
    except PrimeRateError as exc:
        logger.error("%s", exc)
        return exc.exit_code
    except Exception:
        logger.exception("Unexpected error while running prime rate tracker")
        return 1


def _run_once(*, db_path: Path, timeout: float, dry_run: bool) -> int:
    prime = fetch_latest_prime(timeout=timeout)
    database = PrimeRateDatabase(db_path)
    database.ensure_schema()
    database.apply_update(prime, dry_run=dry_run)
    return 0


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track the Canadian prime rate.")
    parser.add_argument(
        "--db",
        default="data/prime_rates.sqlite3",
        help="Path to SQLite database file (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Network timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch data but do not write to the database",
    )
    return parser.parse_args(argv)


def _configure_logging(*, verbose: bool) -> None:
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(message)s")

