"""
Utility functions for MV Orchestra v2.8

This module provides common utilities used throughout the project including:
- File I/O operations (JSON read/write)
- Directory management
- Timestamp formatting
- Session ID generation
- Path validation
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write data to a JSON file with pretty formatting.

    Args:
        file_path: Path where the JSON file will be written
        data: Dictionary to serialize to JSON
        indent: Number of spaces for indentation (default: 2)

    Raises:
        OSError: If the file cannot be written
    """
    file_path = Path(file_path)

    # Ensure parent directory exists
    ensure_dir(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def ensure_dir(dir_path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        dir_path: Path to the directory

    Returns:
        Path object for the directory

    Raises:
        OSError: If the directory cannot be created
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.

    Args:
        format_str: strftime format string (default: "YYYY-MM-DD HH:MM:SS")

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO 8601 format.

    Returns:
        ISO formatted timestamp (e.g., "2025-11-14T15:30:45.123456")
    """
    return datetime.now().isoformat()


def generate_session_id(prefix: str = "session") -> str:
    """
    Generate a unique session ID.

    Args:
        prefix: Prefix for the session ID (default: "session")

    Returns:
        Unique session ID in format: prefix_YYYYMMDD_HHMMSS_uuid
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{short_uuid}"


def validate_path(path: str, must_exist: bool = False,
                 must_be_file: bool = False,
                 must_be_dir: bool = False) -> bool:
    """
    Validate a file system path.

    Args:
        path: Path to validate
        must_exist: If True, path must exist (default: False)
        must_be_file: If True, path must be a file (default: False)
        must_be_dir: If True, path must be a directory (default: False)

    Returns:
        True if validation passes, False otherwise

    Note:
        must_exist must be True if must_be_file or must_be_dir is True
    """
    path_obj = Path(path)

    if must_exist and not path_obj.exists():
        return False

    if must_be_file:
        if not path_obj.exists() or not path_obj.is_file():
            return False

    if must_be_dir:
        if not path_obj.exists() or not path_obj.is_dir():
            return False

    return True


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path object pointing to /home/user/test
    """
    return Path("/home/user/test")


def get_session_dir(session_id: str) -> Path:
    """
    Get the directory path for a specific session.

    Args:
        session_id: The session identifier

    Returns:
        Path object for the session directory
    """
    return get_project_root() / "shared-workspace" / "sessions" / session_id


def get_evaluations_dir(session_id: str) -> Path:
    """
    Get the evaluations directory path for a specific session.

    Args:
        session_id: The session identifier

    Returns:
        Path object for the evaluations directory
    """
    return get_session_dir(session_id) / "evaluations"


def safe_filename(filename: str) -> str:
    """
    Convert a string to a safe filename by removing/replacing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename safe for file system use
    """
    # Remove or replace characters that are unsafe for filenames
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename

    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')

    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip('. ')

    # Ensure filename is not empty
    if not safe_name:
        safe_name = "unnamed"

    return safe_name
