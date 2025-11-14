"""
Utility functions for Phase 3: Clip Division

This module provides helper functions for:
- Beat alignment and snapping
- Clip validation and coverage checking
- Clip ID generation
- Complexity estimation
- Beat data loading and processing
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def snap_to_beat(
    time: float,
    beat_times: List[float],
    tolerance: float = 0.2
) -> float:
    """
    Snap a time to the nearest beat within tolerance.

    Args:
        time: The time to snap (in seconds)
        beat_times: List of beat timestamps (in seconds)
        tolerance: Maximum distance to snap (in seconds)

    Returns:
        Snapped time (closest beat within tolerance, or original time if none found)
    """
    if not beat_times:
        return time

    # Find the closest beat
    closest_beat = min(beat_times, key=lambda b: abs(b - time))
    distance = abs(closest_beat - time)

    # Only snap if within tolerance
    if distance <= tolerance:
        return closest_beat
    else:
        return time


def find_nearest_beat(time: float, beat_times: List[float]) -> Optional[float]:
    """
    Find the nearest beat to a given time (no tolerance limit).

    Args:
        time: The time to find nearest beat for
        beat_times: List of beat timestamps

    Returns:
        Nearest beat time, or None if beat_times is empty
    """
    if not beat_times:
        return None

    return min(beat_times, key=lambda b: abs(b - time))


def find_beat_range(
    start_time: float,
    end_time: float,
    beat_times: List[float]
) -> List[float]:
    """
    Find all beats within a time range.

    Args:
        start_time: Range start time
        end_time: Range end time
        beat_times: List of beat timestamps

    Returns:
        List of beats within the range
    """
    return [b for b in beat_times if start_time <= b <= end_time]


def load_beat_data(analysis_data: Dict[str, Any]) -> List[float]:
    """
    Extract beat timestamps from analysis.json data.

    Args:
        analysis_data: Parsed analysis.json dictionary

    Returns:
        List of beat timestamps in seconds
    """
    # Try different possible keys for beat data
    beats = analysis_data.get('beats', [])

    if not beats:
        beats = analysis_data.get('beat_times', [])

    if not beats:
        beats = analysis_data.get('timing', {}).get('beats', [])

    # Validate beat data
    if beats and isinstance(beats[0], dict):
        # If beats are dictionaries, extract time field
        beats = [b.get('time', b.get('start', 0.0)) for b in beats]

    # Ensure beats are sorted
    beats = sorted(beats)

    logger.info(f"Loaded {len(beats)} beats from analysis data")

    return beats


def validate_clip_coverage(
    clips: List[Dict[str, Any]],
    total_duration: float,
    allow_gaps: bool = True,
    max_gap: float = 0.5
) -> bool:
    """
    Validate that clips provide proper coverage of the timeline.

    Args:
        clips: List of clip dictionaries
        total_duration: Total duration to cover (in seconds)
        allow_gaps: Whether small gaps between clips are acceptable
        max_gap: Maximum acceptable gap size (in seconds)

    Returns:
        True if validation passes

    Raises:
        ValueError: If validation fails
    """
    if not clips:
        raise ValueError("Empty clips list")

    # Sort clips by start time
    sorted_clips = sorted(clips, key=lambda c: c['start_time'])

    # Check for overlaps and gaps
    for i in range(len(sorted_clips) - 1):
        current_end = sorted_clips[i]['end_time']
        next_start = sorted_clips[i + 1]['start_time']

        # Check for overlap
        if current_end > next_start + 0.01:  # Small tolerance for floating point
            raise ValueError(
                f"Clip overlap detected: Clip {sorted_clips[i]['clip_id']} "
                f"ends at {current_end}, but {sorted_clips[i + 1]['clip_id']} "
                f"starts at {next_start}"
            )

        # Check for gaps
        gap = next_start - current_end
        if not allow_gaps and gap > 0.01:
            raise ValueError(
                f"Gap detected between {sorted_clips[i]['clip_id']} and "
                f"{sorted_clips[i + 1]['clip_id']}: {gap:.3f}s"
            )
        elif allow_gaps and gap > max_gap:
            logger.warning(
                f"Large gap detected between {sorted_clips[i]['clip_id']} and "
                f"{sorted_clips[i + 1]['clip_id']}: {gap:.3f}s"
            )

    # Validate each clip
    for clip in sorted_clips:
        duration = clip['end_time'] - clip['start_time']

        if duration <= 0:
            raise ValueError(
                f"Clip {clip['clip_id']} has invalid duration: {duration}"
            )

        if duration < 0.5:
            logger.warning(
                f"Clip {clip['clip_id']} is very short: {duration:.2f}s"
            )

    # Check timeline coverage
    first_clip_start = sorted_clips[0]['start_time']
    last_clip_end = sorted_clips[-1]['end_time']

    if first_clip_start > 0.5:
        logger.warning(
            f"Clips start at {first_clip_start:.2f}s, leaving beginning uncovered"
        )

    if last_clip_end < total_duration - 0.5:
        logger.warning(
            f"Clips end at {last_clip_end:.2f}s, but duration is {total_duration:.2f}s"
        )

    logger.info(
        f"Clip coverage validation passed for {len(clips)} clips "
        f"({first_clip_start:.2f}s - {last_clip_end:.2f}s)"
    )

    return True


def generate_clip_id(index: int, prefix: str = "clip") -> str:
    """
    Generate a clip ID from an index.

    Args:
        index: Clip index (1-based)
        prefix: Prefix for the ID (default: "clip")

    Returns:
        Formatted clip ID (e.g., "clip_001")
    """
    return f"{prefix}_{index:03d}"


def parse_clip_id(clip_id: str) -> Optional[int]:
    """
    Parse an index from a clip ID.

    Args:
        clip_id: Clip ID string (e.g., "clip_001")

    Returns:
        Parsed index, or None if parsing fails
    """
    try:
        parts = clip_id.split('_')
        if len(parts) >= 2:
            return int(parts[-1])
    except (ValueError, AttributeError):
        pass

    return None


def estimate_clip_complexity(
    shot_type: str,
    duration: float,
    has_movement: bool = True
) -> str:
    """
    Estimate the complexity level of a clip.

    Args:
        shot_type: Type of shot (wide, medium, close-up, etc.)
        duration: Clip duration in seconds
        has_movement: Whether the clip has camera movement

    Returns:
        Complexity level: "low", "medium", or "high"
    """
    complexity_score = 0

    # Shot type complexity
    shot_lower = shot_type.lower()
    if 'close' in shot_lower or 'detail' in shot_lower:
        complexity_score += 2
    elif 'medium' in shot_lower:
        complexity_score += 1
    elif 'wide' in shot_lower or 'establishing' in shot_lower:
        complexity_score += 1

    # Duration complexity (shorter clips are generally harder)
    if duration < 2.0:
        complexity_score += 2
    elif duration < 3.5:
        complexity_score += 1

    # Movement complexity
    if has_movement:
        complexity_score += 1

    # Map score to level
    if complexity_score <= 2:
        return "low"
    elif complexity_score <= 4:
        return "medium"
    else:
        return "high"


def calculate_clip_statistics(clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics about a clip list.

    Args:
        clips: List of clip dictionaries

    Returns:
        Dictionary with clip statistics
    """
    if not clips:
        return {
            'total_clips': 0,
            'total_duration': 0.0,
            'average_duration': 0.0,
            'min_duration': 0.0,
            'max_duration': 0.0,
            'beat_aligned_count': 0,
            'complexity_distribution': {}
        }

    durations = [c['end_time'] - c['start_time'] for c in clips]
    total_duration = sum(durations)

    # Count beat-aligned clips
    beat_aligned = sum(1 for c in clips if c.get('beat_aligned', False))

    # Count complexity distribution
    complexity_dist = {}
    for clip in clips:
        complexity = clip.get('complexity', 'unknown')
        complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1

    # Count by section
    section_dist = {}
    for clip in clips:
        section = clip.get('section', 'unknown')
        section_dist[section] = section_dist.get(section, 0) + 1

    return {
        'total_clips': len(clips),
        'total_duration': round(total_duration, 2),
        'average_duration': round(sum(durations) / len(durations), 2),
        'min_duration': round(min(durations), 2),
        'max_duration': round(max(durations), 2),
        'beat_aligned_count': beat_aligned,
        'beat_aligned_percentage': round(100 * beat_aligned / len(clips), 1),
        'complexity_distribution': complexity_dist,
        'section_distribution': section_dist
    }


def optimize_beat_alignment(
    clips: List[Dict[str, Any]],
    beat_times: List[float],
    tolerance: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Optimize clip boundaries to align with beats.

    Args:
        clips: List of clip dictionaries
        beat_times: List of beat timestamps
        tolerance: Maximum distance to snap to beat

    Returns:
        List of clips with optimized beat alignment
    """
    optimized_clips = []

    for clip in clips:
        optimized_clip = clip.copy()

        # Try to snap start time to nearest beat
        original_start = clip['start_time']
        snapped_start = snap_to_beat(original_start, beat_times, tolerance)

        # Try to snap end time to nearest beat
        original_end = clip['end_time']
        snapped_end = snap_to_beat(original_end, beat_times, tolerance)

        # Make sure clip doesn't become too short
        min_duration = 1.0
        if snapped_end - snapped_start < min_duration:
            # Keep original times if snapping makes it too short
            snapped_start = original_start
            snapped_end = original_end

        optimized_clip['start_time'] = round(snapped_start, 2)
        optimized_clip['end_time'] = round(snapped_end, 2)
        optimized_clip['duration'] = round(snapped_end - snapped_start, 2)
        optimized_clip['beat_aligned'] = (
            abs(snapped_start - original_start) > 0.01 or
            abs(snapped_end - original_end) > 0.01
        )

        optimized_clips.append(optimized_clip)

    return optimized_clips


def merge_short_clips(
    clips: List[Dict[str, Any]],
    min_duration: float = 1.5
) -> List[Dict[str, Any]]:
    """
    Merge clips that are shorter than a minimum duration.

    Args:
        clips: List of clip dictionaries
        min_duration: Minimum acceptable clip duration

    Returns:
        List of clips with short clips merged
    """
    if not clips:
        return []

    sorted_clips = sorted(clips, key=lambda c: c['start_time'])
    merged_clips = []
    current_group = [sorted_clips[0]]

    for i in range(1, len(sorted_clips)):
        current_clip = sorted_clips[i]
        previous_clip = current_group[-1]

        # Check if previous clip is too short
        prev_duration = previous_clip['end_time'] - previous_clip['start_time']

        if prev_duration < min_duration:
            # Merge with current clip if they're adjacent
            gap = current_clip['start_time'] - previous_clip['end_time']
            if gap < 0.1:  # Very close together
                current_group.append(current_clip)
                continue

        # Finalize previous group
        if len(current_group) > 1:
            merged_clip = _merge_clip_group(current_group)
            merged_clips.append(merged_clip)
        else:
            merged_clips.append(current_group[0])

        # Start new group
        current_group = [current_clip]

    # Don't forget last group
    if len(current_group) > 1:
        merged_clip = _merge_clip_group(current_group)
        merged_clips.append(merged_clip)
    else:
        merged_clips.append(current_group[0])

    logger.info(f"Merged {len(clips)} clips into {len(merged_clips)} clips")

    return merged_clips


def _merge_clip_group(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge a group of clips into a single clip."""
    if not group:
        return {}

    if len(group) == 1:
        return group[0]

    merged = {
        'clip_id': f"merged_{group[0]['clip_id']}",
        'start_time': group[0]['start_time'],
        'end_time': group[-1]['end_time'],
        'duration': group[-1]['end_time'] - group[0]['start_time'],
        'section': group[0].get('section', 'unknown'),
        'shot_type': 'merged shot',
        'camera_movement': 'varied',
        'complexity': 'high',  # Merged clips are typically more complex
        'beat_aligned': group[0].get('beat_aligned', False),
        'base_allocation': group[-1]['end_time'] - group[0]['start_time'],
        'merged_from': [c['clip_id'] for c in group]
    }

    return merged


def split_long_clips(
    clips: List[Dict[str, Any]],
    max_duration: float = 8.0,
    beat_times: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Split clips that are longer than a maximum duration.

    Args:
        clips: List of clip dictionaries
        max_duration: Maximum acceptable clip duration
        beat_times: Optional beat times for splitting on beats

    Returns:
        List of clips with long clips split
    """
    split_clips = []

    for clip in clips:
        duration = clip['end_time'] - clip['start_time']

        if duration <= max_duration:
            split_clips.append(clip)
            continue

        # Split the clip
        num_splits = int(duration / max_duration) + 1
        segment_duration = duration / num_splits

        for i in range(num_splits):
            segment_start = clip['start_time'] + (i * segment_duration)
            segment_end = clip['start_time'] + ((i + 1) * segment_duration)

            # Optionally snap to beats
            if beat_times:
                segment_start = snap_to_beat(segment_start, beat_times, tolerance=0.3)
                segment_end = snap_to_beat(segment_end, beat_times, tolerance=0.3)

            split_clip = clip.copy()
            split_clip['clip_id'] = f"{clip['clip_id']}_part{i + 1}"
            split_clip['start_time'] = round(segment_start, 2)
            split_clip['end_time'] = round(segment_end, 2)
            split_clip['duration'] = round(segment_end - segment_start, 2)
            split_clip['split_from'] = clip['clip_id']

            split_clips.append(split_clip)

    logger.info(f"Split {len(clips)} clips into {len(split_clips)} clips")

    return split_clips
