"""Process-level file lock helper."""

from __future__ import annotations

import fcntl
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .errors import AlreadyRunningError, FilesystemError


@contextmanager
def process_lock(lock_path: Path) -> Iterator[bool]:
    try:
        lock_file = Path(lock_path)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        # Keep the file handle open for the lifetime of the lock.
        with lock_file.open("a+") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise AlreadyRunningError("Another instance is already running") from exc
            try:
                yield True
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
    except AlreadyRunningError:
        raise
    except OSError as exc:
        raise FilesystemError(f"Lock file error: {exc}") from exc
