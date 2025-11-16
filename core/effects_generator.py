"""
Effects Code Generator for MV Orchestra v3.0

Generates Remotion effects code using multiple agents with different styles.
"""

import logging
from dataclasses import dataclass, field
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
            "React",  # Must use React
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
        non_empty_lines = [line for line in lines if line.strip()]

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
            "transform",
            "rotate",
            "scale",
            "skew",
            "blend",
            "composite",
            "filter",
            "gradient",
            "mask",
            "clipPath",
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
            performance_score=performance_score,
        )

    def select_best_effects(
        self, effects_codes: List[EffectsCode], evaluation_output: Dict[str, Any]
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
            partial_adoptions=partial_adoptions,
        )

    def merge_effects_code(
        self,
        base_code: EffectsCode,
        adoptions: List[Dict[str, Any]],
        all_codes: Optional[List[EffectsCode]] = None,
    ) -> str:
        """
        Merge effects code with partial adoptions.

        Args:
            base_code: Base effects code (winner)
            adoptions: List of partial adoptions from other agents
            all_codes: All effects codes (for extracting specific features)

        Returns:
            Merged effects code
        """
        if not adoptions:
            return base_code.code

        logger.info(
            f"Merging {len(adoptions)} partial adoptions into {base_code.agent_name}'s code"
        )

        # Extract components from base code
        base_imports = self._extract_imports(base_code.code)
        # base_components is not used in merge, so we skip extraction

        # Collect additional components from adoptions
        additional_components = []
        additional_imports = set(base_imports)

        for adoption in adoptions:
            source = adoption.get("from", "").lower()
            feature = adoption.get("feature", "")

            # Find source code
            source_code = None
            if all_codes:
                for code in all_codes:
                    if code.agent_name.lower() == source:
                        source_code = code
                        break

            if source_code:
                # Extract specific component if feature name is given
                component = self._extract_component_by_name(source_code.code, feature)
                if component:
                    additional_components.append(
                        {"name": feature, "code": component, "source": source}
                    )

                    # Extract imports from source
                    source_imports = self._extract_imports(source_code.code)
                    additional_imports.update(source_imports)

        # Build merged code
        merged_parts = []

        # Header comment
        merged_parts.append("/**")
        merged_parts.append(" * Remotion Effects for MV Orchestra")
        merged_parts.append(f" * Base: {base_code.agent_name}")
        if additional_components:
            merged_parts.append(" * Partial adoptions:")
            for comp in additional_components:
                merged_parts.append(f" *   - {comp['name']} (from {comp['source']})")
        merged_parts.append(" */\n")

        # Imports
        merged_parts.append("// Imports")
        for imp in sorted(additional_imports):
            merged_parts.append(imp)
        merged_parts.append("")

        # Base components
        merged_parts.append("// Base effects")
        merged_parts.append(self._extract_components_code(base_code.code))

        # Additional components
        if additional_components:
            merged_parts.append("\n// Adopted effects")
            for comp in additional_components:
                merged_parts.append(f"\n// {comp['name']} (from {comp['source']})")
                merged_parts.append(comp["code"])

        merged_code = "\n".join(merged_parts)
        return merged_code

    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from TypeScript code."""
        import re

        import_pattern = r"^import\s+.*?;$"
        imports = re.findall(import_pattern, code, re.MULTILINE)
        return imports

    def _extract_components(self, code: str) -> List[str]:
        """Extract component names from TypeScript code."""
        import re

        # Match: export const ComponentName or export function ComponentName
        pattern = r"export\s+(?:const|function)\s+([A-Z][a-zA-Z0-9]+)"
        matches = re.findall(pattern, code)
        return matches

    def _extract_components_code(self, code: str) -> str:
        """Extract all component code (everything after imports)."""
        import re

        # Remove imports
        code_without_imports = re.sub(r"^import\s+.*?;$", "", code, flags=re.MULTILINE)
        # Remove leading empty lines
        code_without_imports = code_without_imports.lstrip()
        return code_without_imports

    def _extract_component_by_name(self, code: str, component_name: str) -> Optional[str]:
        """
        Extract a specific component from TypeScript code.

        Args:
            code: Full TypeScript code
            component_name: Name of component to extract (can be partial match)

        Returns:
            Component code or None if not found
        """
        import re

        # Try to find component by exact name first
        # Pattern: export const/function ComponentName = ...
        pattern = rf"(export\s+(?:const|function)\s+{re.escape(component_name)}[^=]*=.*?)(?=\nexport|\ninterface|\ntype|\Z)"

        match = re.search(pattern, code, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try partial match (case-insensitive)
        components = self._extract_components(code)
        for comp in components:
            if component_name.lower() in comp.lower():
                pattern = rf"(export\s+(?:const|function)\s+{re.escape(comp)}[^=]*=.*?)(?=\nexport|\ninterface|\ntype|\Z)"
                match = re.search(pattern, code, re.DOTALL)
                if match:
                    logger.info(f"Found partial match: {comp} for {component_name}")
                    return match.group(1).strip()

        logger.warning(f"Component '{component_name}' not found in code")
        return None
