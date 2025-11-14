"""
Phase 4: Generation Strategy

This phase handles technical parameters and generation approach
for each clip (prompts, models, settings, etc.).
"""

from .runner import Phase4Runner, run_phase4
from .generation_modes import (
    GenerationMode,
    GenerationModeSpec,
    get_mode_spec,
    recommend_mode,
    get_all_modes_dict,
    VEO2_SPEC,
    SORA_SPEC,
    RUNWAY_GEN3_SPEC,
    PIKA_SPEC,
    TRADITIONAL_SPEC,
    HYBRID_SPEC
)
from .prompt_builder import (
    PromptTemplate,
    PromptBuilder,
    create_character_prompt,
    create_establishing_prompt,
    create_transition_prompt,
    enhance_prompt_for_consistency,
    get_default_negative_prompts,
    get_quality_presets
)
from .asset_manager import (
    AssetManager,
    Asset,
    AssetType,
    ClipAssets,
    create_character_consistency_asset,
    create_style_guide_asset,
    create_audio_segment_asset
)

__version__ = "2.8"

__all__ = [
    # Runner
    'Phase4Runner',
    'run_phase4',

    # Generation Modes
    'GenerationMode',
    'GenerationModeSpec',
    'get_mode_spec',
    'recommend_mode',
    'get_all_modes_dict',
    'VEO2_SPEC',
    'SORA_SPEC',
    'RUNWAY_GEN3_SPEC',
    'PIKA_SPEC',
    'TRADITIONAL_SPEC',
    'HYBRID_SPEC',

    # Prompt Building
    'PromptTemplate',
    'PromptBuilder',
    'create_character_prompt',
    'create_establishing_prompt',
    'create_transition_prompt',
    'enhance_prompt_for_consistency',
    'get_default_negative_prompts',
    'get_quality_presets',

    # Asset Management
    'AssetManager',
    'Asset',
    'AssetType',
    'ClipAssets',
    'create_character_consistency_asset',
    'create_style_guide_asset',
    'create_audio_segment_asset',
]
