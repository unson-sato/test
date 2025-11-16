#!/usr/bin/env python3
"""
Example: Audio Analysis Only

This example shows how to use the audio analysis tools
without running the full pipeline.

Usage:
    python3 examples/example_analysis_only.py [audio_file.mp3]
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_audio_file(audio_path: str, lyrics_path: str = None):
    """
    Analyze an audio file and generate analysis.json.

    Args:
        audio_path: Path to MP3 file
        lyrics_path: Optional path to lyrics file
    """
    print("=" * 70)
    print("AUDIO ANALYSIS")
    print("=" * 70)

    print(f"\nAudio file: {audio_path}")
    if lyrics_path:
        print(f"Lyrics file: {lyrics_path}")

    try:
        from tools.build_analysis import build_analysis_from_audio

        print("\n→ Analyzing audio...")

        # Build analysis
        analysis = build_analysis_from_audio(
            audio_path=audio_path,
            lyrics_path=lyrics_path,
            output_path="output_analysis.json"
        )

        print("\n✓ Analysis complete!")

        # Display summary
        print("\n" + "=" * 70)
        print("ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"\nTitle: {analysis.get('title', 'Unknown')}")
        print(f"Artist: {analysis.get('artist', 'Unknown')}")
        print(f"Duration: {analysis.get('duration', 0):.1f} seconds")
        print(f"BPM: {analysis.get('bpm', 0)}")
        print(f"Key: {analysis.get('key', 'Unknown')}")

        # Sections
        sections = analysis.get('sections', [])
        print(f"\nSections: {len(sections)}")
        for section in sections:
            print(f"  - {section['name']:10} {section['start']:6.1f}s - {section['end']:6.1f}s  ({section['mood']})")

        # Mood
        print(f"\nOverall Mood: {analysis.get('mood', 'Unknown')}")

        # Energy profile
        energy = analysis.get('energy_profile', {})
        if energy:
            print("\nEnergy Profile:")
            for section, level in energy.items():
                if section != 'average':
                    print(f"  {section:10} → {level}")

        print(f"\n✓ Analysis saved to: output_analysis.json")

        return analysis

    except ImportError:
        print("\n✗ Audio analysis tools not available")
        print("\nTo use audio analysis, install:")
        print("  pip install librosa scipy")
        return None

    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        return None


def demonstrate_manual_analysis():
    """
    Demonstrate creating analysis manually.

    This shows the structure of analysis.json if you want to
    create it without audio processing libraries.
    """
    print("\n" + "=" * 70)
    print("MANUAL ANALYSIS CREATION")
    print("=" * 70)

    from core import write_json

    # Create minimal analysis structure
    manual_analysis = {
        "title": "My Song",
        "artist": "My Artist",
        "genre": "Pop",
        "bpm": 120,
        "key": "C major",
        "duration": 180.0,
        "sections": [
            {
                "name": "intro",
                "start": 0.0,
                "end": 10.0,
                "duration": 10.0,
                "mood": "calm",
                "energy": "low"
            },
            {
                "name": "verse1",
                "start": 10.0,
                "end": 30.0,
                "duration": 20.0,
                "mood": "building",
                "energy": "medium"
            },
            {
                "name": "chorus1",
                "start": 30.0,
                "end": 50.0,
                "duration": 20.0,
                "mood": "energetic",
                "energy": "high"
            }
        ],
        "lyrics": {
            "verse1": "Sample lyrics for verse 1",
            "chorus": "Sample lyrics for chorus"
        },
        "mood": "uplifting, energetic"
    }

    output_path = "manual_analysis.json"
    write_json(output_path, manual_analysis)

    print(f"\n✓ Manual analysis created: {output_path}")
    print("\nYou can now use this with:")
    print(f"  python3 run_all_phases.py my_session --analysis {output_path}")

    return manual_analysis


def main():
    """Run analysis example."""
    print("=" * 70)
    print("MV ORCHESTRA v2.8 - Audio Analysis Example")
    print("=" * 70)

    # Check for audio file argument
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        lyrics_file = sys.argv[2] if len(sys.argv) > 2 else None

        if not Path(audio_file).exists():
            print(f"\n✗ File not found: {audio_file}")
            return 1

        analyze_audio_file(audio_file, lyrics_file)

    else:
        print("\nNo audio file provided.")
        print("\nOption 1: Analyze an audio file")
        print("  python3 examples/example_analysis_only.py song.mp3 [lyrics.txt]")

        print("\nOption 2: Create manual analysis")
        demonstrate_manual_analysis()


if __name__ == "__main__":
    sys.exit(main() or 0)
