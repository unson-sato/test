"""
Security utilities for MV Orchestra v3.0

Provides functions for secure file system operations, input validation,
and prevention of common vulnerabilities.
"""

import re
from pathlib import Path

from .constants import (
    ALLOWED_EXTENSIONS,
    FORBIDDEN_PATH_CHARS,
    FORBIDDEN_PATH_SEQUENCES,
    MAX_SESSION_ID_LENGTH,
)


class SecurityError(Exception):
    """Raised when a security violation is detected."""

    pass


def validate_session_id(session_id: str) -> str:
    """
    Validate and sanitize a session ID to prevent path traversal attacks.

    Args:
        session_id: The session ID to validate

    Returns:
        The validated session ID

    Raises:
        SecurityError: If the session ID is invalid or potentially malicious
    """
    if not session_id:
        raise SecurityError("Session ID cannot be empty")

    if len(session_id) > MAX_SESSION_ID_LENGTH:
        raise SecurityError(f"Session ID too long (max {MAX_SESSION_ID_LENGTH} chars)")

    # Check for forbidden sequences
    for seq in FORBIDDEN_PATH_SEQUENCES:
        if seq in session_id:
            raise SecurityError(f"Session ID contains forbidden sequence: {seq}")

    # Check for forbidden characters
    for char in FORBIDDEN_PATH_CHARS:
        if char in session_id:
            raise SecurityError(f"Session ID contains forbidden character: {char}")

    # Must be alphanumeric with hyphens and underscores only
    if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
        raise SecurityError("Session ID must be alphanumeric with hyphens/underscores only")

    return session_id


def validate_path_within_workspace(path: Path, workspace: Path) -> Path:
    """
    Validate that a path is within the workspace directory (prevent path traversal).

    Uses the resolve() method to get absolute paths and checks that the resolved
    path starts with the workspace path.

    Args:
        path: The path to validate
        workspace: The workspace root directory

    Returns:
        The resolved, validated path

    Raises:
        SecurityError: If the path is outside the workspace
    """
    # Resolve both paths to absolute paths
    workspace_resolved = workspace.resolve()
    path_resolved = path.resolve()

    # Check if path is within workspace
    try:
        path_resolved.relative_to(workspace_resolved)
    except ValueError:
        raise SecurityError(f"Path traversal detected: {path} is outside workspace {workspace}")

    return path_resolved


def validate_file_extension(path: Path, category: str) -> Path:
    """
    Validate that a file has an allowed extension for its category.

    Args:
        path: The file path to validate
        category: The category (audio, video, image, json)

    Returns:
        The validated path

    Raises:
        SecurityError: If the extension is not allowed
    """
    suffix = path.suffix.lower()

    if category not in ALLOWED_EXTENSIONS:
        raise SecurityError(f"Unknown file category: {category}")

    if suffix not in ALLOWED_EXTENSIONS[category]:
        allowed = ", ".join(ALLOWED_EXTENSIONS[category])
        raise SecurityError(f"Invalid {category} file extension: {suffix} (allowed: {allowed})")

    return path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.

    Args:
        filename: The filename to sanitize

    Returns:
        The sanitized filename

    Raises:
        SecurityError: If the filename is invalid
    """
    if not filename:
        raise SecurityError("Filename cannot be empty")

    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Check for forbidden sequences
    for seq in FORBIDDEN_PATH_SEQUENCES:
        if seq in filename:
            raise SecurityError(f"Filename contains forbidden sequence: {seq}")

    # Must not start with a dot (hidden file) unless explicitly allowed
    if filename.startswith("."):
        raise SecurityError("Filename cannot start with a dot")

    # Must have some alphanumeric characters
    if not any(c.isalnum() for c in filename):
        raise SecurityError("Filename must contain alphanumeric characters")

    return filename


def validate_json_size(path: Path, max_size: int) -> Path:
    """
    Validate that a JSON file is not too large (prevent DoS).

    Args:
        path: The file path to check
        max_size: Maximum allowed size in bytes

    Returns:
        The validated path

    Raises:
        SecurityError: If the file is too large
    """
    if path.exists():
        size = path.stat().st_size
        if size > max_size:
            raise SecurityError(f"File too large: {size} bytes (max {max_size} bytes)")

    return path


def validate_command_args(args: list[str]) -> list[str]:
    """
    Validate command arguments to prevent injection attacks.

    This is a basic validation; the best practice is to avoid shell=True
    and pass arguments as a list to subprocess.

    Args:
        args: List of command arguments

    Returns:
        The validated arguments list

    Raises:
        SecurityError: If potentially dangerous characters are detected
    """
    dangerous_chars = {";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"}

    for arg in args:
        for char in dangerous_chars:
            if char in arg:
                raise SecurityError(f"Potentially dangerous character in command argument: {char}")

    return args
