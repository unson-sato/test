#!/usr/bin/env python3
"""
Run MV Orchestra Phase 0-4 (Design Phases)

Executes the orchestrator agent for design phases with multi-agent competition.

Usage:
    python3 run_orchestrator.py <session_id> [options]

Example:
    python3 run_orchestrator.py my_session --audio audio.mp3 --start-phase 1 --end-phase 4
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import OrchestratorAgent, PipelineState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run MV Orchestra Phase 0-4 (Design Phases)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full design pipeline (Phase 0-4)
  python3 run_orchestrator.py my_session --audio song.mp3

  # Run only Phase 1-4 (skip audio analysis)
  python3 run_orchestrator.py my_session --start-phase 1 --end-phase 4

  # Run with custom quality threshold
  python3 run_orchestrator.py my_session --audio song.mp3 --threshold 80

  # Run with verbose logging
  python3 run_orchestrator.py my_session --audio song.mp3 -v

After completion, run Phase 5-9 with:
  python3 run_phase5_9.py my_session --mock
        """
    )

    parser.add_argument(
        'session_id',
        help='Session identifier'
    )

    parser.add_argument(
        '--audio',
        type=Path,
        help='Path to audio file (for Phase 0)'
    )

    parser.add_argument(
        '--start-phase',
        type=int,
        default=0,
        choices=[0, 1, 2, 3, 4],
        help='Starting phase (default: 0)'
    )

    parser.add_argument(
        '--end-phase',
        type=int,
        default=4,
        choices=[0, 1, 2, 3, 4],
        help='Ending phase (default: 4)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=70.0,
        help='Quality threshold (0-100, default: 70)'
    )

    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum feedback iterations per phase (default: 3)'
    )

    parser.add_argument(
        '--claude-cli',
        type=str,
        default='claude',
        help='Path to Claude CLI executable (default: claude)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate args
    if args.start_phase > args.end_phase:
        parser.error("Start phase must be <= end phase")

    if args.start_phase == 0 and not args.audio:
        parser.error("--audio is required when starting from Phase 0")

    # Run orchestrator
    try:
        success = asyncio.run(run_orchestrator(
            session_id=args.session_id,
            audio_file=args.audio,
            start_phase=args.start_phase,
            end_phase=args.end_phase,
            quality_threshold=args.threshold,
            max_iterations=args.max_iterations,
            claude_cli=args.claude_cli
        ))

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}", exc_info=args.verbose)
        sys.exit(1)


async def run_orchestrator(
    session_id: str,
    audio_file: Optional[Path],
    start_phase: int,
    end_phase: int,
    quality_threshold: float,
    max_iterations: int,
    claude_cli: str
) -> bool:
    """
    Run the orchestrator.

    Args:
        session_id: Session identifier
        audio_file: Path to audio file (for Phase 0)
        start_phase: Starting phase
        end_phase: Ending phase
        quality_threshold: Quality threshold (0-100)
        max_iterations: Maximum feedback iterations
        claude_cli: Claude CLI executable path

    Returns:
        True if successful
    """
    logger.info("=" * 80)
    logger.info("MV ORCHESTRA - DESIGN PHASES (0-4)")
    logger.info("=" * 80)
    logger.info(f"Session: {session_id}")
    logger.info(f"Phase range: {start_phase}-{end_phase}")
    logger.info(f"Quality threshold: {quality_threshold}")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info("")

    # Initialize orchestrator
    orchestrator = OrchestratorAgent(
        session_id=session_id,
        claude_cli=claude_cli,
        quality_threshold=quality_threshold,
        max_iterations=max_iterations
    )

    # Run pipeline
    if start_phase == 0 and end_phase >= 4:
        # Full pipeline (Phase 0-4)
        logger.info("Running full design pipeline (Phase 0-4)...")
        results = await orchestrator.run_full_pipeline(audio_file=audio_file)

    elif start_phase == 0:
        # Phase 0 only or Phase 0-X
        logger.info("Running Phase 0 (audio analysis)...")
        phase0_result = await orchestrator._run_audio_analysis(audio_file)

        if end_phase > 0:
            logger.info(f"\nRunning Phase {max(1, start_phase)}-{end_phase}...")
            results = await orchestrator.run_design_phases(
                start_phase=max(1, start_phase),
                end_phase=end_phase
            )
            results["phase0"] = phase0_result
        else:
            results = {"phase0": phase0_result}

    else:
        # Phase 1-4 only
        logger.info(f"Running Phase {start_phase}-{end_phase}...")
        results = await orchestrator.run_design_phases(
            start_phase=start_phase,
            end_phase=end_phase
        )

    # Show summary
    logger.info("\n" + "=" * 80)
    logger.info("DESIGN PHASES COMPLETED")
    logger.info("=" * 80)

    # Get pipeline state
    pipeline_state = PipelineState(session_id)
    summary = pipeline_state.get_summary()

    logger.info(f"\nSession: {session_id}")
    logger.info(f"Completed phases: {summary['progress']['completed_phases']}")
    logger.info(f"Progress: {summary['progress']['progress_percentage']:.1f}%")

    if summary['progress']['design_complete']:
        logger.info("\n✓ Design phases (1-4) complete!")
        logger.info("\nNext step: Run Phase 5-9 with:")
        logger.info(f"  python3 run_phase5_9.py {session_id} --mock")
    else:
        logger.info(f"\n⚠ Design incomplete. Run remaining phases to continue.")

    # Show validation
    validation = summary['validation']
    if validation['warnings']:
        logger.warning("\nWarnings:")
        for warning in validation['warnings']:
            logger.warning(f"  - {warning}")

    if validation['issues']:
        logger.error("\nIssues:")
        for issue in validation['issues']:
            logger.error(f"  - {issue}")
        return False

    return True


if __name__ == "__main__":
    from typing import Optional
    main()
