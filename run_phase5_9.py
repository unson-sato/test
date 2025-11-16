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

from phase5 import run_phase5
from phase6 import run_phase6
from phase7 import run_phase7
from phase8 import run_phase8
from phase9 import run_phase9
from core import SharedState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def run_pipeline(
    session_id: str,
    start_phase: int = 5,
    end_phase: int = 9,
    mock_mode: bool = True,
    verbose: bool = False
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

    # Load session
    try:
        session = SharedState.load_session(session_id)
        logger.info(f"Loaded session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        return False

    # Check prerequisites
    phase0_data = session.get_phase_data(0)
    if not phase0_data:
        logger.error("Phase 0 (audio analysis) not found. Please run Phase 0 first.")
        return False

    # Phase 5: MCP Clip Generation
    if start_phase <= 5 <= end_phase:
        try:
            logger.info("\n" + "=" * 80)
            logger.info("RUNNING PHASE 5: MCP Clip Generation")
            logger.info("=" * 80)

            run_phase5(
                session_id=session_id,
                mock_mode=mock_mode
            )

            logger.info("✓ Phase 5 completed successfully")
        except Exception as e:
            logger.error(f"✗ Phase 5 failed: {e}", exc_info=verbose)
            return False

    # Phase 6: CLIP Quality Evaluation
    if start_phase <= 6 <= end_phase:
        try:
            logger.info("\n" + "=" * 80)
            logger.info("RUNNING PHASE 6: CLIP Quality Evaluation")
            logger.info("=" * 80)

            run_phase6(
                session_id=session_id,
                mock_mode=mock_mode
            )

            logger.info("✓ Phase 6 completed successfully")
        except Exception as e:
            logger.error(f"✗ Phase 6 failed: {e}", exc_info=verbose)
            return False

    # Phase 7: Video Editing
    if start_phase <= 7 <= end_phase:
        try:
            logger.info("\n" + "=" * 80)
            logger.info("RUNNING PHASE 7: Video Editing")
            logger.info("=" * 80)

            run_phase7(
                session_id=session_id,
                mock_mode=mock_mode
            )

            logger.info("✓ Phase 7 completed successfully")
        except Exception as e:
            logger.error(f"✗ Phase 7 failed: {e}", exc_info=verbose)
            return False

    # Phase 8: Effects Code Generation
    if start_phase <= 8 <= end_phase:
        try:
            logger.info("\n" + "=" * 80)
            logger.info("RUNNING PHASE 8: Effects Code Generation")
            logger.info("=" * 80)

            run_phase8(
                session_id=session_id,
                mock_mode=mock_mode
            )

            logger.info("✓ Phase 8 completed successfully")
        except Exception as e:
            logger.error(f"✗ Phase 8 failed: {e}", exc_info=verbose)
            return False

    # Phase 9: Remotion Final Rendering
    if start_phase <= 9 <= end_phase:
        try:
            logger.info("\n" + "=" * 80)
            logger.info("RUNNING PHASE 9: Remotion Final Rendering")
            logger.info("=" * 80)

            run_phase9(
                session_id=session_id,
                mock_mode=mock_mode
            )

            logger.info("✓ Phase 9 completed successfully")
        except Exception as e:
            logger.error(f"✗ Phase 9 failed: {e}", exc_info=verbose)
            return False

    # Success
    logger.info("\n" + "=" * 80)
    logger.info("🎬 PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)

    # Show final output
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
        """
    )

    parser.add_argument(
        'session_id',
        help='Session identifier'
    )

    parser.add_argument(
        '--start-phase',
        type=int,
        default=5,
        choices=[5, 6, 7, 8, 9],
        help='Starting phase (default: 5)'
    )

    parser.add_argument(
        '--end-phase',
        type=int,
        default=9,
        choices=[5, 6, 7, 8, 9],
        help='Ending phase (default: 9)'
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        default=True,
        help='Use mock mode (default: True)'
    )

    parser.add_argument(
        '--no-mock',
        action='store_false',
        dest='mock',
        help='Disable mock mode (requires external dependencies)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

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
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
