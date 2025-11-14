"""
Phase 0: Overall Design (全体設計)
MV Orchestra v2.8

This phase implements the initial competition where 5 directors propose
overall MV concepts based on song analysis.

Main Components:
- Phase0Runner: Main orchestration class
- run_phase0: Convenience function for running the phase
"""

from .runner import Phase0Runner, run_phase0

__version__ = "2.8"

__all__ = [
    'Phase0Runner',
    'run_phase0'
]
