#!/usr/bin/env python3
"""
MV Orchestra v2.8 - Main Pipeline Runner

Orchestrates the complete multi-director competition pipeline for music video generation.
Runs all phases from Phase 0 (Overall Design) through Phase 5 (Claude Review).

Usage:
    python3 run_all_phases.py <session_id> [OPTIONS]

Examples:
    # Basic usage with auto-detected input
    python3 run_all_phases.py my_session

    # Specify custom audio and lyrics
    python3 run_all_phases.py my_session --audio song.mp3 --lyrics song.txt

    # Rebuild analysis from audio
    python3 run_all_phases.py my_session --rebuild-analysis --audio song.mp3 --lyrics song.txt

    # Skip Phase 5 (Claude review)
    python3 run_all_phases.py my_session --skip-phase5

    # Use real Claude API for Phase 5
    python3 run_all_phases.py my_session --phase5-mode real

Author: MV Orchestra Team
Version: 2.8
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List

from core import (
    SharedState,
    read_json,
    write_json,
    get_project_root,
    get_session_dir,
    ensure_dir,
    get_iso_timestamp
)
from phase0 import run_phase0
from phase1 import run_phase1
from phase2 import run_phase2
from phase3 import run_phase3
from phase4 import run_phase4
from phase5 import run_phase5


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the pipeline.

    Args:
        verbose: If True, enable DEBUG level logging

    Returns:
        Logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="MV Orchestra v2.8 - Multi-Director Music Video Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with auto-detected input
  python3 run_all_phases.py my_session

  # Specify custom audio and lyrics
  python3 run_all_phases.py my_session --audio song.mp3 --lyrics song.txt

  # Rebuild analysis from audio
  python3 run_all_phases.py my_session --rebuild-analysis --audio song.mp3 --lyrics song.txt

  # Skip validation
  python3 run_all_phases.py my_session --no-validate

  # Use real Claude API for Phase 5
  python3 run_all_phases.py my_session --phase5-mode real

For more information, see the documentation at:
  - USER_GUIDE.md
  - README.md
        """
    )

    # Required arguments
    parser.add_argument(
        'session_id',
        type=str,
        help='Session ID (unique identifier for this pipeline run)'
    )

    # Input file arguments
    parser.add_argument(
        '--audio',
        type=str,
        default=None,
        help='MP3 file path (default: auto-detect in shared-workspace/input/*.mp3)'
    )
    parser.add_argument(
        '--lyrics',
        type=str,
        default=None,
        help='Lyrics text file (default: shared-workspace/input/lyrics.txt)'
    )
    parser.add_argument(
        '--analysis',
        type=str,
        default=None,
        help='Existing analysis.json (default: shared-workspace/input/analysis.json)'
    )

    # Analysis control
    parser.add_argument(
        '--rebuild-analysis',
        action='store_true',
        help='Force rebuild analysis.json from --audio and --lyrics'
    )

    # Phase control
    parser.add_argument(
        '--skip-phase5',
        action='store_true',
        help='Skip Phase 5 (Claude review)'
    )
    parser.add_argument(
        '--phase5-mode',
        type=str,
        choices=['skip', 'mock', 'real'],
        default='skip',
        help='Phase 5 mode: skip|mock|real (default: skip)'
    )

    # Execution control
    parser.add_argument(
        '--mode',
        type=str,
        choices=['mock', 'claudecode', 'interactive'],
        default='mock',
        help='Evaluation mode: mock|claudecode|interactive (default: mock)'
    )
    parser.add_argument(
        '--mock-mode',
        action='store_true',
        help='DEPRECATED: Use --mode mock instead'
    )
    parser.add_argument(
        '--real-mode',
        action='store_true',
        help='DEPRECATED: Use --mode claudecode instead'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        default=True,
        help='Run validators after Phase 3 and 4 (default: True)'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation steps'
    )

    # Output control
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose logging (DEBUG level)'
    )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Minimal output (WARNING level only)'
    )

    args = parser.parse_args()

    # Handle deprecated flags
    if args.real_mode:
        print("⚠ Warning: --real-mode is deprecated. Use --mode claudecode instead.")
        args.mode = 'claudecode'
    if args.mock_mode:
        # mock_mode defaults to True, only warn if explicitly set
        if '--mock-mode' in sys.argv:
            print("⚠ Warning: --mock-mode is deprecated. Use --mode mock instead.")
        args.mode = 'mock'

    # Handle other flags
    if args.no_validate:
        args.validate = False
    if args.skip_phase5:
        args.phase5_mode = 'skip'

    return args


def find_input_file(pattern: str, default_path: str, logger: logging.Logger) -> Optional[Path]:
    """
    Find an input file by pattern or use default path.

    Args:
        pattern: Glob pattern to search for
        default_path: Default path if pattern doesn't match
        logger: Logger instance

    Returns:
        Path to file or None if not found
    """
    project_root = get_project_root()
    input_dir = project_root / 'shared-workspace' / 'input'

    # Try pattern match
    matches = list(input_dir.glob(pattern))
    if matches:
        return matches[0]

    # Try default path
    default = input_dir / default_path
    if default.exists():
        return default

    return None


def ensure_analysis_json(args: argparse.Namespace, logger: logging.Logger) -> Path:
    """
    Load or build analysis.json.

    Args:
        args: Command-line arguments
        logger: Logger instance

    Returns:
        Path to analysis.json

    Raises:
        FileNotFoundError: If analysis.json cannot be found or built
    """
    project_root = get_project_root()
    input_dir = project_root / 'shared-workspace' / 'input'

    # If analysis path specified, use it
    if args.analysis:
        analysis_path = Path(args.analysis)
        if not analysis_path.exists():
            raise FileNotFoundError(f"Analysis file not found: {analysis_path}")
        logger.info(f"Using specified analysis file: {analysis_path}")
        return analysis_path

    # If rebuild requested, build from audio
    if args.rebuild_analysis:
        if not args.audio:
            raise ValueError("--rebuild-analysis requires --audio argument")

        logger.info("Rebuilding analysis.json from audio file...")

        # Import build_analysis tool
        try:
            from tools.build_analysis import build_analysis_from_audio

            audio_path = Path(args.audio)
            lyrics_path = Path(args.lyrics) if args.lyrics else None

            # Build analysis
            analysis_data = build_analysis_from_audio(
                audio_path=str(audio_path),
                lyrics_path=str(lyrics_path) if lyrics_path else None,
                output_path=str(input_dir / 'analysis.json')
            )

            logger.info(f"Analysis saved to: {input_dir / 'analysis.json'}")
            return input_dir / 'analysis.json'

        except ImportError:
            logger.warning("build_analysis tool not available, using manual approach")
            raise FileNotFoundError(
                "Cannot rebuild analysis: build_analysis tool not found. "
                "Please provide --analysis with an existing analysis.json file."
            )

    # Try to find existing analysis.json
    analysis_path = input_dir / 'analysis.json'
    if analysis_path.exists():
        logger.info(f"Using existing analysis file: {analysis_path}")
        return analysis_path

    # Try sample_analysis.json as fallback
    sample_path = project_root / 'sample_analysis.json'
    if sample_path.exists():
        logger.warning(f"analysis.json not found, using sample: {sample_path}")
        return sample_path

    raise FileNotFoundError(
        "No analysis.json found. Please provide one of:\n"
        "  --analysis PATH           Use existing analysis.json\n"
        "  --rebuild-analysis        Build from audio file\n"
        "  Or place analysis.json in shared-workspace/input/"
    )


def run_phase_with_logging(
    phase_num: int,
    phase_name: str,
    runner_func: callable,
    args: argparse.Namespace,
    logger: logging.Logger,
    **kwargs
) -> Dict[str, Any]:
    """
    Run a phase with consistent logging.

    Args:
        phase_num: Phase number (0-5)
        phase_name: Human-readable phase name
        runner_func: Phase runner function
        args: Command-line arguments
        logger: Logger instance
        **kwargs: Additional arguments to pass to runner

    Returns:
        Phase results dictionary
    """
    logger.info("=" * 70)
    logger.info(f"Phase {phase_num}: {phase_name}")
    logger.info("=" * 70)

    try:
        # Run the phase
        # Support both old mock_mode and new mode parameter
        if 'mock_mode' in runner_func.__code__.co_varnames:
            # Old-style phase runner (backward compatibility)
            results = runner_func(**kwargs, mock_mode=(args.mode == 'mock'))
        else:
            # New-style phase runner with mode parameter
            results = runner_func(**kwargs, mode=args.mode)

        # Log winner
        if 'winner' in results:
            winner = results['winner']
            logger.info(f"✓ Winner: {winner.get('director', 'Unknown')}")
            logger.info(f"  Score: {winner.get('score', 0):.1f}/100")

        logger.info(f"✓ Phase {phase_num} completed successfully")
        return results

    except Exception as e:
        logger.error(f"✗ Phase {phase_num} failed: {e}")
        raise


def run_optimization_tools(
    session_id: str,
    phase_num: int,
    logger: logging.Logger
) -> None:
    """
    Run optimization tools after specific phases.

    Args:
        session_id: Session ID
        phase_num: Phase number
        logger: Logger instance
    """
    if phase_num == 2:
        # Run emotion target builder after Phase 2
        try:
            logger.info("\n→ Running emotion target builder...")
            from tools.optimization.emotion_target_builder import EmotionTargetBuilder

            builder = EmotionTargetBuilder(session_id)
            result = builder.build_targets()

            if result['success']:
                logger.info(f"  ✓ Built {result['stats']['total_targets']} emotion targets")
            else:
                logger.warning(f"  ⚠ Emotion target builder had warnings")

        except Exception as e:
            logger.warning(f"  ⚠ Emotion target builder failed: {e}")

    elif phase_num == 3:
        # Run clip optimizer after Phase 3
        try:
            logger.info("\n→ Running clip optimizer...")
            from tools.optimization.clip_optimizer import ClipOptimizer

            optimizer = ClipOptimizer(session_id)
            result = optimizer.optimize_clips()

            if result['success']:
                logger.info(f"  ✓ Optimized {result['stats']['total_clips']} clips")
                logger.info(f"  ✓ Applied {result['stats']['optimizations_applied']} optimizations")
            else:
                logger.warning(f"  ⚠ Clip optimizer had warnings")

        except Exception as e:
            logger.warning(f"  ⚠ Clip optimizer failed: {e}")


def run_validation_tools(
    session_id: str,
    phase_num: int,
    logger: logging.Logger
) -> None:
    """
    Run validation tools after specific phases.

    Args:
        session_id: Session ID
        phase_num: Phase number
        logger: Logger instance
    """
    if phase_num == 3:
        # Validate clip division after Phase 3
        try:
            logger.info("\n→ Validating clip division...")
            from tools.validators import validate_clip_division

            result = validate_clip_division(session_id)

            if result.get('valid'):
                logger.info(f"  ✓ Clip division is valid")
            else:
                errors = result.get('errors', [])
                logger.warning(f"  ⚠ Clip division has {len(errors)} errors")
                for error in errors[:3]:  # Show first 3 errors
                    logger.warning(f"    - {error}")

        except Exception as e:
            logger.warning(f"  ⚠ Clip division validation failed: {e}")

    elif phase_num == 4:
        # Validate Phase 4 strategies
        try:
            logger.info("\n→ Validating generation strategies...")
            from tools.validators import validate_phase4_strategies

            result = validate_phase4_strategies(session_id)

            if result.get('valid'):
                logger.info(f"  ✓ Generation strategies are valid")
            else:
                errors = result.get('errors', [])
                logger.warning(f"  ⚠ Strategies have {len(errors)} errors")
                for error in errors[:3]:  # Show first 3 errors
                    logger.warning(f"    - {error}")

        except Exception as e:
            logger.warning(f"  ⚠ Strategy validation failed: {e}")


def generate_summary(session: SharedState, logger: logging.Logger) -> Dict[str, Any]:
    """
    Generate final summary report.

    Args:
        session: Session state
        logger: Logger instance

    Returns:
        Summary dictionary
    """
    summary = {
        'session_id': session.session_id,
        'completed_at': get_iso_timestamp(),
        'phases': {},
        'winners': {},
        'statistics': {}
    }

    # Collect phase information
    for phase_num, phase_data in session.phases.items():
        summary['phases'][f'phase_{phase_num}'] = {
            'status': phase_data.status,
            'started_at': phase_data.started_at,
            'completed_at': phase_data.completed_at
        }

        # Extract winner information
        if phase_data.data and 'winner' in phase_data.data:
            winner = phase_data.data['winner']
            summary['winners'][f'phase_{phase_num}'] = {
                'director': winner.get('director'),
                'score': winner.get('score'),
                'concept': winner.get('concept', '')[:200]  # First 200 chars
            }

    # Calculate statistics
    if 'phase_3' in summary['phases']:
        try:
            phase3_data = session.get_phase_data(3)
            if phase3_data and 'winner' in phase3_data:
                clips = phase3_data['winner'].get('clips', [])
                summary['statistics']['total_clips'] = len(clips)
                summary['statistics']['total_duration'] = sum(
                    c.get('duration', 0) for c in clips
                )
        except:
            pass

    return summary


def print_summary(summary: Dict[str, Any], logger: logging.Logger) -> None:
    """
    Print summary report to console.

    Args:
        summary: Summary dictionary
        logger: Logger instance
    """
    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 70)

    logger.info(f"\nSession ID: {summary['session_id']}")
    logger.info(f"Completed at: {summary['completed_at']}")

    # Print phase winners
    logger.info("\n" + "-" * 70)
    logger.info("Phase Winners:")
    logger.info("-" * 70)

    for phase_name, winner in summary['winners'].items():
        phase_num = phase_name.split('_')[1]
        logger.info(f"\nPhase {phase_num}: {winner.get('director', 'Unknown')}")
        score = winner.get('score')
        if score is not None:
            logger.info(f"  Score: {score:.1f}/100")
        concept = winner.get('concept', '')
        if concept:
            logger.info(f"  Concept: {concept}")

    # Print statistics
    if summary['statistics']:
        logger.info("\n" + "-" * 70)
        logger.info("Statistics:")
        logger.info("-" * 70)
        for key, value in summary['statistics'].items():
            logger.info(f"  {key}: {value}")

    logger.info("\n" + "=" * 70)


def run_pipeline(
    session_id: str,
    analysis_path: Path,
    args: argparse.Namespace,
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Run the complete pipeline.

    Args:
        session_id: Session ID
        analysis_path: Path to analysis.json
        args: Command-line arguments
        logger: Logger instance

    Returns:
        Summary dictionary
    """
    logger.info("\n" + "=" * 70)
    logger.info("MV ORCHESTRA v2.8 - PIPELINE START")
    logger.info("=" * 70)
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Analysis: {analysis_path}")
    logger.info(f"Evaluation Mode: {args.mode}")
    logger.info(f"Validation: {args.validate}")
    if args.mode == 'claudecode':
        logger.info("⚠ Claude Code mode: Evaluations will be exported for manual processing")
    elif args.mode == 'interactive':
        logger.info("⚠ Interactive mode: You will be prompted to provide evaluations")
    logger.info("=" * 70)

    # Create or load session
    try:
        session = SharedState.load_session(session_id)
        logger.info(f"Loaded existing session: {session_id}")
    except:
        # Create new session with specific ID
        session = SharedState(session_id=session_id)
        session.metadata.input_files = {'analysis': str(analysis_path)}
        ensure_dir(session.session_dir)
        session.save_session()
        logger.info(f"Created new session: {session_id}")

    # Load analysis
    analysis = read_json(analysis_path)
    logger.info(f"Loaded analysis: {analysis.get('title', 'Unknown')}")

    # Phase 0: Overall Design
    phase0_results = run_phase_with_logging(
        0, "Overall Design",
        run_phase0,
        args, logger,
        session_id=session_id,
        analysis_path=str(analysis_path)
    )

    # Phase 1: Character Design
    phase1_results = run_phase_with_logging(
        1, "Character Design",
        run_phase1,
        args, logger,
        session_id=session_id
    )

    # Phase 2: Section Direction
    phase2_results = run_phase_with_logging(
        2, "Section Direction",
        run_phase2,
        args, logger,
        session_id=session_id
    )
    run_optimization_tools(session_id, 2, logger)

    # Phase 3: Clip Division
    phase3_results = run_phase_with_logging(
        3, "Clip Division",
        run_phase3,
        args, logger,
        session_id=session_id
    )
    run_optimization_tools(session_id, 3, logger)
    if args.validate:
        run_validation_tools(session_id, 3, logger)

    # Phase 4: Generation Strategy
    phase4_results = run_phase_with_logging(
        4, "Generation Strategy",
        run_phase4,
        args, logger,
        session_id=session_id
    )
    if args.validate:
        run_validation_tools(session_id, 4, logger)

    # Phase 5: Claude Review (optional)
    if args.phase5_mode != 'skip':
        logger.info("\n" + "=" * 70)
        logger.info(f"Phase 5: Claude Review (mode: {args.phase5_mode})")
        logger.info("=" * 70)

        try:
            phase5_results = run_phase5(
                session_id=session_id,
                mode=args.phase5_mode
            )
            logger.info("✓ Phase 5 completed")
        except Exception as e:
            logger.warning(f"⚠ Phase 5 skipped or failed: {e}")
    else:
        logger.info("\n→ Skipping Phase 5 (Claude Review)")

    # Reload session to get all updates
    session = SharedState.load_session(session_id)

    # Generate summary
    summary = generate_summary(session, logger)

    # Save summary to session directory
    session_dir = get_session_dir(session_id)
    summary_path = session_dir / 'pipeline_summary.json'
    write_json(summary_path, summary)
    logger.info(f"\n✓ Summary saved to: {summary_path}")

    return summary


def main():
    """Main entry point."""
    args = parse_args()

    # Setup logging
    if args.quiet:
        logger = setup_logging(verbose=False)
        logger.setLevel(logging.WARNING)
    else:
        logger = setup_logging(verbose=args.verbose)

    try:
        # Validate inputs
        logger.info("Validating inputs...")

        # Ensure analysis.json
        analysis_path = ensure_analysis_json(args, logger)

        # Run pipeline
        summary = run_pipeline(args.session_id, analysis_path, args, logger)

        # Print summary
        print_summary(summary, logger)

        logger.info("\n✓ Pipeline completed successfully!")
        logger.info(f"✓ Session saved to: {get_session_dir(args.session_id)}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {e}")
        return 1

    except Exception as e:
        logger.error(f"✗ Pipeline failed: {e}")
        if args.verbose:
            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
