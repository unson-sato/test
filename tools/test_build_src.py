#!/usr/bin/env python3
"""
Test suite for build_src.py

Tests the SRC (lyrics timecode) generation tool with various modes.
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
        "First line of the song",
        "Second line continues",
        "Third line builds up",
        "Fourth line is the hook",
        "Fifth line slows down",
        "Sixth line wraps up"
    ]

    temp_lyrics = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_lyrics.write('\n'.join(lyrics))
    temp_lyrics.close()

    return temp_lyrics.name


def test_heuristic_mode():
    """Test heuristic mode (should always work)."""
    print("=" * 60)
    print("TEST 1: Heuristic Mode (No Dependencies)")
    print("=" * 60)

    # Create test files
    print("\n[1/4] Creating test files...")
    mp3_path = create_test_mp3(duration=60.0)
    if not mp3_path:
        print("✗ Failed to create test MP3")
        return False

    lyrics_path = create_test_lyrics()
    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    print("✓ Test files created")

    # Run build_src.py in heuristic mode
    print("\n[2/4] Running build_src.py (heuristic mode)...")
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_src.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path,
        "--mode", "heuristic"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ build_src.py failed with code {result.returncode}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

    print("✓ build_src.py completed")

    # Validate output
    print("\n[3/4] Validating output...")
    try:
        src = read_json(output_path)

        # Check required fields
        required_fields = ["metadata", "lines", "total_lines", "coverage"]
        for field in required_fields:
            if field not in src:
                print(f"✗ Missing required field: {field}")
                return False

        # Check metadata
        metadata = src["metadata"]
        assert metadata["mode_used"] == "heuristic"
        assert "created_at" in metadata
        assert "source_audio" in metadata
        assert "source_lyrics" in metadata

        # Check lines
        lines = src["lines"]
        assert len(lines) > 0
        assert src["total_lines"] == len(lines)

        for i, line in enumerate(lines):
            assert line["index"] == i
            assert "text" in line
            assert "start_time" in line
            assert "end_time" in line
            assert "duration" in line
            assert line["start_time"] < line["end_time"]

        # Check coverage
        coverage = src["coverage"]
        assert "first_line_start" in coverage
        assert "last_line_end" in coverage
        assert "total_duration" in coverage

        print("✓ All validation checks passed")
        print(f"\nSummary:")
        print(f"  Mode: {metadata['mode_used']}")
        print(f"  Total lines: {src['total_lines']}")
        print(f"  First line: {lines[0]['start_time']:.2f}s")
        print(f"  Last line: {lines[-1]['end_time']:.2f}s")

        # Check timing is reasonable
        print("\n[4/4] Checking timing distribution...")
        for i in range(len(lines) - 1):
            current_end = lines[i]["end_time"]
            next_start = lines[i + 1]["start_time"]
            # Lines should be adjacent or close
            assert abs(next_start - current_end) < 0.1, f"Gap between lines {i} and {i+1}"

        print("✓ Timing distribution looks good")

        return True

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        try:
            Path(mp3_path).unlink()
            Path(lyrics_path).unlink()
            Path(output_path).unlink()
        except:
            pass


def test_auto_mode():
    """Test auto mode (should fall back to heuristic if aeneas unavailable)."""
    print("\n" + "=" * 60)
    print("TEST 2: Auto Mode (Graceful Fallback)")
    print("=" * 60)

    # Create test files
    print("\n[1/3] Creating test files...")
    mp3_path = create_test_mp3(duration=30.0)
    if not mp3_path:
        print("✗ Failed to create test MP3")
        return False

    lyrics_path = create_test_lyrics()
    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    print("✓ Test files created")

    # Run build_src.py in auto mode
    print("\n[2/3] Running build_src.py (auto mode)...")
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_src.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path,
        "--mode", "auto"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ build_src.py failed with code {result.returncode}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

    print("✓ build_src.py completed")

    # Validate output
    print("\n[3/3] Validating output...")
    try:
        src = read_json(output_path)

        # Check that some mode was used
        mode_used = src["metadata"]["mode_used"]
        print(f"  Mode used: {mode_used}")

        # Should be either aeneas or heuristic
        assert mode_used in ["aeneas", "heuristic"]

        # Basic validation
        assert len(src["lines"]) > 0
        assert src["total_lines"] == len(src["lines"])

        print("✓ Auto mode worked correctly")
        return True

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    finally:
        try:
            Path(mp3_path).unlink()
            Path(lyrics_path).unlink()
            Path(output_path).unlink()
        except:
            pass


def test_output_format():
    """Test that output format matches specification."""
    print("\n" + "=" * 60)
    print("TEST 3: Output Format Verification")
    print("=" * 60)

    # Create test files
    mp3_path = create_test_mp3(duration=45.0)
    if not mp3_path:
        print("✗ Failed to create test MP3")
        return False

    lyrics_path = create_test_lyrics()
    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    # Run SRC generation
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_src.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path,
        "--mode", "heuristic"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("✗ build_src.py failed")
        return False

    # Check format details
    try:
        src = read_json(output_path)

        # Verify metadata structure
        metadata = src["metadata"]
        assert "mode_used" in metadata
        assert "created_at" in metadata
        assert "source_audio" in metadata
        assert "source_lyrics" in metadata
        assert "duration" in metadata

        # Verify lines structure
        for line in src["lines"]:
            assert "index" in line
            assert "text" in line
            assert "start_time" in line
            assert "end_time" in line
            assert "duration" in line

        # Verify coverage structure
        coverage = src["coverage"]
        assert "first_line_start" in coverage
        assert "last_line_end" in coverage
        assert "total_duration" in coverage

        # Verify total_lines
        assert "total_lines" in src
        assert src["total_lines"] == len(src["lines"])

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


def test_missing_file():
    """Test error handling for missing files."""
    print("\n" + "=" * 60)
    print("TEST 4: Missing File Error Handling")
    print("=" * 60)

    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    cmd = [
        "python3",
        str(Path(__file__).parent / "build_src.py"),
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


def test_timing_accuracy():
    """Test that timing is sensible."""
    print("\n" + "=" * 60)
    print("TEST 5: Timing Accuracy Check")
    print("=" * 60)

    # Create test files with known duration
    duration = 100.0
    mp3_path = create_test_mp3(duration=duration)
    if not mp3_path:
        print("✗ Failed to create test MP3")
        return False

    # Create lyrics with known number of lines
    lyrics = [f"Line {i+1}" for i in range(10)]
    temp_lyrics = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_lyrics.write('\n'.join(lyrics))
    temp_lyrics.close()
    lyrics_path = temp_lyrics.name

    output_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

    # Run SRC generation
    cmd = [
        "python3",
        str(Path(__file__).parent / "build_src.py"),
        "--mp3", mp3_path,
        "--lyrics", lyrics_path,
        "--output", output_path,
        "--mode", "heuristic"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("✗ build_src.py failed")
        return False

    try:
        src = read_json(output_path)

        # Check timing constraints
        lines = src["lines"]

        # All lines should be within audio duration
        for line in lines:
            assert 0 <= line["start_time"] <= duration
            assert 0 <= line["end_time"] <= duration
            assert line["start_time"] < line["end_time"]

        # Lines should be in order
        for i in range(len(lines) - 1):
            assert lines[i]["end_time"] <= lines[i + 1]["start_time"] + 0.1

        # Coverage should match duration
        coverage = src["coverage"]
        assert coverage["total_duration"] == duration

        # First and last lines should be reasonably placed
        assert coverage["first_line_start"] >= 0
        assert coverage["last_line_end"] <= duration

        print("✓ Timing accuracy checks passed")
        print(f"  Duration: {duration}s")
        print(f"  Lines: {len(lines)}")
        print(f"  Coverage: {coverage['first_line_start']:.1f}s - {coverage['last_line_end']:.1f}s")
        print(f"  Avg line duration: {sum(l['duration'] for l in lines) / len(lines):.2f}s")

        return True

    except Exception as e:
        print(f"✗ Timing validation failed: {e}")
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
    print("BUILD_SRC.PY TEST SUITE")
    print("=" * 60)

    tests = [
        ("Heuristic Mode", test_heuristic_mode),
        ("Auto Mode", test_auto_mode),
        ("Output Format Verification", test_output_format),
        ("Missing File Error Handling", test_missing_file),
        ("Timing Accuracy Check", test_timing_accuracy),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
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
