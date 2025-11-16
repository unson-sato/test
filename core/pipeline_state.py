"""
Pipeline State Manager for MV Orchestra v3.0

High-level pipeline state management.
This is a thin wrapper around SharedState for pipeline-level operations.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .shared_state import SharedState


logger = logging.getLogger(__name__)


class PipelineState:
    """
    High-level pipeline state manager.

    Provides pipeline-level operations and validation on top of SharedState.
    """

    def __init__(self, session_id: str):
        """
        Initialize Pipeline State.

        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.shared_state = SharedState.load_session(session_id)

    @classmethod
    def create(cls, session_id: str, audio_file: Optional[Path] = None) -> "PipelineState":
        """
        Create new pipeline state.

        Args:
            session_id: Session identifier
            audio_file: Optional audio file path

        Returns:
            PipelineState instance
        """
        SharedState.create_session(session_id, audio_file)
        return cls(session_id)

    def can_execute_phase(self, phase_num: int) -> bool:
        """
        Check if a phase can be executed.

        Args:
            phase_num: Phase number (0-9)

        Returns:
            True if can execute
        """
        return self.shared_state.can_execute_phase(phase_num)

    def mark_phase_started(self, phase_num: int) -> None:
        """
        Mark phase as started.

        Args:
            phase_num: Phase number (0-9)
        """
        self.shared_state.mark_phase_started(phase_num)

    def mark_phase_completed(
        self, phase_num: int, result: Dict[str, Any], success: bool = True
    ) -> None:
        """
        Mark phase as completed.

        Args:
            phase_num: Phase number (0-9)
            result: Phase result data
            success: Whether phase completed successfully
        """
        self.shared_state.mark_phase_completed(phase_num, result, success)

    def get_phase_data(self, phase_num: int) -> Optional[Dict[str, Any]]:
        """
        Get phase result data.

        Args:
            phase_num: Phase number (0-9)

        Returns:
            Phase data or None
        """
        return self.shared_state.get_phase_data(phase_num)

    def get_completed_phases(self) -> List[int]:
        """
        Get list of completed phase numbers.

        Returns:
            List of completed phase numbers
        """
        completed = []
        for phase_num, phase in self.shared_state.phases.items():
            if phase.status == "completed":
                completed.append(phase_num)
        return sorted(completed)

    def get_pipeline_progress(self) -> Dict[str, Any]:
        """
        Get pipeline progress summary.

        Returns:
            Progress dictionary
        """
        completed_phases = self.get_completed_phases()
        total_phases = 10  # Phase 0-9

        return {
            "completed_phases": completed_phases,
            "total_phases": total_phases,
            "progress_percentage": len(completed_phases) / total_phases * 100,
            "current_phase": max(completed_phases) + 1 if completed_phases else 0,
            "design_complete": 4 in completed_phases,  # Phase 1-4
            "generation_complete": 9 in completed_phases,  # Phase 5-9
        }

    def validate_pipeline_state(self) -> Dict[str, Any]:
        """
        Validate pipeline state and check for issues.

        Returns:
            Validation result with issues list
        """
        issues = []
        warnings = []

        # Check Phase 0
        if not self.can_execute_phase(1):
            issues.append("Phase 0 (audio analysis) not completed")

        # Check Phase 1-4 sequence
        for phase_num in range(1, 5):
            phase_data = self.get_phase_data(phase_num)
            if phase_data and "winner" not in phase_data:
                warnings.append(f"Phase {phase_num} completed but no winner found")

        # Check Phase 5-9 prerequisites
        if self.can_execute_phase(5):
            phase3_data = self.get_phase_data(3)
            if phase3_data and "winner" in phase3_data:
                clips = phase3_data["winner"].get("clips", [])
                if not clips:
                    warnings.append("Phase 3 has no clips defined")

        return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}

    def get_summary(self) -> Dict[str, Any]:
        """
        Get complete pipeline summary.

        Returns:
            Summary dictionary
        """
        progress = self.get_pipeline_progress()
        validation = self.validate_pipeline_state()
        session_summary = self.shared_state.get_session_summary()

        return {**session_summary, "progress": progress, "validation": validation}

    def save(self) -> None:
        """Save pipeline state."""
        self.shared_state.save()
