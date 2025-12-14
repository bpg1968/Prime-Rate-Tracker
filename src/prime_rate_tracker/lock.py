"""Process-level file lock helper."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def process_lock(lock_path: Path) -> Iterator[bool]:
    """Placeholder context manager for a file-based lock."""
    raise NotImplementedError("Locking implementation pending.")

