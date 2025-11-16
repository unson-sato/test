"""
Shared State Management for MV Orchestra v2.8

This module manages session state across all phases of the multi-director
AI competition system. It handles:
- Session creation and loading
- Phase data storage and retrieval
- Metadata tracking (timestamps, versions, optimization logs)
- Persistence to JSON files
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from .utils import (
    ensure_dir,
    get_session_dir,
    get_timestamp,
    get_iso_timestamp,
    read_json,
    write_json,
    generate_session_id
)


@dataclass
class PhaseData:
    """
    Data for a single phase of the orchestration process.

    Attributes:
        phase_number: The phase number (0-9)
        phase_name: Human-readable phase name
        status: Current status (pending, in_progress, completed, failed)
        started_at: Timestamp when phase started
        completed_at: Timestamp when phase completed
        data: Phase-specific data (proposals, evaluations, decisions, etc.)
        metadata: Additional metadata for the phase
    """
    phase_number: int
    phase_name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class SessionMetadata:
    """
    Metadata for an orchestration session.

    Attributes:
        session_id: Unique session identifier
        created_at: Session creation timestamp
        updated_at: Last update timestamp
        version: Session format version
        input_files: Information about input files (MP3, lyrics, analysis)
        optimization_logs: Logs from optimization processes
        current_phase: Current active phase number
        status: Overall session status
    """
    session_id: str
    created_at: str
    updated_at: str
    version: str = "2.8"
    input_files: Dict[str, str] = field(default_factory=dict)
    optimization_logs: List[Dict[str, Any]] = field(default_factory=list)
    current_phase: int = 0
    status: str = "active"  # active, completed, archived, failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class SharedState:
    """
    Manages shared state across all phases of MV Orchestra v2.8.

    This class provides centralized state management, ensuring consistent
    data access and persistence across the entire orchestration process.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize SharedState.

        Args:
            session_id: Existing session ID to load, or None to create new session
        """
        if session_id is None:
            session_id = generate_session_id("mvorch")

        self.session_id = session_id
        self.session_dir = get_session_dir(session_id)

        # Initialize metadata
        self.metadata = SessionMetadata(
            session_id=session_id,
            created_at=get_iso_timestamp(),
            updated_at=get_iso_timestamp()
        )

        # Initialize phase data for all phases (0-9)
        self.phases: Dict[int, PhaseData] = {
            0: PhaseData(0, "Overall Design"),
            1: PhaseData(1, "Character Design"),
            2: PhaseData(2, "Section Direction"),
            3: PhaseData(3, "Clip Division"),
            4: PhaseData(4, "Generation Strategy"),
            5: PhaseData(5, "Real Claude Review (Optional)"),
            6: PhaseData(6, "Video Generation Execution"),
            7: PhaseData(7, "Editing & Timeline Assembly"),
            8: PhaseData(8, "Effects & Lyric Motion"),
            9: PhaseData(9, "Final Rendering & Export")
        }

        # Global session data (shared across phases)
        self.global_data: Dict[str, Any] = {}

    @classmethod
    def load_session(cls, session_id: str) -> 'SharedState':
        """
        Load an existing session from disk.

        Args:
            session_id: The session ID to load

        Returns:
            SharedState instance with loaded data

        Raises:
            FileNotFoundError: If session file doesn't exist
            json.JSONDecodeError: If session file is invalid
        """
        instance = cls(session_id=session_id)
        session_file = instance.session_dir / "state.json"

        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        # Load session data
        data = read_json(str(session_file))

        # Restore metadata
        instance.metadata = SessionMetadata(**data['metadata'])

        # Restore phase data
        for phase_num, phase_data in data['phases'].items():
            instance.phases[int(phase_num)] = PhaseData(**phase_data)

        # Restore global data
        instance.global_data = data.get('global_data', {})

        return instance

    @classmethod
    def create_session(cls, input_files: Optional[Dict[str, str]] = None) -> 'SharedState':
        """
        Create a new session with optional input files.

        Args:
            input_files: Dictionary of input file information
                        (e.g., {'mp3': 'path/to/song.mp3', 'lyrics': 'path/to/lyrics.txt'})

        Returns:
            New SharedState instance
        """
        instance = cls()

        if input_files:
            instance.metadata.input_files = input_files

        # Create session directory
        ensure_dir(instance.session_dir)

        # Save initial state
        instance.save_session()

        return instance

    def save_session(self) -> None:
        """
        Save current session state to disk.

        Creates/updates the state.json file in the session directory.
        """
        # Update timestamp
        self.metadata.updated_at = get_iso_timestamp()

        # Ensure session directory exists
        ensure_dir(self.session_dir)

        # Prepare data for serialization
        data = {
            'metadata': self.metadata.to_dict(),
            'phases': {
                phase_num: phase.to_dict()
                for phase_num, phase in self.phases.items()
            },
            'global_data': self.global_data
        }

        # Write to file
        session_file = self.session_dir / "state.json"
        write_json(str(session_file), data)

    def get_phase_data(self, phase_number: int) -> PhaseData:
        """
        Get data for a specific phase.

        Args:
            phase_number: The phase number (0-9)

        Returns:
            PhaseData object for the requested phase

        Raises:
            KeyError: If phase_number is invalid
        """
        if phase_number not in self.phases:
            raise KeyError(f"Invalid phase number: {phase_number}")

        return self.phases[phase_number]

    def set_phase_data(self, phase_number: int, data: Dict[str, Any],
                      metadata: Optional[Dict[str, Any]] = None,
                      auto_save: bool = True) -> None:
        """
        Set data for a specific phase.

        Args:
            phase_number: The phase number (0-9)
            data: Data to store for the phase
            metadata: Optional metadata to merge with existing metadata
            auto_save: Whether to automatically save session (default: True)

        Raises:
            KeyError: If phase_number is invalid
        """
        if phase_number not in self.phases:
            raise KeyError(f"Invalid phase number: {phase_number}")

        phase = self.phases[phase_number]
        phase.data.update(data)

        if metadata:
            phase.metadata.update(metadata)

        if auto_save:
            self.save_session()

    def start_phase(self, phase_number: int, auto_save: bool = True) -> None:
        """
        Mark a phase as started.

        Args:
            phase_number: The phase number (0-9)
            auto_save: Whether to automatically save session (default: True)

        Raises:
            KeyError: If phase_number is invalid
        """
        if phase_number not in self.phases:
            raise KeyError(f"Invalid phase number: {phase_number}")

        phase = self.phases[phase_number]
        phase.status = "in_progress"
        phase.started_at = get_iso_timestamp()

        self.metadata.current_phase = phase_number

        if auto_save:
            self.save_session()

    def complete_phase(self, phase_number: int, auto_save: bool = True) -> None:
        """
        Mark a phase as completed.

        Args:
            phase_number: The phase number (0-9)
            auto_save: Whether to automatically save session (default: True)

        Raises:
            KeyError: If phase_number is invalid
        """
        if phase_number not in self.phases:
            raise KeyError(f"Invalid phase number: {phase_number}")

        phase = self.phases[phase_number]
        phase.status = "completed"
        phase.completed_at = get_iso_timestamp()

        if auto_save:
            self.save_session()

    def fail_phase(self, phase_number: int, error_info: Optional[Dict[str, Any]] = None,
                  auto_save: bool = True) -> None:
        """
        Mark a phase as failed.

        Args:
            phase_number: The phase number (0-9)
            error_info: Optional error information to store
            auto_save: Whether to automatically save session (default: True)

        Raises:
            KeyError: If phase_number is invalid
        """
        if phase_number not in self.phases:
            raise KeyError(f"Invalid phase number: {phase_number}")

        phase = self.phases[phase_number]
        phase.status = "failed"
        phase.completed_at = get_iso_timestamp()

        if error_info:
            phase.metadata['error'] = error_info

        if auto_save:
            self.save_session()

    def add_optimization_log(self, log_entry: Dict[str, Any],
                            auto_save: bool = True) -> None:
        """
        Add an entry to the optimization logs.

        Args:
            log_entry: Log entry to add (should include timestamp, message, etc.)
            auto_save: Whether to automatically save session (default: True)
        """
        # Add timestamp if not present
        if 'timestamp' not in log_entry:
            log_entry['timestamp'] = get_iso_timestamp()

        self.metadata.optimization_logs.append(log_entry)

        if auto_save:
            self.save_session()

    def set_global_data(self, key: str, value: Any, auto_save: bool = True) -> None:
        """
        Set a global data value (shared across all phases).

        Args:
            key: Data key
            value: Data value
            auto_save: Whether to automatically save session (default: True)
        """
        self.global_data[key] = value

        if auto_save:
            self.save_session()

    def get_global_data(self, key: str, default: Any = None) -> Any:
        """
        Get a global data value.

        Args:
            key: Data key
            default: Default value if key doesn't exist

        Returns:
            The stored value or default
        """
        return self.global_data.get(key, default)

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session state.

        Returns:
            Dictionary containing session summary information
        """
        return {
            'session_id': self.session_id,
            'version': self.metadata.version,
            'status': self.metadata.status,
            'created_at': self.metadata.created_at,
            'updated_at': self.metadata.updated_at,
            'current_phase': self.metadata.current_phase,
            'phase_status': {
                phase_num: phase.status
                for phase_num, phase in self.phases.items()
            },
            'input_files': self.metadata.input_files,
            'optimization_log_count': len(self.metadata.optimization_logs)
        }

    def export_session(self, output_path: str) -> None:
        """
        Export session to a specific file path.

        Args:
            output_path: Path where the session should be exported
        """
        data = {
            'metadata': self.metadata.to_dict(),
            'phases': {
                phase_num: phase.to_dict()
                for phase_num, phase in self.phases.items()
            },
            'global_data': self.global_data
        }

        write_json(output_path, data)

    def __repr__(self) -> str:
        """String representation of SharedState"""
        return (f"SharedState(session_id='{self.session_id}', "
                f"current_phase={self.metadata.current_phase}, "
                f"status='{self.metadata.status}')")
