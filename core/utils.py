"""
Utility functions for MV Orchestra v3.0
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assumes this file is in core/ directory
    return Path(__file__).parent.parent


def get_session_dir(session_id: str) -> Path:
    """
    Get the session directory for a given session ID.

    Args:
        session_id: Session identifier

    Returns:
        Path to session directory
    """
    project_root = get_project_root()
    session_dir = project_root / "sessions" / session_id
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
    Read JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write JSON file.

    Args:
        file_path: Path to JSON file
        data: Data to write
        indent: JSON indentation (default: 2)
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()
