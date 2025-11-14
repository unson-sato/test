"""
Phase 1: Character Design (キャラクター設計)
MV Orchestra v2.8

This module implements the second phase where 5 directors compete to design
main characters, costumes, and visual consistency based on Phase 0's winning concept.

Workflow:
1. Load Phase 0 winner's concept from session state
2. Each director generates a character design proposal
3. Each director evaluates all character designs
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


class Phase1Runner:
    """
    Runs Phase 1: Character Design competition among 5 directors.
    """

    def __init__(self, session: SharedState, config: Dict[str, Any],
                 mock_mode: bool = True):
        """
        Initialize Phase 1 Runner.

        Args:
            session: SharedState instance for this orchestration session
            config: Configuration dictionary (from config.json)
            mock_mode: If True, use mock evaluations (default: True)
        """
        self.session = session
        self.config = config
        self.mock_mode = mock_mode
        self.codex_runner = CodexRunner(mock_mode=mock_mode)
        self.phase_number = 1
        self.prompts_dir = get_project_root() / ".claude" / "prompts_v2"

    def load_phase0_concept(self) -> Dict[str, Any]:
        """
        Load Phase 0 winner's concept from session state.

        Returns:
            Phase 0 winner concept

        Raises:
            ValueError: If Phase 0 is not completed
        """
        phase0_data = self.session.get_phase_data(0)

        if phase0_data.status != "completed":
            raise ValueError("Phase 0 must be completed before running Phase 1")

        winner = phase0_data.data.get("winner")
        if not winner:
            raise ValueError("No winner found in Phase 0 data")

        logger.info(f"Loaded Phase 0 concept from {winner['director']}")
        return winner

    def load_director_prompt(self, director_type: DirectorType) -> str:
        """
        Load Phase 1 prompt template for a specific director.

        Args:
            director_type: The director type

        Returns:
            Prompt template content

        Raises:
            FileNotFoundError: If prompt template doesn't exist
        """
        prompt_file = self.prompts_dir / f"phase1_{director_type.value}.md"

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_character_design(self, director_type: DirectorType,
                                  phase0_concept: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a character design proposal from a specific director.

        Args:
            director_type: The director type
            phase0_concept: Phase 0 winner's concept

        Returns:
            Character design proposal dictionary
        """
        logger.info(f"Generating character design from {director_type.value}")

        profile = get_director_profile(director_type)
        prompt_template = self.load_director_prompt(director_type)

        # In mock mode, generate a mock character design
        # In real mode, this would send the prompt to Claude API
        if self.mock_mode:
            design = self._generate_mock_character_design(
                director_type, profile, phase0_concept
            )
        else:
            # TODO: Implement real AI character design generation
            design = self._generate_mock_character_design(
                director_type, profile, phase0_concept
            )

        return design

    def _generate_mock_character_design(self, director_type: DirectorType,
                                       profile: DirectorProfile,
                                       phase0_concept: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a mock character design for testing.

        Args:
            director_type: The director type
            profile: Director profile
            phase0_concept: Phase 0 winner's concept

        Returns:
            Mock character design dictionary
        """
        concept_theme = phase0_concept.get("proposal", {}).get("concept_theme", "Unknown")

        # Generate director-specific character design
        designs_by_type = {
            DirectorType.CORPORATE: {
                "characters": [
                    {
                        "name": "主人公 (Protagonist)",
                        "appearance": "Clean, professional styling with broad appeal",
                        "personality": "Relatable, aspirational, positive",
                        "costume": "Contemporary, brand-safe wardrobe with commercial appeal",
                        "role": "Hero's journey protagonist"
                    }
                ],
                "visual_consistency_strategy": "Professional styling guides, tested color palettes",
                "character_arc": "Clear emotional progression aligned with song structure"
            },
            DirectorType.FREELANCER: {
                "characters": [
                    {
                        "name": "アーティスト (The Artist)",
                        "appearance": "Unconventional, artistic, unique features",
                        "personality": "Complex, authentic, vulnerable",
                        "costume": "Experimental fashion, bold color choices, artistic layers",
                        "role": "Unconventional protagonist defying norms"
                    }
                ],
                "visual_consistency_strategy": "Fluid visual language, intentional inconsistency for artistic effect",
                "character_arc": "Non-linear emotional journey, abstract transformation"
            },
            DirectorType.VETERAN: {
                "characters": [
                    {
                        "name": "クラシックヒーロー (Classic Hero)",
                        "appearance": "Timeless features, classic proportions, refined presence",
                        "personality": "Depth, gravitas, emotional complexity",
                        "costume": "Cinematic tailoring, quality fabrics, timeless silhouettes",
                        "role": "Traditional protagonist with universal appeal"
                    }
                ],
                "visual_consistency_strategy": "Masterful cinematographic consistency, meticulous continuity",
                "character_arc": "Classic three-act structure, profound emotional depth"
            },
            DirectorType.AWARD_WINNER: {
                "characters": [
                    {
                        "name": "象徴的存在 (Symbolic Figure)",
                        "appearance": "Striking, memorable, award-worthy presence",
                        "personality": "Multi-layered, culturally resonant, sophisticated",
                        "costume": "Artistically excellent design with symbolic meaning",
                        "role": "Culturally significant protagonist"
                    }
                ],
                "visual_consistency_strategy": "Sophisticated visual language with symbolic coherence",
                "character_arc": "Layered transformation with cultural commentary"
            },
            DirectorType.NEWCOMER: {
                "characters": [
                    {
                        "name": "現代の若者 (Modern Youth)",
                        "appearance": "Fresh, trendy, Gen-Z aesthetic",
                        "personality": "Authentic, energetic, relatable to young audiences",
                        "costume": "Trending streetwear, social-media-ready outfits",
                        "role": "Contemporary protagonist with viral potential"
                    }
                ],
                "visual_consistency_strategy": "Flexible for trending formats, optimized for social media",
                "character_arc": "Fast-paced, meme-able moments, authentic emotional beats"
            }
        }

        base_design = designs_by_type.get(director_type, designs_by_type[DirectorType.CORPORATE])

        return {
            "director": director_type.value,
            "director_name": profile.name_en,
            "characters": base_design["characters"],
            "visual_consistency_strategy": base_design["visual_consistency_strategy"],
            "character_arc": base_design["character_arc"],
            "concept_alignment": f"Designed to match: {concept_theme}",
            "mock": True
        }

    def evaluate_character_designs(self, designs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Have each director evaluate all character designs.

        Args:
            designs: List of all character designs

        Returns:
            List of evaluation results
        """
        logger.info("Starting character design evaluation phase")
        evaluations = []

        for evaluator_type in DirectorType:
            logger.info(f"{evaluator_type.value} evaluating all character designs")

            evaluator_scores = {
                "evaluator": evaluator_type.value,
                "scores": {},
                "feedback": {}
            }

            for design in designs:
                score = self._evaluate_single_design(
                    evaluator_type,
                    design
                )

                design_director = design["director"]
                evaluator_scores["scores"][design_director] = score["score"]
                evaluator_scores["feedback"][design_director] = score["feedback"]

            evaluations.append(evaluator_scores)

        return evaluations

    def _evaluate_single_design(self, evaluator_type: DirectorType,
                               design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single character design from a specific director's perspective.

        Args:
            evaluator_type: The director doing the evaluation
            design: The character design to evaluate

        Returns:
            Evaluation result with score and feedback
        """
        evaluator_profile = get_director_profile(evaluator_type)

        # Create evaluation request
        request = EvaluationRequest(
            session_id=self.session.session_id,
            phase_number=self.phase_number,
            director_type=evaluator_type,
            evaluation_type="character_design",
            context={
                "design": design,
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

    def aggregate_scores(self, designs: List[Dict[str, Any]],
                        evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate evaluation scores and select winner.

        Args:
            designs: List of all character designs
            evaluations: List of all evaluations

        Returns:
            Winner information with scores
        """
        logger.info("Aggregating character design scores")

        # Get weights from config
        weights = self.config.get("directors", {}).get("weights", {})

        # Calculate total scores for each design
        design_scores = {}

        for design in designs:
            director = design["director"]
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
            design_scores[director] = avg_score

        # Find winner
        winner_director = max(design_scores, key=design_scores.get)
        winner_design = next(d for d in designs if d["director"] == winner_director)

        winner_info = {
            "director": winner_director,
            "total_score": design_scores[winner_director],
            "proposal": winner_design,
            "all_scores": design_scores
        }

        logger.info(f"Winner: {winner_director} with score {winner_info['total_score']:.2f}")

        return winner_info

    def run(self) -> Dict[str, Any]:
        """
        Run the complete Phase 1 process.

        Returns:
            Phase 1 results dictionary

        Raises:
            Exception: If phase fails
        """
        try:
            # Start phase
            self.session.start_phase(self.phase_number)
            logger.info(f"Starting Phase {self.phase_number}: Character Design")

            # Load Phase 0 concept
            phase0_concept = self.load_phase0_concept()

            # Generate character designs from all directors
            designs = []
            for director_type in DirectorType:
                design = self.generate_character_design(director_type, phase0_concept)
                designs.append(design)

            # Evaluate all character designs
            evaluations = self.evaluate_character_designs(designs)

            # Aggregate scores and select winner
            winner = self.aggregate_scores(designs, evaluations)

            # Prepare output
            phase_output = {
                "proposals": designs,
                "evaluations": evaluations,
                "winner": winner,
                "phase0_concept": phase0_concept
            }

            # Save to session state
            self.session.set_phase_data(
                self.phase_number,
                phase_output,
                metadata={"based_on_phase0_winner": phase0_concept["director"]}
            )

            # Complete phase
            self.session.complete_phase(self.phase_number)
            logger.info(f"Phase {self.phase_number} completed successfully")

            return phase_output

        except Exception as e:
            logger.error(f"Phase {self.phase_number} failed: {str(e)}")
            self.session.fail_phase(self.phase_number, {"error": str(e)})
            raise


def run_phase1(session_id: str,
               config_path: str = "/home/user/test/config.json",
               mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 1.

    Args:
        session_id: Session ID (must exist with completed Phase 0)
        config_path: Path to config.json
        mock_mode: Use mock evaluations (default: True)

    Returns:
        Phase 1 results
    """
    # Load config
    config = read_json(config_path)

    # Load session (must exist)
    session = SharedState.load_session(session_id)

    # Run phase
    runner = Phase1Runner(session, config, mock_mode=mock_mode)
    return runner.run()
