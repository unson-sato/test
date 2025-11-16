"""
Phase 6: Video Generation Execution

This phase handles the actual generation of video clips based on Phase 4 strategies.
Coordinates with external AI video generation services (Veo2, Sora, Runway, Pika, etc.)
"""

from .runner import Phase6Runner, run_phase6

__all__ = ['Phase6Runner', 'run_phase6']
