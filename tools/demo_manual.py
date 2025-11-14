#!/usr/bin/env python3
"""
Manual demonstration of audio analysis tools without ffmpeg.

This script demonstrates the core functionality of the audio analysis
tools using mock data, since ffmpeg is not available in sandbox.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import write_json, get_iso_timestamp
from tools.audio_utils import (
    estimate_bpm_heuristic,
    detect_key_heuristic,
    generate_beats,
    detect_sections_heuristic,
    generate_energy_profile,
)

print("=" * 60)
print("MV Orchestra v2.8 - Audio Analysis Tools Demo")
print("=" * 60)

# Simulate a 3-minute song
duration = 180.0
bpm = 120

print(f"\nSimulating analysis for {duration}s song at {bpm} BPM")

# Step 1: Generate analysis.json structure
print("\n[1/3] Building analysis.json structure...")

sections = detect_sections_heuristic(duration)
beats = generate_beats(duration, bpm)
energy_profile = generate_energy_profile(duration, sections)

# Load demo lyrics
lyrics_file = Path(__file__).parent / "demo_lyrics.txt"
with open(lyrics_file, 'r') as f:
    lyrics_lines = [line.strip() for line in f if line.strip()]

analysis = {
    "metadata": {
        "title": "Demo Song",
        "artist": "Demo Artist",
        "duration": duration,
        "bpm": bpm,
        "key": detect_key_heuristic(),
        "created_at": get_iso_timestamp(),
        "source_audio": "demo_song.mp3",
        "analyzer_version": "2.8.0",
        "analysis_method": "heuristic"
    },
    "sections": sections,
    "beats": beats[:10],  # Just first 10 for demo
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

output_analysis = Path(__file__).parent / "demo_analysis.json"
write_json(str(output_analysis), analysis)
print(f"✓ Written to: {output_analysis}")

# Step 2: Generate SRC structure
print("\n[2/3] Building src.json structure (heuristic mode)...")

# Distribute lyrics evenly across duration
start_offset = duration * 0.05
end_offset = duration * 0.95
usable_duration = end_offset - start_offset
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

src = {
    "metadata": {
        "mode_used": "heuristic",
        "created_at": get_iso_timestamp(),
        "source_audio": "demo_song.mp3",
        "source_lyrics": str(lyrics_file),
        "duration": duration
    },
    "lines": timed_lines,
    "total_lines": len(timed_lines),
    "coverage": {
        "first_line_start": timed_lines[0]["start_time"],
        "last_line_end": timed_lines[-1]["end_time"],
        "total_duration": duration
    }
}

output_src = Path(__file__).parent / "demo_src.json"
write_json(str(output_src), src)
print(f"✓ Written to: {output_src}")

# Step 3: Summary
print("\n[3/3] Summary:")
print(f"  Duration: {duration}s ({duration//60:.0f}m {duration%60:.0f}s)")
print(f"  BPM: {bpm}")
print(f"  Key: {analysis['metadata']['key']}")
print(f"  Sections: {len(sections)}")
print(f"  Beats: {len(beats)} (showing first 10 in demo)")
print(f"  Lyrics lines: {len(lyrics_lines)}")
print(f"  Energy samples: {len(energy_profile)}")
print(f"\nFiles created:")
print(f"  - {output_analysis}")
print(f"  - {output_src}")

print("\n" + "=" * 60)
print("Demo completed successfully!")
print("=" * 60)
print("\nNote: In production with ffmpeg installed, these tools would")
print("analyze real audio files to extract accurate timing data.")
