"""
Effects Code Generator for MV Orchestra v3.0

Generates Remotion effects code using multiple agents with different styles.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import get_iso_timestamp

logger = logging.getLogger(__name__)


class EffectsGenerationError(Exception):
    """Raised when effects code generation fails"""
    pass


@dataclass
class EffectsCode:
    """Generated Remotion effects code"""
    agent_name: str
    code: str
    effects_list: List[str]
    reasoning: str
    complexity_score: float  # 0.0-1.0
    creativity_score: float  # 0.0-1.0
    performance_score: float  # 0.0-1.0
    timestamp: str = field(default_factory=get_iso_timestamp)


@dataclass
class EffectsEvaluation:
    """Evaluation of generated effects code"""
    winner: str
    winner_code: EffectsCode
    scores: Dict[str, float]
    reasoning: str
    partial_adoptions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=get_iso_timestamp)


class EffectsGenerator:
    """
    Generates Remotion effects code using multiple agents.

    Uses 3 different agents with different approaches:
    - Minimalist: Clean, simple effects
    - Creative: Bold, experimental effects
    - Balanced: Professional, well-rounded effects
    """

    def __init__(self):
        """Initialize Effects Generator."""
        logger.info("EffectsGenerator initialized")

    def validate_effects_code(self, code: str) -> bool:
        """
        Validate generated effects code.

        Checks:
        - Valid TypeScript/React syntax (basic check)
        - Contains required imports
        - Contains effect components
        - Exports effects properly

        Args:
            code: Generated TypeScript code

        Returns:
            True if valid, False otherwise
        """
        required_patterns = [
            "import",  # Must have imports
            "export",  # Must export
            "React",   # Must use React
        ]

        for pattern in required_patterns:
            if pattern not in code:
                logger.warning(f"Effects code missing required pattern: {pattern}")
                return False

        # Check for obvious syntax errors
        if code.count("{") != code.count("}"):
            logger.warning("Effects code has mismatched braces")
            return False

        if code.count("(") != code.count(")"):
            logger.warning("Effects code has mismatched parentheses")
            return False

        return True

    def extract_effects_list(self, code: str) -> List[str]:
        """
        Extract list of effects from generated code.

        Looks for effect component names (typically capitalized function names).

        Args:
            code: Generated TypeScript code

        Returns:
            List of effect names
        """
        import re

        # Find all exported function/component names
        # Pattern: export (const|function) EffectName
        pattern = r"export\s+(?:const|function)\s+([A-Z][a-zA-Z0-9]+)"
        matches = re.findall(pattern, code)

        return matches

    def calculate_complexity_score(self, code: str) -> float:
        """
        Calculate complexity score of generated code.

        Higher score = more complex effects.

        Args:
            code: Generated TypeScript code

        Returns:
            Complexity score (0.0-1.0)
        """
        # Simple heuristics for complexity
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        # Factors:
        # - Number of lines
        # - Number of effects
        # - Use of animations (useCurrentFrame, interpolate)
        # - Use of advanced features (spring, etc.)

        line_score = min(len(non_empty_lines) / 200.0, 1.0)  # Normalize to 200 lines

        animation_keywords = ["useCurrentFrame", "interpolate", "spring", "animate"]
        animation_count = sum(code.count(kw) for kw in animation_keywords)
        animation_score = min(animation_count / 10.0, 1.0)  # Normalize to 10 uses

        # Average scores
        complexity = (line_score + animation_score) / 2.0

        return complexity

    def calculate_creativity_score(self, code: str, effects_list: List[str]) -> float:
        """
        Calculate creativity score of generated effects.

        Higher score = more creative/unique effects.

        Args:
            code: Generated TypeScript code
            effects_list: List of effect names

        Returns:
            Creativity score (0.0-1.0)
        """
        # Heuristics for creativity:
        # - Variety of effects
        # - Use of transformations
        # - Use of blending/compositing
        # - Unique combinations

        variety_score = min(len(effects_list) / 10.0, 1.0)  # Normalize to 10 effects

        creative_keywords = [
            "transform", "rotate", "scale", "skew",
            "blend", "composite", "filter",
            "gradient", "mask", "clipPath"
        ]
        creative_count = sum(code.count(kw) for kw in creative_keywords)
        creative_score = min(creative_count / 15.0, 1.0)  # Normalize to 15 uses

        # Average scores
        creativity = (variety_score + creative_score) / 2.0

        return creativity

    def calculate_performance_score(self, code: str) -> float:
        """
        Calculate estimated performance score.

        Higher score = better performance.

        Args:
            code: Generated TypeScript code

        Returns:
            Performance score (0.0-1.0)
        """
        # Heuristics for performance:
        # - Use of memoization (useMemo, useCallback)
        # - Avoiding expensive operations in render
        # - Proper key usage

        performance_keywords = ["useMemo", "useCallback", "React.memo"]
        performance_count = sum(code.count(kw) for kw in performance_keywords)
        performance_score = min(performance_count / 5.0, 1.0)  # Normalize to 5 uses

        # Penalty for expensive operations
        expensive_keywords = ["filter", "map", "forEach"]
        expensive_count = sum(code.count(kw) for kw in expensive_keywords)
        expensive_penalty = min(expensive_count / 20.0, 0.3)  # Max 30% penalty

        performance = max(0.5 + performance_score * 0.5 - expensive_penalty, 0.0)

        return performance

    def parse_agent_output(self, agent_name: str, output: Dict[str, Any]) -> EffectsCode:
        """
        Parse agent output into EffectsCode.

        Args:
            agent_name: Name of the agent
            output: Agent's JSON output

        Returns:
            EffectsCode object
        """
        code = output.get("effects_code", "")
        reasoning = output.get("reasoning", "")

        # Validate code
        if not self.validate_effects_code(code):
            raise EffectsGenerationError(f"Invalid effects code from {agent_name}")

        # Extract effects list
        effects_list = self.extract_effects_list(code)

        # Calculate scores
        complexity_score = self.calculate_complexity_score(code)
        creativity_score = self.calculate_creativity_score(code, effects_list)
        performance_score = self.calculate_performance_score(code)

        return EffectsCode(
            agent_name=agent_name,
            code=code,
            effects_list=effects_list,
            reasoning=reasoning,
            complexity_score=complexity_score,
            creativity_score=creativity_score,
            performance_score=performance_score
        )

    def select_best_effects(
        self,
        effects_codes: List[EffectsCode],
        evaluation_output: Dict[str, Any]
    ) -> EffectsEvaluation:
        """
        Select best effects code based on evaluation.

        Args:
            effects_codes: List of generated effects codes
            evaluation_output: Evaluation agent's JSON output

        Returns:
            EffectsEvaluation object
        """
        winner_name = evaluation_output.get("winner", "")
        reasoning = evaluation_output.get("reasoning", "")
        scores = evaluation_output.get("scores", {})
        partial_adoptions = evaluation_output.get("partial_adoptions", [])

        # Find winner code
        winner_code = None
        for code in effects_codes:
            if code.agent_name.lower() in winner_name.lower():
                winner_code = code
                break

        if not winner_code:
            # Fallback to first code if winner not found
            logger.warning(f"Winner '{winner_name}' not found, using first code")
            winner_code = effects_codes[0]

        return EffectsEvaluation(
            winner=winner_name,
            winner_code=winner_code,
            scores=scores,
            reasoning=reasoning,
            partial_adoptions=partial_adoptions
        )

    def merge_effects_code(
        self,
        base_code: EffectsCode,
        adoptions: List[Dict[str, Any]]
    ) -> str:
        """
        Merge effects code with partial adoptions.

        Args:
            base_code: Base effects code (winner)
            adoptions: List of partial adoptions from other agents

        Returns:
            Merged effects code
        """
        # For now, just return base code
        # TODO: Implement actual code merging logic
        logger.info(f"Merging {len(adoptions)} partial adoptions into {base_code.agent_name}'s code")

        merged_code = base_code.code

        # Add comments about adoptions
        if adoptions:
            adoption_comments = "\n// Partial adoptions:\n"
            for adoption in adoptions:
                source = adoption.get("from", "unknown")
                feature = adoption.get("feature", "unknown")
                adoption_comments += f"// - {feature} (from {source})\n"

            merged_code = adoption_comments + merged_code

        return merged_code
