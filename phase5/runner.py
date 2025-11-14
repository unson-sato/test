"""
Phase 5: Real Claude Review (Optional) Runner

This module implements the optional Claude API review phase
where real Claude evaluates the generation strategies.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from core import (
    SharedState,
    get_iso_timestamp
)
from .api_client import ClaudeAPIClient, create_client


class Phase5Runner:
    """
    Runner for Phase 5: Real Claude Review (Optional).

    This phase uses real Claude API to review and potentially
    refine generation mode selections.
    """

    def __init__(self, session_id: str, mode: str = "mock"):
        """
        Initialize Phase 5 runner.

        Args:
            session_id: Session identifier
            mode: "mock", "real", or "skip"
        """
        self.session_id = session_id
        self.mode = mode
        self.session = SharedState.load_session(session_id)

        # Create API client (or None if skipped)
        self.client = create_client(mode)

        # Load Phase 4 data
        self.phase4_data = self.session.get_phase_data(4).data

    def run(
        self,
        max_clips_to_review: Optional[int] = None,
        adjustment_threshold: float = 6.5
    ) -> Dict[str, Any]:
        """
        Execute Phase 5: Real Claude Review.

        Args:
            max_clips_to_review: Maximum number of clips to review (for cost control)
            adjustment_threshold: Score below which adjustments are considered

        Returns:
            Phase 5 results including reviews and any adjustments
        """
        print(f"\n{'='*60}")
        print("Phase 5: Real Claude Review (Optional)")
        print(f"{'='*60}")
        print(f"Session ID: {self.session_id}")
        print(f"Mode: {self.mode.upper()}")

        # Check if skipped
        if self.mode == "skip" or self.client is None:
            print("\nPhase 5 skipped (disabled in config or explicitly skipped)")
            results = {
                'phase': 5,
                'phase_name': 'Real Claude Review (Optional)',
                'timestamp': get_iso_timestamp(),
                'skipped': True,
                'reason': 'Phase 5 disabled or explicitly skipped'
            }
            self.session.set_phase_data(5, results)
            self.session.complete_phase(5)
            return results

        # Mark phase as started
        self.session.start_phase(5)

        try:
            # Step 1: Extract winning strategy from Phase 4
            print("\n[1/5] Loading Phase 4 winner's generation strategy...")
            winning_strategy = self._get_winning_strategy()
            total_clips = len(winning_strategy.get('generation_strategies', []))
            print(f"      Found {total_clips} clips to review")

            # Step 2: Estimate cost (if real mode)
            if self.mode == "real":
                print("\n[2/5] Estimating API cost...")
                cost_estimate = self.client.estimate_cost(
                    num_clips=min(max_clips_to_review or total_clips, total_clips)
                )
                print(f"      Estimated cost: ${cost_estimate['estimated_total_cost_usd']:.2f} USD")
                print(f"      Input tokens: ~{cost_estimate['estimated_input_tokens']}")
                print(f"      Output tokens: ~{cost_estimate['estimated_output_tokens']}")

                # In real implementation, could ask for user confirmation here
                # For now, we proceed
            else:
                cost_estimate = {'estimated_total_cost_usd': 0.0}

            # Step 3: Review clips
            print(f"\n[3/5] Reviewing generation strategies with Claude...")
            reviews = self._review_strategies(
                winning_strategy['generation_strategies'],
                max_clips=max_clips_to_review
            )
            print(f"      Completed {len(reviews)} reviews")

            # Step 4: Analyze reviews and make adjustments
            print(f"\n[4/5] Analyzing reviews and making adjustments...")
            adjustments = self._analyze_and_adjust(
                reviews,
                winning_strategy,
                threshold=adjustment_threshold
            )
            print(f"      Adjustments made: {len(adjustments)}")

            # Step 5: Save results
            print("\n[5/5] Saving Phase 5 results...")
            results = {
                'phase': 5,
                'phase_name': 'Real Claude Review (Optional)',
                'timestamp': get_iso_timestamp(),
                'skipped': False,
                'mode': self.mode,
                'review_conducted': True,
                'api_provider': 'anthropic',
                'model': 'claude-sonnet-4-5-20250929',
                'reviews': reviews,
                'summary': self._create_summary(reviews),
                'adjustments': adjustments,
                'final_strategy': self._apply_adjustments(winning_strategy, adjustments),
                'cost_estimate': cost_estimate
            }

            self.session.set_phase_data(5, results)
            self.session.complete_phase(5)

            print("\n" + "="*60)
            print("Phase 5 completed successfully!")
            print("="*60)

            return results

        except Exception as e:
            print(f"\nError in Phase 5: {e}")
            self.session.fail_phase(5, {'error': str(e)})
            raise

    def _get_winning_strategy(self) -> Dict[str, Any]:
        """
        Get winning strategy from Phase 4.

        Returns:
            Winning proposal dictionary
        """
        if 'winner' in self.phase4_data and 'proposal' in self.phase4_data['winner']:
            return self.phase4_data['winner']['proposal']
        else:
            raise ValueError("No winner found in Phase 4 data")

    def _review_strategies(
        self,
        strategies: List[Dict[str, Any]],
        max_clips: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Review generation strategies with Claude.

        Args:
            strategies: List of generation strategies
            max_clips: Maximum clips to review

        Returns:
            List of review results
        """
        if max_clips:
            strategies = strategies[:max_clips]

        return self.client.batch_review(strategies, max_clips=None)

    def _analyze_and_adjust(
        self,
        reviews: List[Dict[str, Any]],
        winning_strategy: Dict[str, Any],
        threshold: float = 6.5
    ) -> List[Dict[str, Any]]:
        """
        Analyze reviews and determine adjustments.

        Args:
            reviews: List of review results
            winning_strategy: Winning generation strategy
            threshold: Score threshold for making adjustments

        Returns:
            List of adjustments made
        """
        adjustments = []

        for review in reviews:
            score = review.get('claude_score', 0)
            clip_id = review.get('clip_id', '')
            suggested_alt = review.get('suggested_alternative')

            # Make adjustment if score is below threshold and there's a suggestion
            if score < threshold and suggested_alt:
                adjustments.append({
                    'clip_id': clip_id,
                    'original_mode': review.get('original_mode', ''),
                    'new_mode': suggested_alt,
                    'reason': review.get('claude_feedback', ''),
                    'original_score': score,
                    'timestamp': get_iso_timestamp()
                })

        return adjustments

    def _apply_adjustments(
        self,
        winning_strategy: Dict[str, Any],
        adjustments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply adjustments to winning strategy.

        Args:
            winning_strategy: Original winning strategy
            adjustments: List of adjustments

        Returns:
            Updated strategy
        """
        # Deep copy the strategy
        import copy
        updated_strategy = copy.deepcopy(winning_strategy)

        # Create adjustment map
        adjustment_map = {adj['clip_id']: adj for adj in adjustments}

        # Apply adjustments
        for strategy in updated_strategy.get('generation_strategies', []):
            clip_id = strategy.get('clip_id', '')
            if clip_id in adjustment_map:
                adj = adjustment_map[clip_id]
                strategy['generation_mode'] = adj['new_mode']
                strategy['adjusted_by_claude'] = True
                strategy['adjustment_reason'] = adj['reason']

        # Update summary
        updated_strategy['phase5_adjustments'] = len(adjustments)
        updated_strategy['phase5_reviewed'] = True

        return updated_strategy

    def _create_summary(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary of reviews.

        Args:
            reviews: List of review results

        Returns:
            Summary dictionary
        """
        if not reviews:
            return {
                'total_clips_reviewed': 0,
                'average_score': 0.0,
                'min_score': 0.0,
                'max_score': 0.0
            }

        scores = [r.get('claude_score', 0) for r in reviews]
        suggestions = sum(1 for r in reviews if r.get('suggested_alternative'))

        # Calculate cost if real mode
        if self.mode == "real":
            total_input_tokens = sum(
                r.get('api_usage', {}).get('input_tokens', 0)
                for r in reviews
            )
            total_output_tokens = sum(
                r.get('api_usage', {}).get('output_tokens', 0)
                for r in reviews
            )
            input_cost = (total_input_tokens / 1_000_000) * 3.0
            output_cost = (total_output_tokens / 1_000_000) * 15.0
            actual_cost = input_cost + output_cost
        else:
            total_input_tokens = 0
            total_output_tokens = 0
            actual_cost = 0.0

        return {
            'total_clips_reviewed': len(reviews),
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'min_score': min(scores) if scores else 0.0,
            'max_score': max(scores) if scores else 0.0,
            'clips_with_suggestions': suggestions,
            'mode': self.mode,
            'actual_cost_usd': round(actual_cost, 2) if self.mode == "real" else None,
            'total_input_tokens': total_input_tokens if self.mode == "real" else None,
            'total_output_tokens': total_output_tokens if self.mode == "real" else None
        }


def run_phase5(
    session_id: str,
    mode: str = "mock",
    max_clips: Optional[int] = None,
    adjustment_threshold: float = 6.5
) -> Dict[str, Any]:
    """
    Run Phase 5 for a session.

    Args:
        session_id: Session identifier
        mode: "mock", "real", or "skip"
        max_clips: Maximum clips to review (for cost control)
        adjustment_threshold: Score threshold for adjustments

    Returns:
        Phase 5 results
    """
    runner = Phase5Runner(session_id, mode=mode)
    return runner.run(
        max_clips_to_review=max_clips,
        adjustment_threshold=adjustment_threshold
    )
