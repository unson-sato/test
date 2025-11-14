#!/usr/bin/env python3
"""
Phase 3 Clip Division Validator for MV Orchestra v2.8

Technical validation of Phase 3 clip division output to ensure quality and correctness.
This validator checks:
- Clip ID uniqueness
- Timing consistency
- Section coverage
- Timeline coverage
- Beat alignment
- Base allocation & creative adjustments
- Duration sanity

Usage:
    python3 tools/validators/validate_clip_division.py <session_id>
"""

import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import SharedState
from core.utils import read_json, write_json, get_session_dir, get_iso_timestamp, get_project_root
from tools.validators.validation_utils import (
    print_header,
    print_check,
    print_summary,
    validate_unique_ids,
    validate_timing_consistency,
    validate_timeline_coverage,
    validate_duration_sanity,
    load_analysis_metadata,
    extract_clips_from_phase3,
    build_validation_summary
)


def validate_section_coverage(
    clips: List[Dict[str, Any]],
    analysis_sections: List[str]
) -> Dict[str, Any]:
    """
    Validate that all clips are assigned to valid sections.

    Args:
        clips: List of clip dictionaries
        analysis_sections: Valid section names from analysis.json

    Returns:
        Validation result dictionary
    """
    unassigned_clips = []
    invalid_sections = []

    # If no sections provided in analysis, accept any section assignment
    if not analysis_sections:
        for clip in clips:
            if 'section' not in clip or not clip['section']:
                unassigned_clips.append(clip.get('clip_id', 'unknown'))
    else:
        # Validate against known sections
        valid_section_names = set(s.get('name', s.get('section_name', '')) for s in analysis_sections if isinstance(s, dict))

        # If sections are just strings
        if analysis_sections and isinstance(analysis_sections[0], str):
            valid_section_names = set(analysis_sections)

        for clip in clips:
            clip_id = clip.get('clip_id', 'unknown')
            section = clip.get('section', '')

            if not section:
                unassigned_clips.append(clip_id)
            elif section not in valid_section_names:
                invalid_sections.append({
                    'clip_id': clip_id,
                    'section': section
                })

    passed = len(unassigned_clips) == 0 and len(invalid_sections) == 0

    message = "All clips properly assigned to sections"
    if not passed:
        parts = []
        if unassigned_clips:
            parts.append(f"{len(unassigned_clips)} unassigned")
        if invalid_sections:
            parts.append(f"{len(invalid_sections)} invalid sections")
        message = f"Found {', '.join(parts)}"

    return {
        "passed": passed,
        "unassigned_clips": unassigned_clips,
        "invalid_sections": invalid_sections,
        "message": message
    }


def validate_beat_alignment(
    clips: List[Dict[str, Any]],
    beat_times: Optional[List[float]] = None,
    tolerance: float = 0.3
) -> Dict[str, Any]:
    """
    Check if clips align to beat boundaries.

    Args:
        clips: List of clip dictionaries
        beat_times: List of beat timestamps (if available)
        tolerance: Alignment tolerance in seconds

    Returns:
        Validation result dictionary
    """
    if not beat_times:
        # Cannot validate without beat data
        return {
            "passed": True,
            "alignment_percentage": 0.0,
            "misaligned_clips": [],
            "message": "No beat data available for alignment check"
        }

    aligned_count = 0
    misaligned_clips = []

    for clip in clips:
        clip_id = clip.get('clip_id', 'unknown')
        start_time = clip.get('start_time', 0)
        end_time = clip.get('end_time', 0)

        # Check if marked as beat aligned
        is_beat_aligned = clip.get('beat_aligned', False)

        # Find nearest beats
        start_distances = [abs(start_time - beat) for beat in beat_times]
        end_distances = [abs(end_time - beat) for beat in beat_times]

        min_start_dist = min(start_distances) if start_distances else float('inf')
        min_end_dist = min(end_distances) if end_distances else float('inf')

        # Check alignment
        start_aligned = min_start_dist <= tolerance
        end_aligned = min_end_dist <= tolerance

        if start_aligned and end_aligned:
            aligned_count += 1
        else:
            # Flag if marked as aligned but actually isn't
            if is_beat_aligned:
                misaligned_clips.append(clip_id)

    alignment_percentage = (aligned_count / len(clips) * 100) if clips else 0

    # Pass if most clips are aligned (>90%)
    passed = alignment_percentage >= 90.0

    return {
        "passed": passed,
        "alignment_percentage": round(alignment_percentage, 1),
        "misaligned_clips": misaligned_clips[:5],  # Limit to first 5
        "message": f"{alignment_percentage:.0f}% of clips aligned to beats"
    }


def validate_base_allocation(clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify base_allocation exists for clips.

    Args:
        clips: List of clip dictionaries

    Returns:
        Validation result dictionary
    """
    clips_with_allocation = 0
    clips_without_allocation = 0

    for clip in clips:
        if 'base_allocation' in clip:
            clips_with_allocation += 1
        else:
            clips_without_allocation += 1

    passed = clips_without_allocation == 0

    return {
        "passed": passed,
        "clips_with_allocation": clips_with_allocation,
        "clips_without_allocation": clips_without_allocation,
        "message": "All clips have base_allocation" if passed else f"{clips_without_allocation} clips missing base_allocation"
    }


def validate_creative_adjustments(clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify creative_adjustments structure where present.

    Args:
        clips: List of clip dictionaries

    Returns:
        Validation result dictionary
    """
    clips_with_adjustments = 0

    for clip in clips:
        if 'creative_adjustments' in clip:
            clips_with_adjustments += 1

    # Creative adjustments are optional, so this always passes
    passed = True

    return {
        "passed": passed,
        "clips_with_adjustments": clips_with_adjustments,
        "message": f"Creative adjustments present in {clips_with_adjustments} clips" if clips_with_adjustments > 0 else "No creative adjustments applied"
    }


def validate_clip_division(session_id: str) -> Dict[str, Any]:
    """
    Main validation function for Phase 3 clip division.

    Args:
        session_id: Session identifier

    Returns:
        Complete validation results dictionary
    """
    # Print header
    print_header("=== MV Orchestra v2.8 - Phase 3 Clip Division Validation ===", session_id)

    # Load session
    try:
        session = SharedState.load_session(session_id)
    except FileNotFoundError:
        print(f"Error: Session '{session_id}' not found")
        sys.exit(1)

    # Get Phase 3 data
    phase3_data = session.get_phase_data(3)

    if phase3_data.status != "completed":
        print(f"Warning: Phase 3 status is '{phase3_data.status}', not 'completed'")

    # Extract clips
    clips = extract_clips_from_phase3(phase3_data.data)

    if not clips:
        print("Error: No clips found in Phase 3 data")
        sys.exit(1)

    print(f"Total Clips: {len(clips)}\n")

    # Load analysis metadata
    project_root = get_project_root()
    analysis_path = project_root / "shared-workspace" / "input" / "analysis.json"

    if analysis_path.exists():
        analysis = read_json(str(analysis_path))
        metadata = load_analysis_metadata(analysis_path)
        beat_times = analysis.get('beats', [])
    else:
        print("Warning: analysis.json not found, using defaults")
        metadata = {'duration': 180.0, 'bpm': 120, 'sections': []}
        beat_times = []

    # Run validation checks
    validation_results = {}

    # 1. Clip ID Uniqueness
    validation_results['clip_id_uniqueness'] = validate_unique_ids(clips, 'clip_id')
    print_check("Clip ID Uniqueness", validation_results['clip_id_uniqueness'])

    # 2. Timing Consistency
    validation_results['timing_consistency'] = validate_timing_consistency(clips)
    print_check("Timing Consistency", validation_results['timing_consistency'])

    # 3. Section Coverage
    sections = metadata.get('sections', [])
    validation_results['section_coverage'] = validate_section_coverage(clips, sections)
    print_check("Section Coverage", validation_results['section_coverage'])

    # 4. Timeline Coverage
    total_duration = metadata.get('duration', 180.0)
    validation_results['timeline_coverage'] = validate_timeline_coverage(clips, total_duration)
    print_check("Timeline Coverage", validation_results['timeline_coverage'])

    # 5. Beat Alignment
    validation_results['beat_alignment'] = validate_beat_alignment(clips, beat_times)
    print_check("Beat Alignment", validation_results['beat_alignment'])

    # 6. Base Allocation
    validation_results['base_allocation'] = validate_base_allocation(clips)
    print_check("Base Allocation", validation_results['base_allocation'])

    # 7. Creative Adjustments
    validation_results['creative_adjustments'] = validate_creative_adjustments(clips)
    print_check("Creative Adjustments", validation_results['creative_adjustments'])

    # 8. Duration Sanity
    validation_results['duration_sanity'] = validate_duration_sanity(clips)
    print_check("Duration Sanity", validation_results['duration_sanity'])

    # Build summary
    summary = build_validation_summary(validation_results)

    # Print summary
    print_summary(summary)

    # Build full report
    report = {
        "session_id": session_id,
        "validated_at": get_iso_timestamp(),
        "phase": 3,
        "total_clips": len(clips),
        "validation_results": validation_results,
        "summary": summary
    }

    # Save report
    session_dir = get_session_dir(session_id)
    report_path = session_dir / "validation_clip_division.json"
    write_json(str(report_path), report)

    print(f"Validation complete. Report saved to:")
    print(f"{report_path}")

    return report


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Phase 3 clip division output for MV Orchestra v2.8"
    )
    parser.add_argument(
        "session_id",
        help="Session ID to validate"
    )

    args = parser.parse_args()

    # Run validation
    report = validate_clip_division(args.session_id)

    # Exit with appropriate code
    if report['summary']['overall_status'] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
