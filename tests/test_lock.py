from pathlib import Path

import pytest

from prime_rate_tracker.errors import AlreadyRunningError
from prime_rate_tracker.lock import process_lock


def test_lock_prevents_concurrent_execution(tmp_path) -> None:
    lock_path = tmp_path / "prime.sqlite3.lock"

    with process_lock(lock_path):
        with pytest.raises(AlreadyRunningError):
            with process_lock(lock_path):
                pass
