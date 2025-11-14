"""
Shared audio processing utilities for MV Orchestra v2.8

This module provides common audio analysis functions used by:
- build_analysis.py: Generate analysis.json from MP3 + lyrics
- build_src.py: Generate SRC (lyrics timecode) from MP3 + lyrics

Provides simple heuristic-based analysis with graceful fallbacks.
"""

import subprocess
import sys
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def get_audio_duration(mp3_path: str) -> Optional[float]:
    """
    Extract audio duration using ffprobe.

    Args:
        mp3_path: Path to MP3 file

    Returns:
        Duration in seconds, or None if extraction fails
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                mp3_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"Extracted duration: {duration:.2f}s")
            return duration
        else:
            logger.error(f"ffprobe failed: {result.stderr}")
            return None

    except FileNotFoundError:
        logger.error("ffprobe not found. Please install ffmpeg.")
        return None
    except subprocess.TimeoutExpired:
        logger.error("ffprobe timed out")
        return None
    except Exception as e:
        logger.error(f"Error extracting duration: {e}")
        return None


def estimate_bpm_heuristic(duration: float, target_bpm: int = 120) -> int:
    """
    Simple BPM estimation using heuristic.

    For a production system, use librosa or essentia.
    This is a placeholder that returns a reasonable default.

    Args:
        duration: Audio duration in seconds
        target_bpm: Default BPM to return (default: 120)

    Returns:
        Estimated BPM
    """
    # In a real implementation, you would analyze the audio
    # For now, return a sensible default
    logger.info(f"Using heuristic BPM: {target_bpm}")
    return target_bpm


def detect_key_heuristic() -> str:
    """
    Simple key detection using heuristic.

    For production, use librosa or essentia for actual key detection.
    This returns a placeholder.

    Returns:
        Musical key (e.g., "C major")
    """
    # In real implementation, analyze audio for key
    # For now, return a common key
    key = "C major"
    logger.info(f"Using heuristic key: {key}")
    return key


def generate_beats(duration: float, bpm: int) -> List[Dict[str, float]]:
    """
    Generate beat timestamps based on BPM.

    Args:
        duration: Audio duration in seconds
        bpm: Beats per minute

    Returns:
        List of beat dictionaries with time, bar, and beat info
    """
    beats = []
    beat_interval = 60.0 / bpm  # seconds per beat
    beats_per_bar = 4  # assume 4/4 time signature

    current_time = 0.0
    beat_count = 0

    while current_time < duration:
        bar = beat_count // beats_per_bar
        beat = beat_count % beats_per_bar

        beats.append({
            "time": round(current_time, 3),
            "bar": bar,
            "beat": beat
        })

        current_time += beat_interval
        beat_count += 1

    logger.info(f"Generated {len(beats)} beats at {bpm} BPM")
    return beats


def detect_sections_heuristic(duration: float) -> List[Dict[str, any]]:
    """
    Detect song sections using simple heuristics.

    This uses basic time-based rules. For production, use actual
    audio analysis with librosa or essentia.

    Args:
        duration: Audio duration in seconds

    Returns:
        List of section dictionaries
    """
    sections = []

    # Simple heuristic: intro, verse, chorus, verse, chorus, bridge, chorus, outro
    # Adjust based on duration

    if duration < 60:
        # Short song
        sections = [
            {"name": "intro", "start_time": 0.0, "end_time": min(8, duration * 0.1)},
            {"name": "verse", "start_time": min(8, duration * 0.1), "end_time": duration * 0.4},
            {"name": "chorus", "start_time": duration * 0.4, "end_time": duration * 0.7},
            {"name": "verse", "start_time": duration * 0.7, "end_time": duration * 0.9},
            {"name": "outro", "start_time": duration * 0.9, "end_time": duration}
        ]
    elif duration < 180:
        # Normal song (1-3 minutes)
        sections = [
            {"name": "intro", "start_time": 0.0, "end_time": 10.0},
            {"name": "verse", "start_time": 10.0, "end_time": 30.0},
            {"name": "chorus", "start_time": 30.0, "end_time": 50.0},
            {"name": "verse", "start_time": 50.0, "end_time": 70.0},
            {"name": "chorus", "start_time": 70.0, "end_time": 90.0},
            {"name": "bridge", "start_time": 90.0, "end_time": 110.0},
            {"name": "chorus", "start_time": 110.0, "end_time": duration - 10},
            {"name": "outro", "start_time": duration - 10, "end_time": duration}
        ]
    else:
        # Longer song
        sections = [
            {"name": "intro", "start_time": 0.0, "end_time": 15.0},
            {"name": "verse", "start_time": 15.0, "end_time": 45.0},
            {"name": "chorus", "start_time": 45.0, "end_time": 75.0},
            {"name": "verse", "start_time": 75.0, "end_time": 105.0},
            {"name": "chorus", "start_time": 105.0, "end_time": 135.0},
            {"name": "bridge", "start_time": 135.0, "end_time": 165.0},
            {"name": "chorus", "start_time": 165.0, "end_time": duration - 15},
            {"name": "outro", "start_time": duration - 15, "end_time": duration}
        ]

    # Add mood and energy to each section
    for i, section in enumerate(sections):
        section["type"] = section["name"]

        # Simple mood assignment based on section type
        mood_map = {
            "intro": "mysterious",
            "verse": "introspective",
            "chorus": "euphoric",
            "bridge": "emotional",
            "outro": "resolving"
        }
        section["mood"] = mood_map.get(section["name"], "neutral")

        # Energy progression: low intro, building, high chorus
        if section["name"] == "intro":
            section["energy"] = 0.3
        elif section["name"] == "verse":
            section["energy"] = 0.5
        elif section["name"] == "chorus":
            section["energy"] = 0.8 + (i * 0.05)  # Increase energy in later choruses
        elif section["name"] == "bridge":
            section["energy"] = 0.4
        elif section["name"] == "outro":
            section["energy"] = 0.3
        else:
            section["energy"] = 0.5

        # Cap energy at 1.0
        section["energy"] = min(section["energy"], 1.0)

    logger.info(f"Detected {len(sections)} sections using heuristics")
    return sections


def generate_energy_profile(duration: float, sections: List[Dict]) -> List[Dict[str, float]]:
    """
    Generate energy profile sampled at regular intervals.

    Args:
        duration: Audio duration in seconds
        sections: List of detected sections

    Returns:
        List of energy measurements at different timestamps
    """
    energy_profile = []
    sample_interval = 10.0  # Sample every 10 seconds

    current_time = 0.0
    while current_time <= duration:
        # Find which section this timestamp belongs to
        energy = 0.5  # default
        for section in sections:
            if section["start_time"] <= current_time < section["end_time"]:
                energy = section["energy"]
                break

        energy_profile.append({
            "time": round(current_time, 1),
            "energy": round(energy, 2)
        })

        current_time += sample_interval

    logger.info(f"Generated energy profile with {len(energy_profile)} samples")
    return energy_profile


def load_lyrics_lines(lyrics_path: str) -> List[str]:
    """
    Load lyrics from text file and split into lines.

    Args:
        lyrics_path: Path to lyrics text file

    Returns:
        List of lyrics lines (non-empty)

    Raises:
        FileNotFoundError: If lyrics file doesn't exist
    """
    lyrics_file = Path(lyrics_path)

    if not lyrics_file.exists():
        raise FileNotFoundError(f"Lyrics file not found: {lyrics_path}")

    with open(lyrics_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    # Filter out empty lines
    lines = [line for line in lines if line]

    logger.info(f"Loaded {len(lines)} lyrics lines")
    return lines


def check_ffmpeg_available() -> bool:
    """
    Check if ffmpeg/ffprobe is available on the system.

    Returns:
        True if ffmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_aeneas_available() -> bool:
    """
    Check if aeneas library is available.

    Returns:
        True if aeneas can be imported, False otherwise
    """
    try:
        import aeneas
        return True
    except ImportError:
        return False


def check_whisper_available() -> bool:
    """
    Check if OpenAI Whisper is available.

    Returns:
        True if whisper can be imported, False otherwise
    """
    try:
        import whisper
        return True
    except ImportError:
        return False
