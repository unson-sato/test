"""
Shared State Management for MV Orchestra v3.0

Manages session state across all phases.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import get_session_dir, read_json, write_json, get_iso_timestamp


logger = logging.getLogger(__name__)


@dataclass
class PhaseAttempt:
    """Record of a single phase execution attempt"""
    attempt_number: int
    started_at: str
    completed_at: Optional[str] = None
    success: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class PhaseState:
    """State for a single phase"""
    phase_number: int
    status: str = "not_started"  # not_started, in_progress, completed, failed
    attempts: List[PhaseAttempt] = field(default_factory=list)
    current_result: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class SharedState:
    """
    Manages shared state across all phases of the orchestration process.

    Provides session management, phase tracking, and state persistence.
    """

    def __init__(self, session_id: str):
        """
        Initialize shared state for a session.

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.session_dir = get_session_dir(session_id)
        self.state_file = self.session_dir / "state.json"

        # Phase states (0-9)
        self.phases: Dict[int, PhaseState] = {
            i: PhaseState(phase_number=i)
            for i in range(10)
        }

        # Session metadata
        self.created_at = get_iso_timestamp()
        self.updated_at = get_iso_timestamp()

        # Load existing state if available
        if self.state_file.exists():
            self._load_state()

    @classmethod
    def load_session(cls, session_id: str) -> 'SharedState':
        """
        Load an existing session or create a new one.

        Args:
            session_id: Session identifier

        Returns:
            SharedState instance
        """
        return cls(session_id)

    @classmethod
    def create_session(cls, session_id: str, audio_file: Optional[Path] = None) -> 'SharedState':
        """
        Create a new session.

        Args:
            session_id: Session identifier
            audio_file: Optional path to audio file

        Returns:
            SharedState instance
        """
        state = cls(session_id)

        # Initialize Phase 0 with audio file if provided
        if audio_file:
            state.mark_phase_completed(0, {
                "audio_file": str(audio_file),
                "timestamp": get_iso_timestamp()
            })

        state.save()
        return state

    def get_phase_data(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """
        Get data from a completed phase.

        Args:
            phase_number: Phase number (0-9)

        Returns:
            Phase result data or None if not completed
        """
        if phase_number not in self.phases:
            return None

        phase = self.phases[phase_number]
        return phase.current_result

    def mark_phase_started(self, phase_number: int) -> None:
        """
        Mark a phase as started.

        Args:
            phase_number: Phase number (0-9)
        """
        if phase_number not in self.phases:
            logger.warning(f"Invalid phase number: {phase_number}")
            return

        phase = self.phases[phase_number]

        if phase.status not in ["not_started", "failed"]:
            logger.warning(f"Phase {phase_number} already started")
            return

        phase.status = "in_progress"
        phase.started_at = get_iso_timestamp()

        # Create new attempt
        attempt_number = len(phase.attempts) + 1
        attempt = PhaseAttempt(
            attempt_number=attempt_number,
            started_at=get_iso_timestamp()
        )
        phase.attempts.append(attempt)

        self.updated_at = get_iso_timestamp()
        self.save()

        logger.info(f"Phase {phase_number} started (attempt {attempt_number})")

    def mark_phase_completed(
        self,
        phase_number: int,
        result: Dict[str, Any],
        success: bool = True
    ) -> None:
        """
        Mark a phase as completed.

        Args:
            phase_number: Phase number (0-9)
            result: Phase result data
            success: Whether the phase completed successfully
        """
        if phase_number not in self.phases:
            logger.warning(f"Invalid phase number: {phase_number}")
            return

        phase = self.phases[phase_number]

        # Update current attempt
        if phase.attempts:
            current_attempt = phase.attempts[-1]
            current_attempt.completed_at = get_iso_timestamp()
            current_attempt.success = success
            current_attempt.result = result

        # Update phase state
        phase.status = "completed" if success else "failed"
        phase.completed_at = get_iso_timestamp()
        phase.current_result = result

        self.updated_at = get_iso_timestamp()
        self.save()

        status_str = "✓" if success else "✗"
        logger.info(f"{status_str} Phase {phase_number} completed")

    def can_execute_phase(self, phase_number: int) -> bool:
        """
        Check if a phase can be executed.

        Args:
            phase_number: Phase number (0-9)

        Returns:
            True if phase can be executed, False otherwise
        """
        if phase_number not in self.phases:
            return False

        # Phase 0 can always run
        if phase_number == 0:
            return True

        # Check if previous phase is completed
        prev_phase = self.phases.get(phase_number - 1)
        if not prev_phase or prev_phase.status != "completed":
            logger.warning(f"Cannot execute phase {phase_number}: previous phase not completed")
            return False

        return True

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of session state.

        Returns:
            Session summary dictionary
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "phases": {
                phase_num: {
                    "status": phase.status,
                    "attempts": len(phase.attempts),
                    "started_at": phase.started_at,
                    "completed_at": phase.completed_at,
                    "has_result": phase.current_result is not None
                }
                for phase_num, phase in self.phases.items()
            }
        }

    def save(self) -> None:
        """Save state to disk."""
        self.session_dir.mkdir(parents=True, exist_ok=True)

        state_data = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "phases": {
                str(phase_num): {
                    "phase_number": phase.phase_number,
                    "status": phase.status,
                    "started_at": phase.started_at,
                    "completed_at": phase.completed_at,
                    "current_result": phase.current_result,
                    "attempts": [
                        {
                            "attempt_number": att.attempt_number,
                            "started_at": att.started_at,
                            "completed_at": att.completed_at,
                            "success": att.success,
                            "result": att.result,
                            "error": att.error
                        }
                        for att in phase.attempts
                    ]
                }
                for phase_num, phase in self.phases.items()
            }
        }

        write_json(self.state_file, state_data)

    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            state_data = read_json(self.state_file)

            self.created_at = state_data.get("created_at", self.created_at)
            self.updated_at = state_data.get("updated_at", self.updated_at)

            # Load phase states
            phases_data = state_data.get("phases", {})
            for phase_num_str, phase_data in phases_data.items():
                phase_num = int(phase_num_str)

                if phase_num not in self.phases:
                    continue

                phase = self.phases[phase_num]
                phase.status = phase_data.get("status", "not_started")
                phase.started_at = phase_data.get("started_at")
                phase.completed_at = phase_data.get("completed_at")
                phase.current_result = phase_data.get("current_result")

                # Load attempts
                attempts_data = phase_data.get("attempts", [])
                phase.attempts = [
                    PhaseAttempt(
                        attempt_number=att_data["attempt_number"],
                        started_at=att_data["started_at"],
                        completed_at=att_data.get("completed_at"),
                        success=att_data.get("success", False),
                        result=att_data.get("result"),
                        error=att_data.get("error")
                    )
                    for att_data in attempts_data
                ]

            logger.debug(f"Loaded state for session {self.session_id}")

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
