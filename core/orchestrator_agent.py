"""
Orchestrator Agent for MV Orchestra v3.0

Main orchestrator coordinating the entire Phase 0-9 pipeline.
Manages design phases (Phase 1-4) with multi-agent competition and evaluation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .constants import (
    DEFAULT_QUALITY_THRESHOLD,
    DEFAULT_MAX_ITERATIONS,
    PHASE_0_AUDIO_ANALYSIS,
    PHASE_1_STORY_MESSAGE,
    PHASE_2_SECTION_BREAKDOWN,
    PHASE_3_CLIP_DESIGN,
    PHASE_4_REFINEMENT,
)
from .shared_state import SharedState
from .agent_executor import AgentExecutor
from .evaluation_agent import EvaluationAgent
from .feedback_loop_manager import FeedbackLoopManager
from .utils import get_session_dir, ensure_dir, write_json, get_iso_timestamp


logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Main orchestrator for MV Orchestra pipeline.

    Coordinates Phase 0-9 execution with:
    - Multi-agent design competition (Phase 1-4)
    - Automatic evaluation and winner selection
    - Quality-driven feedback loops
    - State persistence and resume capability
    """

    def __init__(
        self,
        session_id: str,
        claude_cli: str = "claude",
        quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ):
        """
        Initialize Orchestrator Agent.

        Args:
            session_id: Session identifier
            claude_cli: Path to Claude CLI executable
            quality_threshold: Minimum quality score (0-100)
            max_iterations: Maximum feedback iterations per phase
        """
        self.session_id = session_id
        self.session_dir = get_session_dir(session_id)
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations

        # Initialize components
        self.state = SharedState.load_session(session_id)
        self.agent_executor = AgentExecutor(claude_cli=claude_cli)
        self.evaluation_agent = EvaluationAgent(claude_cli=claude_cli)
        self.feedback_manager = FeedbackLoopManager(
            agent_executor=self.agent_executor,
            evaluation_agent=self.evaluation_agent,
            quality_threshold=quality_threshold,
            max_iterations=max_iterations,
        )

        logger.info("OrchestratorAgent initialized for session: {}".format(session_id))

    async def run_design_phases(self, start_phase: int = 1, end_phase: int = 4) -> Dict[str, Any]:
        """
        Run design phases (Phase 1-4) with multi-agent competition.

        Args:
            start_phase: Starting phase (1-4)
            end_phase: Ending phase (1-4)

        Returns:
            Results dictionary
        """
        logger.info("=" * 80)
        logger.info(f"DESIGN PHASES {start_phase}-{end_phase}")
        logger.info("=" * 80)

        results = {}

        for phase_num in range(start_phase, end_phase + 1):
            logger.info(f"\n{'=' * 80}")
            logger.info(f"PHASE {phase_num}")
            logger.info(f"{'=' * 80}")

            try:
                phase_result = await self._run_design_phase(phase_num)
                results[f"phase{phase_num}"] = phase_result
                logger.info(f"✓ Phase {phase_num} completed")

            except Exception as e:
                logger.error(f"✗ Phase {phase_num} failed: {e}")
                raise

        logger.info(f"\n{'=' * 80}")
        logger.info(f"DESIGN PHASES {start_phase}-{end_phase} COMPLETED")
        logger.info(f"{'=' * 80}")

        return results

    async def _run_design_phase(self, phase_num: int) -> Dict[str, Any]:
        """
        Run a single design phase with feedback loop.

        Args:
            phase_num: Phase number (1-4)

        Returns:
            Phase result
        """
        # Check if can execute
        if not self.state.can_execute_phase(phase_num):
            raise RuntimeError(f"Cannot execute phase {phase_num}: prerequisites not met")

        # Mark phase as started
        self.state.mark_phase_started(phase_num)

        # Get context from previous phases
        context = self._build_context(phase_num)

        # Create output directory
        output_dir = self.session_dir / f"phase{phase_num}"
        ensure_dir(output_dir)

        # Run with feedback loop
        logger.info(f"Running Phase {phase_num} with feedback loop...")

        result = await self.feedback_manager.run_with_feedback(
            phase_num=phase_num, initial_context=context, output_dir=output_dir
        )

        # Save results
        result_file = output_dir / "results.json"
        result_data = {
            "phase": phase_num,
            "winner": result.final_result,
            "iterations": result.iteration_count,
            "final_score": result.final_score,
            "improvement": result.total_improvement,
            "timestamp": get_iso_timestamp(),
        }

        write_json(result_file, result_data)

        # Mark phase as completed
        self.state.mark_phase_completed(phase_num, result_data)

        logger.info(f"Phase {phase_num} results:")
        logger.info(f"  Winner: {result.winner_name}")
        logger.info(f"  Score: {result.final_score:.1f}/100")
        logger.info(f"  Iterations: {result.iteration_count}")
        logger.info(f"  Improvement: +{result.total_improvement:.1f}")

        return result_data

    def _build_context(self, phase_num: int) -> Dict[str, Any]:
        """
        Build context for a phase from previous phase results.

        Args:
            phase_num: Current phase number

        Returns:
            Context dictionary
        """
        context = {}

        # Phase 0: Audio analysis
        phase0_data = self.state.get_phase_data(PHASE_0_AUDIO_ANALYSIS)
        if phase0_data:
            context["audio_analysis"] = phase0_data

        # Phase 1: Story & Message (no prerequisites)
        if phase_num == PHASE_1_STORY_MESSAGE:
            return context

        # Phase 2: Section Division (needs Phase 1)
        if phase_num >= PHASE_2_SECTION_BREAKDOWN:
            phase1_data = self.state.get_phase_data(PHASE_1_STORY_MESSAGE)
            if phase1_data and "winner" in phase1_data:
                context["story"] = phase1_data["winner"]

        # Phase 3: Clip Division (needs Phase 1, 2)
        if phase_num >= PHASE_3_CLIP_DESIGN:
            phase2_data = self.state.get_phase_data(PHASE_2_SECTION_BREAKDOWN)
            if phase2_data and "winner" in phase2_data:
                context["sections"] = phase2_data["winner"]

        # Phase 4: Generation Strategy (needs Phase 1, 2, 3)
        if phase_num >= PHASE_4_REFINEMENT:
            phase3_data = self.state.get_phase_data(PHASE_3_CLIP_DESIGN)
            if phase3_data and "winner" in phase3_data:
                context["clips"] = phase3_data["winner"]

        return context

    async def run_full_pipeline(self, audio_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run complete Phase 0-9 pipeline.

        Args:
            audio_file: Path to audio file (for Phase 0)

        Returns:
            Complete pipeline results
        """
        logger.info("=" * 80)
        logger.info("MV ORCHESTRA - FULL PIPELINE")
        logger.info("=" * 80)

        results = {}

        # Phase 0: Audio Analysis
        if audio_file:
            logger.info("\nPhase 0: Audio Analysis")
            phase0_result = await self._run_audio_analysis(audio_file)
            results["phase0"] = phase0_result

        # Phase 1-4: Design
        logger.info("\nPhase 1-4: Design")
        design_results = await self.run_design_phases(1, 4)
        results.update(design_results)

        # Phase 5-9: Generation & Post-processing
        # These will be called separately via run_phase5_9.py

        logger.info("\n" + "=" * 80)
        logger.info("DESIGN PIPELINE (0-4) COMPLETED")
        logger.info("=" * 80)
        logger.info("\nNext: Run Phase 5-9 with:")
        logger.info(f"  python3 run_phase5_9.py {self.session_id}")

        return results

    async def _run_audio_analysis(self, audio_file: Path) -> Dict[str, Any]:
        """
        Run Phase 0: Audio Analysis.

        Args:
            audio_file: Path to audio file

        Returns:
            Analysis results
        """
        logger.info(f"Analyzing audio: {audio_file}")

        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Mark phase started
        self.state.mark_phase_started(PHASE_0_AUDIO_ANALYSIS)

        # Create output directory
        output_dir = self.session_dir / "phase0"
        ensure_dir(output_dir)

        # Placeholder for actual audio analysis
        # In real implementation, use librosa for:
        # - BPM detection
        # - Beat tracking
        # - Spectral analysis
        # - Energy analysis
        # - Section detection

        result = {
            "audio_file": str(audio_file),
            "duration": 180.0,  # Placeholder
            "bpm": 120,  # Placeholder
            "beats": [],  # Placeholder
            "sections": [],  # Placeholder
            "timestamp": get_iso_timestamp(),
        }

        # Save results
        result_file = output_dir / "results.json"
        write_json(result_file, result)

        # Mark phase completed
        self.state.mark_phase_completed(PHASE_0_AUDIO_ANALYSIS, result)

        logger.info("✓ Phase 0 completed")
        logger.info(f"  Duration: {result['duration']:.1f}s")
        logger.info(f"  BPM: {result['bpm']}")

        return result

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session state.

        Returns:
            Session summary
        """
        return self.state.get_session_summary()
