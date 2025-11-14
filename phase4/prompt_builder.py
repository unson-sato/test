"""
Prompt Building Utilities for MV Orchestra v2.8

This module provides utilities for building and managing prompts
for AI video generation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PromptTemplate:
    """
    Template for video generation prompts.

    Attributes:
        base_prompt: Main prompt description
        style_modifiers: Style-related modifiers
        technical_specs: Technical specifications (camera, lighting, etc.)
        negative_prompt: Things to avoid
        quality_tags: Quality enhancement tags
        custom_params: Custom generation parameters
    """
    base_prompt: str
    style_modifiers: List[str] = field(default_factory=list)
    technical_specs: List[str] = field(default_factory=list)
    negative_prompt: str = ""
    quality_tags: List[str] = field(default_factory=list)
    custom_params: Dict[str, Any] = field(default_factory=dict)

    def build(self) -> str:
        """
        Build complete prompt string.

        Returns:
            Complete prompt string
        """
        parts = [self.base_prompt]

        if self.style_modifiers:
            parts.extend(self.style_modifiers)

        if self.technical_specs:
            parts.extend(self.technical_specs)

        if self.quality_tags:
            parts.extend(self.quality_tags)

        return ", ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'base_prompt': self.base_prompt,
            'style_modifiers': self.style_modifiers,
            'technical_specs': self.technical_specs,
            'negative_prompt': self.negative_prompt,
            'quality_tags': self.quality_tags,
            'custom_params': self.custom_params,
            'full_prompt': self.build()
        }


class PromptBuilder:
    """
    Builder class for constructing video generation prompts.
    """

    def __init__(self):
        """Initialize prompt builder"""
        self.base_prompt = ""
        self.style_modifiers = []
        self.technical_specs = []
        self.negative_prompt = ""
        self.quality_tags = []
        self.custom_params = {}

    def set_base(self, description: str) -> 'PromptBuilder':
        """
        Set base prompt description.

        Args:
            description: Main scene description

        Returns:
            Self for chaining
        """
        self.base_prompt = description
        return self

    def add_style(self, *modifiers: str) -> 'PromptBuilder':
        """
        Add style modifiers.

        Args:
            *modifiers: Style descriptions

        Returns:
            Self for chaining
        """
        self.style_modifiers.extend(modifiers)
        return self

    def add_technical(self, *specs: str) -> 'PromptBuilder':
        """
        Add technical specifications.

        Args:
            *specs: Technical specifications

        Returns:
            Self for chaining
        """
        self.technical_specs.extend(specs)
        return self

    def set_negative(self, negative: str) -> 'PromptBuilder':
        """
        Set negative prompt.

        Args:
            negative: Things to avoid

        Returns:
            Self for chaining
        """
        self.negative_prompt = negative
        return self

    def add_quality(self, *tags: str) -> 'PromptBuilder':
        """
        Add quality enhancement tags.

        Args:
            *tags: Quality tags

        Returns:
            Self for chaining
        """
        self.quality_tags.extend(tags)
        return self

    def set_param(self, key: str, value: Any) -> 'PromptBuilder':
        """
        Set custom parameter.

        Args:
            key: Parameter name
            value: Parameter value

        Returns:
            Self for chaining
        """
        self.custom_params[key] = value
        return self

    def build(self) -> PromptTemplate:
        """
        Build prompt template.

        Returns:
            PromptTemplate object
        """
        return PromptTemplate(
            base_prompt=self.base_prompt,
            style_modifiers=self.style_modifiers.copy(),
            technical_specs=self.technical_specs.copy(),
            negative_prompt=self.negative_prompt,
            quality_tags=self.quality_tags.copy(),
            custom_params=self.custom_params.copy()
        )


def create_character_prompt(
    character_name: str,
    action: str,
    setting: str,
    emotion: Optional[str] = None,
    clothing: Optional[str] = None,
    camera_angle: Optional[str] = None
) -> PromptTemplate:
    """
    Create a prompt template for character-focused clips.

    Args:
        character_name: Name or description of character
        action: What the character is doing
        setting: Where the scene takes place
        emotion: Emotional state (optional)
        clothing: Clothing description (optional)
        camera_angle: Camera angle (optional)

    Returns:
        PromptTemplate for character clip
    """
    builder = PromptBuilder()

    # Build base description
    base_parts = [character_name]
    if clothing:
        base_parts.append(f"wearing {clothing}")
    base_parts.append(action)
    base_parts.append(f"in {setting}")
    if emotion:
        base_parts.append(f"with {emotion} expression")

    builder.set_base(", ".join(base_parts))

    # Add technical specs
    if camera_angle:
        builder.add_technical(camera_angle)
    builder.add_technical("professional cinematography", "natural lighting")

    # Add quality tags
    builder.add_quality("high quality", "cinematic", "detailed")

    # Set negative prompt
    builder.set_negative("blurry, distorted, multiple people, low quality, artifacts")

    return builder.build()


def create_establishing_prompt(
    location: str,
    time_of_day: str,
    mood: str,
    camera_movement: Optional[str] = None
) -> PromptTemplate:
    """
    Create a prompt template for establishing shots.

    Args:
        location: Location description
        time_of_day: Time of day (e.g., "golden hour", "night")
        mood: Mood/atmosphere
        camera_movement: Camera movement description (optional)

    Returns:
        PromptTemplate for establishing shot
    """
    builder = PromptBuilder()

    # Build base description
    base = f"Wide establishing shot of {location} at {time_of_day}"
    builder.set_base(base)

    # Add style
    builder.add_style(mood, "atmospheric")

    # Add technical specs
    if camera_movement:
        builder.add_technical(camera_movement)
    builder.add_technical("wide angle lens", "cinematic composition")

    # Add quality
    builder.add_quality("4K quality", "professional color grading", "sharp details")

    # Set negative
    builder.set_negative("people, blur, distortion, low quality")

    return builder.build()


def create_transition_prompt(
    transition_type: str,
    from_scene: str,
    to_scene: str,
    style: Optional[str] = None
) -> PromptTemplate:
    """
    Create a prompt template for transition clips.

    Args:
        transition_type: Type of transition (e.g., "abstract", "geometric")
        from_scene: Description of outgoing scene
        to_scene: Description of incoming scene
        style: Style description (optional)

    Returns:
        PromptTemplate for transition
    """
    builder = PromptBuilder()

    # Build base description
    base = f"{transition_type} transition from {from_scene} to {to_scene}"
    builder.set_base(base)

    # Add style
    if style:
        builder.add_style(style)
    builder.add_style("smooth motion", "creative")

    # Add technical specs
    builder.add_technical("dynamic camera", "fluid movement")

    # Add quality
    builder.add_quality("high quality", "seamless")

    return builder.build()


def enhance_prompt_for_consistency(
    base_template: PromptTemplate,
    character_reference: Optional[str] = None,
    style_reference: Optional[str] = None,
    consistency_strength: float = 0.8
) -> PromptTemplate:
    """
    Enhance a prompt template with consistency parameters.

    Args:
        base_template: Base prompt template to enhance
        character_reference: Character reference identifier
        style_reference: Style reference identifier
        consistency_strength: Strength of consistency enforcement (0.0-1.0)

    Returns:
        Enhanced PromptTemplate
    """
    enhanced = PromptTemplate(
        base_prompt=base_template.base_prompt,
        style_modifiers=base_template.style_modifiers.copy(),
        technical_specs=base_template.technical_specs.copy(),
        negative_prompt=base_template.negative_prompt,
        quality_tags=base_template.quality_tags.copy(),
        custom_params=base_template.custom_params.copy()
    )

    # Add consistency parameters
    if character_reference:
        enhanced.custom_params['character_reference'] = character_reference
        enhanced.custom_params['character_consistency_strength'] = consistency_strength

    if style_reference:
        enhanced.custom_params['style_reference'] = style_reference
        enhanced.custom_params['style_consistency_strength'] = consistency_strength

    # Add consistency tags
    enhanced.style_modifiers.append("consistent with previous shots")

    return enhanced


def get_default_negative_prompts() -> Dict[str, str]:
    """
    Get default negative prompts for different scenarios.

    Returns:
        Dictionary of scenario: negative_prompt
    """
    return {
        'character': "blurry, distorted, multiple people, wrong clothing, inconsistent face, low quality, artifacts",
        'establishing': "people, blur, distortion, low quality, overexposed, underexposed",
        'transition': "harsh cuts, stuttering, low quality, artifacts, static",
        'performance': "blurry faces, inconsistent character, wrong emotion, low quality, distorted",
        'general': "low quality, blurry, distorted, artifacts, inconsistent, poor lighting"
    }


def get_quality_presets() -> Dict[str, List[str]]:
    """
    Get quality tag presets for different quality levels.

    Returns:
        Dictionary of quality_level: quality_tags
    """
    return {
        'high': [
            "4K quality",
            "professional cinematography",
            "cinematic color grading",
            "sharp details",
            "high production value"
        ],
        'medium': [
            "HD quality",
            "good cinematography",
            "color graded",
            "clear details"
        ],
        'experimental': [
            "creative",
            "artistic",
            "experimental visuals",
            "unique style"
        ]
    }
