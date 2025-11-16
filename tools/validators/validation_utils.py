"""
Shared validation utilities for MV Orchestra v2.8 validators

This module provides common utilities used across different validators including:
- Console formatting functions
- Data extraction helpers
- Validation result builders
- Common validation checks
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


def print_header(title: str, session_id: str) -> None:
    """
    Print a formatted header for validation output.

    Args:
        title: Title of the validation
        session_id: Session identifier
    """
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Session: {session_id}")
    print()


def print_check(name: str, result: Dict[str, Any], indent: int = 0) -> None:
    """
    Print a formatted validation check result.

    Args:
        name: Name of the check
        result: Result dictionary containing 'passed', 'message', etc.
        indent: Indentation level (spaces)
    """
    indent_str = " " * indent
    status = "✓" if result["passed"] else "✗"
    status_text = "PASS" if result["passed"] else "FAIL"

    # Add percentage or count info if available
    extra_info = ""
    if "coverage_percentage" in result:
        extra_info = f" ({result['coverage_percentage']:.1f}%)"
    elif "alignment_percentage" in result:
        extra_info = f" ({result['alignment_percentage']:.1f}%)"

    print(f"{indent_str}[{status}] {name}: {status_text}{extra_info}")
    print(f"{indent_str}    {result['message']}")

    # Print warnings if any
    if "warnings" in result and result["warnings"]:
        for warning in result["warnings"]:
            print(f"{indent_str}    ! {warning}")


def print_summary(summary: Dict[str, Any]) -> None:
    """
    Print validation summary.

    Args:
        summary: Summary dictionary with counts and status
    """
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Passed: {summary['passed_checks']}/{summary['total_checks']} checks")
    if summary.get('warnings', 0) > 0:
        print(f"Warnings: {summary['warnings']}")
    print()


def validate_unique_ids(items: List[Dict[str, Any]], id_key: str = "clip_id") -> Dict[str, Any]:
    """
    Validate that all IDs are unique in a list of items.

    Args:
        items: List of items to check
        id_key: Key name for the ID field

    Returns:
        Validation result dictionary
    """
    ids = [item.get(id_key) for item in items if id_key in item]
    duplicate_ids = []
    seen = set()

    for item_id in ids:
        if item_id in seen:
            duplicate_ids.append(item_id)
        else:
            seen.add(item_id)

    passed = len(duplicate_ids) == 0

    return {
        "passed": passed,
        "duplicate_ids": duplicate_ids,
        "message": "All IDs are unique" if passed else f"Found {len(duplicate_ids)} duplicate IDs"
    }


def validate_timing_consistency(clips: List[Dict[str, Any]], tolerance: float = 0.01) -> Dict[str, Any]:
    """
    Validate timing consistency for clips.

    Args:
        clips: List of clip dictionaries
        tolerance: Tolerance for float comparisons (seconds)

    Returns:
        Validation result dictionary
    """
    issues = []

    for clip in clips:
        clip_id = clip.get('clip_id', 'unknown')
        start = clip.get('start_time', 0)
        end = clip.get('end_time', 0)
        duration = clip.get('duration', 0)

        # Check start < end
        if start >= end:
            issues.append(f"{clip_id}: start_time ({start}) >= end_time ({end})")
            continue

        # Check duration consistency
        expected_duration = end - start
        if abs(duration - expected_duration) > tolerance:
            issues.append(
                f"{clip_id}: duration mismatch (got {duration}, expected {expected_duration:.2f})"
            )

        # Check for negative values
        if start < 0 or end < 0 or duration < 0:
            issues.append(f"{clip_id}: negative timing values detected")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "message": "All clip timings are consistent" if passed else f"Found {len(issues)} timing issues"
    }


def validate_timeline_coverage(
    clips: List[Dict[str, Any]],
    total_duration: float,
    gap_tolerance: float = 0.5
) -> Dict[str, Any]:
    """
    Validate that clips cover the full timeline without gaps or overlaps.

    Args:
        clips: List of clip dictionaries
        total_duration: Total duration that should be covered
        gap_tolerance: Maximum allowed gap size (seconds)

    Returns:
        Validation result dictionary
    """
    # Sort clips by start time
    sorted_clips = sorted(clips, key=lambda c: c.get('start_time', 0))

    gaps = []
    overlaps = []
    current_time = 0.0

    for clip in sorted_clips:
        start = clip.get('start_time', 0)
        end = clip.get('end_time', 0)
        clip_id = clip.get('clip_id', 'unknown')

        # Check for gap
        gap_size = start - current_time
        if gap_size > gap_tolerance:
            gaps.append({
                'start': current_time,
                'end': start,
                'size': gap_size
            })

        # Check for overlap
        if start < current_time - 0.01:  # Small tolerance for rounding
            overlaps.append({
                'clip_id': clip_id,
                'overlap_start': start,
                'overlap_end': min(end, current_time),
                'size': current_time - start
            })

        current_time = max(current_time, end)

    # Check final coverage
    final_gap = total_duration - current_time
    if final_gap > gap_tolerance:
        gaps.append({
            'start': current_time,
            'end': total_duration,
            'size': final_gap
        })

    # Calculate coverage percentage
    coverage_percentage = (current_time / total_duration * 100) if total_duration > 0 else 0

    passed = len(gaps) == 0 and len(overlaps) == 0

    message = "Timeline fully covered"
    if not passed:
        parts = []
        if gaps:
            parts.append(f"{len(gaps)} gaps")
        if overlaps:
            parts.append(f"{len(overlaps)} overlaps")
        message = f"Found {', '.join(parts)}"

    return {
        "passed": passed,
        "gaps": gaps,
        "overlaps": overlaps,
        "coverage_percentage": round(coverage_percentage, 2),
        "message": message
    }


def validate_duration_sanity(
    clips: List[Dict[str, Any]],
    min_duration: float = 0.5,
    max_duration: float = 30.0
) -> Dict[str, Any]:
    """
    Validate that clip durations are within reasonable bounds.

    Args:
        clips: List of clip dictionaries
        min_duration: Minimum reasonable duration (seconds)
        max_duration: Maximum reasonable duration (seconds)

    Returns:
        Validation result dictionary
    """
    warnings = []
    durations = []

    for clip in clips:
        clip_id = clip.get('clip_id', 'unknown')
        duration = clip.get('duration', 0)
        durations.append(duration)

        if duration < min_duration:
            warnings.append(f"{clip_id}: duration too short ({duration}s < {min_duration}s)")

        if duration > max_duration:
            warnings.append(f"{clip_id}: duration too long ({duration}s > {max_duration}s)")

    # Calculate statistics
    if durations:
        min_dur = min(durations)
        max_dur = max(durations)
        avg_dur = sum(durations) / len(durations)
    else:
        min_dur = max_dur = avg_dur = 0

    passed = len(warnings) == 0

    return {
        "passed": passed,
        "warnings": warnings,
        "min_duration": round(min_dur, 2),
        "max_duration": round(max_dur, 2),
        "avg_duration": round(avg_dur, 2),
        "message": "All durations within reasonable bounds" if passed else f"{len(warnings)} duration warnings"
    }


def parse_cost_range(cost_str: str) -> Tuple[float, float]:
    """
    Parse a cost range string like "$50-150" or "$100+".

    Args:
        cost_str: Cost string to parse

    Returns:
        Tuple of (min_cost, max_cost)
    """
    try:
        # Remove $ and spaces
        clean = cost_str.replace('$', '').replace(' ', '')

        # Handle range (e.g., "50-150")
        if '-' in clean:
            parts = clean.split('-')
            return float(parts[0]), float(parts[1])

        # Handle plus (e.g., "100+")
        if '+' in clean:
            value = float(clean.replace('+', ''))
            return value, value * 2  # Estimate max as 2x

        # Single value
        value = float(clean)
        return value, value

    except (ValueError, IndexError):
        return 0.0, 0.0


def load_analysis_metadata(analysis_path: Path) -> Dict[str, Any]:
    """
    Load metadata from analysis.json.

    Args:
        analysis_path: Path to analysis.json

    Returns:
        Dictionary with duration, bpm, sections, etc.
    """
    from core.utils import read_json

    if not analysis_path.exists():
        return {
            'duration': 180.0,
            'bpm': 120,
            'sections': []
        }

    analysis = read_json(str(analysis_path))

    return {
        'duration': analysis.get('duration', 180.0),
        'bpm': analysis.get('bpm', 120),
        'time_signature': analysis.get('time_signature', '4/4'),
        'sections': analysis.get('sections', [])
    }


def extract_clips_from_phase3(phase3_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract flat list of clips from Phase 3 data structure.

    Args:
        phase3_data: Phase 3 data from SharedState

    Returns:
        List of clip dictionaries
    """
    clips = []

    # Get winner's proposal
    winner = phase3_data.get('winner', {})
    proposal = winner.get('proposal', {})

    # Check if clips are in sections structure
    if 'sections' in proposal:
        for section in proposal['sections']:
            if 'clips' in section:
                for clip in section['clips']:
                    # Add section context to clip
                    enhanced_clip = clip.copy()
                    enhanced_clip['section'] = section.get('section_name', '')
                    clips.append(enhanced_clip)

    # Check if clips are directly in proposal
    elif 'clips' in proposal:
        clips = proposal['clips']

    return clips


def build_validation_summary(validation_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build summary from validation results.

    Args:
        validation_results: Dictionary of validation check results

    Returns:
        Summary dictionary
    """
    total_checks = len(validation_results)
    passed_checks = sum(1 for r in validation_results.values() if r.get('passed', False))
    failed_checks = total_checks - passed_checks

    # Count warnings
    total_warnings = 0
    for result in validation_results.values():
        if 'warnings' in result:
            total_warnings += len(result['warnings'])
        if 'misaligned_clips' in result:
            total_warnings += len(result['misaligned_clips'])

    overall_status = "PASS" if failed_checks == 0 else "FAIL"

    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "warnings": total_warnings,
        "overall_status": overall_status
    }
