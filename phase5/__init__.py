"""
Phase 5: Real Claude Review (Optional)

This optional phase provides a final quality control review
by actual Claude AI for the complete music video design.
"""

from .runner import Phase5Runner, run_phase5
from .api_client import ClaudeAPIClient, create_client

__version__ = "2.8"

__all__ = [
    'Phase5Runner',
    'run_phase5',
    'ClaudeAPIClient',
    'create_client',
]
