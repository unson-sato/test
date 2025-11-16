"""
Codex Runner for MV Orchestra v2.8

This module handles execution of AI evaluations for the multi-director
competition system. It:
- Loads prompt templates from .claude/prompts_v2/evaluations/
- Executes evaluation logic (with mock implementation support)
- Saves evaluation results to session directories
- Manages director-specific evaluation contexts
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from .utils import (
    ensure_dir,
    get_evaluations_dir,
    get_project_root,
    get_iso_timestamp,
    read_json,
    write_json,
    safe_filename
)
from .director_profiles import DirectorProfile, DirectorType, get_director_profile


@dataclass
class EvaluationRequest:
    """
    Request for an AI evaluation.

    Attributes:
        session_id: The session identifier
        phase_number: Phase number (0-5)
        director_type: Type of director performing evaluation
        evaluation_type: Type of evaluation (e.g., "overall_design", "character_design")
        context: Context data to include in evaluation
        template_name: Name of the prompt template to use (optional)
        metadata: Additional metadata
    """
    session_id: str
    phase_number: int
    director_type: DirectorType
    evaluation_type: str
    context: Dict[str, Any]
    template_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """
    Result of an AI evaluation.

    Attributes:
        session_id: The session identifier
        phase_number: Phase number
        director_type: Type of director who performed evaluation
        evaluation_type: Type of evaluation performed
        timestamp: When evaluation was performed
        score: Numerical score (0-100)
        feedback: Textual feedback from the director
        suggestions: Specific suggestions for improvement
        highlights: Positive highlights
        concerns: Concerns or issues identified
        raw_response: Raw response from AI (if applicable)
        metadata: Additional metadata
    """
    session_id: str
    phase_number: int
    director_type: DirectorType
    evaluation_type: str
    timestamp: str
    score: float
    feedback: str
    suggestions: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    raw_response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'phase_number': self.phase_number,
            'director_type': self.director_type.value if isinstance(self.director_type, DirectorType) else self.director_type,
            'evaluation_type': self.evaluation_type,
            'timestamp': self.timestamp,
            'score': self.score,
            'feedback': self.feedback,
            'suggestions': self.suggestions,
            'highlights': self.highlights,
            'concerns': self.concerns,
            'raw_response': self.raw_response,
            'metadata': self.metadata
        }


class CodexRunner:
    """
    Executes AI evaluations for the multi-director competition system.

    This class manages prompt loading, evaluation execution, and result persistence.
    It supports both real AI evaluations and mock evaluations for testing.
    """

    def __init__(self, mock_mode: bool = False):
        """
        Initialize CodexRunner.

        Args:
            mock_mode: If True, use mock evaluations instead of real AI calls
        """
        self.mock_mode = mock_mode
        self.project_root = get_project_root()
        self.prompts_dir = self.project_root / ".claude" / "prompts_v2" / "evaluations"

        # Ensure prompts directory exists
        ensure_dir(self.prompts_dir)

    def load_prompt_template(self, template_name: str) -> str:
        """
        Load a prompt template from the evaluations directory.

        Args:
            template_name: Name of the template file (without .md extension)

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.prompts_dir / f"{template_name}.md"

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def prepare_evaluation_context(self, request: EvaluationRequest,
                                   director_profile: DirectorProfile) -> Dict[str, Any]:
        """
        Prepare the context for an evaluation request.

        Args:
            request: The evaluation request
            director_profile: The director's profile

        Returns:
            Dictionary containing all context for the evaluation
        """
        context = {
            'session_id': request.session_id,
            'phase_number': request.phase_number,
            'evaluation_type': request.evaluation_type,
            'director': {
                'type': director_profile.director_type.value,
                'name_ja': director_profile.name_ja,
                'name_en': director_profile.name_en,
                'description': director_profile.description,
                'evaluation_focus': director_profile.evaluation_focus,
                'risk_tolerance': director_profile.risk_tolerance,
                'commercial_focus': director_profile.commercial_focus,
                'artistic_focus': director_profile.artistic_focus,
                'innovation_focus': director_profile.innovation_focus
            },
            'request_context': request.context,
            'timestamp': get_iso_timestamp()
        }

        return context

    def execute_evaluation(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Execute an evaluation request.

        Args:
            request: The evaluation request

        Returns:
            EvaluationResult containing the evaluation outcome

        Note:
            Currently uses mock implementation. Replace with actual AI calls
            when integrating with real AI services.
        """
        # Get director profile
        director_profile = get_director_profile(request.director_type)

        # Prepare context
        context = self.prepare_evaluation_context(request, director_profile)

        if self.mock_mode:
            # Mock evaluation
            result = self._mock_evaluation(request, director_profile, context)
        else:
            # Real evaluation (to be implemented)
            result = self._real_evaluation(request, director_profile, context)

        # Save result
        self.save_evaluation_result(result)

        return result

    def _mock_evaluation(self, request: EvaluationRequest,
                        director_profile: DirectorProfile,
                        context: Dict[str, Any]) -> EvaluationResult:
        """
        Generate a mock evaluation result for testing.

        Args:
            request: The evaluation request
            director_profile: The director's profile
            context: Evaluation context

        Returns:
            Mock EvaluationResult
        """
        # Generate mock score based on director characteristics
        base_score = 70.0
        score_variation = (director_profile.risk_tolerance * 10) - 5
        mock_score = base_score + score_variation

        # Generate mock feedback
        mock_feedback = (
            f"As {director_profile.name_en}, I've evaluated this {request.evaluation_type}. "
            f"Based on my focus on {', '.join(director_profile.evaluation_focus[:2])}, "
            f"I find this work to be {'innovative and bold' if director_profile.innovation_focus > 0.7 else 'solid and well-executed'}."
        )

        # Generate mock suggestions
        mock_suggestions = [
            f"Consider enhancing the {director_profile.evaluation_focus[0].lower()}",
            f"Focus more on {director_profile.evaluation_focus[1].lower()}"
        ]

        # Generate mock highlights
        mock_highlights = [
            "Strong conceptual foundation",
            f"Good alignment with {director_profile.evaluation_focus[0].lower()}"
        ]

        # Generate mock concerns
        mock_concerns = []
        if director_profile.commercial_focus > 0.7:
            mock_concerns.append("May need more commercial appeal")
        if director_profile.risk_tolerance < 0.5:
            mock_concerns.append("Some creative choices feel risky")

        return EvaluationResult(
            session_id=request.session_id,
            phase_number=request.phase_number,
            director_type=request.director_type,
            evaluation_type=request.evaluation_type,
            timestamp=get_iso_timestamp(),
            score=mock_score,
            feedback=mock_feedback,
            suggestions=mock_suggestions,
            highlights=mock_highlights,
            concerns=mock_concerns,
            raw_response="[Mock evaluation - no actual AI call made]",
            metadata={'mock': True, 'director_profile': director_profile.name_en}
        )

    def _real_evaluation(self, request: EvaluationRequest,
                        director_profile: DirectorProfile,
                        context: Dict[str, Any]) -> EvaluationResult:
        """
        Execute a real AI evaluation.

        Args:
            request: The evaluation request
            director_profile: The director's profile
            context: Evaluation context

        Returns:
            EvaluationResult from actual AI evaluation

        Note:
            This is a placeholder for real AI integration.
            Implement actual AI calls here when ready.
        """
        # TODO: Implement real AI evaluation
        # This would involve:
        # 1. Loading the appropriate prompt template
        # 2. Formatting the prompt with context
        # 3. Calling the AI service (Claude API, etc.)
        # 4. Parsing the response
        # 5. Extracting score, feedback, suggestions, etc.

        # For now, fall back to mock
        return self._mock_evaluation(request, director_profile, context)

    def save_evaluation_result(self, result: EvaluationResult) -> Path:
        """
        Save an evaluation result to the session directory.

        Args:
            result: The evaluation result to save

        Returns:
            Path to the saved file
        """
        # Get evaluations directory for this session
        eval_dir = get_evaluations_dir(result.session_id)
        ensure_dir(eval_dir)

        # Create filename
        director_name = result.director_type.value if isinstance(result.director_type, DirectorType) else result.director_type
        filename = safe_filename(
            f"phase{result.phase_number}_{director_name}_{result.evaluation_type}.json"
        )

        # Save to file
        output_path = eval_dir / filename
        write_json(str(output_path), result.to_dict())

        return output_path

    def load_evaluation_result(self, session_id: str, phase_number: int,
                               director_type: DirectorType,
                               evaluation_type: str) -> Optional[EvaluationResult]:
        """
        Load a previously saved evaluation result.

        Args:
            session_id: The session identifier
            phase_number: Phase number
            director_type: Type of director
            evaluation_type: Type of evaluation

        Returns:
            EvaluationResult if found, None otherwise
        """
        eval_dir = get_evaluations_dir(session_id)

        director_name = director_type.value
        filename = safe_filename(
            f"phase{phase_number}_{director_name}_{evaluation_type}.json"
        )

        file_path = eval_dir / filename

        if not file_path.exists():
            return None

        data = read_json(str(file_path))

        # Convert director_type string back to enum
        data['director_type'] = DirectorType(data['director_type'])

        return EvaluationResult(**data)

    def get_all_evaluations(self, session_id: str,
                           phase_number: Optional[int] = None) -> List[EvaluationResult]:
        """
        Get all evaluation results for a session.

        Args:
            session_id: The session identifier
            phase_number: Optional phase number to filter by

        Returns:
            List of EvaluationResult objects
        """
        eval_dir = get_evaluations_dir(session_id)

        if not eval_dir.exists():
            return []

        results = []

        # Find all JSON files in the evaluations directory
        for file_path in eval_dir.glob("*.json"):
            try:
                data = read_json(str(file_path))

                # Filter by phase if specified
                if phase_number is not None and data.get('phase_number') != phase_number:
                    continue

                # Convert director_type string back to enum
                if 'director_type' in data and isinstance(data['director_type'], str):
                    data['director_type'] = DirectorType(data['director_type'])

                results.append(EvaluationResult(**data))
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Skip invalid files
                print(f"Warning: Could not load evaluation from {file_path}: {e}")
                continue

        return results

    def aggregate_scores(self, evaluations: List[EvaluationResult],
                        weights: Optional[Dict[DirectorType, float]] = None) -> Dict[str, Any]:
        """
        Aggregate scores from multiple evaluations.

        Args:
            evaluations: List of evaluation results
            weights: Optional weights for each director type

        Returns:
            Dictionary containing aggregated scores and statistics
        """
        if not evaluations:
            return {
                'average_score': 0.0,
                'weighted_score': 0.0,
                'min_score': 0.0,
                'max_score': 0.0,
                'count': 0
            }

        scores = [e.score for e in evaluations]

        # Calculate weighted score if weights provided
        weighted_score = 0.0
        total_weight = 0.0

        if weights:
            for eval_result in evaluations:
                weight = weights.get(eval_result.director_type, 1.0)
                weighted_score += eval_result.score * weight
                total_weight += weight

            if total_weight > 0:
                weighted_score /= total_weight
        else:
            weighted_score = sum(scores) / len(scores)

        return {
            'average_score': sum(scores) / len(scores),
            'weighted_score': weighted_score,
            'min_score': min(scores),
            'max_score': max(scores),
            'count': len(evaluations),
            'by_director': {
                e.director_type.value if isinstance(e.director_type, DirectorType) else e.director_type: e.score
                for e in evaluations
            }
        }
