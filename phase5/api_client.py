"""
Claude API Client for MV Orchestra v2.8

This module provides a wrapper for Claude API calls,
supporting both real API and mock modes.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ClaudeAPIClient:
    """
    Wrapper for Claude API calls with mock mode support.
    """

    def __init__(self, mock_mode: bool = True, api_key: Optional[str] = None):
        """
        Initialize Claude API client.

        Args:
            mock_mode: Whether to use mock mode (default: True)
            api_key: API key for real mode (optional, reads from env if not provided)
        """
        self.mock_mode = mock_mode
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        # Try to import anthropic SDK if in real mode
        self.client = None
        if not self.mock_mode:
            try:
                import anthropic
                if not self.api_key:
                    raise ValueError(
                        "ANTHROPIC_API_KEY not found in environment. "
                        "Set it or use mock_mode=True"
                    )
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )

    def review_generation_strategy(
        self,
        clip_id: str,
        generation_mode: str,
        prompt: str,
        clip_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ask Claude to review a generation mode selection.

        Args:
            clip_id: Clip identifier
            generation_mode: Selected generation mode
            prompt: Generation prompt
            clip_context: Context about the clip

        Returns:
            Review results
        """
        if self.mock_mode:
            return self._mock_review(clip_id, generation_mode, prompt, clip_context)
        else:
            return self._real_review(clip_id, generation_mode, prompt, clip_context)

    def _mock_review(
        self,
        clip_id: str,
        generation_mode: str,
        prompt: str,
        clip_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mock review response.

        Args:
            clip_id: Clip identifier
            generation_mode: Selected generation mode
            prompt: Generation prompt
            clip_context: Context about the clip

        Returns:
            Mock review results
        """
        # Generate deterministic but varied mock responses
        clip_hash = hash(clip_id) % 100

        # Most clips get good scores
        if clip_hash < 70:
            score = 7.5 + (clip_hash % 20) / 10.0
            feedback = f"The {generation_mode} mode is appropriate for this {clip_context.get('clip_type', 'clip')}. The prompt is well-structured and should produce good results."
            suggested_alternative = None
            adjustment_made = False
        # Some clips get suggestions
        elif clip_hash < 90:
            score = 6.0 + (clip_hash % 15) / 10.0
            feedback = f"While {generation_mode} can work, consider the alternative for better results given the clip requirements."
            # Suggest different modes based on context
            if generation_mode == "sora":
                suggested_alternative = "veo2"
            elif generation_mode == "veo2":
                suggested_alternative = "runway_gen3"
            else:
                suggested_alternative = "hybrid"
            adjustment_made = False
        # Few clips need adjustment
        else:
            score = 5.0 + (clip_hash % 10) / 10.0
            feedback = f"The current mode may not be optimal. Recommend switching to a more suitable approach."
            suggested_alternative = "traditional" if clip_context.get('clip_type') == 'performance' else "hybrid"
            adjustment_made = True

        return {
            'clip_id': clip_id,
            'original_mode': generation_mode,
            'prompt_reviewed': prompt[:100] + "..." if len(prompt) > 100 else prompt,
            'claude_feedback': feedback,
            'claude_score': score,
            'suggested_alternative': suggested_alternative,
            'adjustment_made': adjustment_made,
            'review_timestamp': datetime.utcnow().isoformat() + 'Z',
            'mock_mode': True
        }

    def _real_review(
        self,
        clip_id: str,
        generation_mode: str,
        prompt: str,
        clip_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get real Claude API review.

        Args:
            clip_id: Clip identifier
            generation_mode: Selected generation mode
            prompt: Generation prompt
            clip_context: Context about the clip

        Returns:
            Real review results
        """
        # Build review prompt
        review_prompt = f"""You are reviewing a video generation strategy for a music video clip.

Clip ID: {clip_id}
Clip Type: {clip_context.get('clip_type', 'unknown')}
Duration: {clip_context.get('duration', 0)} seconds
Description: {clip_context.get('description', 'N/A')}

Selected Generation Mode: {generation_mode}
Generation Prompt: {prompt}

Please evaluate:
1. Is the selected generation mode appropriate for this clip?
2. Is the prompt well-structured and likely to produce good results?
3. Are there any concerns or suggestions for improvement?

Respond in JSON format:
{{
    "score": <float 0-10>,
    "feedback": "<brief feedback>",
    "suggested_alternative": "<mode name or null>",
    "concerns": ["<concern 1>", ...],
    "suggestions": ["<suggestion 1>", ...]
}}
"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": review_prompt
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Try to extract JSON
            try:
                # Look for JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback to basic parsing
                    result = {'score': 7.0, 'feedback': response_text}
            except json.JSONDecodeError:
                result = {'score': 7.0, 'feedback': response_text}

            return {
                'clip_id': clip_id,
                'original_mode': generation_mode,
                'prompt_reviewed': prompt[:100] + "..." if len(prompt) > 100 else prompt,
                'claude_feedback': result.get('feedback', ''),
                'claude_score': result.get('score', 7.0),
                'suggested_alternative': result.get('suggested_alternative'),
                'concerns': result.get('concerns', []),
                'suggestions': result.get('suggestions', []),
                'adjustment_made': False,
                'review_timestamp': datetime.utcnow().isoformat() + 'Z',
                'mock_mode': False,
                'api_usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
            }

        except Exception as e:
            # Return error result
            return {
                'clip_id': clip_id,
                'original_mode': generation_mode,
                'error': str(e),
                'claude_score': 0.0,
                'review_timestamp': datetime.utcnow().isoformat() + 'Z',
                'mock_mode': False
            }

    def estimate_cost(self, num_clips: int, tokens_per_clip: int = 500) -> Dict[str, Any]:
        """
        Estimate cost for reviewing clips.

        Args:
            num_clips: Number of clips to review
            tokens_per_clip: Average tokens per clip review

        Returns:
            Cost estimation
        """
        # Claude Sonnet 4.5 pricing (approximate)
        # Input: $3 per million tokens
        # Output: $15 per million tokens

        input_tokens = num_clips * tokens_per_clip
        output_tokens = num_clips * 300  # Estimated response tokens

        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost

        return {
            'num_clips': num_clips,
            'estimated_input_tokens': input_tokens,
            'estimated_output_tokens': output_tokens,
            'estimated_input_cost_usd': round(input_cost, 2),
            'estimated_output_cost_usd': round(output_cost, 2),
            'estimated_total_cost_usd': round(total_cost, 2)
        }

    def batch_review(
        self,
        clips_with_strategies: List[Dict[str, Any]],
        max_clips: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Review multiple clips in batch.

        Args:
            clips_with_strategies: List of clip strategies to review
            max_clips: Maximum number of clips to review (for cost control)

        Returns:
            List of review results
        """
        if max_clips:
            clips_with_strategies = clips_with_strategies[:max_clips]

        reviews = []
        for i, clip_strategy in enumerate(clips_with_strategies, 1):
            print(f"      Reviewing clip {i}/{len(clips_with_strategies)}: {clip_strategy.get('clip_id', 'unknown')}...", end=" ")

            review = self.review_generation_strategy(
                clip_id=clip_strategy.get('clip_id', ''),
                generation_mode=clip_strategy.get('generation_mode', ''),
                prompt=clip_strategy.get('prompt_template', {}).get('full_prompt', ''),
                clip_context={
                    'clip_type': clip_strategy.get('clip_type', ''),
                    'duration': clip_strategy.get('duration', 0),
                    'description': clip_strategy.get('description', '')
                }
            )

            reviews.append(review)
            print(f"Score: {review.get('claude_score', 0):.1f}/10")

        return reviews


def create_client(mode: str = "mock") -> ClaudeAPIClient:
    """
    Create a Claude API client.

    Args:
        mode: "mock", "real", or "skip"

    Returns:
        ClaudeAPIClient instance or None if skipped

    Raises:
        ValueError: If mode is invalid
    """
    if mode == "mock":
        return ClaudeAPIClient(mock_mode=True)
    elif mode == "real":
        return ClaudeAPIClient(mock_mode=False)
    elif mode == "skip":
        return None
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'mock', 'real', or 'skip'")
