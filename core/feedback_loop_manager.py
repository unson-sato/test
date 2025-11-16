"""
Feedback Loop Manager for MV Orchestra v3.0

Manages iterative improvement cycles with agent feedback.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .agent_executor import AgentExecutor, AgentResult
from .evaluation_agent import EvaluationAgent, SelectionResult
from .utils import get_iso_timestamp


logger = logging.getLogger(__name__)


@dataclass
class IterationResult:
    """Result of a single iteration"""

    iteration_num: int
    agent_results: List[AgentResult]
    evaluation: SelectionResult
    score: float
    improvement: float = 0.0
    timestamp: str = field(default_factory=get_iso_timestamp)


@dataclass
class FeedbackLoopResult:
    """Result of complete feedback loop"""

    winner_name: str
    final_result: Dict[str, Any]
    final_score: float
    iteration_count: int
    total_improvement: float
    iterations: List[IterationResult]
    timestamp: str = field(default_factory=get_iso_timestamp)


class FeedbackLoopManager:
    """
    Manages iterative improvement cycles.

    Process:
    1. Run all agents in parallel
    2. Evaluate and select winner
    3. If score < threshold and iterations < max:
        - Generate feedback from evaluation
        - Add feedback to context
        - Go to step 1
    4. Return final winner
    """

    def __init__(
        self,
        agent_executor: AgentExecutor,
        evaluation_agent: EvaluationAgent,
        quality_threshold: float = 70.0,
        max_iterations: int = 3,
    ):
        """
        Initialize Feedback Loop Manager.

        Args:
            agent_executor: Agent executor instance
            evaluation_agent: Evaluation agent instance
            quality_threshold: Minimum quality score (0-100)
            max_iterations: Maximum feedback iterations
        """
        self.agent_executor = agent_executor
        self.evaluation_agent = evaluation_agent
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations

        logger.info(
            f"FeedbackLoopManager initialized: threshold={quality_threshold}, max_iter={max_iterations}"
        )

    async def run_with_feedback(
        self, phase_num: int, initial_context: Dict[str, Any], output_dir: Path
    ) -> FeedbackLoopResult:
        """
        Run agents with feedback loop until quality threshold met.

        Args:
            phase_num: Phase number (1-4)
            initial_context: Initial context data
            output_dir: Output directory

        Returns:
            FeedbackLoopResult
        """
        logger.info(f"Starting feedback loop for Phase {phase_num}")
        logger.info(f"  Quality threshold: {self.quality_threshold}")
        logger.info(f"  Max iterations: {self.max_iterations}")

        context = initial_context.copy()
        iterations = []
        previous_score = 0.0

        for iteration_num in range(1, self.max_iterations + 1):
            logger.info(f"\n{'─' * 60}")
            logger.info(f"ITERATION {iteration_num}/{self.max_iterations}")
            logger.info(f"{'─' * 60}")

            # Create iteration output directory
            iter_dir = output_dir / f"iteration_{iteration_num}"
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Run all agents in parallel
            logger.info("Step 1: Running agents in parallel...")
            agent_results = await self.agent_executor.run_all_directors_parallel(
                phase_num=phase_num, context=context, output_dir=iter_dir
            )

            # Check if any agents succeeded
            successful_results = [r for r in agent_results if r.success]
            if not successful_results:
                logger.error("No successful agent results, aborting feedback loop")
                break

            # Prepare submissions for evaluation
            submissions = [
                {
                    "director_type": r.director_type,
                    "success": r.success,
                    "output": r.output,
                    "execution_time": r.execution_time,
                }
                for r in agent_results
            ]

            # Step 2: Evaluate and select winner
            logger.info("\nStep 2: Evaluating submissions...")
            evaluation = await self.evaluation_agent.evaluate_and_select(
                phase_num=phase_num, submissions=submissions, context=context, output_dir=iter_dir
            )

            # Calculate score
            score = self.evaluation_agent.calculate_score(evaluation)
            improvement = score - previous_score

            logger.info(f"\nIteration {iteration_num} results:")
            logger.info(f"  Winner: {evaluation.winner_name}")
            logger.info(f"  Score: {score:.1f}/100")
            logger.info(f"  Improvement: {'+' if improvement >= 0 else ''}{improvement:.1f}")

            # Record iteration
            iteration_result = IterationResult(
                iteration_num=iteration_num,
                agent_results=agent_results,
                evaluation=evaluation,
                score=score,
                improvement=improvement,
            )
            iterations.append(iteration_result)

            # Step 3: Check if threshold met
            if score >= self.quality_threshold:
                logger.info(f"\n✓ Quality threshold met ({score:.1f} >= {self.quality_threshold})")
                break

            # Step 4: Generate feedback and continue (if not last iteration)
            if iteration_num < self.max_iterations:
                logger.info("\n⟲ Score below threshold, generating feedback for next iteration...")
                feedback = self._generate_feedback(evaluation, score)
                context = self._update_context_with_feedback(context, feedback, iteration_result)
                previous_score = score
            else:
                logger.info("\n⚠ Max iterations reached ({})".format(self.max_iterations))

        # Final result
        final_iteration = iterations[-1] if iterations else None

        if not final_iteration:
            raise RuntimeError("No successful iterations")

        total_improvement = final_iteration.score - (
            iterations[0].score if len(iterations) > 1 else 0
        )

        result = FeedbackLoopResult(
            winner_name=final_iteration.evaluation.winner_name,
            final_result=final_iteration.evaluation.winner_output,
            final_score=final_iteration.score,
            iteration_count=len(iterations),
            total_improvement=total_improvement,
            iterations=iterations,
        )

        logger.info("\n" + "═" * 60)
        logger.info("FEEDBACK LOOP COMPLETE")
        logger.info("═" * 60)
        logger.info(f"Final winner: {result.winner_name}")
        logger.info(f"Final score: {result.final_score:.1f}/100")
        logger.info(f"Iterations: {result.iteration_count}")
        logger.info(f"Total improvement: +{result.total_improvement:.1f}")

        return result

    def _generate_feedback(self, evaluation: SelectionResult, score: float) -> Dict[str, Any]:
        """
        Generate feedback from evaluation result.

        Args:
            evaluation: Evaluation result
            score: Current score

        Returns:
            Feedback dictionary
        """
        feedback: Dict[str, Any] = {
            "previous_winner": evaluation.winner_name,
            "previous_score": score,
            "evaluation_reasoning": evaluation.reasoning,
            "areas_to_improve": [],
            "partial_adoptions": evaluation.partial_adoptions,
        }

        # Analyze scores to identify improvement areas
        if evaluation.scores:
            max_score = max(evaluation.scores.values())

            areas_to_improve = feedback["areas_to_improve"]
            if isinstance(areas_to_improve, list):
                if score < 60:
                    areas_to_improve.append("Overall quality needs significant improvement")
                elif score < self.quality_threshold:
                    areas_to_improve.append(f"Score needs to reach {self.quality_threshold}")

                if max_score - score > 10:
                    areas_to_improve.append(
                        "Consider incorporating strengths from other submissions"
                    )

        # Add specific improvement suggestions
        if evaluation.partial_adoptions:
            feedback["suggestions"] = [
                f"Consider adopting {adoption.get('feature', 'feature')} from {adoption.get('from', 'other submission')}"
                for adoption in evaluation.partial_adoptions
            ]

        return feedback

    def _update_context_with_feedback(
        self, context: Dict[str, Any], feedback: Dict[str, Any], iteration_result: IterationResult
    ) -> Dict[str, Any]:
        """
        Update context with feedback for next iteration.

        Args:
            context: Current context
            feedback: Generated feedback
            iteration_result: Current iteration result

        Returns:
            Updated context
        """
        updated_context = context.copy()

        # Add feedback history
        if "feedback_history" not in updated_context:
            updated_context["feedback_history"] = []

        updated_context["feedback_history"].append(
            {
                "iteration": iteration_result.iteration_num,
                "feedback": feedback,
                "score": iteration_result.score,
            }
        )

        # Add latest feedback
        updated_context["feedback"] = feedback

        return updated_context
