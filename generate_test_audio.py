#!/usr/bin/env python3
"""
Generate a simple 10-second test MP3 file

Creates a test audio file with:
- Duration: 10 seconds
- Sample rate: 22050 Hz
- Simple tone pattern with beat
"""

import numpy as np
import soundfile as sf
from pathlib import Path


def generate_test_audio(output_path: str, duration: float = 10.0, sample_rate: int = 22050):
    """
    Generate test audio with rhythmic pattern

    Args:
        output_path: Path to save MP3/WAV file
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    """
    print(f"Generating {duration}s test audio...")

    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create base tone (440 Hz - A4 note)
    base_freq = 440.0
    audio = 0.3 * np.sin(2 * np.pi * base_freq * t)

    # Add harmonics for richer sound
    audio += 0.2 * np.sin(2 * np.pi * (base_freq * 2) * t)
    audio += 0.1 * np.sin(2 * np.pi * (base_freq * 3) * t)

    # Add rhythmic pattern (beat every 0.5 seconds)
    beat_freq = 2.0  # 2 Hz = 120 BPM
    beat_pattern = np.abs(np.sin(2 * np.pi * beat_freq * t))

    # Apply beat envelope
    audio = audio * (0.5 + 0.5 * beat_pattern)

    # Add some variation in melody
    melody_freq = 0.2  # Slow variation
    melody_mod = 1.0 + 0.2 * np.sin(2 * np.pi * melody_freq * t)
    audio = audio * melody_mod

    # Normalize to prevent clipping
    audio = audio / np.max(np.abs(audio)) * 0.9

    # Save as WAV (soundfile doesn't support MP3 directly)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Change extension to .wav if .mp3 was specified
    if output_file.suffix.lower() == '.mp3':
        output_file = output_file.with_suffix('.wav')
        print("  Note: Saving as WAV (librosa can read it)")

    sf.write(str(output_file), audio, sample_rate)

    print(f"✓ Generated: {output_file}")
    print(f"  Duration: {duration}s")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Tempo: ~120 BPM")
    print(f"  Format: WAV (compatible with librosa)")

    return str(output_file)


if __name__ == "__main__":
    import sys

    output = sys.argv[1] if len(sys.argv) > 1 else "test_audio_10sec.wav"
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    audio_file = generate_test_audio(output, duration)

    print(f"\n✅ Test audio ready!")
    print(f"\nNext steps:")
    print(f"  1. Test audio analyzer:")
    print(f"     python mv_orchestra/tools/audio_analyzer.py {audio_file}")
    print(f"  2. Run full orchestrator:")
    print(f"     python mv_orchestra/core/orchestrator.py {audio_file} 10")
