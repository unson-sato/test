"""
Utility functions for MV Orchestra v3.0
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .atomic_file import atomic_write_json
from .constants import MAX_JSON_FILE_SIZE
from .security import validate_path_within_workspace, validate_session_id


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assumes this file is in core/ directory
    return Path(__file__).parent.parent


def get_session_dir(session_id: str) -> Path:
    """
    Get the session directory for a given session ID (with security validation).

    Args:
        session_id: Session identifier

    Returns:
        Path to session directory
    """
    session_id = validate_session_id(session_id)  # Validate first
    project_root = get_project_root()
    session_dir = project_root / "sessions" / session_id
    # Validate path is within sessions directory
    sessions_root = project_root / "sessions"
    validate_path_within_workspace(session_dir, sessions_root)
    return session_dir


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to directory

    Returns:
        Path to directory
    """
    if isinstance(path, str):
        path = Path(path)

    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(file_path: Path) -> Dict[str, Any]:
    """
    Read JSON data from file with size validation.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    from .security import validate_json_size

    if isinstance(file_path, str):
        file_path = Path(file_path)

    validate_json_size(file_path, MAX_JSON_FILE_SIZE)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write JSON data to file atomically.

    Args:
        file_path: Path to JSON file
        data: Data to write
        indent: JSON indentation (default: 2)
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    atomic_write_json(file_path, data, indent=indent)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()
