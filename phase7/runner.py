"""
Phase 7 Runner: Video Editing (Trim & Merge)

Trims clips to exact durations and merges them into sequences.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core import (
    SharedState,
    get_session_dir,
    ensure_dir,
    write_json,
    read_json,
    get_iso_timestamp,
    get_project_root
)
from core.video_editor import VideoEditor, TrimSpec, MergeSpec


logger = logging.getLogger(__name__)


def run_phase7(
    session_id: str,
    max_parallel_trims: int = 3,
    transition_duration: float = 0.0,
    transition_type: str = "none",
    mock_mode: bool = True
) -> Dict[str, Any]:
    """
    Run Phase 7: Trim and merge video clips.

    Args:
        session_id: Session identifier
        max_parallel_trims: Maximum parallel trim operations
        transition_duration: Duration of transitions between clips (seconds)
        transition_type: Type of transition (none, crossfade, fade)
        mock_mode: If True, simulate video editing without actual ffmpeg calls

    Returns:
        Phase 7 results dictionary
    """
    logger.info("=" * 70)
    logger.info("PHASE 7: Video Editing (Trim & Merge)")
    logger.info("=" * 70)

    # Load session
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Get Phase 6 evaluation results
    phase6_data = session.get_phase_data(6)
    if not phase6_data or "evaluations" not in phase6_data:
        raise ValueError("Phase 6 data not found. Run Phase 6 first.")

    evaluations = phase6_data["evaluations"]
    passing_clips = [e for e in evaluations if e["meets_threshold"]]

    if not passing_clips:
        raise ValueError("No passing clips from Phase 6 to edit")

    logger.info(f"Editing {len(passing_clips)} clips from Phase 6")

    # Get Phase 3 clip designs
    phase3_data = session.get_phase_data(3)
    clip_designs = phase3_data["winner"]["clips"]

    # Get Phase 2 section division for merging
    phase2_data = session.get_phase_data(2)
    sections = phase2_data["winner"]["sections"]

    logger.info(f"Video structure: {len(sections)} sections, {len(passing_clips)} clips")

    # Create output directories
    trim_dir = session_dir / "phase7" / "trimmed_clips"
    merge_dir = session_dir / "phase7" / "merged_sections"
    ensure_dir(trim_dir)
    ensure_dir(merge_dir)

    # Initialize Video Editor
    editor = VideoEditor(mock_mode=mock_mode)

    # Step 1: Trim all clips
    logger.info(f"\nStep 1: Trimming clips to exact durations...")
    trim_specs = editor.create_trim_specs(passing_clips, clip_designs, trim_dir)

    trim_results = asyncio.run(
        editor.trim_all_clips(trim_specs, max_parallel=max_parallel_trims)
    )

    successful_trims = [r for r in trim_results if r.success]
    failed_trims = [r for r in trim_results if not r.success]

    logger.info(f"Trim results: {len(successful_trims)}/{len(trim_results)} successful")

    if failed_trims:
        logger.warning(f"  {len(failed_trims)} clips failed to trim")

    # Step 2: Organize clips by section
    logger.info(f"\nStep 2: Organizing clips by section...")
    clips_by_section = _organize_clips_by_section(
        successful_trims,
        clip_designs,
        sections
    )

    logger.info(f"Organized into {len(clips_by_section)} sections")

    # Step 3: Merge clips within each section
    logger.info(f"\nStep 3: Merging clips within sections...")
    section_merges = []

    for section_id, section_clips in clips_by_section.items():
        if not section_clips:
            logger.warning(f"  Section {section_id}: No clips, skipping")
            continue

        logger.info(f"  Section {section_id}: Merging {len(section_clips)} clips")

        # Sort clips by clip_id to maintain order
        section_clips.sort(key=lambda x: x["clip_id"])

        # Create merge spec
        merge_spec = MergeSpec(
            clips=[Path(c["path"]) for c in section_clips],
            output_path=merge_dir / f"section_{section_id:03d}.mp4",
            transition_duration=transition_duration,
            transition_type=transition_type
        )

        # Merge
        merge_result = asyncio.run(editor.merge_clips(merge_spec))

        if merge_result.success:
            logger.info(f"    ✓ Section {section_id}: {merge_result.duration:.1f}s")
            section_merges.append({
                "section_id": section_id,
                "path": str(merge_result.output_path),
                "duration": merge_result.duration,
                "clip_count": len(section_clips),
                "clips": [c["clip_id"] for c in section_clips]
            })
        else:
            logger.error(f"    ✗ Section {section_id}: {merge_result.error}")

    # Step 4: Merge all sections into final sequence (optional)
    final_merge_path = None
    if len(section_merges) > 1:
        logger.info(f"\nStep 4: Merging all sections into final sequence...")

        final_spec = MergeSpec(
            clips=[Path(s["path"]) for s in section_merges],
            output_path=merge_dir / "full_sequence.mp4",
            transition_duration=transition_duration,
            transition_type=transition_type
        )

        final_result = asyncio.run(editor.merge_clips(final_spec))

        if final_result.success:
            final_merge_path = str(final_result.output_path)
            total_duration = final_result.duration
            logger.info(f"  ✓ Final sequence: {total_duration:.1f}s ({len(section_merges)} sections)")
        else:
            logger.error(f"  ✗ Final merge failed: {final_result.error}")
            total_duration = sum(s["duration"] for s in section_merges)
    else:
        # Only one section, use it as final output
        if section_merges:
            final_merge_path = section_merges[0]["path"]
            total_duration = section_merges[0]["duration"]
            logger.info(f"Single section video: {total_duration:.1f}s")
        else:
            total_duration = 0.0

    # Calculate statistics
    total_clips = len(trim_results)
    successful_clips = len(successful_trims)
    total_sections = len(section_merges)

    logger.info(f"\n{'=' * 70}")
    logger.info(f"EDITING SUMMARY")
    logger.info(f"{'=' * 70}")
    logger.info(f"Trimmed clips: {successful_clips}/{total_clips}")
    logger.info(f"Merged sections: {total_sections}/{len(sections)}")
    logger.info(f"Total duration: {total_duration:.1f}s")

    # Save results
    phase7_results = {
        "total_clips": total_clips,
        "successful_trims": successful_clips,
        "failed_trims": len(failed_trims),
        "trimmed_clips": [
            {
                "clip_id": spec.clip_id,
                "success": result.success,
                "path": str(result.output_path) if result.output_path else None,
                "duration": result.duration,
                "error": result.error
            }
            for spec, result in zip(trim_specs, trim_results)
        ],
        "sections": section_merges,
        "final_sequence": {
            "path": final_merge_path,
            "duration": total_duration,
            "section_count": len(section_merges)
        },
        "transition_settings": {
            "duration": transition_duration,
            "type": transition_type
        },
        "timestamp": get_iso_timestamp()
    }

    # Save to session
    result_file = session_dir / "phase7" / "results.json"
    ensure_dir(result_file.parent)
    write_json(result_file, phase7_results)

    # Update session state
    session.mark_phase_started(7)
    session.mark_phase_completed(7, phase7_results)

    logger.info(f"\n✓ Phase 7 completed")
    logger.info(f"  Results saved to: {result_file}")

    if final_merge_path:
        logger.info(f"  Final sequence: {final_merge_path}")

    return phase7_results


def _organize_clips_by_section(
    trim_results: List,
    clip_designs: List[Dict[str, Any]],
    sections: List[Dict[str, Any]]
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Organize trimmed clips by their sections.

    Returns:
        Dictionary mapping section_id to list of clip info dicts
    """
    # Create clip lookup by clip_id
    designs_by_id = {d["clip_id"]: d for d in clip_designs}

    # Create result lookup by clip_id (from TrimSpec)
    results_by_id = {}
    for result in trim_results:
        if result.success and result.output_path:
            # Extract clip_id from output path (format: clip_XXX_trimmed.mp4)
            filename = result.output_path.stem
            if filename.startswith("clip_"):
                try:
                    clip_id = int(filename.split("_")[1])
                    results_by_id[clip_id] = result
                except (IndexError, ValueError):
                    continue

    # Initialize sections
    clips_by_section = {i: [] for i in range(len(sections))}

    # Assign clips to sections
    for clip_id, result in results_by_id.items():
        design = designs_by_id.get(clip_id)
        if not design:
            continue

        # Get section_id from design
        section_id = design.get("section_id", 0)

        clips_by_section[section_id].append({
            "clip_id": clip_id,
            "path": str(result.output_path),
            "duration": result.duration,
            "design": design
        })

    return clips_by_section
