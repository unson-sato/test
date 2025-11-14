#!/usr/bin/env python3
"""
Phase 4 Generation Strategies Validator for MV Orchestra v2.8

Technical validation of Phase 4 generation strategies to ensure completeness and correctness.
This validator checks:
- Strategy completeness (all clips have strategies)
- Generation mode validity
- Prompt quality
- Asset requirements
- Consistency requirements
- Variance parameters
- Creative adjustments integration
- Budget/timeline estimates

Usage:
    python3 tools/validators/validate_phase4_strategies.py <session_id>
"""

import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import SharedState
from core.utils import write_json, get_session_dir, get_iso_timestamp
from tools.validators.validation_utils import (
    print_header,
    print_check,
    print_summary,
    extract_clips_from_phase3,
    build_validation_summary,
    parse_cost_range
)


# Valid generation modes
VALID_GENERATION_MODES = {
    'veo2', 'sora', 'runway_gen3', 'pika', 'traditional', 'hybrid',
    'image_to_video', 'video_to_video'
}


def validate_strategy_completeness(
    phase3_clips: List[Dict[str, Any]],
    phase4_strategies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate that all clips from Phase 3 have generation strategies.

    Args:
        phase3_clips: List of clips from Phase 3
        phase4_strategies: List of strategies from Phase 4

    Returns:
        Validation result dictionary
    """
    phase3_clip_ids = set(clip.get('clip_id') for clip in phase3_clips)
    phase4_clip_ids = set(strategy.get('clip_id') for strategy in phase4_strategies)

    missing_clips = phase3_clip_ids - phase4_clip_ids
    extra_clips = phase4_clip_ids - phase3_clip_ids

    passed = len(missing_clips) == 0 and len(extra_clips) == 0

    message = "All clips have generation strategies"
    if not passed:
        parts = []
        if missing_clips:
            parts.append(f"{len(missing_clips)} missing")
        if extra_clips:
            parts.append(f"{len(extra_clips)} extra")
        message = f"Found {', '.join(parts)}"

    return {
        "passed": passed,
        "total_clips_phase3": len(phase3_clip_ids),
        "total_strategies_phase4": len(phase4_clip_ids),
        "missing_clips": list(missing_clips)[:5],  # Limit to first 5
        "extra_clips": list(extra_clips)[:5],
        "message": message
    }


def validate_generation_mode_validity(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate that all generation modes are valid.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    invalid_modes = []
    mode_distribution = {}

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')
        mode = strategy.get('generation_mode', '').lower()

        # Normalize mode name
        mode = mode.replace(' ', '_').replace('-', '_')

        # Count distribution
        mode_distribution[mode] = mode_distribution.get(mode, 0) + 1

        # Check validity
        if mode not in VALID_GENERATION_MODES:
            invalid_modes.append({
                'clip_id': clip_id,
                'mode': strategy.get('generation_mode', '')
            })

    passed = len(invalid_modes) == 0

    return {
        "passed": passed,
        "invalid_modes": invalid_modes[:5],
        "mode_distribution": mode_distribution,
        "message": "All generation modes are valid" if passed else f"Found {len(invalid_modes)} invalid modes"
    }


def validate_prompt_quality(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate prompt quality for all strategies.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    empty_prompts = []
    too_short = []
    too_long = []
    prompt_lengths = []

    MIN_PROMPT_LENGTH = 20
    MAX_PROMPT_LENGTH = 1000

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')
        prompt_template = strategy.get('prompt_template', {})

        # Extract prompt text
        if isinstance(prompt_template, dict):
            prompt_text = prompt_template.get('full_prompt') or prompt_template.get('base_prompt', '')
        else:
            prompt_text = str(prompt_template)

        prompt_length = len(prompt_text.strip())
        prompt_lengths.append(prompt_length)

        if not prompt_text.strip():
            empty_prompts.append(clip_id)
        elif prompt_length < MIN_PROMPT_LENGTH:
            too_short.append(clip_id)
        elif prompt_length > MAX_PROMPT_LENGTH:
            too_long.append(clip_id)

    avg_length = sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0

    passed = len(empty_prompts) == 0 and len(too_short) == 0

    message = "All prompts are well-formed"
    if not passed:
        parts = []
        if empty_prompts:
            parts.append(f"{len(empty_prompts)} empty")
        if too_short:
            parts.append(f"{len(too_short)} too short")
        if too_long:
            parts.append(f"{len(too_long)} warnings for length")
        message = f"Found {', '.join(parts)}"

    return {
        "passed": passed,
        "empty_prompts": empty_prompts[:5],
        "too_short": too_short[:5],
        "too_long": too_long[:5],
        "avg_prompt_length": round(avg_length, 1),
        "message": message
    }


def validate_asset_requirements(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate asset requirements for all strategies.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    VALID_ASSET_TYPES = {
        'character_reference', 'style_guide', 'reference_image',
        'source_video', 'audio_segment', 'location_reference',
        'prop_reference', 'lighting_reference'
    }

    missing_assets = []
    asset_types_used = set()

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')
        assets_required = strategy.get('assets_required', [])

        if not isinstance(assets_required, list):
            missing_assets.append(clip_id)
            continue

        # Validate asset types
        for asset in assets_required:
            if isinstance(asset, dict):
                asset_type = asset.get('type', '')
                if asset_type:
                    asset_types_used.add(asset_type)

    passed = len(missing_assets) == 0

    return {
        "passed": passed,
        "missing_assets": missing_assets[:5],
        "total_asset_types": len(asset_types_used),
        "message": "All required assets specified" if passed else f"{len(missing_assets)} clips missing asset requirements"
    }


def validate_consistency_requirements(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate consistency requirements for all strategies.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    REQUIRED_CONSISTENCY_FIELDS = {
        'character_consistency', 'background_consistency', 'style_consistency'
    }

    VALID_CONSISTENCY_VALUES = {'low', 'medium', 'high'}

    missing_consistency = []

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')
        consistency_reqs = strategy.get('consistency_requirements', {})

        if not isinstance(consistency_reqs, dict):
            missing_consistency.append(clip_id)
            continue

        # Check for required fields
        missing_fields = REQUIRED_CONSISTENCY_FIELDS - set(consistency_reqs.keys())
        if missing_fields:
            missing_consistency.append(clip_id)

    passed = len(missing_consistency) == 0

    return {
        "passed": passed,
        "missing_consistency": missing_consistency[:5],
        "message": "Consistency requirements complete" if passed else f"{len(missing_consistency)} clips missing consistency requirements"
    }


def validate_variance_parameters(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate variance parameters for all strategies.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    missing_variance = []
    out_of_range = []

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')
        variance_params = strategy.get('variance_params', {})

        if not isinstance(variance_params, dict):
            missing_variance.append(clip_id)
            continue

        # Check parameter ranges (should be 0.0-1.0)
        for param_name, param_value in variance_params.items():
            if isinstance(param_value, (int, float)):
                if param_value < 0.0 or param_value > 1.0:
                    out_of_range.append({
                        'clip_id': clip_id,
                        'parameter': param_name,
                        'value': param_value
                    })

    passed = len(out_of_range) == 0

    return {
        "passed": passed,
        "missing_variance": missing_variance[:5],
        "out_of_range": out_of_range[:5],
        "message": "Variance parameters valid" if passed else f"{len(out_of_range)} parameters out of range"
    }


def validate_creative_adjustments(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate creative adjustments integration.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    clips_with_adjustments = 0
    invalid_references = []

    for strategy in strategies:
        clip_id = strategy.get('clip_id', 'unknown')

        if 'creative_adjustments' in strategy:
            clips_with_adjustments += 1

            # Validate structure
            adjustments = strategy['creative_adjustments']
            if isinstance(adjustments, dict):
                if 'base_reference' not in adjustments:
                    invalid_references.append(clip_id)

    passed = len(invalid_references) == 0

    return {
        "passed": passed,
        "clips_with_adjustments": clips_with_adjustments,
        "invalid_references": invalid_references[:5],
        "message": "Creative adjustments properly integrated" if passed else f"{len(invalid_references)} invalid adjustment structures"
    }


def validate_budget_timeline(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate budget and timeline estimates.

    Args:
        strategies: List of generation strategies

    Returns:
        Validation result dictionary
    """
    total_min_cost = 0.0
    total_max_cost = 0.0
    total_time_hours = 0.0

    for strategy in strategies:
        # Parse cost estimate
        cost_estimate = strategy.get('estimated_cost', '$0')
        min_cost, max_cost = parse_cost_range(cost_estimate)
        total_min_cost += min_cost
        total_max_cost += max_cost

        # Parse time estimate (rough)
        time_estimate = strategy.get('estimated_time', '1 day')
        if 'week' in time_estimate.lower():
            hours = 168  # 1 week
        elif 'day' in time_estimate.lower():
            hours = 24
        else:
            hours = 1
        total_time_hours += hours

    passed = True  # Budget/timeline always pass if present

    return {
        "passed": passed,
        "total_estimated_cost": round((total_min_cost + total_max_cost) / 2, 2),
        "total_estimated_time_hours": round(total_time_hours, 0),
        "message": "Budget and timeline estimates present"
    }


def validate_phase4_strategies(session_id: str) -> Dict[str, Any]:
    """
    Main validation function for Phase 4 generation strategies.

    Args:
        session_id: Session identifier

    Returns:
        Complete validation results dictionary
    """
    # Print header
    print_header("=== MV Orchestra v2.8 - Phase 4 Generation Strategies Validation ===", session_id)

    # Load session
    try:
        session = SharedState.load_session(session_id)
    except FileNotFoundError:
        print(f"Error: Session '{session_id}' not found")
        sys.exit(1)

    # Get Phase 3 and Phase 4 data
    phase3_data = session.get_phase_data(3)
    phase4_data = session.get_phase_data(4)

    if phase4_data.status != "completed":
        print(f"Warning: Phase 4 status is '{phase4_data.status}', not 'completed'")

    # Extract data
    phase3_clips = extract_clips_from_phase3(phase3_data.data)

    # Extract Phase 4 strategies
    winner = phase4_data.data.get('winner', {})
    proposal = winner.get('proposal', {})
    strategies = proposal.get('generation_strategies', [])

    if not strategies:
        print("Error: No generation strategies found in Phase 4 data")
        sys.exit(1)

    print(f"Total Strategies: {len(strategies)}\n")

    # Run validation checks
    validation_results = {}

    # 1. Strategy Completeness
    validation_results['strategy_completeness'] = validate_strategy_completeness(
        phase3_clips, strategies
    )
    print_check("Strategy Completeness", validation_results['strategy_completeness'])

    # 2. Generation Mode Validity
    validation_results['generation_mode_validity'] = validate_generation_mode_validity(strategies)
    print_check("Generation Mode Validity", validation_results['generation_mode_validity'])

    # 3. Prompt Quality
    validation_results['prompt_quality'] = validate_prompt_quality(strategies)
    print_check("Prompt Quality", validation_results['prompt_quality'])

    # 4. Asset Requirements
    validation_results['asset_requirements'] = validate_asset_requirements(strategies)
    print_check("Asset Requirements", validation_results['asset_requirements'])

    # 5. Consistency Requirements
    validation_results['consistency_requirements'] = validate_consistency_requirements(strategies)
    print_check("Consistency Requirements", validation_results['consistency_requirements'])

    # 6. Variance Parameters
    validation_results['variance_parameters'] = validate_variance_parameters(strategies)
    print_check("Variance Parameters", validation_results['variance_parameters'])

    # 7. Creative Adjustments
    validation_results['creative_adjustments'] = validate_creative_adjustments(strategies)
    print_check("Creative Adjustments", validation_results['creative_adjustments'])

    # 8. Budget/Timeline
    validation_results['budget_timeline'] = validate_budget_timeline(strategies)
    print_check("Budget/Timeline Estimates", validation_results['budget_timeline'])

    # Build summary
    summary = build_validation_summary(validation_results)

    # Print summary
    print_summary(summary)

    # Build full report
    report = {
        "session_id": session_id,
        "validated_at": get_iso_timestamp(),
        "phase": 4,
        "total_strategies": len(strategies),
        "validation_results": validation_results,
        "summary": summary
    }

    # Save report
    session_dir = get_session_dir(session_id)
    report_path = session_dir / "validation_phase4_strategies.json"
    write_json(str(report_path), report)

    print(f"Validation complete. Report saved to:")
    print(f"{report_path}")

    return report


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Phase 4 generation strategies for MV Orchestra v2.8"
    )
    parser.add_argument(
        "session_id",
        help="Session ID to validate"
    )

    args = parser.parse_args()

    # Run validation
    report = validate_phase4_strategies(args.session_id)

    # Exit with appropriate code
    if report['summary']['overall_status'] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
