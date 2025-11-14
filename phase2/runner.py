"""
Phase 2 Runner: Section Direction Design

This module implements the Phase 2 competition where 5 directors design
section-by-section direction (intro, verse, chorus, bridge, outro) based on:
- Phase 0 concept (overall design)
- Phase 1 characters
- Song sections from analysis.json

Each director proposes direction for each section, all directors evaluate,
and the winner is selected based on aggregated scores.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from core import SharedState, CodexRunner, DirectorType
from core.utils import read_json, write_json, get_iso_timestamp
from .section_utils import (
    validate_section_coverage,
    load_song_sections,
    extract_section_summary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2Runner:
    """
    Runs the Phase 2 section direction design competition.

    This runner:
    1. Loads Phase 0 concept and Phase 1 characters
    2. Loads song sections from analysis.json
    3. Has each director create section-by-section direction
    4. Has all directors evaluate each proposal
    5. Selects winner based on aggregated scores
    6. Saves all results to SharedState
    """

    def __init__(self, session_id: str, mock_mode: bool = True):
        """
        Initialize Phase 2 Runner.

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

    def load_phase_inputs(self) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load inputs from previous phases and analysis.json.

        Returns:
            Tuple of (phase0_concept, phase1_characters, song_sections)

        Raises:
            RuntimeError: If required phase data is missing
        """
        # Load Phase 0 data
        phase0_data = self.session.get_phase_data(0)
        if phase0_data.status != "completed":
            raise RuntimeError("Phase 0 must be completed before running Phase 2")

        phase0_concept = phase0_data.data.get('winner', {}).get('proposal', {})
        if not phase0_concept:
            raise RuntimeError("Phase 0 winner concept not found")

        # Load Phase 1 data
        phase1_data = self.session.get_phase_data(1)
        if phase1_data.status != "completed":
            raise RuntimeError("Phase 1 must be completed before running Phase 2")

        phase1_characters = phase1_data.data.get('winner', {}).get('proposal', {})
        if not phase1_characters:
            raise RuntimeError("Phase 1 winner characters not found")

        # Load song sections from analysis.json
        analysis_path = self.project_root / "shared-workspace" / "input" / "analysis.json"
        if not analysis_path.exists():
            raise FileNotFoundError(f"analysis.json not found at {analysis_path}")

        analysis_data = read_json(str(analysis_path))
        song_sections = analysis_data.get('sections', [])

        if not song_sections:
            raise RuntimeError("No sections found in analysis.json")

        logger.info(f"Loaded {len(song_sections)} sections from analysis.json")

        return phase0_concept, phase1_characters, song_sections

    def generate_section_proposal(
        self,
        director_type: DirectorType,
        phase0_concept: Dict[str, Any],
        phase1_characters: Dict[str, Any],
        song_sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a section direction proposal from a specific director.

        Args:
            director_type: The type of director
            phase0_concept: Winner concept from Phase 0
            phase1_characters: Winner characters from Phase 1
            song_sections: List of song sections with timing

        Returns:
            Dictionary containing the director's section direction proposal
        """
        logger.info(f"Generating section proposal for {director_type.value}")

        # In mock mode, generate a mock proposal
        # In real mode, this would load the prompt template and call AI
        if self.mock_mode:
            proposal = self._generate_mock_section_proposal(
                director_type, phase0_concept, phase1_characters, song_sections
            )
        else:
            # TODO: Implement real AI call using prompt templates
            proposal = self._generate_real_section_proposal(
                director_type, phase0_concept, phase1_characters, song_sections
            )

        return proposal

    def _generate_mock_section_proposal(
        self,
        director_type: DirectorType,
        phase0_concept: Dict[str, Any],
        phase1_characters: Dict[str, Any],
        song_sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a mock section proposal for testing."""
        from core.director_profiles import get_director_profile

        profile = get_director_profile(director_type)

        # Create mock sections based on song structure
        sections = []
        for section_data in song_sections:
            section_name = section_data.get('label', 'unknown')
            start_time = section_data.get('start', 0.0)
            end_time = section_data.get('end', 0.0)

            # Generate section direction based on director personality
            if profile.innovation_focus > 0.7:
                emotional_tone = f"experimental, {section_name}-driven energy"
                camera_work = "unconventional angles, dynamic movement"
            elif profile.commercial_focus > 0.7:
                emotional_tone = f"engaging, audience-friendly {section_name}"
                camera_work = "professional, polished coverage"
            else:
                emotional_tone = f"emotional, artistic {section_name}"
                camera_work = "thoughtful composition, meaningful shots"

            sections.append({
                'section_name': section_name,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'emotional_tone': emotional_tone,
                'camera_work': camera_work,
                'lighting': f"{profile.name_en} signature lighting style",
                'character_action': f"Character interaction designed by {profile.name_en}",
                'transition': f"Smooth transition to next section",
                'director_notes': f"Section designed with {', '.join(profile.evaluation_focus[:2])}"
            })

        proposal = {
            'director': director_type.value,
            'sections': sections,
            'overall_emotional_arc': f"Arc designed by {profile.name_en} focusing on {profile.evaluation_focus[0]}",
            'visual_continuity_notes': f"Maintains {profile.name_en} visual signature throughout",
            'metadata': {
                'director_profile': profile.name_en,
                'total_sections': len(sections),
                'timestamp': get_iso_timestamp()
            }
        }

        return proposal

    def _generate_real_section_proposal(
        self,
        director_type: DirectorType,
        phase0_concept: Dict[str, Any],
        phase1_characters: Dict[str, Any],
        song_sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a real section proposal using AI (placeholder)."""
        # TODO: Implement real AI call
        # This would:
        # 1. Load prompt template from .claude/prompts_v2/phase2_{director}.md
        # 2. Format prompt with context (phase0, phase1, sections)
        # 3. Call AI service
        # 4. Parse response into structured format

        # For now, fall back to mock
        return self._generate_mock_section_proposal(
            director_type, phase0_concept, phase1_characters, song_sections
        )

    def evaluate_proposal(
        self,
        evaluator_type: DirectorType,
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Have a director evaluate a section proposal.

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
        base_score = 75.0

        # Adjust based on evaluator's focus
        if evaluator_profile.commercial_focus > 0.7:
            base_score += 5.0  # Reward clear structure
        if evaluator_profile.innovation_focus > 0.7:
            base_score -= 3.0  # Might want more experimentation
        if evaluator_profile.artistic_focus > 0.8:
            base_score += 2.0  # Appreciate artistic vision

        # Add some variance
        import random
        random.seed(hash(f"{evaluator_type.value}_{proposal_director}"))
        variance = random.uniform(-5.0, 5.0)
        final_score = max(0, min(100, base_score + variance))

        evaluation = {
            'evaluator': evaluator_type.value,
            'proposal_director': proposal_director,
            'score': round(final_score, 2),
            'feedback': f"{evaluator_profile.name_en}'s evaluation: Strong section design with clear {evaluator_profile.evaluation_focus[0]}",
            'strengths': [
                f"Good {evaluator_profile.evaluation_focus[0]}",
                f"Effective {evaluator_profile.evaluation_focus[1]}"
            ],
            'concerns': [
                f"Could enhance {evaluator_profile.evaluation_focus[2]}" if len(evaluator_profile.evaluation_focus) > 2 else "Minor refinements possible"
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

        logger.info(f"Phase 2 winner: {winner_director} with score {winner_score:.2f}")

        return {
            'director': winner_director,
            'total_score': round(winner_score, 2),
            'proposal': winner_proposal,
            'all_scores': avg_scores
        }

    def run(self) -> Dict[str, Any]:
        """
        Run the complete Phase 2 process.

        Returns:
            Dictionary containing all Phase 2 results

        Raises:
            RuntimeError: If phase execution fails
        """
        try:
            # Start phase
            self.session.start_phase(2)
            logger.info(f"Starting Phase 2 for session {self.session_id}")

            # Load inputs
            phase0_concept, phase1_characters, song_sections = self.load_phase_inputs()

            # Validate section coverage
            validate_section_coverage(song_sections)

            # Generate proposals from all directors
            proposals = []
            for director_type in DirectorType:
                proposal = self.generate_section_proposal(
                    director_type,
                    phase0_concept,
                    phase1_characters,
                    song_sections
                )
                proposals.append(proposal)

            logger.info(f"Generated {len(proposals)} section proposals")

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
                    'song_sections_count': len(song_sections),
                    'timestamp': get_iso_timestamp()
                }
            }

            # Save to session
            self.session.set_phase_data(2, results)
            self.session.complete_phase(2)

            logger.info("Phase 2 completed successfully")

            # TODO: Auto-trigger Emotion Target Builder (Wave 3)
            # tools.optimization.emotion_target_builder.build_target_curve(session_id)

            return results

        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            self.session.fail_phase(2, {'error': str(e)})
            raise


def run_phase2(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 2.

    Args:
        session_id: The session identifier
        mock_mode: If True, use mock AI responses

    Returns:
        Phase 2 results dictionary
    """
    runner = Phase2Runner(session_id, mock_mode=mock_mode)
    return runner.run()
