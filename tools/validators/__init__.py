"""
Validation Tools for MV Orchestra v2.8

Tools for validating inputs, outputs, and intermediate results.

This package provides technical validation tools for different phases:
- validate_clip_division: Phase 3 clip division validator
- validate_phase4_strategies: Phase 4 generation strategies validator
- validation_utils: Shared validation utilities

Usage:
    from tools.validators import validate_clip_division, validate_phase4_strategies

    # Validate Phase 3
    report = validate_clip_division(session_id)

    # Validate Phase 4
    report = validate_phase4_strategies(session_id)
"""

__version__ = "2.8"

from .validate_clip_division import validate_clip_division
from .validate_phase4_strategies import validate_phase4_strategies

__all__ = [
    'validate_clip_division',
    'validate_phase4_strategies'
]
