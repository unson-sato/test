#!/usr/bin/env python3
"""
Example: Basic Usage of MV Orchestra v2.8

This example demonstrates the simplest way to use MV Orchestra:
run the complete pipeline with default settings.

Usage:
    python3 examples/example_basic.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SharedState, get_session_dir
from phase0 import run_phase0
from phase1 import run_phase1
from phase2 import run_phase2
from phase3 import run_phase3
from phase4 import run_phase4


def main():
    """Run basic pipeline example."""
    print("=" * 70)
    print("MV ORCHESTRA v2.8 - Basic Usage Example")
    print("=" * 70)

    # 1. Set up session
    session_id = "example_basic"
    print(f"\n1. Creating session: {session_id}")

    # Create session with specific ID
    from core import ensure_dir
    session = SharedState(session_id=session_id)
    ensure_dir(session.session_dir)
    session.save_session()

    # 2. Use sample analysis
    analysis_path = "sample_analysis.json"
    print(f"2. Using analysis: {analysis_path}")

    # 3. Run all phases with mock evaluations
    print("\n3. Running all phases...")

    print("\n→ Phase 0: Overall Design")
    phase0_results = run_phase0(session_id, analysis_path, mock_mode=True)
    print(f"  Winner: {phase0_results['winner']['director']}")

    print("\n→ Phase 1: Character Design")
    phase1_results = run_phase1(session_id, mock_mode=True)
    print(f"  Winner: {phase1_results['winner']['director']}")

    print("\n→ Phase 2: Section Direction")
    phase2_results = run_phase2(session_id, mock_mode=True)
    print(f"  Winner: {phase2_results['winner']['director']}")

    print("\n→ Phase 3: Clip Division")
    phase3_results = run_phase3(session_id, mock_mode=True)
    print(f"  Winner: {phase3_results['winner']['director']}")
    print(f"  Clips generated: {len(phase3_results['winner']['clips'])}")

    print("\n→ Phase 4: Generation Strategy")
    phase4_results = run_phase4(session_id, mock_mode=True)
    print(f"  Winner: {phase4_results['winner']['director']}")

    # 4. Show results
    print("\n" + "=" * 70)
    print("Pipeline Complete!")
    print("=" * 70)
    print(f"Session saved to: {get_session_dir(session_id)}")
    print("\nNext steps:")
    print("  - Review session data in shared-workspace/sessions/")
    print("  - Examine phase results and winner proposals")
    print("  - Use the generation strategies to create your music video")


if __name__ == "__main__":
    main()
