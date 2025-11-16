"""
AI Integration module for shot list generation
Supports multiple AI providers: Anthropic Claude, OpenAI GPT
"""

import os
import json
from typing import List, Optional, Dict, Any
from dataclasses import asdict


class AIProvider:
    """Base class for AI providers"""

    def generate_shot_list(self, prompt: str) -> str:
        """Generate shot list from prompt. Returns JSON string."""
        raise NotImplementedError


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate_shot_list(self, prompt: str) -> str:
        """Generate shot list using Claude API"""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the response text
            response_text = message.content[0].text

            # Try to extract JSON from the response
            # Look for JSON array pattern
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)

            if json_match:
                return json_match.group(0)
            else:
                # If no JSON array found, return the whole response
                # (might need manual parsing)
                return response_text

        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")


class OpenAIProvider(AIProvider):
    """OpenAI GPT API provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate_shot_list(self, prompt: str) -> str:
        """Generate shot list using OpenAI API"""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )

        openai.api_key = self.api_key

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert music video director and cinematographer."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=8000,
                temperature=0.7
            )

            response_text = response.choices[0].message.content

            # Try to extract JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)

            if json_match:
                return json_match.group(0)
            else:
                return response_text

        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")


class MockAIProvider(AIProvider):
    """Mock AI provider for testing without API calls"""

    def generate_shot_list(self, prompt: str) -> str:
        """Return a mock shot list"""
        mock_shots = [
            {
                "shot_number": 1,
                "section": "intro",
                "duration_seconds": 5.0,
                "shot_size": "extreme_wide_shot",
                "lens_type": "wide",
                "camera_movement": "drone_aerial",
                "composition": "rule_of_thirds",
                "lighting": "blue_hour_melancholy",
                "emotional_tone": "mysterious",
                "description": "Aerial cityscape at dusk, slowly descending towards neon-lit streets",
                "technical_notes": "Use ND filter for proper exposure balance"
            },
            {
                "shot_number": 2,
                "section": "intro",
                "duration_seconds": 3.0,
                "shot_size": "medium_shot",
                "lens_type": "standard",
                "camera_movement": "dolly_push",
                "composition": "center_framing",
                "lighting": "neon_night_urban",
                "emotional_tone": "anticipation",
                "description": "Artist stands in urban alley, camera pushes in as they turn to face camera",
                "technical_notes": None
            }
        ]

        return json.dumps(mock_shots, indent=2)


def get_ai_provider(provider_name: str = "anthropic", **kwargs) -> AIProvider:
    """Factory function to get AI provider"""

    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "mock": MockAIProvider
    }

    if provider_name not in providers:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {', '.join(providers.keys())}"
        )

    provider_class = providers[provider_name]

    try:
        return provider_class(**kwargs)
    except ValueError as e:
        print(f"⚠ Warning: {e}")
        print(f"⚠ Falling back to mock provider")
        return MockAIProvider()
    except ImportError as e:
        print(f"⚠ Warning: {e}")
        print(f"⚠ Falling back to mock provider")
        return MockAIProvider()
