"""
Evaluation Agent for MV Orchestra v3.0

Evaluates director submissions and selects the winner.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .utils import get_project_root, get_iso_timestamp


logger = logging.getLogger(__name__)


@dataclass
class SelectionResult:
    """Result of evaluation and winner selection"""

    winner_name: str
    winner_output: Dict[str, Any]
    scores: Dict[str, float]
    reasoning: str
    partial_adoptions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=get_iso_timestamp)


class EvaluationAgent:
    """
    Evaluates director submissions and selects winner.

    Uses a dedicated evaluation prompt for each phase to:
    - Score all submissions objectively
    - Select the best submission
    - Identify valuable features in non-winning submissions
    - Recommend partial adoptions
    """

    def __init__(self, claude_cli: str = "claude"):
        """
        Initialize Evaluation Agent.

        Args:
            claude_cli: Path to Claude CLI executable
        """
        self.claude_cli = claude_cli
        logger.info("EvaluationAgent initialized")

    async def evaluate_and_select(
        self,
        phase_num: int,
        submissions: List[Dict[str, Any]],
        context: Dict[str, Any],
        output_dir: Path,
    ) -> SelectionResult:
        """
        Evaluate all submissions and select winner.

        Args:
            phase_num: Phase number (1-4)
            submissions: List of director submissions
            context: Context data for evaluation
            output_dir: Output directory

        Returns:
            SelectionResult
        """
        logger.info(f"Evaluating {len(submissions)} submissions for Phase {phase_num}...")

        # Get evaluation prompt
        project_root = get_project_root()
        prompt_file = project_root / ".claude" / "prompts" / f"phase{phase_num}_evaluation.md"

        if not prompt_file.exists():
            logger.warning(f"Evaluation prompt not found: {prompt_file}")
            # Fallback to simple scoring
            return self._fallback_evaluation(submissions)

        # Build evaluation context
        eval_context = {**context, "submissions": submissions, "phase": phase_num}

        # Create context file
        output_dir.mkdir(parents=True, exist_ok=True)
        context_file = output_dir / "evaluation_context.json"

        with open(context_file, "w") as f:
            json.dump(eval_context, f, indent=2)

        # Build Claude CLI command
        cmd = [
            self.claude_cli,
            "-p",
            str(prompt_file),
            "--dangerous-skip-permission",
            "--output-format",
            "json",
        ]

        logger.debug(f"Running evaluation: {' '.join(cmd)}")

        try:
            # Run evaluation
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Pass context as stdin
            context_json = json.dumps(eval_context).encode()
            stdout, stderr = await process.communicate(input=context_json)

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Evaluation failed: {error_msg}")
                return self._fallback_evaluation(submissions)

            # Parse output
            output_str = stdout.decode()
            try:
                eval_output = json.loads(output_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse evaluation output")
                # Try to extract JSON
                import re

                json_match = re.search(r"\{.*\}", output_str, re.DOTALL)
                if json_match:
                    try:
                        eval_output = json.loads(json_match.group())
                    except (json.JSONDecodeError, ValueError):
                        return self._fallback_evaluation(submissions)
                else:
                    return self._fallback_evaluation(submissions)

            # Parse selection result
            result = self._parse_evaluation_output(eval_output, submissions)

            logger.info("✓ Evaluation complete")
            logger.info(f"  Winner: {result.winner_name}")
            logger.info(f"  Scores: {result.scores}")

            return result

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return self._fallback_evaluation(submissions)

    def _parse_evaluation_output(
        self, eval_output: Dict[str, Any], submissions: List[Dict[str, Any]]
    ) -> SelectionResult:
        """
        Parse evaluation output into SelectionResult.

        Args:
            eval_output: Evaluation agent output
            submissions: Original submissions

        Returns:
            SelectionResult
        """
        winner_name = eval_output.get("winner", "")
        scores = eval_output.get("scores", {})
        reasoning = eval_output.get("reasoning", "")
        partial_adoptions = eval_output.get("partial_adoptions", [])

        # Find winner submission
        winner_output = None
        for submission in submissions:
            director_type = submission.get("director_type", "")
            if director_type.lower() in winner_name.lower():
                winner_output = submission.get("output", {})
                break

        if not winner_output:
            # Fallback to first submission
            logger.warning(f"Winner '{winner_name}' not found, using first submission")
            if submissions:
                winner_output = submissions[0].get("output", {})
                winner_name = submissions[0].get("director_type", "unknown")
            else:
                winner_output = {}

        return SelectionResult(
            winner_name=winner_name,
            winner_output=winner_output or {},
            scores=scores,
            reasoning=reasoning,
            partial_adoptions=partial_adoptions,
        )

    def _fallback_evaluation(self, submissions: List[Dict[str, Any]]) -> SelectionResult:
        """
        Fallback evaluation using simple scoring.

        Args:
            submissions: List of submissions

        Returns:
            SelectionResult
        """
        logger.info("Using fallback evaluation (simple scoring)")

        if not submissions:
            return SelectionResult(
                winner_name="none",
                winner_output={},
                scores={},
                reasoning="No submissions to evaluate",
            )

        # Simple scoring: prefer successful submissions, then first one
        successful_submissions = [s for s in submissions if s.get("success", False)]

        if successful_submissions:
            winner = successful_submissions[0]
        else:
            winner = submissions[0]

        winner_name = winner.get("director_type", "unknown")
        winner_output = winner.get("output", {})

        # Create simple scores
        scores = {}
        for submission in submissions:
            director_type = submission.get("director_type", "unknown")
            success = submission.get("success", False)
            scores[director_type] = 80.0 if success else 40.0

        # Give winner higher score
        scores[winner_name] = 85.0

        return SelectionResult(
            winner_name=winner_name,
            winner_output=winner_output,
            scores=scores,
            reasoning=f"Fallback evaluation: selected {winner_name}",
        )

    def calculate_score(self, result: SelectionResult) -> float:
        """
        Calculate overall score from evaluation result.

        Args:
            result: Selection result

        Returns:
            Overall score (0-100)
        """
        if not result.scores:
            return 50.0  # Default score

        winner_score = result.scores.get(result.winner_name, 50.0)
        return winner_score
