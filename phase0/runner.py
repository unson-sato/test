"""
Phase 0: Overall Design (全体設計)
MV Orchestra v2.8

This module implements the first phase where 5 directors compete to propose
the overall MV concept based on song analysis.

Workflow:
1. Load song analysis data
2. Each director generates a proposal using their personality
3. Each director evaluates all proposals
4. Aggregate scores and select winner
5. Save results to session state
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core import (
    SharedState,
    DirectorType,
    DirectorProfile,
    get_director_profile,
    CodexRunner,
    EvaluationRequest,
    EvaluationResult,
    read_json,
    write_json,
    get_project_root
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase0Runner:
    """
    Runs Phase 0: Overall Design competition among 5 directors.
    """

    def __init__(self, session: SharedState, config: Dict[str, Any],
                 mock_mode: bool = True):
        """
        Initialize Phase 0 Runner.

        Args:
            session: SharedState instance for this orchestration session
            config: Configuration dictionary (from config.json)
            mock_mode: If True, use mock evaluations (default: True)
        """
        self.session = session
        self.config = config
        self.mock_mode = mock_mode
        self.codex_runner = CodexRunner(mock_mode=mock_mode)
        self.phase_number = 0
        self.prompts_dir = get_project_root() / ".claude" / "prompts_v2"

    def load_song_analysis(self, analysis_path: str) -> Dict[str, Any]:
        """
        Load song analysis data from JSON file.

        Args:
            analysis_path: Path to analysis.json

        Returns:
            Song analysis data dictionary

        Raises:
            FileNotFoundError: If analysis file doesn't exist
        """
        logger.info(f"Loading song analysis from: {analysis_path}")
        return read_json(analysis_path)

    def load_director_prompt(self, director_type: DirectorType) -> str:
        """
        Load Phase 0 prompt template for a specific director.

        Args:
            director_type: The director type

        Returns:
            Prompt template content

        Raises:
            FileNotFoundError: If prompt template doesn't exist
        """
        prompt_file = self.prompts_dir / f"phase0_{director_type.value}.md"

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_proposal(self, director_type: DirectorType,
                         analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a proposal from a specific director.

        Args:
            director_type: The director type
            analysis_data: Song analysis data

        Returns:
            Proposal dictionary
        """
        logger.info(f"Generating proposal from {director_type.value}")

        profile = get_director_profile(director_type)
        prompt_template = self.load_director_prompt(director_type)

        # In mock mode, generate a mock proposal
        # In real mode, this would send the prompt to Claude API
        if self.mock_mode:
            proposal = self._generate_mock_proposal(director_type, profile, analysis_data)
        else:
            # TODO: Implement real AI proposal generation
            proposal = self._generate_mock_proposal(director_type, profile, analysis_data)

        return proposal

    def _generate_mock_proposal(self, director_type: DirectorType,
                                profile: DirectorProfile,
                                analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a mock proposal for testing.

        Args:
            director_type: The director type
            profile: Director profile
            analysis_data: Song analysis data

        Returns:
            Mock proposal dictionary
        """
        # Extract basic song info
        song_title = analysis_data.get('title', 'Unknown Song')
        bpm = analysis_data.get('bpm', 120)
        energy = analysis_data.get('energy_profile', {}).get('average', 'medium')

        # Generate director-specific proposal
        proposals_by_type = {
            DirectorType.CORPORATE: {
                "concept_theme": f"Commercial appeal for {song_title} - Safe, marketable concept",
                "visual_style": "Polished, high-production-value aesthetic with broad appeal",
                "narrative_structure": "Linear storytelling with clear emotional beats",
                "target_audience": "18-35 demographics, mainstream music consumers",
                "references": ["Major label MVs", "Award-winning commercial work"]
            },
            DirectorType.FREELANCER: {
                "concept_theme": f"Experimental vision for {song_title} - Bold artistic statement",
                "visual_style": "Unconventional, artistic, boundary-pushing visuals",
                "narrative_structure": "Non-linear, abstract emotional journey",
                "target_audience": "Art-focused viewers, indie music enthusiasts",
                "references": ["Independent film aesthetics", "Avant-garde MVs"]
            },
            DirectorType.VETERAN: {
                "concept_theme": f"Timeless approach for {song_title} - Classic storytelling",
                "visual_style": "Refined cinematography with traditional techniques",
                "narrative_structure": "Proven narrative structure with emotional depth",
                "target_audience": "Cross-generational appeal, quality-focused viewers",
                "references": ["Classic cinema", "Iconic music videos"]
            },
            DirectorType.AWARD_WINNER: {
                "concept_theme": f"Award-worthy concept for {song_title} - Artistic excellence",
                "visual_style": "Sophisticated visual language, cultural relevance",
                "narrative_structure": "Layered narrative with symbolic depth",
                "target_audience": "Critics, festival audiences, discerning viewers",
                "references": ["Award-winning films", "Critically acclaimed MVs"]
            },
            DirectorType.NEWCOMER: {
                "concept_theme": f"Fresh take on {song_title} - Contemporary viral potential",
                "visual_style": "Trendy, social-media-optimized, energetic visuals",
                "narrative_structure": "Fast-paced, meme-able moments, authentic energy",
                "target_audience": "Gen Z, TikTok users, trend-conscious viewers",
                "references": ["Viral MVs", "Social media trends"]
            }
        }

        base_proposal = proposals_by_type.get(director_type, proposals_by_type[DirectorType.CORPORATE])

        return {
            "director": director_type.value,
            "director_name": profile.name_en,
            "concept_theme": base_proposal["concept_theme"],
            "visual_style": base_proposal["visual_style"],
            "narrative_structure": base_proposal["narrative_structure"],
            "target_audience": base_proposal["target_audience"],
            "references": base_proposal["references"],
            "bpm_alignment": f"Designed for {bpm} BPM rhythm",
            "energy_match": f"Matches {energy} energy level",
            "mock": True
        }

    def evaluate_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Have each director evaluate all proposals.

        Args:
            proposals: List of all proposals

        Returns:
            List of evaluation results
        """
        logger.info("Starting evaluation phase")
        evaluations = []

        for evaluator_type in DirectorType:
            logger.info(f"{evaluator_type.value} evaluating all proposals")

            evaluator_scores = {
                "evaluator": evaluator_type.value,
                "scores": {},
                "feedback": {}
            }

            for proposal in proposals:
                score = self._evaluate_single_proposal(
                    evaluator_type,
                    proposal
                )

                proposal_director = proposal["director"]
                evaluator_scores["scores"][proposal_director] = score["score"]
                evaluator_scores["feedback"][proposal_director] = score["feedback"]

            evaluations.append(evaluator_scores)

        return evaluations

    def _evaluate_single_proposal(self, evaluator_type: DirectorType,
                                  proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single proposal from a specific director's perspective.

        Args:
            evaluator_type: The director doing the evaluation
            proposal: The proposal to evaluate

        Returns:
            Evaluation result with score and feedback
        """
        evaluator_profile = get_director_profile(evaluator_type)

        # Create evaluation request
        request = EvaluationRequest(
            session_id=self.session.session_id,
            phase_number=self.phase_number,
            director_type=evaluator_type,
            evaluation_type="overall_design",
            context={
                "proposal": proposal,
                "evaluator_profile": evaluator_profile.to_dict()
            }
        )

        # Execute evaluation
        result = self.codex_runner.execute_evaluation(request)

        return {
            "score": result.score,
            "feedback": result.feedback,
            "suggestions": result.suggestions,
            "highlights": result.highlights,
            "concerns": result.concerns
        }

    def aggregate_scores(self, proposals: List[Dict[str, Any]],
                        evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate evaluation scores and select winner.

        Args:
            proposals: List of all proposals
            evaluations: List of all evaluations

        Returns:
            Winner information with scores
        """
        logger.info("Aggregating scores")

        # Get weights from config
        weights = self.config.get("directors", {}).get("weights", {})

        # Calculate total scores for each proposal
        proposal_scores = {}

        for proposal in proposals:
            director = proposal["director"]
            total_score = 0.0
            total_weight = 0.0

            for evaluation in evaluations:
                evaluator = evaluation["evaluator"]
                score = evaluation["scores"].get(director, 0.0)
                weight = weights.get(evaluator, 1.0)

                total_score += score * weight
                total_weight += weight

            # Calculate weighted average
            avg_score = total_score / total_weight if total_weight > 0 else 0.0
            proposal_scores[director] = avg_score

        # Find winner
        winner_director = max(proposal_scores, key=proposal_scores.get)
        winner_proposal = next(p for p in proposals if p["director"] == winner_director)

        winner_info = {
            "director": winner_director,
            "total_score": proposal_scores[winner_director],
            "proposal": winner_proposal,
            "all_scores": proposal_scores
        }

        logger.info(f"Winner: {winner_director} with score {winner_info['total_score']:.2f}")

        return winner_info

    def run(self, analysis_path: str) -> Dict[str, Any]:
        """
        Run the complete Phase 0 process.

        Args:
            analysis_path: Path to song analysis JSON file

        Returns:
            Phase 0 results dictionary

        Raises:
            Exception: If phase fails
        """
        try:
            # Start phase
            self.session.start_phase(self.phase_number)
            logger.info(f"Starting Phase {self.phase_number}: Overall Design")

            # Load song analysis
            analysis_data = self.load_song_analysis(analysis_path)

            # Generate proposals from all directors
            proposals = []
            for director_type in DirectorType:
                proposal = self.generate_proposal(director_type, analysis_data)
                proposals.append(proposal)

            # Evaluate all proposals
            evaluations = self.evaluate_proposals(proposals)

            # Aggregate scores and select winner
            winner = self.aggregate_scores(proposals, evaluations)

            # Prepare output
            phase_output = {
                "proposals": proposals,
                "evaluations": evaluations,
                "winner": winner,
                "analysis_data": analysis_data
            }

            # Save to session state
            self.session.set_phase_data(
                self.phase_number,
                phase_output,
                metadata={"analysis_file": analysis_path}
            )

            # Complete phase
            self.session.complete_phase(self.phase_number)
            logger.info(f"Phase {self.phase_number} completed successfully")

            return phase_output

        except Exception as e:
            logger.error(f"Phase {self.phase_number} failed: {str(e)}")
            self.session.fail_phase(self.phase_number, {"error": str(e)})
            raise


def run_phase0(session_id: str, analysis_path: str,
               config_path: str = "/home/user/test/config.json",
               mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 0.

    Args:
        session_id: Session ID (or None to create new session)
        analysis_path: Path to analysis.json
        config_path: Path to config.json
        mock_mode: Use mock evaluations (default: True)

    Returns:
        Phase 0 results
    """
    # Load config
    config = read_json(config_path)

    # Load or create session
    if session_id:
        session = SharedState.load_session(session_id)
    else:
        session = SharedState.create_session(
            input_files={"analysis": analysis_path}
        )

    # Run phase
    runner = Phase0Runner(session, config, mock_mode=mock_mode)
    return runner.run(analysis_path)
