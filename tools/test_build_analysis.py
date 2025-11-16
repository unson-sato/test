#!/usr/bin/env python3
"""
Test suite for build_analysis.py

Tests the audio analysis tool with various inputs and edge cases.
"""

import sys
import json
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import read_json


def create_test_mp3(duration: float = 60.0) -> str:
    """
    Create a test MP3 file using ffmpeg.

    Args:
        duration: Duration in seconds

    Returns:
        Path to temporary MP3 file
    """
    temp_mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_mp3.close()

    # Generate silent audio
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(duration),
        "-c:a", "libmp3lame",
        "-b:a", "128k",
        "-y",
        temp_mp3.name
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        return temp_mp3.name
    except Exception as e:
        print(f"Error creating test MP3: {e}")
        return None


def create_test_lyrics() -> str:
    """
    Create a test lyrics file.

    Returns:
        Path to temporary lyrics file
    """
    lyrics = [
        "This is the first line",
        "This is the second line",
        "Chorus comes here now",
        "With more words to sing",
        "",
        "Verse two begins",
        "With different content",
        "But same melody",
        "",
        "Final chorus line",
        "To end the song"
    ]

    temp_lyrics = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_lyrics.write('\n'.join(lyrics))
    temp_lyrics.close()

    return temp_lyrics.name


def test_basic_analysis():
    """Test basic analysis generation."""
    print("=" * 60)
    print("TEST 1: Basic Analysis Generation")
    print("=" * 60)

    # Create test files
    print("\n[1/4] Creating test MP3...")
    mp3_path = create_test_mp3(duration=60.0)
    if not mp3_path:
        print("✗ Failed to create test MP3 (ffmpeg not available?)")
        return False

    print("✓ Test MP3 created")

    print("\n[2/4] Creating test lyrics...")
    lyrics_path = create_test_lyrics()
    print("✓ Test lyrics created")

    # Create temp output
    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    # Run build_analysis.py
    print("\n[3/4] Running build_analysis.py...")
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_analysis.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path,
        "--title", "Test Song",
        "--artist", "Test Artist"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ build_analysis.py failed with code {result.returncode}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

    print("✓ build_analysis.py completed")

    # Validate output
    print("\n[4/4] Validating output...")
    try:
        analysis = read_json(output_path)

        # Check required fields
        required_fields = ["metadata", "sections", "beats", "lyrics", "energy_profile"]
        for field in required_fields:
            if field not in analysis:
                print(f"✗ Missing required field: {field}")
                return False

        # Check metadata
        metadata = analysis["metadata"]
        assert metadata["title"] == "Test Song"
        assert metadata["artist"] == "Test Artist"
        assert metadata["duration"] > 0
        assert metadata["bpm"] > 0

        # Check sections
        sections = analysis["sections"]
        assert len(sections) > 0
        assert all("name" in s for s in sections)
        assert all("start_time" in s for s in sections)
        assert all("end_time" in s for s in sections)

        # Check beats
        beats = analysis["beats"]
        assert len(beats) > 0
        assert all("time" in b for b in beats)
        assert all("bar" in b for b in beats)
        assert all("beat" in b for b in beats)

        # Check lyrics
        lyrics = analysis["lyrics"]
        assert "lines" in lyrics
        assert "total_lines" in lyrics
        assert len(lyrics["lines"]) > 0

        # Check energy profile
        energy_profile = analysis["energy_profile"]
        assert len(energy_profile) > 0
        assert all("time" in e for e in energy_profile)
        assert all("energy" in e for e in energy_profile)

        print("✓ All validation checks passed")
        print(f"\nSummary:")
        print(f"  Duration: {metadata['duration']}s")
        print(f"  BPM: {metadata['bpm']}")
        print(f"  Sections: {len(sections)}")
        print(f"  Beats: {len(beats)}")
        print(f"  Lyrics lines: {lyrics['total_lines']}")
        print(f"  Energy samples: {len(energy_profile)}")

        return True

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    finally:
        # Cleanup
        try:
            Path(mp3_path).unlink()
            Path(lyrics_path).unlink()
            Path(output_path).unlink()
        except:
            pass


def test_missing_file():
    """Test error handling for missing files."""
    print("\n" + "=" * 60)
    print("TEST 2: Missing File Error Handling")
    print("=" * 60)

    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    cmd = [
        "python3",
        str(Path(__file__).parent / "build_analysis.py"),
        "--mp3", "/nonexistent/file.mp3",
        "--lyrics", "/nonexistent/lyrics.txt",
        "--output", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✗ Should have failed with missing file")
        return False

    print("✓ Correctly reported missing file error")
    return True


def test_output_format():
    """Test that output format matches specification."""
    print("\n" + "=" * 60)
    print("TEST 3: Output Format Verification")
    print("=" * 60)

    # Create test files
    mp3_path = create_test_mp3(duration=30.0)
    if not mp3_path:
        print("✗ Failed to create test MP3")
        return False

    lyrics_path = create_test_lyrics()
    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    # Run analysis
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_analysis.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("✗ build_analysis.py failed")
        return False

    # Check format details
    try:
        analysis = read_json(output_path)

        # Verify metadata structure
        metadata = analysis["metadata"]
        assert "title" in metadata
        assert "artist" in metadata
        assert "duration" in metadata
        assert "bpm" in metadata
        assert "key" in metadata
        assert "created_at" in metadata
        assert "source_audio" in metadata

        # Verify sections structure
        for section in analysis["sections"]:
            assert "name" in section
            assert "start_time" in section
            assert "end_time" in section
            assert "type" in section
            assert "mood" in section
            assert "energy" in section

        # Verify beats structure
        for beat in analysis["beats"]:
            assert "time" in beat
            assert "bar" in beat
            assert "beat" in beat

        # Verify lyrics structure
        for line in analysis["lyrics"]["lines"]:
            assert "index" in line
            assert "text" in line
            assert "start_time" in line
            assert "end_time" in line

        # Verify energy profile structure
        for energy in analysis["energy_profile"]:
            assert "time" in energy
            assert "energy" in energy

        print("✓ Output format matches specification")
        return True

    except Exception as e:
        print(f"✗ Format validation failed: {e}")
        return False

    finally:
        try:
            Path(mp3_path).unlink()
            Path(lyrics_path).unlink()
            Path(output_path).unlink()
        except:
            pass


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BUILD_ANALYSIS.PY TEST SUITE")
    print("=" * 60)

    tests = [
        ("Basic Analysis Generation", test_basic_analysis),
        ("Missing File Error Handling", test_missing_file),
        ("Output Format Verification", test_output_format),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
