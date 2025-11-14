"""
Phase 3 Runner: Clip Division

This module implements the Phase 3 competition where 5 directors divide
the timeline into clips aligned to beats, based on:
- Phase 2 section directions
- Beat/bar data from analysis.json
- Emotional flow optimization

Each director proposes a clip division strategy, all directors evaluate,
and the winner is selected based on aggregated scores.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from core import SharedState, CodexRunner, DirectorType
from core.utils import read_json, write_json, get_iso_timestamp
from .clip_utils import (
    snap_to_beat,
    validate_clip_coverage,
    load_beat_data,
    generate_clip_id,
    estimate_clip_complexity
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase3Runner:
    """
    Runs the Phase 3 clip division competition.

    This runner:
    1. Loads Phase 2 section directions
    2. Loads beat/bar data from analysis.json
    3. Has each director create clip division strategy
    4. Has all directors evaluate each proposal
    5. Selects winner based on aggregated scores
    6. Saves all results to SharedState
    """

    def __init__(self, session_id: str, mock_mode: bool = True):
        """
        Initialize Phase 3 Runner.

        Args:
            session_id: The session identifier
            mock_mode: If True, use mock AI responses for testing
        """
        self.session_id = session_id
        self.mock_mode = mock_mode
        self.session = SharedState.load_session(session_id)
        self.codex_runner = CodexRunner(mock_mode=mock_mode)

        # Get project root for loading analysis.json
        from core.utils import get_project_root
        self.project_root = get_project_root()

    def load_phase_inputs(self) -> Tuple[Dict[str, Any], List[float], Dict[str, Any]]:
        """
        Load inputs from previous phases and analysis.json.

        Returns:
            Tuple of (phase2_directions, beat_times, analysis_metadata)

        Raises:
            RuntimeError: If required phase data is missing
        """
        # Load Phase 2 data
        phase2_data = self.session.get_phase_data(2)
        if phase2_data.status != "completed":
            raise RuntimeError("Phase 2 must be completed before running Phase 3")

        phase2_directions = phase2_data.data.get('winner', {}).get('proposal', {})
        if not phase2_directions:
            raise RuntimeError("Phase 2 winner directions not found")

        # Load beat data from analysis.json
        analysis_path = self.project_root / "shared-workspace" / "input" / "analysis.json"
        if not analysis_path.exists():
            raise FileNotFoundError(f"analysis.json not found at {analysis_path}")

        analysis_data = read_json(str(analysis_path))
        beat_times = load_beat_data(analysis_data)

        if not beat_times:
            logger.warning("No beat data found in analysis.json, using estimated beats")
            # Estimate beats based on BPM if available
            beat_times = self._estimate_beats(analysis_data)

        logger.info(f"Loaded {len(beat_times)} beat timestamps")

        # Extract metadata
        metadata = {
            'bpm': analysis_data.get('bpm', 120),
            'duration': analysis_data.get('duration', 0.0),
            'time_signature': analysis_data.get('time_signature', '4/4')
        }

        return phase2_directions, beat_times, metadata

    def _estimate_beats(self, analysis_data: Dict[str, Any]) -> List[float]:
        """Estimate beat times if not provided in analysis."""
        bpm = analysis_data.get('bpm', 120)
        duration = analysis_data.get('duration', 180.0)  # Default 3 minutes

        # Calculate beat interval (60 seconds / BPM)
        beat_interval = 60.0 / bpm

        # Generate beat times
        beat_times = []
        current_time = 0.0

        while current_time < duration:
            beat_times.append(current_time)
            current_time += beat_interval

        logger.info(f"Estimated {len(beat_times)} beats at {bpm} BPM")
        return beat_times

    def generate_clip_proposal(
        self,
        director_type: DirectorType,
        phase2_directions: Dict[str, Any],
        beat_times: List[float],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a clip division proposal from a specific director.

        Args:
            director_type: The type of director
            phase2_directions: Winner directions from Phase 2
            beat_times: List of beat timestamps
            metadata: Analysis metadata (BPM, duration, etc.)

        Returns:
            Dictionary containing the director's clip division proposal
        """
        logger.info(f"Generating clip proposal for {director_type.value}")

        # In mock mode, generate a mock proposal
        # In real mode, this would load the prompt template and call AI
        if self.mock_mode:
            proposal = self._generate_mock_clip_proposal(
                director_type, phase2_directions, beat_times, metadata
            )
        else:
            # TODO: Implement real AI call using prompt templates
            proposal = self._generate_real_clip_proposal(
                director_type, phase2_directions, beat_times, metadata
            )

        return proposal

    def _generate_mock_clip_proposal(
        self,
        director_type: DirectorType,
        phase2_directions: Dict[str, Any],
        beat_times: List[float],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a mock clip proposal for testing."""
        from core.director_profiles import get_director_profile

        profile = get_director_profile(director_type)

        # Get sections from phase2_directions
        sections = phase2_directions.get('sections', [])

        # Determine clip density based on director personality
        if profile.innovation_focus > 0.7:
            # More experimental, more clips
            avg_clip_duration = 2.5
        elif profile.commercial_focus > 0.7:
            # Commercial, moderate pacing
            avg_clip_duration = 3.5
        else:
            # Balanced approach
            avg_clip_duration = 3.0

        clips = []
        clip_counter = 1
        total_duration = metadata.get('duration', 180.0)

        # Sort sections by start time to ensure proper ordering
        sorted_sections = sorted(sections, key=lambda s: s.get('start_time', 0.0))

        # Generate clips for each section
        for section in sorted_sections:
            section_start = section.get('start_time', 0.0)
            section_end = section.get('end_time', total_duration)
            section_name = section.get('section_name', 'unknown')

            current_time = section_start

            while current_time < section_end:
                # Calculate clip end time
                clip_end = min(current_time + avg_clip_duration, section_end)

                # Snap to nearest beat
                snapped_start = snap_to_beat(current_time, beat_times, tolerance=0.3)
                snapped_end = snap_to_beat(clip_end, beat_times, tolerance=0.3)

                # Ensure snapped_start doesn't go backwards
                if snapped_start < current_time - 0.01:
                    snapped_start = current_time

                # Ensure clips don't get too short from snapping
                if snapped_end - snapped_start < 1.0:
                    snapped_end = snapped_start + avg_clip_duration

                # Ensure we don't exceed section end
                snapped_end = min(snapped_end, section_end)

                clip_id = generate_clip_id(clip_counter)
                duration = snapped_end - snapped_start

                # Determine shot type based on clip position in section
                progress = (current_time - section_start) / (section_end - section_start)
                if progress < 0.2:
                    shot_type = "establishing wide"
                elif progress < 0.5:
                    shot_type = "medium coverage"
                elif progress < 0.8:
                    shot_type = "close-up detail"
                else:
                    shot_type = "transition shot"

                clips.append({
                    'clip_id': clip_id,
                    'start_time': round(snapped_start, 2),
                    'end_time': round(snapped_end, 2),
                    'duration': round(duration, 2),
                    'section': section_name,
                    'shot_type': shot_type,
                    'camera_movement': profile.name_en + " style camera",
                    'complexity': estimate_clip_complexity(shot_type, duration),
                    'beat_aligned': True,
                    'base_allocation': round(duration, 2)
                })

                current_time = snapped_end
                clip_counter += 1

        proposal = {
            'director': director_type.value,
            'clips': clips,
            'total_clips': len(clips),
            'average_clip_length': round(sum(c['duration'] for c in clips) / len(clips), 2) if clips else 0.0,
            'beat_alignment_strategy': f"{profile.name_en} beat alignment approach",
            'metadata': {
                'director_profile': profile.name_en,
                'timestamp': get_iso_timestamp()
            }
        }

        return proposal

    def _generate_real_clip_proposal(
        self,
        director_type: DirectorType,
        phase2_directions: Dict[str, Any],
        beat_times: List[float],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a real clip proposal using AI (placeholder)."""
        # TODO: Implement real AI call
        # This would:
        # 1. Load prompt template from .claude/prompts_v2/phase3_{director}.md
        # 2. Format prompt with context (phase2, beats, metadata)
        # 3. Call AI service
        # 4. Parse response into structured format

        # For now, fall back to mock
        return self._generate_mock_clip_proposal(
            director_type, phase2_directions, beat_times, metadata
        )

    def evaluate_proposal(
        self,
        evaluator_type: DirectorType,
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Have a director evaluate a clip proposal.

        Args:
            evaluator_type: The director doing the evaluation
            proposal: The proposal to evaluate

        Returns:
            Evaluation dictionary with score and feedback
        """
        from core.director_profiles import get_director_profile

        evaluator_profile = get_director_profile(evaluator_type)
        proposal_director = proposal.get('director', 'unknown')

        # Base score influenced by evaluator's characteristics
        base_score = 72.0

        # Adjust based on clip characteristics
        total_clips = proposal.get('total_clips', 0)
        avg_clip_length = proposal.get('average_clip_length', 3.0)

        # Different directors prefer different pacing
        if evaluator_profile.innovation_focus > 0.7:
            # Prefer more clips, faster pacing
            if total_clips > 50:
                base_score += 5.0
            if avg_clip_length < 3.0:
                base_score += 3.0
        elif evaluator_profile.commercial_focus > 0.7:
            # Prefer moderate pacing
            if 30 <= total_clips <= 60:
                base_score += 4.0
        else:
            # Artistic, may prefer longer clips
            if avg_clip_length > 3.5:
                base_score += 2.0

        # Add some variance
        import random
        random.seed(hash(f"{evaluator_type.value}_{proposal_director}"))
        variance = random.uniform(-5.0, 5.0)
        final_score = max(0, min(100, base_score + variance))

        evaluation = {
            'evaluator': evaluator_type.value,
            'proposal_director': proposal_director,
            'score': round(final_score, 2),
            'feedback': f"{evaluator_profile.name_en}'s evaluation: Effective clip division with {total_clips} clips",
            'strengths': [
                f"Good pacing with {avg_clip_length:.1f}s average",
                f"Strong {evaluator_profile.evaluation_focus[0]}"
            ],
            'concerns': [
                "Could optimize beat alignment" if random.random() > 0.5 else "Minor timing adjustments possible"
            ],
            'timestamp': get_iso_timestamp()
        }

        return evaluation

    def select_winner(
        self,
        proposals: List[Dict[str, Any]],
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select the winning proposal based on evaluation scores.

        Args:
            proposals: List of all proposals
            evaluations: List of all evaluations

        Returns:
            Dictionary with winner information
        """
        # Aggregate scores for each proposal
        scores_by_director = {}

        for evaluation in evaluations:
            proposal_director = evaluation['proposal_director']
            score = evaluation['score']

            if proposal_director not in scores_by_director:
                scores_by_director[proposal_director] = []

            scores_by_director[proposal_director].append(score)

        # Calculate average scores
        avg_scores = {
            director: sum(scores) / len(scores)
            for director, scores in scores_by_director.items()
        }

        # Find winner
        winner_director = max(avg_scores.items(), key=lambda x: x[1])[0]
        winner_score = avg_scores[winner_director]

        # Find the winner's proposal
        winner_proposal = next(
            (p for p in proposals if p['director'] == winner_director),
            None
        )

        logger.info(f"Phase 3 winner: {winner_director} with score {winner_score:.2f}")

        return {
            'director': winner_director,
            'total_score': round(winner_score, 2),
            'proposal': winner_proposal,
            'all_scores': avg_scores
        }

    def run(self) -> Dict[str, Any]:
        """
        Run the complete Phase 3 process.

        Returns:
            Dictionary containing all Phase 3 results

        Raises:
            RuntimeError: If phase execution fails
        """
        try:
            # Start phase
            self.session.start_phase(3)
            logger.info(f"Starting Phase 3 for session {self.session_id}")

            # Load inputs
            phase2_directions, beat_times, metadata = self.load_phase_inputs()

            # Generate proposals from all directors
            proposals = []
            for director_type in DirectorType:
                proposal = self.generate_clip_proposal(
                    director_type,
                    phase2_directions,
                    beat_times,
                    metadata
                )
                proposals.append(proposal)

            logger.info(f"Generated {len(proposals)} clip proposals")

            # Validate clip coverage for each proposal
            for proposal in proposals:
                clips = proposal.get('clips', [])
                validate_clip_coverage(clips, metadata.get('duration', 180.0))

            # Evaluate all proposals
            evaluations = []
            for proposal in proposals:
                for evaluator_type in DirectorType:
                    evaluation = self.evaluate_proposal(evaluator_type, proposal)
                    evaluations.append(evaluation)

            logger.info(f"Completed {len(evaluations)} evaluations")

            # Select winner
            winner = self.select_winner(proposals, evaluations)

            # Prepare results
            results = {
                'proposals': proposals,
                'evaluations': evaluations,
                'winner': winner,
                'metadata': {
                    'total_proposals': len(proposals),
                    'total_evaluations': len(evaluations),
                    'beat_count': len(beat_times),
                    'bpm': metadata.get('bpm', 120),
                    'timestamp': get_iso_timestamp()
                }
            }

            # Save to session
            self.session.set_phase_data(3, results)
            self.session.complete_phase(3)

            logger.info("Phase 3 completed successfully")

            # TODO: Auto-trigger Clip Optimizer (Wave 3)
            # tools.optimization.clip_optimizer.optimize_clips(session_id)

            return results

        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            self.session.fail_phase(3, {'error': str(e)})
            raise


def run_phase3(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 3.

    Args:
        session_id: The session identifier
        mock_mode: If True, use mock AI responses

    Returns:
        Phase 3 results dictionary
    """
    runner = Phase3Runner(session_id, mock_mode=mock_mode)
    return runner.run()
