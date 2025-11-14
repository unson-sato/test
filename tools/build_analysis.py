#!/usr/bin/env python3
"""
build_analysis.py - Generate analysis.json from MP3 + lyrics

This tool analyzes an audio file and lyrics to produce a comprehensive
analysis.json file suitable for use by run_all_phases.py in MV Orchestra v2.8.

Usage:
    python3 tools/build_analysis.py --mp3 <audio.mp3> --lyrics <lyrics.txt> --output <analysis.json>

Features:
    - Audio duration extraction (ffprobe)
    - BPM estimation (heuristic)
    - Key detection (heuristic)
    - Section detection (heuristic)
    - Beat generation
    - Energy profile generation
    - Lyrics loading

For production use, consider integrating:
    - librosa for BPM and key detection
    - essentia for music analysis
    - madmom for beat tracking
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import write_json, get_iso_timestamp
from tools.audio_utils import (
    get_audio_duration,
    estimate_bpm_heuristic,
    detect_key_heuristic,
    generate_beats,
    detect_sections_heuristic,
    generate_energy_profile,
    load_lyrics_lines,
    check_ffmpeg_available
)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def build_analysis(mp3_path: str, lyrics_path: str, output_path: str,
                   title: str = None, artist: str = None) -> bool:
    """
    Build analysis.json from MP3 and lyrics files.

    Args:
        mp3_path: Path to MP3 audio file
        lyrics_path: Path to lyrics text file
        output_path: Path where analysis.json will be written
        title: Optional song title (default: filename)
        artist: Optional artist name (default: "Unknown Artist")

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("MV Orchestra v2.8 - Audio Analysis Builder")
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

    if not check_ffmpeg_available():
        logger.error("ffmpeg/ffprobe not available. Please install ffmpeg.")
        return False

    # Extract metadata
    if title is None:
        title = mp3_file.stem
    if artist is None:
        artist = "Unknown Artist"

    logger.info(f"Analyzing: {title} by {artist}")
    logger.info(f"Audio file: {mp3_path}")
    logger.info(f"Lyrics file: {lyrics_path}")

    # Step 1: Get audio duration
    logger.info("\n[1/6] Extracting audio duration...")
    duration = get_audio_duration(mp3_path)
    if duration is None:
        logger.error("Failed to extract audio duration")
        return False

    # Step 2: Estimate BPM
    logger.info("\n[2/6] Estimating BPM...")
    bpm = estimate_bpm_heuristic(duration)

    # Step 3: Detect key
    logger.info("\n[3/6] Detecting musical key...")
    key = detect_key_heuristic()

    # Step 4: Generate beats
    logger.info("\n[4/6] Generating beat timestamps...")
    beats = generate_beats(duration, bpm)

    # Step 5: Detect sections
    logger.info("\n[5/6] Detecting song sections...")
    sections = detect_sections_heuristic(duration)

    # Step 6: Load lyrics
    logger.info("\n[6/6] Loading lyrics...")
    try:
        lyrics_lines = load_lyrics_lines(lyrics_path)
    except Exception as e:
        logger.error(f"Failed to load lyrics: {e}")
        return False

    # Generate energy profile
    energy_profile = generate_energy_profile(duration, sections)

    # Build analysis structure
    analysis = {
        "metadata": {
            "title": title,
            "artist": artist,
            "duration": round(duration, 2),
            "bpm": bpm,
            "key": key,
            "created_at": get_iso_timestamp(),
            "source_audio": str(mp3_file.resolve()),
            "analyzer_version": "2.8.0",
            "analysis_method": "heuristic"
        },
        "sections": sections,
        "beats": beats,
        "lyrics": {
            "lines": [
                {
                    "index": i,
                    "text": line,
                    "start_time": None,
                    "end_time": None
                }
                for i, line in enumerate(lyrics_lines)
            ],
            "total_lines": len(lyrics_lines)
        },
        "energy_profile": energy_profile
    }

    # Write output
    logger.info(f"\nWriting analysis to: {output_path}")
    try:
        write_json(output_path, analysis)
        logger.info("✓ Analysis generated successfully!")
        logger.info(f"\nSummary:")
        logger.info(f"  Duration: {duration:.1f}s ({duration // 60:.0f}m {duration % 60:.0f}s)")
        logger.info(f"  BPM: {bpm}")
        logger.info(f"  Key: {key}")
        logger.info(f"  Sections: {len(sections)}")
        logger.info(f"  Beats: {len(beats)}")
        logger.info(f"  Lyrics lines: {len(lyrics_lines)}")
        logger.info(f"\nNext step: Use build_src.py to add lyrics timestamps")
        return True
    except Exception as e:
        logger.error(f"Failed to write analysis file: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate analysis.json from MP3 + lyrics for MV Orchestra v2.8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 tools/build_analysis.py --mp3 song.mp3 --lyrics lyrics.txt --output analysis.json

  # With metadata
  python3 tools/build_analysis.py --mp3 song.mp3 --lyrics lyrics.txt --output analysis.json \\
      --title "Electric Dreams" --artist "Neon Pulse"

Requirements:
  - ffmpeg/ffprobe must be installed
  - MP3 file must be valid
  - Lyrics file must be plain text

Note:
  This tool uses heuristic analysis. For production-quality analysis,
  consider integrating librosa, essentia, or madmom.
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
        help="Path to lyrics text file (one line per lyric line)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where analysis.json will be written"
    )

    parser.add_argument(
        "--title",
        help="Song title (default: filename)"
    )

    parser.add_argument(
        "--artist",
        help="Artist name (default: 'Unknown Artist')"
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

    # Run analysis
    success = build_analysis(
        mp3_path=args.mp3,
        lyrics_path=args.lyrics,
        output_path=args.output,
        title=args.title,
        artist=args.artist
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
