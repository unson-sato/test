"""
Generation Mode Definitions for MV Orchestra v2.8

This module defines the various AI video generation modes available
and provides utilities for working with them.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class GenerationMode(Enum):
    """Available video generation modes"""
    VEO2 = "veo2"
    SORA = "sora"
    RUNWAY_GEN3 = "runway_gen3"
    PIKA = "pika"
    TRADITIONAL = "traditional"
    HYBRID = "hybrid"
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"


@dataclass
class GenerationModeSpec:
    """
    Specification for a generation mode.

    Attributes:
        mode: The generation mode enum
        name: Human-readable name
        description: Detailed description
        strengths: List of strengths
        limitations: List of limitations
        best_for: Use cases where this mode excels
        typical_cost_per_clip: Estimated cost range
        typical_turnaround: Expected turnaround time
        quality_level: Quality rating (1-10)
        consistency_level: Consistency rating (1-10)
        control_level: Amount of creative control (1-10)
    """
    mode: GenerationMode
    name: str
    description: str
    strengths: List[str]
    limitations: List[str]
    best_for: List[str]
    typical_cost_per_clip: str
    typical_turnaround: str
    quality_level: int
    consistency_level: int
    control_level: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'mode': self.mode.value,
            'name': self.name,
            'description': self.description,
            'strengths': self.strengths,
            'limitations': self.limitations,
            'best_for': self.best_for,
            'typical_cost_per_clip': self.typical_cost_per_clip,
            'typical_turnaround': self.typical_turnaround,
            'quality_level': self.quality_level,
            'consistency_level': self.consistency_level,
            'control_level': self.control_level,
            'metadata': self.metadata
        }


# Define generation mode specifications
VEO2_SPEC = GenerationModeSpec(
    mode=GenerationMode.VEO2,
    name="Google Veo 2",
    description="Google's advanced video generation model with high quality and good motion understanding",
    strengths=[
        "High quality output",
        "Good understanding of motion and physics",
        "Handles complex scenes well",
        "Strong prompt adherence",
        "Photorealistic results"
    ],
    limitations=[
        "Character consistency requires careful prompting",
        "Can be slower than alternatives",
        "May have access limitations",
        "Higher cost than some options"
    ],
    best_for=[
        "Realistic human motion",
        "Complex camera work",
        "Character-focused shots",
        "Establishing shots",
        "High-quality requirements"
    ],
    typical_cost_per_clip="$50-150",
    typical_turnaround="1-3 days",
    quality_level=9,
    consistency_level=7,
    control_level=8
)

SORA_SPEC = GenerationModeSpec(
    mode=GenerationMode.SORA,
    name="OpenAI Sora",
    description="OpenAI's cinematic video generation model for high-quality, longer-form content",
    strengths=[
        "Cinematic quality",
        "Longer clips (up to 20s)",
        "Excellent temporal coherence",
        "Great for slow-motion",
        "Sophisticated camera movements"
    ],
    limitations=[
        "Slower generation times",
        "Higher cost",
        "Limited availability",
        "Character consistency challenges"
    ],
    best_for=[
        "Key cinematic moments",
        "Slow-motion sequences",
        "Aerial/drone shots",
        "Longer establishing shots",
        "High-budget productions"
    ],
    typical_cost_per_clip="$100-300",
    typical_turnaround="2-5 days",
    quality_level=10,
    consistency_level=8,
    control_level=7
)

RUNWAY_GEN3_SPEC = GenerationModeSpec(
    mode=GenerationMode.RUNWAY_GEN3,
    name="Runway Gen-3",
    description="Fast iteration video generation for experimental and creative work",
    strengths=[
        "Fast generation",
        "Good for experimentation",
        "Lower cost per iteration",
        "Flexible creative options",
        "Quick turnaround"
    ],
    limitations=[
        "Less photorealistic than Veo2/Sora",
        "Shorter clips (typically 4-10s)",
        "May have more artifacts",
        "Character consistency variable"
    ],
    best_for=[
        "Abstract sequences",
        "Rapid transitions",
        "Experimental visuals",
        "Quick prototyping",
        "Budget-conscious projects"
    ],
    typical_cost_per_clip="$20-60",
    typical_turnaround="12-48 hours",
    quality_level=7,
    consistency_level=6,
    control_level=8
)

PIKA_SPEC = GenerationModeSpec(
    mode=GenerationMode.PIKA,
    name="Pika",
    description="Stylized video generation with strong anime/cartoon aesthetics",
    strengths=[
        "Great for stylized content",
        "Anime-friendly",
        "Creative stylization",
        "Good motion quality",
        "Affordable pricing"
    ],
    limitations=[
        "Less realistic motion for live-action",
        "Stylization may not fit all projects",
        "Shorter duration",
        "Limited photorealism"
    ],
    best_for=[
        "Stylized MVs",
        "Anime-style projects",
        "Cartoon aesthetics",
        "Creative/artistic videos",
        "Non-realistic styles"
    ],
    typical_cost_per_clip="$15-50",
    typical_turnaround="12-36 hours",
    quality_level=7,
    consistency_level=7,
    control_level=7
)

TRADITIONAL_SPEC = GenerationModeSpec(
    mode=GenerationMode.TRADITIONAL,
    name="Traditional Shooting",
    description="Live action shooting with real actors, locations, and equipment",
    strengths=[
        "Complete creative control",
        "Highest quality",
        "Perfect character consistency",
        "Authentic human performances",
        "No AI artifacts"
    ],
    limitations=[
        "Highest cost",
        "Complex logistics",
        "Weather/location dependent",
        "Requires scheduling",
        "Limited iteration flexibility"
    ],
    best_for=[
        "High-budget productions",
        "Character performances",
        "Emotional moments",
        "Specific talent requirements",
        "Complex choreography"
    ],
    typical_cost_per_clip="$500-5000+",
    typical_turnaround="1-4 weeks",
    quality_level=10,
    consistency_level=10,
    control_level=10
)

HYBRID_SPEC = GenerationModeSpec(
    mode=GenerationMode.HYBRID,
    name="Hybrid Approach",
    description="Combination of traditional shooting with AI enhancement/generation",
    strengths=[
        "Best of both worlds",
        "Cost optimization",
        "Maintains quality where needed",
        "Creative flexibility",
        "AI for specific elements"
    ],
    limitations=[
        "Complex workflow",
        "Requires planning",
        "Integration challenges",
        "Multiple production pipelines"
    ],
    best_for=[
        "Budget optimization",
        "VFX enhancement",
        "Background replacement",
        "Complex productions",
        "Balanced approach"
    ],
    typical_cost_per_clip="$100-1000",
    typical_turnaround="1-3 weeks",
    quality_level=9,
    consistency_level=9,
    control_level=9
)


# Dictionary for easy access
GENERATION_MODE_SPECS: Dict[GenerationMode, GenerationModeSpec] = {
    GenerationMode.VEO2: VEO2_SPEC,
    GenerationMode.SORA: SORA_SPEC,
    GenerationMode.RUNWAY_GEN3: RUNWAY_GEN3_SPEC,
    GenerationMode.PIKA: PIKA_SPEC,
    GenerationMode.TRADITIONAL: TRADITIONAL_SPEC,
    GenerationMode.HYBRID: HYBRID_SPEC
}


def get_mode_spec(mode: GenerationMode) -> GenerationModeSpec:
    """
    Get specification for a generation mode.

    Args:
        mode: The generation mode

    Returns:
        GenerationModeSpec object

    Raises:
        KeyError: If mode not found
    """
    return GENERATION_MODE_SPECS[mode]


def recommend_mode(
    clip_type: str,
    budget_level: str = "medium",
    quality_priority: bool = True,
    character_focused: bool = False
) -> GenerationMode:
    """
    Recommend a generation mode based on requirements.

    Args:
        clip_type: Type of clip (e.g., "performance", "establishing", "transition")
        budget_level: Budget level ("low", "medium", "high")
        quality_priority: Whether quality is top priority
        character_focused: Whether clip focuses on characters

    Returns:
        Recommended GenerationMode
    """
    # Character-focused clips
    if character_focused:
        if budget_level == "high":
            return GenerationMode.TRADITIONAL
        else:
            return GenerationMode.HYBRID

    # Clip type recommendations
    if clip_type in ["performance", "emotional", "dialogue"]:
        return GenerationMode.TRADITIONAL if quality_priority else GenerationMode.HYBRID

    elif clip_type in ["establishing", "landscape", "cityscape"]:
        if budget_level == "high":
            return GenerationMode.SORA
        else:
            return GenerationMode.VEO2

    elif clip_type in ["transition", "abstract", "experimental"]:
        return GenerationMode.RUNWAY_GEN3

    elif clip_type in ["stylized", "anime", "cartoon"]:
        return GenerationMode.PIKA

    # Default to hybrid for balanced approach
    return GenerationMode.HYBRID


def get_all_modes_dict() -> Dict[str, Dict[str, Any]]:
    """
    Get all generation mode specs as dictionary.

    Returns:
        Dictionary mapping mode names to spec dictionaries
    """
    return {
        mode.value: spec.to_dict()
        for mode, spec in GENERATION_MODE_SPECS.items()
    }
