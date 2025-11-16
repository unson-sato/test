"""
Emotion Utilities for MV Orchestra v2.8

Shared utilities for mapping emotional descriptions to numeric values
and interpolating emotion curves across timeline sections.
"""

from typing import Dict, List, Tuple, Optional
import re


# Emotion keyword to numeric value mapping (0.0-1.0 scale)
# Lower values = calmer/lower energy
# Higher values = more intense/higher energy
EMOTION_MAP = {
    # Very low energy (0.1-0.2)
    "calm": 0.2,
    "peaceful": 0.2,
    "serene": 0.2,
    "quiet": 0.15,
    "gentle": 0.2,
    "soft": 0.15,
    "tranquil": 0.2,

    # Low-medium energy (0.3-0.4)
    "mysterious": 0.4,
    "anticipation": 0.4,
    "anticipatory": 0.4,
    "building": 0.35,
    "introspective": 0.3,
    "reflective": 0.3,
    "contemplative": 0.35,
    "subtle": 0.3,

    # Medium energy (0.5-0.6)
    "neutral": 0.5,
    "medium": 0.5,
    "balanced": 0.5,
    "steady": 0.5,
    "emotional": 0.6,
    "longing": 0.55,
    "nostalgic": 0.55,
    "nostalgia": 0.55,
    "melancholic": 0.5,

    # Medium-high energy (0.7-0.8)
    "upbeat": 0.8,
    "energetic": 0.8,
    "joyful": 0.75,
    "joy": 0.75,
    "happy": 0.75,
    "uplifting": 0.8,
    "euphoric": 0.85,
    "euphoria": 0.85,
    "exciting": 0.8,

    # High energy (0.85-1.0)
    "intense": 1.0,
    "climactic": 1.0,
    "explosive": 1.0,
    "powerful": 0.95,
    "dramatic": 0.9,
    "high": 0.9,
    "very-high": 0.95,
    "peak": 1.0,

    # Special cases
    "resolving": 0.4,
    "fading": 0.3,
    "building-up": 0.6,
    "tension": 0.7,
}


def map_emotion_to_value(emotion_text: str, default: float = 0.5) -> Tuple[float, str]:
    """
    Map emotion text to numeric value using keyword matching.

    Args:
        emotion_text: Text description of emotion (e.g., "mysterious and anticipatory")
        default: Default value if no match found

    Returns:
        Tuple of (emotion_value, matched_keyword)
        - emotion_value: float between 0.0 and 1.0
        - matched_keyword: the keyword that was matched, or "neutral"
    """
    if not emotion_text:
        return default, "neutral"

    # Normalize text
    text_lower = emotion_text.lower().strip()

    # Try exact match first
    if text_lower in EMOTION_MAP:
        return EMOTION_MAP[text_lower], text_lower

    # Try to find keywords in the text
    best_match = None
    best_keyword = None

    for keyword, value in EMOTION_MAP.items():
        if keyword in text_lower:
            # Prefer longer matches (more specific)
            if best_match is None or len(keyword) > len(best_keyword):
                best_match = value
                best_keyword = keyword

    if best_match is not None:
        return best_match, best_keyword

    # No match found, check for energy level descriptors
    if "high" in text_lower or "intense" in text_lower:
        return 0.8, "high"
    elif "low" in text_lower or "calm" in text_lower:
        return 0.3, "low"
    elif "medium" in text_lower or "moderate" in text_lower:
        return 0.5, "medium"

    return default, "neutral"


def interpolate_linear(start_value: float, end_value: float,
                       start_time: float, end_time: float,
                       target_time: float) -> float:
    """
    Linear interpolation between two emotion values.

    Args:
        start_value: Emotion value at start time
        end_value: Emotion value at end time
        start_time: Start time in seconds
        end_time: End time in seconds
        target_time: Time to interpolate to

    Returns:
        Interpolated emotion value
    """
    if end_time <= start_time:
        return start_value

    # Calculate interpolation factor (0.0 to 1.0)
    factor = (target_time - start_time) / (end_time - start_time)
    factor = max(0.0, min(1.0, factor))  # Clamp to [0, 1]

    # Linear interpolation
    return start_value + (end_value - start_value) * factor


def interpolate_smooth(start_value: float, end_value: float,
                       start_time: float, end_time: float,
                       target_time: float) -> float:
    """
    Smooth (ease-in-out) interpolation between two emotion values.
    Uses smoothstep function for more natural transitions.

    Args:
        start_value: Emotion value at start time
        end_value: Emotion value at end time
        start_time: Start time in seconds
        end_time: End time in seconds
        target_time: Time to interpolate to

    Returns:
        Interpolated emotion value with smooth transition
    """
    if end_time <= start_time:
        return start_value

    # Calculate interpolation factor (0.0 to 1.0)
    t = (target_time - start_time) / (end_time - start_time)
    t = max(0.0, min(1.0, t))  # Clamp to [0, 1]

    # Smoothstep interpolation (3t^2 - 2t^3)
    smooth_t = t * t * (3.0 - 2.0 * t)

    return start_value + (end_value - start_value) * smooth_t


def get_section_emotion_value(section: Dict) -> Tuple[float, str]:
    """
    Extract emotion value from a section dictionary.
    Tries multiple fields: emotional_tone, mood, energy.

    Args:
        section: Section dictionary with emotion-related fields

    Returns:
        Tuple of (emotion_value, label)
    """
    # Try emotional_tone first (Phase 2 format)
    if "emotional_tone" in section:
        return map_emotion_to_value(section["emotional_tone"])

    # Try mood field (analysis.json format)
    if "mood" in section:
        return map_emotion_to_value(section["mood"])

    # Try energy field
    if "energy" in section:
        return map_emotion_to_value(section["energy"])

    # Default
    return 0.5, "neutral"


def normalize_emotion_curve(curve: List[Dict], target_min: float = 0.0,
                            target_max: float = 1.0) -> List[Dict]:
    """
    Normalize emotion curve to fit within target range.
    Useful for ensuring consistent emotion value scaling.

    Args:
        curve: List of curve points with 'emotion' field
        target_min: Minimum target value
        target_max: Maximum target value

    Returns:
        Normalized curve (modifies in place and returns)
    """
    if not curve:
        return curve

    # Find current min and max
    current_min = min(point["emotion"] for point in curve)
    current_max = max(point["emotion"] for point in curve)

    # Avoid division by zero
    if current_max - current_min < 0.01:
        # All values are similar, set to middle of target range
        mid_value = (target_min + target_max) / 2
        for point in curve:
            point["emotion"] = mid_value
        return curve

    # Normalize each point
    for point in curve:
        # Map from [current_min, current_max] to [target_min, target_max]
        normalized = (point["emotion"] - current_min) / (current_max - current_min)
        point["emotion"] = target_min + normalized * (target_max - target_min)

    return curve


def get_emotion_statistics(curve: List[Dict]) -> Dict:
    """
    Calculate statistics for an emotion curve.

    Args:
        curve: List of curve points with 'emotion' field

    Returns:
        Dictionary with min, max, avg, std_dev
    """
    if not curve:
        return {
            "min_emotion": 0.0,
            "max_emotion": 0.0,
            "avg_emotion": 0.0,
            "std_dev": 0.0,
            "total_samples": 0
        }

    emotions = [point["emotion"] for point in curve]

    min_emotion = min(emotions)
    max_emotion = max(emotions)
    avg_emotion = sum(emotions) / len(emotions)

    # Calculate standard deviation
    variance = sum((e - avg_emotion) ** 2 for e in emotions) / len(emotions)
    std_dev = variance ** 0.5

    return {
        "min_emotion": round(min_emotion, 3),
        "max_emotion": round(max_emotion, 3),
        "avg_emotion": round(avg_emotion, 3),
        "std_dev": round(std_dev, 3),
        "total_samples": len(curve)
    }
