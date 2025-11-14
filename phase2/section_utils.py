"""
Utility functions for Phase 2: Section Direction Design

This module provides helper functions for:
- Loading and validating song sections
- Extracting section summaries
- Validating section coverage
- Section data transformation
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def load_song_sections(analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract song sections from analysis.json data.

    Args:
        analysis_data: Parsed analysis.json dictionary

    Returns:
        List of section dictionaries with timing information

    Raises:
        ValueError: If sections are missing or invalid
    """
    sections = analysis_data.get('sections', [])

    if not sections:
        raise ValueError("No sections found in analysis data")

    # Validate section structure
    for idx, section in enumerate(sections):
        if 'start' not in section or 'end' not in section:
            raise ValueError(f"Section {idx} missing start or end time")

        if 'label' not in section:
            logger.warning(f"Section {idx} missing label, using 'section_{idx}'")
            section['label'] = f"section_{idx}"

    return sections


def validate_section_coverage(sections: List[Dict[str, Any]]) -> bool:
    """
    Validate that sections have proper coverage and don't overlap.

    Args:
        sections: List of section dictionaries

    Returns:
        True if validation passes

    Raises:
        ValueError: If validation fails
    """
    if not sections:
        raise ValueError("Empty sections list")

    # Sort sections by start time
    sorted_sections = sorted(sections, key=lambda s: s['start'])

    # Check for gaps and overlaps
    for i in range(len(sorted_sections) - 1):
        current_end = sorted_sections[i]['end']
        next_start = sorted_sections[i + 1]['start']

        # Check for overlap
        if current_end > next_start:
            logger.warning(
                f"Section overlap detected: Section {i} ends at {current_end}, "
                f"but Section {i+1} starts at {next_start}"
            )

        # Small gaps (< 0.5s) are acceptable for timing precision
        gap = next_start - current_end
        if gap > 0.5:
            logger.warning(
                f"Gap detected between sections {i} and {i+1}: {gap:.2f} seconds"
            )

    # Validate duration consistency
    for i, section in enumerate(sorted_sections):
        duration = section['end'] - section['start']
        if duration <= 0:
            raise ValueError(f"Section {i} has invalid duration: {duration}")

        if duration < 0.5:
            logger.warning(f"Section {i} is very short: {duration:.2f} seconds")

    logger.info(f"Section coverage validation passed for {len(sections)} sections")
    return True


def extract_section_summary(sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract summary information from sections.

    Args:
        sections: List of section dictionaries

    Returns:
        Dictionary with section summary statistics
    """
    if not sections:
        return {
            'total_sections': 0,
            'total_duration': 0.0,
            'section_labels': [],
            'average_duration': 0.0
        }

    sorted_sections = sorted(sections, key=lambda s: s['start'])

    total_duration = sorted_sections[-1]['end'] - sorted_sections[0]['start']
    section_labels = [s.get('label', 'unknown') for s in sorted_sections]

    durations = [s['end'] - s['start'] for s in sorted_sections]
    average_duration = sum(durations) / len(durations)

    return {
        'total_sections': len(sections),
        'total_duration': round(total_duration, 2),
        'section_labels': section_labels,
        'average_duration': round(average_duration, 2),
        'min_duration': round(min(durations), 2),
        'max_duration': round(max(durations), 2),
        'section_types': get_section_types(section_labels)
    }


def get_section_types(labels: List[str]) -> Dict[str, int]:
    """
    Count occurrences of each section type.

    Args:
        labels: List of section labels

    Returns:
        Dictionary mapping section types to counts
    """
    section_counts = {}

    for label in labels:
        # Normalize label (lowercase, remove numbers)
        normalized = label.lower().strip()

        # Extract base type (intro, verse, chorus, etc.)
        base_type = normalized
        for common in ['intro', 'verse', 'chorus', 'bridge', 'outro', 'pre-chorus', 'hook']:
            if common in normalized:
                base_type = common
                break

        section_counts[base_type] = section_counts.get(base_type, 0) + 1

    return section_counts


def format_section_for_prompt(section: Dict[str, Any]) -> str:
    """
    Format a section dictionary for inclusion in AI prompts.

    Args:
        section: Section dictionary

    Returns:
        Formatted string representation
    """
    label = section.get('label', 'unknown')
    start = section.get('start', 0.0)
    end = section.get('end', 0.0)
    duration = end - start

    return (
        f"- **{label}** ({start:.2f}s - {end:.2f}s, duration: {duration:.2f}s)"
    )


def merge_adjacent_sections(
    sections: List[Dict[str, Any]],
    same_type_only: bool = True
) -> List[Dict[str, Any]]:
    """
    Merge adjacent sections of the same type (e.g., verse1 + verse2).

    Args:
        sections: List of section dictionaries
        same_type_only: Only merge sections with same base type

    Returns:
        List of merged sections
    """
    if not sections:
        return []

    sorted_sections = sorted(sections, key=lambda s: s['start'])
    merged = []
    current_group = [sorted_sections[0]]

    for i in range(1, len(sorted_sections)):
        current_section = sorted_sections[i]
        previous_section = current_group[-1]

        # Check if we should merge
        should_merge = False

        if same_type_only:
            # Only merge if same type
            current_type = get_base_section_type(current_section.get('label', ''))
            previous_type = get_base_section_type(previous_section.get('label', ''))

            if current_type == previous_type:
                # Check if they're adjacent (within 0.5s)
                gap = current_section['start'] - previous_section['end']
                if gap <= 0.5:
                    should_merge = True

        if should_merge:
            current_group.append(current_section)
        else:
            # Finish current group and start new one
            merged.append(merge_section_group(current_group))
            current_group = [current_section]

    # Don't forget the last group
    merged.append(merge_section_group(current_group))

    return merged


def get_base_section_type(label: str) -> str:
    """
    Extract base section type from label.

    Args:
        label: Section label (e.g., "verse 1", "chorus_2")

    Returns:
        Base type (e.g., "verse", "chorus")
    """
    normalized = label.lower().strip()

    for common in ['intro', 'verse', 'chorus', 'bridge', 'outro', 'pre-chorus', 'hook']:
        if common in normalized:
            return common

    return normalized


def merge_section_group(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge a group of sections into a single section.

    Args:
        group: List of sections to merge

    Returns:
        Merged section dictionary
    """
    if not group:
        return {}

    if len(group) == 1:
        return group[0]

    # Create merged section
    merged = {
        'label': group[0].get('label', 'merged'),
        'start': group[0]['start'],
        'end': group[-1]['end'],
        'merged_from': [s.get('label', 'unknown') for s in group],
        'subsection_count': len(group)
    }

    return merged


def calculate_emotional_progression(
    sections: List[Dict[str, Any]],
    section_directions: List[Dict[str, Any]]
) -> List[Dict[str, float]]:
    """
    Calculate emotional progression across sections.

    Args:
        sections: List of section dictionaries
        section_directions: List of section direction dictionaries

    Returns:
        List of emotional intensity values (0-100) over time
    """
    # This is a simplified mock implementation
    # Real implementation would analyze emotional_tone from section_directions

    progression = []

    for i, section in enumerate(sections):
        # Mock emotional intensity based on section type
        label = section.get('label', '').lower()
        intensity = 50.0  # Default

        if 'intro' in label:
            intensity = 30.0
        elif 'verse' in label:
            intensity = 45.0
        elif 'pre-chorus' in label or 'pre chorus' in label:
            intensity = 65.0
        elif 'chorus' in label:
            intensity = 85.0
        elif 'bridge' in label:
            intensity = 70.0
        elif 'outro' in label:
            intensity = 35.0

        progression.append({
            'section': label,
            'start_time': section['start'],
            'end_time': section['end'],
            'emotional_intensity': intensity
        })

    return progression
