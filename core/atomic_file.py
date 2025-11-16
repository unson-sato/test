"""
Atomic file operations for MV Orchestra v3.0

Provides safe, atomic file writing to prevent data corruption from crashes
or concurrent access.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


def atomic_write_json(path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Atomically write JSON data to a file.

    Uses a temporary file in the same directory, then atomically replaces
    the target file. This prevents corruption if the process crashes during
    writing.

    Args:
        path: The target file path
        data: The data to write
        indent: JSON indentation level

    Raises:
        OSError: If writing fails
        json.JSONEncodeError: If data cannot be serialized to JSON
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in same directory as target
    # (must be same filesystem for atomic rename)
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")

    try:
        # Write to temporary file
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            # Force write to disk
            os.fsync(f.fileno())

        # Atomically replace target file
        # os.replace() is atomic on all platforms (Python 3.3+)
        os.replace(temp_path, path)

    except Exception:
        # Clean up temporary file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def atomic_write_text(path: Path, content: str) -> None:
    """
    Atomically write text content to a file.

    Args:
        path: The target file path
        content: The text content to write

    Raises:
        OSError: If writing fails
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in same directory
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")

    try:
        # Write to temporary file
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Atomically replace target file
        os.replace(temp_path, path)

    except Exception:
        # Clean up temporary file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def atomic_write_bytes(path: Path, content: bytes) -> None:
    """
    Atomically write binary content to a file.

    Args:
        path: The target file path
        content: The binary content to write

    Raises:
        OSError: If writing fails
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in same directory
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")

    try:
        # Write to temporary file
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Atomically replace target file
        os.replace(temp_path, path)

    except Exception:
        # Clean up temporary file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise
