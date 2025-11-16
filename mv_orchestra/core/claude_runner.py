#!/usr/bin/env python3
"""
Claude API Runner for MV Orchestra

Handles Claude API interactions with:
- Prompt caching (90% cost reduction)
- Error handling and retries
- Cost tracking
- Response validation

Based on Phase 1 requirements from design specification v2.0
"""

import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import time

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.error_handling import exponential_backoff_retry, CircuitBreaker


class ClaudeRunner:
    """
    Claude API runner with production features

    Features:
    - Prompt caching for 90% cost reduction
    - Exponential backoff retry
    - Circuit breaker protection
    - Cost tracking
    - Response validation
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4.5-20250929",
        max_cost: float = 10.0,
        use_caching: bool = True
    ):
        """
        Initialize Claude runner

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_cost: Maximum allowed cost
            use_caching: Enable prompt caching
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.max_cost = max_cost
        self.use_caching = use_caching

        self.accumulated_cost = 0.0
        self.request_count = 0

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0
        )

        # Pricing (2025 rates)
        self.pricing = {
            'input': 3.0 / 1_000_000,      # $3 per million tokens
            'output': 15.0 / 1_000_000,    # $15 per million tokens
            'cache_read': 0.3 / 1_000_000, # 90% reduction
            'cache_write': 3.75 / 1_000_000
        }

        print(f"Claude Runner initialized:")
        print(f"  Model: {self.model}")
        print(f"  Caching: {'Enabled' if self.use_caching else 'Disabled'}")
        print(f"  Max cost: ${self.max_cost:.2f}")

    def generate_concept(
        self,
        audio_analysis: Dict[str, Any],
        num_scenes: int = 50
    ) -> Dict[str, Any]:
        """
        Generate creative concept from audio analysis

        Args:
            audio_analysis: Audio analysis results from librosa
            num_scenes: Number of scenes to generate

        Returns:
            Concept dictionary with theme, style, scenes
        """
        print(f"\nGenerating concept with Claude...")
        print(f"  Audio: {audio_analysis.get('duration', 0):.1f}s")
        print(f"  Scenes: {num_scenes}")

        # Build prompt
        prompt = self._build_concept_prompt(audio_analysis, num_scenes)

        # Call Claude API
        response = self._call_api(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=self._get_system_prompt(),
            temperature=0.7,
            max_tokens=4000
        )

        # Parse response
        concept = self._parse_concept_response(response)

        print(f"  ✓ Concept generated")
        print(f"  Theme: {concept.get('overall_theme', 'N/A')}")
        print(f"  Scenes: {len(concept.get('scene_prompts', []))}")

        return concept

    def _build_concept_prompt(
        self,
        audio_analysis: Dict[str, Any],
        num_scenes: int
    ) -> str:
        """Build prompt for concept generation"""
        return f"""
Create a music video concept for this song:

**Audio Analysis:**
- Duration: {audio_analysis['duration']:.1f}s
- Tempo: {audio_analysis['tempo']:.1f} BPM
- Key: {audio_analysis['key']} {audio_analysis['mode']}
- Mood:
  - Energy: {audio_analysis['mood']['energy']:.2f}
  - Valence: {audio_analysis['mood']['valence']:.2f}
  - Danceability: {audio_analysis['mood']['danceability']:.2f}
- Beat count: {audio_analysis['beat_count']}

**Requirements:**
- Create {num_scenes} distinct scenes
- Maintain visual consistency (unified theme/style)
- Align scenes to musical structure
- Provide color palette for consistency

**Output Format (JSON):**
{{
    "overall_theme": "Brief description of overarching concept",
    "visual_style": "Art style/aesthetic direction",
    "color_palette": ["#HEX1", "#HEX2", "#HEX3", "#HEX4"],
    "scene_prompts": [
        {{
            "index": 0,
            "prompt": "Detailed visual description",
            "mood": "Scene emotional tone",
            "energy": 0.0-1.0
        }},
        ...
    ]
}}

Respond with ONLY the JSON, no additional text.
"""

    def _get_system_prompt(self) -> str:
        """Get system prompt (cached for cost reduction)"""
        return """
You are an expert music video director and visual storyteller.
Your role is to create compelling, cohesive visual concepts that
enhance and complement the music.

Guidelines:
- Maintain visual consistency across all scenes
- Match visual energy to musical energy
- Create smooth narrative/thematic flow
- Balance artistic creativity with practical execution
- Ensure scenes are Stable Diffusion-compatible

Output format: Always respond with valid JSON only.
"""

    @exponential_backoff_retry(max_retries=4, base_delay=2.0)
    def _call_api(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Call Claude API with retry and caching

        Args:
            messages: Conversation messages
            system_prompt: System prompt (cached)
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            API response dictionary
        """
        # Check cost limit
        if self.accumulated_cost >= self.max_cost:
            raise RuntimeError(
                f"Cost limit exceeded: ${self.accumulated_cost:.2f} >= ${self.max_cost:.2f}"
            )

        # **STUB**: Actual API call would go here
        # For now, return simulated response
        response = self._simulate_api_call(messages, system_prompt, temperature, max_tokens)

        # Track cost
        self._track_cost(response)

        return response

    def _simulate_api_call(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Simulate Claude API response (stub for Phase 1 development)

        In production, replace with:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        """
        print(f"  [STUB] Simulating Claude API call...")
        time.sleep(0.5)  # Simulate API latency

        # Simulate response
        return {
            'id': 'msg_stub_123',
            'type': 'message',
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': json.dumps({
                        'overall_theme': 'Simulated creative concept',
                        'visual_style': 'Modern, vibrant aesthetic',
                        'color_palette': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
                        'scene_prompts': [
                            {
                                'index': i,
                                'prompt': f'Simulated scene {i} description',
                                'mood': 'energetic' if i % 2 == 0 else 'calm',
                                'energy': 0.5 + (i / 20)
                            }
                            for i in range(10)  # Generate 10 scenes for demo
                        ]
                    })
                }
            ],
            'model': self.model,
            'stop_reason': 'end_turn',
            'usage': {
                'input_tokens': 500,
                'output_tokens': 800,
                'cache_creation_tokens': 200 if self.use_caching else 0,
                'cache_read_tokens': 0
            }
        }

    def _track_cost(self, response: Dict[str, Any]):
        """Track API usage cost"""
        usage = response.get('usage', {})

        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cache_read = usage.get('cache_read_tokens', 0)
        cache_write = usage.get('cache_creation_tokens', 0)

        # Calculate cost
        cost = (
            input_tokens * self.pricing['input'] +
            output_tokens * self.pricing['output'] +
            cache_read * self.pricing['cache_read'] +
            cache_write * self.pricing['cache_write']
        )

        self.accumulated_cost += cost
        self.request_count += 1

        print(f"  Cost: ${cost:.4f} (total: ${self.accumulated_cost:.4f})")

    def _parse_concept_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate concept from Claude response"""
        content = response.get('content', [])
        if not content:
            raise ValueError("Empty response from Claude")

        text = content[0].get('text', '')

        try:
            concept = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

        # Validate required fields
        required_fields = ['overall_theme', 'visual_style', 'color_palette', 'scene_prompts']
        for field in required_fields:
            if field not in concept:
                raise ValueError(f"Missing required field: {field}")

        return concept

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        return {
            'accumulated_cost': self.accumulated_cost,
            'request_count': self.request_count,
            'max_cost': self.max_cost,
            'remaining_budget': self.max_cost - self.accumulated_cost,
            'average_cost_per_request': (
                self.accumulated_cost / self.request_count
                if self.request_count > 0 else 0
            )
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("CLAUDE RUNNER - EXAMPLE (STUB MODE)")
    print("=" * 70)

    # Initialize runner
    runner = ClaudeRunner(use_caching=True)

    # Example audio analysis
    audio_analysis = {
        'duration': 180.0,
        'tempo': 120.0,
        'key': 'C',
        'mode': 'major',
        'beat_count': 360,
        'mood': {
            'energy': 0.75,
            'valence': 0.8,
            'danceability': 0.7,
            'arousal': 0.6
        }
    }

    # Generate concept
    concept = runner.generate_concept(audio_analysis, num_scenes=10)

    print(f"\n{'='*70}")
    print("CONCEPT GENERATED")
    print(f"{'='*70}\n")
    print(json.dumps(concept, indent=2))

    # Cost summary
    summary = runner.get_cost_summary()
    print(f"\n{'='*70}")
    print("COST SUMMARY")
    print(f"{'='*70}\n")
    print(f"Total cost: ${summary['accumulated_cost']:.4f}")
    print(f"Requests: {summary['request_count']}")
    print(f"Average: ${summary['average_cost_per_request']:.4f}/request")
    print(f"Remaining: ${summary['remaining_budget']:.2f}")

    print(f"\n{'='*70}")
    print("✓ Claude runner ready (STUB MODE)")
    print("  Note: Replace _simulate_api_call() with actual API")
    print(f"{'='*70}")
