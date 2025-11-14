"""
Phase 2: Section Direction

This phase handles direction for individual music sections
(intro, verse, chorus, bridge, outro, etc.).
"""

__version__ = "2.8"

from .runner import Phase2Runner, run_phase2
from .section_utils import (
    load_song_sections,
    validate_section_coverage,
    extract_section_summary,
    get_section_types,
    format_section_for_prompt,
    calculate_emotional_progression
)

__all__ = [
    'Phase2Runner',
    'run_phase2',
    'load_song_sections',
    'validate_section_coverage',
    'extract_section_summary',
    'get_section_types',
    'format_section_for_prompt',
    'calculate_emotional_progression'
]
