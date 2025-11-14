#!/usr/bin/env python3
"""
build_src.py - Generate SRC (lyrics timecode) from MP3 + lyrics

This tool performs forced alignment or heuristic timing to generate
lyrics timestamps (SRC - Synchronized Resource Content).

Usage:
    python3 tools/build_src.py --mp3 <audio> --lyrics <text> --output <src.json>

Modes:
    auto (default): Try aeneas first, fall back to heuristic
    aeneas: Use aeneas library for forced alignment
    whisper: Use OpenAI Whisper for speech recognition with timestamps
    heuristic: Simple equal-interval distribution

Requirements by mode:
    - aeneas: pip install aeneas + ffmpeg + espeak
    - whisper: pip install git+https://github.com/openai/whisper.git
    - heuristic: no dependencies (always works)
"""

import argparse
import logging
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import write_json, get_iso_timestamp
from tools.audio_utils import (
    get_audio_duration,
    load_lyrics_lines,
    check_ffmpeg_available,
    check_aeneas_available,
    check_whisper_available
)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def align_with_heuristic(lyrics_lines: List[str], duration: float) -> List[Dict]:
    """
    Align lyrics using simple equal-interval distribution.

    Args:
        lyrics_lines: List of lyrics lines
        duration: Audio duration in seconds

    Returns:
        List of timed lyrics dictionaries
    """
    logger.info("Using heuristic alignment (equal intervals)")

    if not lyrics_lines:
        logger.warning("No lyrics lines to align")
        return []

    # Reserve 5% at start and end for intro/outro
    start_offset = duration * 0.05
    end_offset = duration * 0.95
    usable_duration = end_offset - start_offset

    # Calculate duration per line
    line_duration = usable_duration / len(lyrics_lines)

    timed_lines = []
    for i, line in enumerate(lyrics_lines):
        start_time = start_offset + (i * line_duration)
        end_time = start_time + line_duration

        timed_lines.append({
            "index": i,
            "text": line,
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "duration": round(line_duration, 2)
        })

    logger.info(f"✓ Aligned {len(timed_lines)} lines using heuristic")
    return timed_lines


def align_with_aeneas(mp3_path: str, lyrics_lines: List[str], duration: float) -> List[Dict]:
    """
    Align lyrics using aeneas forced alignment.

    Args:
        mp3_path: Path to MP3 file
        lyrics_lines: List of lyrics lines
        duration: Audio duration in seconds

    Returns:
        List of timed lyrics dictionaries
    """
    logger.info("Using aeneas for forced alignment")

    try:
        from aeneas.executetask import ExecuteTask
        from aeneas.task import Task
    except ImportError:
        logger.error("aeneas not installed. Install with: pip install aeneas")
        logger.info("Falling back to heuristic mode")
        return align_with_heuristic(lyrics_lines, duration)

    # Create temporary files for aeneas
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        lyrics_file = f.name
        for line in lyrics_lines:
            f.write(line + '\n')

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        sync_map_file = f.name

    try:
        # Configure aeneas task
        config_string = "task_language=eng|is_text_type=plain|os_task_file_format=json"

        # Create and execute task
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = mp3_path
        task.text_file_path_absolute = lyrics_file
        task.sync_map_file_path_absolute = sync_map_file

        logger.info("Running aeneas alignment (this may take a moment)...")
        ExecuteTask(task).execute()

        # Read results
        with open(sync_map_file, 'r') as f:
            sync_map = json.load(f)

        # Convert to our format
        timed_lines = []
        for i, fragment in enumerate(sync_map.get('fragments', [])):
            timed_lines.append({
                "index": i,
                "text": fragment['lines'][0] if fragment.get('lines') else lyrics_lines[i],
                "start_time": float(fragment['begin']),
                "end_time": float(fragment['end']),
                "duration": float(fragment['end']) - float(fragment['begin'])
            })

        logger.info(f"✓ Aligned {len(timed_lines)} lines using aeneas")
        return timed_lines

    except Exception as e:
        logger.error(f"aeneas alignment failed: {e}")
        logger.info("Falling back to heuristic mode")
        return align_with_heuristic(lyrics_lines, duration)

    finally:
        # Cleanup temp files
        try:
            Path(lyrics_file).unlink()
            Path(sync_map_file).unlink()
        except:
            pass


def align_with_whisper(mp3_path: str, lyrics_lines: List[str], duration: float,
                       model_name: str = "base") -> List[Dict]:
    """
    Align lyrics using OpenAI Whisper.

    Note: This may fail in sandboxed environments due to OpenMP restrictions.

    Args:
        mp3_path: Path to MP3 file
        lyrics_lines: List of lyrics lines
        duration: Audio duration in seconds
        model_name: Whisper model to use (tiny, base, small, medium, large)

    Returns:
        List of timed lyrics dictionaries
    """
    logger.info(f"Using Whisper ({model_name} model) for alignment")

    try:
        import whisper
    except ImportError:
        logger.error("Whisper not installed. Install with: pip install git+https://github.com/openai/whisper.git")
        logger.info("Falling back to heuristic mode")
        return align_with_heuristic(lyrics_lines, duration)

    try:
        # Load model
        logger.info(f"Loading Whisper {model_name} model...")
        model = whisper.load_model(model_name)

        # Transcribe with word-level timestamps
        logger.info("Transcribing audio (this may take several minutes)...")
        result = model.transcribe(
            mp3_path,
            word_timestamps=True,
            verbose=False
        )

        # Extract segments
        segments = result.get('segments', [])
        if not segments:
            logger.warning("Whisper returned no segments")
            return align_with_heuristic(lyrics_lines, duration)

        # Match segments to lyrics lines (simple approach)
        # This is a simplified matching - production code would need better alignment
        timed_lines = []

        if len(segments) >= len(lyrics_lines):
            # More segments than lyrics lines - group segments
            segments_per_line = len(segments) // len(lyrics_lines)
            for i, line in enumerate(lyrics_lines):
                start_seg = i * segments_per_line
                end_seg = min((i + 1) * segments_per_line, len(segments))

                start_time = segments[start_seg]['start']
                end_time = segments[end_seg - 1]['end']

                timed_lines.append({
                    "index": i,
                    "text": line,
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(end_time - start_time, 2)
                })
        else:
            # Fewer segments than lyrics - distribute evenly
            for i, line in enumerate(lyrics_lines):
                seg_idx = min(i, len(segments) - 1)
                seg = segments[seg_idx]

                # Estimate timing based on position
                progress = i / len(lyrics_lines)
                start_time = duration * progress
                end_time = duration * ((i + 1) / len(lyrics_lines))

                timed_lines.append({
                    "index": i,
                    "text": line,
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(end_time - start_time, 2)
                })

        logger.info(f"✓ Aligned {len(timed_lines)} lines using Whisper")
        return timed_lines

    except Exception as e:
        logger.error(f"Whisper alignment failed: {e}")
        if "libgomp" in str(e) or "OpenMP" in str(e):
            logger.warning("Whisper failed due to OpenMP/libgomp issues (common in sandboxes)")
        logger.info("Falling back to heuristic mode")
        return align_with_heuristic(lyrics_lines, duration)


def build_src(mp3_path: str, lyrics_path: str, output_path: str,
              mode: str = "auto", whisper_model: str = "base") -> bool:
    """
    Build SRC (lyrics timecode) from MP3 and lyrics files.

    Args:
        mp3_path: Path to MP3 audio file
        lyrics_path: Path to lyrics text file
        output_path: Path where src.json will be written
        mode: Alignment mode (auto, aeneas, whisper, heuristic)
        whisper_model: Whisper model name if using whisper mode

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("MV Orchestra v2.8 - SRC (Lyrics Timecode) Builder")
    logger.info("=" * 60)

    # Validate inputs
    mp3_file = Path(mp3_path)
    lyrics_file = Path(lyrics_path)

    if not mp3_file.exists():
        logger.error(f"MP3 file not found: {mp3_path}")
        return False

    if not lyrics_file.exists():
        logger.error(f"Lyrics file not found: {lyrics_path}")
        return False

    logger.info(f"Audio file: {mp3_path}")
    logger.info(f"Lyrics file: {lyrics_path}")
    logger.info(f"Mode: {mode}")

    # Get audio duration
    logger.info("\nExtracting audio duration...")
    duration = get_audio_duration(mp3_path)
    if duration is None:
        logger.error("Failed to extract audio duration")
        return False

    # Load lyrics
    logger.info("Loading lyrics...")
    try:
        lyrics_lines = load_lyrics_lines(lyrics_path)
    except Exception as e:
        logger.error(f"Failed to load lyrics: {e}")
        return False

    # Determine actual mode to use
    actual_mode = mode
    if mode == "auto":
        logger.info("\nAuto mode: checking available alignment methods...")
        if check_aeneas_available():
            logger.info("✓ aeneas is available")
            actual_mode = "aeneas"
        else:
            logger.info("✗ aeneas not available")
            logger.info("→ Using heuristic fallback")
            actual_mode = "heuristic"

    # Perform alignment
    logger.info(f"\nPerforming alignment using mode: {actual_mode}")

    if actual_mode == "aeneas":
        timed_lines = align_with_aeneas(mp3_path, lyrics_lines, duration)
    elif actual_mode == "whisper":
        timed_lines = align_with_whisper(mp3_path, lyrics_lines, duration, whisper_model)
    elif actual_mode == "heuristic":
        timed_lines = align_with_heuristic(lyrics_lines, duration)
    else:
        logger.error(f"Unknown mode: {mode}")
        return False

    if not timed_lines:
        logger.error("Alignment produced no results")
        return False

    # Build SRC structure
    src = {
        "metadata": {
            "mode_used": actual_mode,
            "created_at": get_iso_timestamp(),
            "source_audio": str(mp3_file.resolve()),
            "source_lyrics": str(lyrics_file.resolve()),
            "duration": round(duration, 2)
        },
        "lines": timed_lines,
        "total_lines": len(timed_lines),
        "coverage": {
            "first_line_start": timed_lines[0]["start_time"] if timed_lines else 0,
            "last_line_end": timed_lines[-1]["end_time"] if timed_lines else 0,
            "total_duration": round(duration, 2)
        }
    }

    # Write output
    logger.info(f"\nWriting SRC to: {output_path}")
    try:
        write_json(output_path, src)
        logger.info("✓ SRC generated successfully!")
        logger.info(f"\nSummary:")
        logger.info(f"  Mode used: {actual_mode}")
        logger.info(f"  Total lines: {len(timed_lines)}")
        logger.info(f"  First line: {timed_lines[0]['start_time']:.2f}s")
        logger.info(f"  Last line: {timed_lines[-1]['end_time']:.2f}s")
        logger.info(f"  Coverage: {src['coverage']['first_line_start']:.1f}s - {src['coverage']['last_line_end']:.1f}s")
        return True
    except Exception as e:
        logger.error(f"Failed to write SRC file: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate SRC (lyrics timecode) from MP3 + lyrics for MV Orchestra v2.8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto mode (tries aeneas, falls back to heuristic)
  python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json

  # Force heuristic mode (no dependencies)
  python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode heuristic

  # Use aeneas (requires: pip install aeneas + ffmpeg + espeak)
  python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode aeneas

  # Use Whisper with specific model (requires: pip install whisper)
  python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode whisper --whisper-model base

Modes:
  auto      - Try aeneas first, fall back to heuristic (default)
  aeneas    - Use aeneas forced alignment (best quality, requires dependencies)
  whisper   - Use OpenAI Whisper (may fail in sandboxes)
  heuristic - Simple equal-interval distribution (always works)

Note:
  Whisper may fail in sandboxed environments due to OpenMP/libgomp restrictions.
  For guaranteed functionality, use heuristic mode or install aeneas.
        """
    )

    parser.add_argument(
        "--mp3",
        required=True,
        help="Path to MP3 audio file"
    )

    parser.add_argument(
        "--lyrics",
        required=True,
        help="Path to lyrics text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where src.json will be written"
    )

    parser.add_argument(
        "--mode",
        choices=["auto", "aeneas", "whisper", "heuristic"],
        default="auto",
        help="Alignment mode (default: auto)"
    )

    parser.add_argument(
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use (default: base)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run SRC generation
    success = build_src(
        mp3_path=args.mp3,
        lyrics_path=args.lyrics,
        output_path=args.output,
        mode=args.mode,
        whisper_model=args.whisper_model
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
