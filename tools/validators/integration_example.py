"""
Integration Example: Using Validators in MV Orchestra Pipeline

This example demonstrates how to integrate validators into the
MV Orchestra orchestration pipeline.
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import SharedState
from tools.validators import validate_clip_division, validate_phase4_strategies


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_phase_with_validation(
    session_id: str,
    phase_number: int,
    phase_runner_func,
    validator_func=None
) -> Dict[str, Any]:
    """
    Run a phase with optional validation.

    Args:
        session_id: Session identifier
        phase_number: Phase number
        phase_runner_func: Function to run the phase
        validator_func: Optional validation function

    Returns:
        Phase results dictionary

    Raises:
        RuntimeError: If validation fails critically
    """
    logger.info(f"Running Phase {phase_number}...")

    # Run the phase
    try:
        results = phase_runner_func(session_id)
        logger.info(f"Phase {phase_number} completed successfully")
    except Exception as e:
        logger.error(f"Phase {phase_number} failed: {e}")
        raise

    # Run validation if provided
    if validator_func:
        logger.info(f"Validating Phase {phase_number} output...")

        try:
            validation_report = validator_func(session_id)

            if validation_report['summary']['overall_status'] == 'PASS':
                logger.info(f"Phase {phase_number} validation: PASS")
            else:
                failed_checks = validation_report['summary']['failed_checks']
                warnings = validation_report['summary']['warnings']

                logger.warning(
                    f"Phase {phase_number} validation: FAIL "
                    f"({failed_checks} failed checks, {warnings} warnings)"
                )

                # Log specific failures
                for check_name, check_result in validation_report['validation_results'].items():
                    if not check_result.get('passed', True):
                        logger.warning(f"  - {check_name}: {check_result['message']}")

        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            # Don't raise - validation failure shouldn't stop the pipeline

    return results


def run_orchestration_with_validation(session_id: str) -> None:
    """
    Example: Run full orchestration pipeline with validation.

    Args:
        session_id: Session identifier
    """
    from phase3.runner import run_phase3
    from phase4.runner import run_phase4

    logger.info(f"Starting orchestration with validation for session {session_id}")

    # Phase 3: Clip Division (with validation)
    phase3_results = run_phase_with_validation(
        session_id=session_id,
        phase_number=3,
        phase_runner_func=run_phase3,
        validator_func=validate_clip_division
    )

    # Phase 4: Generation Strategy (with validation)
    phase4_results = run_phase_with_validation(
        session_id=session_id,
        phase_number=4,
        phase_runner_func=run_phase4,
        validator_func=validate_phase4_strategies
    )

    logger.info("Orchestration completed")


def validate_before_next_phase(session_id: str, phase: int, strict: bool = False) -> bool:
    """
    Validate a phase before proceeding to the next phase.

    Args:
        session_id: Session identifier
        phase: Phase number to validate
        strict: If True, fail on any validation error. If False, only fail on critical errors.

    Returns:
        True if validation passes, False otherwise
    """
    logger.info(f"Validating Phase {phase} before proceeding...")

    try:
        if phase == 3:
            report = validate_clip_division(session_id)
        elif phase == 4:
            report = validate_phase4_strategies(session_id)
        else:
            logger.warning(f"No validator available for Phase {phase}")
            return True

        # Check validation status
        if report['summary']['overall_status'] == 'PASS':
            logger.info(f"Phase {phase} validation passed")
            return True

        # In strict mode, fail on any validation error
        if strict:
            logger.error(f"Phase {phase} validation failed (strict mode)")
            return False

        # In non-strict mode, allow warnings but check for critical failures
        failed_checks = report['summary']['failed_checks']

        # Define critical checks that must pass
        critical_checks = {
            3: ['clip_id_uniqueness', 'timing_consistency'],
            4: ['strategy_completeness', 'generation_mode_validity']
        }

        if phase in critical_checks:
            for check_name in critical_checks[phase]:
                check_result = report['validation_results'].get(check_name, {})
                if not check_result.get('passed', True):
                    logger.error(f"Critical check failed: {check_name}")
                    return False

        # Non-critical failures - log warning but allow to continue
        logger.warning(
            f"Phase {phase} has {failed_checks} failed checks, "
            "but no critical failures detected"
        )
        return True

    except Exception as e:
        logger.error(f"Validation error: {e}")
        # In strict mode, fail on validation errors
        return not strict


def example_usage():
    """Example usage of validators."""
    # Example 1: Validate a specific session
    session_id = "mvorch_20251114_163428_1d481b47"

    print("\n=== Example 1: Direct Validation ===")
    report = validate_clip_division(session_id)
    print(f"Phase 3 Status: {report['summary']['overall_status']}")

    # Example 2: Validate before proceeding
    print("\n=== Example 2: Gate Before Next Phase ===")
    can_proceed = validate_before_next_phase(session_id, phase=3, strict=False)
    print(f"Can proceed to Phase 4: {can_proceed}")

    # Example 3: Run with validation
    print("\n=== Example 3: Run Phase with Auto-Validation ===")
    # run_orchestration_with_validation(session_id)


if __name__ == "__main__":
    example_usage()
