#!/usr/bin/env python3
"""
Run Phase 5-9 Pipeline

Executes the complete video generation and post-processing pipeline.

Usage:
    python3 run_phase5_9.py <session_id> [options]

Example:
    python3 run_phase5_9.py my_session --start-phase 5 --end-phase 9 --mock
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from phase5 import run_phase5  # noqa: E402
from phase6 import run_phase6  # noqa: E402
from phase7 import run_phase7  # noqa: E402
from phase8 import run_phase8  # noqa: E402
from phase9 import run_phase9  # noqa: E402
from core import SharedState  # noqa: E402


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Phase runners mapping
PHASE_RUNNERS = {
    5: ("MCP Clip Generation", run_phase5),
    6: ("CLIP Quality Evaluation", run_phase6),
    7: ("Video Editing", run_phase7),
    8: ("Effects Code Generation", run_phase8),
    9: ("Remotion Final Rendering", run_phase9),
}


def _run_single_phase(
    phase_num: int, phase_name: str, runner_func, session_id: str, mock_mode: bool, verbose: bool
) -> bool:
    """Run a single phase and handle errors."""
    try:
        logger.info("\n" + "=" * 80)
        logger.info(f"RUNNING PHASE {phase_num}: {phase_name}")
        logger.info("=" * 80)

        runner_func(session_id=session_id, mock_mode=mock_mode)

        logger.info(f"✓ Phase {phase_num} completed successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Phase {phase_num} failed: {e}", exc_info=verbose)
        return False


def run_pipeline(
    session_id: str,
    start_phase: int = 5,
    end_phase: int = 9,
    mock_mode: bool = True,
    verbose: bool = False,
):
    """
    Run the Phase 5-9 pipeline.

    Args:
        session_id: Session identifier
        start_phase: Starting phase (5-9)
        end_phase: Ending phase (5-9)
        mock_mode: If True, use mock mode for all phases
        verbose: If True, enable debug logging
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 80)
    logger.info(f"MV ORCHESTRA - PHASE {start_phase}-{end_phase} PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Session: {session_id}")
    logger.info(f"Mock mode: {mock_mode}")
    logger.info("")

    # Load and validate session
    try:
        session = SharedState.load_session(session_id)
        logger.info(f"Loaded session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        return False

    if not session.get_phase_data(0):
        logger.error("Phase 0 (audio analysis) not found. Please run Phase 0 first.")
        return False

    # Run phases in sequence
    for phase_num in range(start_phase, end_phase + 1):
        if phase_num in PHASE_RUNNERS:
            phase_name, runner_func = PHASE_RUNNERS[phase_num]
            if not _run_single_phase(
                phase_num, phase_name, runner_func, session_id, mock_mode, verbose
            ):
                return False

    # Success - show final output
    logger.info("\n" + "=" * 80)
    logger.info("🎬 PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)

    session = SharedState.load_session(session_id)
    phase9_data = session.get_phase_data(9)
    if phase9_data and "output_file" in phase9_data:
        logger.info(f"\n✓ Final video: {phase9_data['output_file']}")
        logger.info(f"  Duration: {phase9_data['duration']:.1f}s")
        logger.info(f"  File size: {phase9_data['file_size_mb']:.1f} MB")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run MV Orchestra Phase 5-9 pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline in mock mode
  python3 run_phase5_9.py my_session --mock

  # Run only Phase 5-6
  python3 run_phase5_9.py my_session --start-phase 5 --end-phase 6 --mock

  # Run with real MCP/ffmpeg/Remotion (requires external dependencies)
  python3 run_phase5_9.py my_session --no-mock

  # Run with verbose logging
  python3 run_phase5_9.py my_session --mock -v
        """,
    )

    parser.add_argument("session_id", help="Session identifier")

    parser.add_argument(
        "--start-phase",
        type=int,
        default=5,
        choices=[5, 6, 7, 8, 9],
        help="Starting phase (default: 5)",
    )

    parser.add_argument(
        "--end-phase",
        type=int,
        default=9,
        choices=[5, 6, 7, 8, 9],
        help="Ending phase (default: 9)",
    )

    parser.add_argument(
        "--mock", action="store_true", default=True, help="Use mock mode (default: True)"
    )

    parser.add_argument(
        "--no-mock",
        action="store_false",
        dest="mock",
        help="Disable mock mode (requires external dependencies)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Validate phase range
    if args.start_phase > args.end_phase:
        parser.error("Start phase must be <= end phase")

    # Run pipeline
    success = run_pipeline(
        session_id=args.session_id,
        start_phase=args.start_phase,
        end_phase=args.end_phase,
        mock_mode=args.mock,
        verbose=args.verbose,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
