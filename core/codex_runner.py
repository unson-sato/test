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
        Execute a real AI evaluation using Claude API.

        Args:
            request: The evaluation request
            director_profile: The director's profile
            context: Evaluation context

        Returns:
            EvaluationResult from actual AI evaluation

        Note:
            Falls back to mock evaluation if any errors occur.
        """
        try:
            # 1. Load prompt template
            template_path = self._get_prompt_template_path(director_profile.director_type)
            prompt_template = self._load_prompt_template(template_path)

            # 2. Format prompt with context
            formatted_prompt = self._format_prompt(prompt_template, request, context)

            # 3. Call Claude API
            response = self._call_claude_api(formatted_prompt)

            # 4. Parse response
            evaluation_data = self._parse_evaluation_response(response)

            # 5. Create EvaluationResult
            return EvaluationResult(
                session_id=request.session_id,
                phase_number=request.phase_number,
                director_type=request.director_type,
                evaluation_type=request.evaluation_type,
                timestamp=get_iso_timestamp(),
                score=evaluation_data['score'],
                feedback=evaluation_data['feedback'],
                suggestions=evaluation_data['suggestions'],
                highlights=evaluation_data.get('highlights', []),
                concerns=evaluation_data.get('concerns', []),
                raw_response=response,
                metadata={'real_ai': True, 'director_profile': director_profile.name_en}
            )

        except Exception as e:
            # Log error and fall back to mock
            print(f"⚠ Real evaluation failed: {e}. Falling back to mock.")
            return self._mock_evaluation(request, director_profile, context)

    def _get_prompt_template_path(self, director_type: DirectorType) -> Path:
        """Get path to evaluation prompt template for this director."""
        base_dir = self.project_root / ".claude" / "prompts_v2"
        filename = f"evaluation_{director_type.value}.md"
        return base_dir / filename

    def _load_prompt_template(self, template_path: Path) -> str:
        """Load prompt template from file."""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text(encoding='utf-8')

    def _format_prompt(self, template: str, request: EvaluationRequest,
                      context: Dict[str, Any]) -> str:
        """
        Format prompt template with evaluation context.

        The prompt should include:
        - Director profile information
        - Phase context (previous phase results)
        - Proposals to evaluate
        - Expected output format
        """
        # Build evaluation context
        eval_context = {
            'director_name': context['director']['name_en'],
            'director_name_ja': context['director']['name_ja'],
            'phase_number': request.phase_number,
            'evaluation_type': request.evaluation_type,
            'proposals': request.context.get('proposals', []),
            'previous_phases': request.context.get('previous_phases', {}),
        }

        # Format the template
        # The template already contains evaluation criteria and format
        # We append the specific evaluation context
        formatted = template + "\n\n" + "="*70 + "\n"
        formatted += "## EVALUATION TASK\n\n"
        formatted += f"**Phase**: {request.phase_number}\n"
        formatted += f"**Evaluation Type**: {request.evaluation_type}\n\n"

        formatted += "### Proposals to Evaluate\n\n"
        if eval_context['proposals']:
            formatted += "```json\n"
            formatted += json.dumps(eval_context['proposals'], indent=2, ensure_ascii=False)
            formatted += "\n```\n\n"
        else:
            formatted += "*No proposals provided*\n\n"

        formatted += "### Your Task\n\n"
        formatted += "Please evaluate the proposal(s) above using your evaluation criteria.\n"
        formatted += "Return your response in the JSON format specified in the template above.\n\n"
        formatted += "**Important**: Your response must be valid JSON matching the Output Format section.\n"
        formatted += "Calculate the total_score by summing all weighted_scores from each criterion.\n"

        return formatted

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API with the formatted prompt.

        Requires ANTHROPIC_API_KEY environment variable.
        """
        import os

        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Set it with: export ANTHROPIC_API_KEY='your-key'"
            )

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install it with: pip install anthropic"
            )

        # Create client
        client = anthropic.Anthropic(api_key=api_key)

        # Call API
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Latest model
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response text
        return message.content[0].text

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's response to extract evaluation data.

        Expected format:
        {
          "total_score": 6.5,
          "recommendation": "NEEDS REVISION",
          "summary": "...",
          "what_works": [...],
          "what_needs_work": [...],
          "honest_feedback": [...]
        }
        """
        import re

        # Try to extract JSON from response
        # Claude might wrap it in markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in Claude's response")

        # Parse JSON
        data = json.loads(json_str)

        # Extract evaluation data
        # The format uses total_score, summary, what_works, what_needs_work, honest_feedback
        score = float(data.get('total_score', 7.0)) * 10  # Convert to 0-100 scale

        # Build feedback from summary and honest_feedback
        feedback_parts = []
        if 'summary' in data:
            feedback_parts.append(data['summary'])
        if 'honest_feedback' in data and data['honest_feedback']:
            feedback_parts.append("\n\nHonest Feedback:")
            feedback_parts.extend([f"- {item}" for item in data['honest_feedback']])

        feedback = "\n".join(feedback_parts) if feedback_parts else "No feedback provided"

        # Extract suggestions from what_needs_work
        suggestions = data.get('what_needs_work', [])
        if not suggestions and 'honest_feedback' in data:
            suggestions = data.get('honest_feedback', [])

        # Extract highlights from what_works
        highlights = data.get('what_works', [])

        # Concerns would be critical items from what_needs_work
        concerns = []
        if 'what_needs_work' in data and len(data['what_needs_work']) > 0:
            # Take first 2-3 most critical items as concerns
            concerns = data['what_needs_work'][:3]

        return {
            'score': min(max(score, 0.0), 100.0),  # Clamp to 0-100
            'feedback': feedback,
            'suggestions': suggestions,
            'highlights': highlights,
            'concerns': concerns
        }

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
