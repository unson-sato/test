"""
Phase 3: Clip Division

This phase handles breaking down sections into individual
clips/shots with specific timing and transitions.
"""

__version__ = "2.8"

from .runner import Phase3Runner, run_phase3
from .clip_utils import (
    snap_to_beat,
    load_beat_data,
    validate_clip_coverage,
    generate_clip_id,
    estimate_clip_complexity,
    calculate_clip_statistics,
    optimize_beat_alignment,
    find_nearest_beat,
    find_beat_range
)

__all__ = [
    'Phase3Runner',
    'run_phase3',
    'snap_to_beat',
    'load_beat_data',
    'validate_clip_coverage',
    'generate_clip_id',
    'estimate_clip_complexity',
    'calculate_clip_statistics',
    'optimize_beat_alignment',
    'find_nearest_beat',
    'find_beat_range'
]
