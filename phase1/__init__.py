"""
Phase 1: Character Design (キャラクター設計)
MV Orchestra v2.8

This phase implements the character design competition where 5 directors
create character concepts based on Phase 0's winning overall design.

Main Components:
- Phase1Runner: Main orchestration class
- run_phase1: Convenience function for running the phase
"""

from .runner import Phase1Runner, run_phase1

__version__ = "2.8"

__all__ = [
    'Phase1Runner',
    'run_phase1'
]
