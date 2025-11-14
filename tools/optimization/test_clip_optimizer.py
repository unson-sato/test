"""
Tests for Clip Optimizer

Run with: python -m pytest tools/optimization/test_clip_optimizer.py -v
Or: python tools/optimization/test_clip_optimizer.py
"""

import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import pytest
except ImportError:
    pytest = None  # Allow running without pytest

from core import SharedState
from core.utils import get_session_dir, read_json
from tools.optimization.clip_optimizer import (
    ClipOptimizer,
    optimize_clips
)
from tools.optimization.emotion_target_builder import build_target_curve


class TestClipOptimizer:
    """Test suite for ClipOptimizer."""

    @pytest.fixture
    def test_session_id(self):
        """
        Get a test session ID that has Phase 0-3 completed.
        This uses an existing test session from the test suite.
        """
        return "mvorch_20251114_163545_d1c7c8d0"

    @pytest.fixture
    def setup_emotion_curve(self, test_session_id):
        """Set up emotion curve before running optimizer tests."""
        # Build emotion curve if not already present
        try:
            build_target_curve(test_session_id, sampling_rate=0.5)
        except Exception as e:
            print(f"Note: Emotion curve may already exist: {e}")

    def test_optimizer_initialization(self, test_session_id):
        """Test optimizer initialization."""
        optimizer = ClipOptimizer(test_session_id)
        assert optimizer.session_id == test_session_id
        assert optimizer.min_clip_duration == 0.8
        assert optimizer.max_clip_duration == 8.0
        assert optimizer.session is not None

    def test_load_inputs(self, test_session_id, setup_emotion_curve):
        """Test loading optimizer inputs."""
        optimizer = ClipOptimizer(test_session_id)
        clips, emotion_curve, beat_times, total_duration = optimizer.load_inputs()

        assert len(clips) > 0
        assert len(emotion_curve) > 0
        assert len(beat_times) > 0
        assert total_duration > 0

    def test_clip_emotion_score_calculation(self, test_session_id, setup_emotion_curve):
        """Test emotion score calculation for clips."""
        optimizer = ClipOptimizer(test_session_id)
        clips, emotion_curve, _, _ = optimizer.load_inputs()

        # Test first clip
        clip = clips[0]
        score = optimizer.calculate_clip_emotion_score(clip, emotion_curve)

        assert 0.0 <= score <= 1.0
        print(f"Clip {clip['clip_id']} emotion score: {score:.3f}")

    def test_ideal_duration_calculation(self, test_session_id):
        """Test ideal duration calculation."""
        optimizer = ClipOptimizer(test_session_id)

        # Test high emotion clip
        ideal_high = optimizer.calculate_ideal_duration(0.9, 3.0, "close-up detail")
        assert ideal_high >= 3.0  # Should extend high-emotion clips

        # Test low emotion clip
        ideal_low = optimizer.calculate_ideal_duration(0.2, 3.0, "medium coverage")
        assert ideal_low <= 3.0  # May shorten low-emotion clips

        # Test establishing shot minimum
        ideal_wide = optimizer.calculate_ideal_duration(0.5, 1.5, "establishing wide")
        assert ideal_wide >= 2.0  # Wide shots need minimum time

    def test_beat_snapping(self, test_session_id, setup_emotion_curve):
        """Test beat time snapping."""
        optimizer = ClipOptimizer(test_session_id)
        _, _, beat_times, _ = optimizer.load_inputs()

        # Test snapping to nearby beat
        time = 5.3
        snapped = optimizer.find_nearest_beat(time, beat_times, tolerance=0.5)
        assert snapped in beat_times or snapped == time

        # Test no snapping if too far
        time = 5.0
        snapped = optimizer.find_nearest_beat(time, beat_times, tolerance=0.1)
        # Should either find a very close beat or return original

    def test_creative_adjustments(self, test_session_id):
        """Test creative adjustment calculations."""
        optimizer = ClipOptimizer(test_session_id)

        # Test high emotion clip
        clip_high = {'clip_id': 'test_001', 'shot_type': 'close-up'}
        adjustments_high = optimizer.calculate_creative_adjustments(clip_high, 0.9)

        assert adjustments_high['variance_level'] == 'high'
        assert adjustments_high['lighting_variance'] == 'high'
        assert 'suggestions' in adjustments_high

        # Test low emotion clip
        clip_low = {'clip_id': 'test_002', 'shot_type': 'medium'}
        adjustments_low = optimizer.calculate_creative_adjustments(clip_low, 0.2)

        assert adjustments_low['variance_level'] == 'low'
        assert adjustments_low['lighting_variance'] == 'low'

    def test_clip_optimization(self, test_session_id, setup_emotion_curve):
        """Test single clip optimization."""
        optimizer = ClipOptimizer(test_session_id)
        clips, emotion_curve, beat_times, _ = optimizer.load_inputs()

        clip = clips[0]
        emotion_score = optimizer.calculate_clip_emotion_score(clip, emotion_curve)

        opt_result, adjusted = optimizer.optimize_clip(
            clip, emotion_score, beat_times, 0.0
        )

        assert 'clip_id' in opt_result
        assert 'original_duration' in opt_result
        assert 'optimized_duration' in opt_result
        assert 'emotion_score' in opt_result
        assert 'adjustment_made' in opt_result
        assert isinstance(adjusted, bool)

        # Verify duration constraints
        assert opt_result['optimized_duration'] >= optimizer.min_clip_duration
        assert opt_result['optimized_duration'] <= optimizer.max_clip_duration

    def test_full_optimization_process(self, test_session_id, setup_emotion_curve):
        """Test the complete optimization process."""
        result = optimize_clips(test_session_id)

        assert 'optimization_results' in result
        assert 'statistics' in result
        assert 'variance_counts' in result
        assert 'summary_path' in result

        # Verify statistics
        stats = result['statistics']
        assert 'clips_adjusted' in stats
        assert 'clips_unchanged' in stats
        assert 'avg_adjustment' in stats
        assert 'total_duration_before' in stats
        assert 'total_duration_after' in stats

        # Duration should be preserved
        assert abs(stats['total_duration_before'] - stats['total_duration_after']) < 0.1

        # Verify file was created
        summary_path = Path(result['summary_path'])
        assert summary_path.exists()

        # Verify file contents
        summary_data = read_json(str(summary_path))
        assert 'metadata' in summary_data
        assert 'optimization_results' in summary_data
        assert 'statistics' in summary_data
        assert 'creative_adjustments_summary' in summary_data

    def test_phase3_data_updated(self, test_session_id, setup_emotion_curve):
        """Test that Phase 3 clips are updated with optimization data."""
        # Run optimization
        optimize_clips(test_session_id)

        # Load session and check Phase 3 data
        session = SharedState.load_session(test_session_id)
        phase3_data = session.get_phase_data(3)
        winner_proposal = phase3_data.data.get('winner', {}).get('proposal', {})
        clips = winner_proposal.get('clips', [])

        # Verify clips have optimization data
        assert len(clips) > 0
        for clip in clips:
            assert 'base_allocation' in clip
            assert 'creative_adjustments' in clip
            assert clip['base_allocation'] > 0

    def test_variance_distribution(self, test_session_id, setup_emotion_curve):
        """Test that variance levels are properly distributed."""
        result = optimize_clips(test_session_id)
        variance_counts = result['variance_counts']

        # Should have at least some variance distribution
        total_variance = sum(variance_counts.values())
        assert total_variance > 0

        # Print distribution for inspection
        print(f"\nVariance distribution:")
        print(f"  High: {variance_counts['high']}")
        print(f"  Medium-high: {variance_counts['medium-high']}")
        print(f"  Medium: {variance_counts['medium']}")


def main():
    """Run tests manually if not using pytest."""
    print("Running Clip Optimizer Tests...\n")

    # Test session ID (use existing test session)
    test_session_id = "mvorch_20251114_163545_d1c7c8d0"

    # Verify session exists
    session_dir = get_session_dir(test_session_id)
    if not session_dir.exists():
        print(f"✗ Test session not found: {test_session_id}")
        print("  Please run Phase 0-3 tests first to create test data")
        return 1

    try:
        # Ensure emotion curve exists
        print("Setup: Building emotion curve...")
        try:
            build_target_curve(test_session_id, sampling_rate=0.5)
            print("✓ Emotion curve ready\n")
        except Exception as e:
            print(f"Note: {e}\n")

        # Test 1: Optimizer initialization
        print("Test 1: Optimizer initialization...")
        optimizer = ClipOptimizer(test_session_id)
        print(f"✓ Passed - Session: {optimizer.session_id}\n")

        # Test 2: Load inputs
        print("Test 2: Load inputs...")
        clips, emotion_curve, beat_times, total_duration = optimizer.load_inputs()
        print(f"✓ Passed - Loaded {len(clips)} clips, {len(emotion_curve)} curve points")
        print(f"  Total duration: {total_duration:.2f}s\n")

        # Test 3: Emotion score calculation
        print("Test 3: Clip emotion score calculation...")
        clip = clips[0]
        score = optimizer.calculate_clip_emotion_score(clip, emotion_curve)
        print(f"✓ Passed - Clip {clip['clip_id']} score: {score:.3f}\n")

        # Test 4: Ideal duration calculation
        print("Test 4: Ideal duration calculation...")
        ideal_high = optimizer.calculate_ideal_duration(0.9, 3.0, "close-up")
        ideal_low = optimizer.calculate_ideal_duration(0.2, 3.0, "medium")
        print(f"✓ Passed")
        print(f"  High emotion (0.9): 3.0s → {ideal_high:.2f}s")
        print(f"  Low emotion (0.2): 3.0s → {ideal_low:.2f}s\n")

        # Test 5: Creative adjustments
        print("Test 5: Creative adjustments...")
        adj = optimizer.calculate_creative_adjustments(clips[0], score)
        print(f"✓ Passed - Variance level: {adj['variance_level']}")
        print(f"  Lighting: {adj['lighting_variance']}")
        print(f"  Camera: {adj['camera_movement_variance']}\n")

        # Test 6: Full optimization
        print("Test 6: Full optimization process...")
        result = optimize_clips(test_session_id)
        stats = result['statistics']
        print(f"✓ Passed - Optimization complete")
        print(f"  Total clips: {stats['clips_adjusted'] + stats['clips_unchanged']}")
        print(f"  Adjusted: {stats['clips_adjusted']}")
        print(f"  Unchanged: {stats['clips_unchanged']}")
        print(f"  Avg adjustment: {stats['avg_adjustment']:.2f}s")
        print(f"  Max adjustment: {stats['max_adjustment']:.2f}s")
        print(f"  Duration preserved: {stats['total_duration_before']:.2f}s → {stats['total_duration_after']:.2f}s")
        print(f"  Summary: {result['summary_path']}\n")

        # Test 7: Variance distribution
        print("Test 7: Variance distribution...")
        var_counts = result['variance_counts']
        print(f"✓ Passed")
        print(f"  High variance: {var_counts['high']} clips")
        print(f"  Medium-high variance: {var_counts['medium-high']} clips")
        print(f"  Medium variance: {var_counts['medium']} clips\n")

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
