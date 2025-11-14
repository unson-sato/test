"""
MV Orchestra v2.8 - Core Module

This module provides the core functionality for the multi-director
AI competition system for music video generation.

Main Components:
- SharedState: Session state management
- DirectorProfile: Director personality definitions
- CodexRunner: AI evaluation execution
- Utilities: Common helper functions
"""

from .shared_state import SharedState, PhaseData, SessionMetadata
from .director_profiles import (
    DirectorProfile,
    DirectorType,
    CORPORATE,
    FREELANCER,
    VETERAN,
    AWARD_WINNER,
    NEWCOMER,
    DIRECTOR_PROFILES,
    get_director_profile,
    get_all_profiles,
    get_profiles_dict
)
from .codex_runner import (
    CodexRunner,
    EvaluationRequest,
    EvaluationResult
)
from .utils import (
    read_json,
    write_json,
    ensure_dir,
    get_timestamp,
    get_iso_timestamp,
    generate_session_id,
    validate_path,
    get_project_root,
    get_session_dir,
    get_evaluations_dir,
    safe_filename
)

__version__ = "2.8"

__all__ = [
    # State management
    'SharedState',
    'PhaseData',
    'SessionMetadata',

    # Director profiles
    'DirectorProfile',
    'DirectorType',
    'CORPORATE',
    'FREELANCER',
    'VETERAN',
    'AWARD_WINNER',
    'NEWCOMER',
    'DIRECTOR_PROFILES',
    'get_director_profile',
    'get_all_profiles',
    'get_profiles_dict',

    # Evaluation
    'CodexRunner',
    'EvaluationRequest',
    'EvaluationResult',

    # Utilities
    'read_json',
    'write_json',
    'ensure_dir',
    'get_timestamp',
    'get_iso_timestamp',
    'generate_session_id',
    'validate_path',
    'get_project_root',
    'get_session_dir',
    'get_evaluations_dir',
    'safe_filename',
]
