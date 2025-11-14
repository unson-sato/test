"""
Simple test runner for optimization tools (no pytest required)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import SharedState
from core.utils import get_session_dir, read_json
from tools.optimization.emotion_target_builder import (
    EmotionTargetBuilder,
    build_target_curve
)
from tools.optimization.clip_optimizer import (
    ClipOptimizer,
    optimize_clips
)
from tools.optimization.emotion_utils import (
    map_emotion_to_value,
    interpolate_linear,
    interpolate_smooth,
    normalize_emotion_curve,
    get_emotion_statistics
)


def test_emotion_utils():
    """Test emotion utilities independently."""
    print("=" * 60)
    print("TEST: Emotion Utilities")
    print("=" * 60)

    # Test emotion mapping
    print("\n1. Testing emotion mapping...")
    value, label = map_emotion_to_value("mysterious")
    assert value == 0.4 and label == "mysterious"
    print(f"   ✓ 'mysterious' → {value} ({label})")

    value, label = map_emotion_to_value("intense")
    assert value == 1.0 and label == "intense"
    print(f"   ✓ 'intense' → {value} ({label})")

    value, label = map_emotion_to_value("calm")
    assert value == 0.2 and label == "calm"
    print(f"   ✓ 'calm' → {value} ({label})")

    # Test linear interpolation
    print("\n2. Testing linear interpolation...")
    value = interpolate_linear(0.2, 0.8, 0.0, 10.0, 5.0)
    assert abs(value - 0.5) < 0.01
    print(f"   ✓ Midpoint interpolation: {value}")

    # Test smooth interpolation
    print("\n3. Testing smooth interpolation...")
    value = interpolate_smooth(0.2, 0.8, 0.0, 10.0, 5.0)
    assert 0.4 < value < 0.6
    print(f"   ✓ Smooth interpolation: {value}")

    # Test normalization
    print("\n4. Testing curve normalization...")
    test_curve = [
        {'time': 0.0, 'emotion': 0.3},
        {'time': 1.0, 'emotion': 0.5},
        {'time': 2.0, 'emotion': 0.7}
    ]
    normalized = normalize_emotion_curve(test_curve, 0.0, 1.0)
    assert abs(normalized[0]['emotion'] - 0.0) < 0.01
    assert abs(normalized[-1]['emotion'] - 1.0) < 0.01
    print(f"   ✓ Normalized min: {normalized[0]['emotion']:.2f}")
    print(f"   ✓ Normalized max: {normalized[-1]['emotion']:.2f}")

    print("\n✓ All emotion utility tests passed!")


def test_emotion_target_builder(test_session_id):
    """Test emotion target builder."""
    print("\n" + "=" * 60)
    print("TEST: Emotion Target Builder")
    print("=" * 60)

    # Test 1: Builder initialization
    print("\n1. Testing builder initialization...")
    builder = EmotionTargetBuilder(test_session_id, sampling_rate=0.5)
    assert builder.session_id == test_session_id
    assert builder.sampling_rate == 0.5
    print(f"   ✓ Initialized builder for session: {builder.session_id}")

    # Test 2: Load Phase 2 data
    print("\n2. Testing Phase 2 data loading...")
    proposal = builder.load_phase2_data()
    assert 'sections' in proposal
    assert len(proposal['sections']) > 0
    print(f"   ✓ Loaded {len(proposal['sections'])} sections")

    # Test 3: Build section metadata
    print("\n3. Testing section metadata building...")
    sections = proposal['sections']
    metadata = builder.build_section_metadata(sections)
    assert len(metadata) == len(sections)
    print(f"   ✓ Built metadata for {len(metadata)} sections")
    for i, sec in enumerate(metadata[:3]):
        print(f"     - {sec['section_name']}: emotion={sec['target_emotion']:.2f} ({sec['emotion_label']})")

    # Test 4: Build emotion curve
    print("\n4. Testing emotion curve building...")
    result = build_target_curve(test_session_id, sampling_rate=0.5)
    assert 'curve' in result
    assert 'statistics' in result
    print(f"   ✓ Built curve with {result['statistics']['total_samples']} samples")
    print(f"   ✓ Curve path: {result['curve_path']}")
    print(f"   ✓ Emotion range: {result['statistics']['min_emotion']:.2f} - {result['statistics']['max_emotion']:.2f}")
    print(f"   ✓ Average emotion: {result['statistics']['avg_emotion']:.2f}")

    # Test 5: Verify file contents
    print("\n5. Testing saved file...")
    curve_path = Path(result['curve_path'])
    assert curve_path.exists()
    curve_data = read_json(str(curve_path))
    assert 'metadata' in curve_data
    assert 'curve' in curve_data
    assert 'sections' in curve_data
    print(f"   ✓ File exists and has correct structure")

    print("\n✓ All emotion target builder tests passed!")


def test_clip_optimizer(test_session_id):
    """Test clip optimizer."""
    print("\n" + "=" * 60)
    print("TEST: Clip Optimizer")
    print("=" * 60)

    # Ensure emotion curve exists
    print("\n0. Ensuring emotion curve exists...")
    try:
        build_target_curve(test_session_id, sampling_rate=0.5)
        print("   ✓ Emotion curve ready")
    except Exception as e:
        print(f"   ! Note: {e}")

    # Test 1: Optimizer initialization
    print("\n1. Testing optimizer initialization...")
    optimizer = ClipOptimizer(test_session_id)
    assert optimizer.session_id == test_session_id
    assert optimizer.min_clip_duration == 0.8
    assert optimizer.max_clip_duration == 8.0
    print(f"   ✓ Initialized optimizer for session: {optimizer.session_id}")

    # Test 2: Load inputs
    print("\n2. Testing input loading...")
    clips, emotion_curve, beat_times, total_duration = optimizer.load_inputs()
    assert len(clips) > 0
    assert len(emotion_curve) > 0
    print(f"   ✓ Loaded {len(clips)} clips")
    print(f"   ✓ Loaded {len(emotion_curve)} curve points")
    print(f"   ✓ Total duration: {total_duration:.2f}s")

    # Test 3: Emotion score calculation
    print("\n3. Testing emotion score calculation...")
    clip = clips[0]
    score = optimizer.calculate_clip_emotion_score(clip, emotion_curve)
    assert 0.0 <= score <= 1.0
    print(f"   ✓ Clip {clip['clip_id']} emotion score: {score:.3f}")

    # Test 4: Ideal duration calculation
    print("\n4. Testing ideal duration calculation...")
    ideal_high = optimizer.calculate_ideal_duration(0.9, 3.0, "close-up")
    ideal_low = optimizer.calculate_ideal_duration(0.2, 3.0, "medium")
    print(f"   ✓ High emotion (0.9): 3.0s → {ideal_high:.2f}s")
    print(f"   ✓ Low emotion (0.2): 3.0s → {ideal_low:.2f}s")

    # Test 5: Creative adjustments
    print("\n5. Testing creative adjustments...")
    adj = optimizer.calculate_creative_adjustments(clips[0], score)
    assert 'variance_level' in adj
    print(f"   ✓ Variance level: {adj['variance_level']}")
    print(f"   ✓ Lighting: {adj['lighting_variance']}")
    print(f"   ✓ Camera: {adj['camera_movement_variance']}")

    # Test 6: Full optimization
    print("\n6. Testing full optimization process...")
    result = optimize_clips(test_session_id)
    stats = result['statistics']
    print(f"   ✓ Total clips: {stats['clips_adjusted'] + stats['clips_unchanged']}")
    print(f"   ✓ Adjusted: {stats['clips_adjusted']}")
    print(f"   ✓ Unchanged: {stats['clips_unchanged']}")
    print(f"   ✓ Avg adjustment: {stats['avg_adjustment']:.2f}s")
    print(f"   ✓ Max adjustment: {stats['max_adjustment']:.2f}s")
    print(f"   ✓ Duration: {stats['total_duration_before']:.2f}s → {stats['total_duration_after']:.2f}s")

    # Test 7: Variance distribution
    print("\n7. Testing variance distribution...")
    var_counts = result['variance_counts']
    print(f"   ✓ High variance: {var_counts['high']} clips")
    print(f"   ✓ Medium-high variance: {var_counts['medium-high']} clips")
    print(f"   ✓ Medium variance: {var_counts['medium']} clips")

    print("\n✓ All clip optimizer tests passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("MV ORCHESTRA v2.8 - OPTIMIZATION TOOLS TEST SUITE")
    print("=" * 70)

    # Test session ID (use existing test session)
    test_session_id = "mvorch_20251114_163545_d1c7c8d0"

    # Verify session exists
    session_dir = get_session_dir(test_session_id)
    if not session_dir.exists():
        print(f"\n✗ Test session not found: {test_session_id}")
        print("  Please run Phase 0-3 tests first to create test data")
        return 1

    print(f"\nUsing test session: {test_session_id}")

    try:
        # Run tests
        test_emotion_utils()
        test_emotion_target_builder(test_session_id)
        test_clip_optimizer(test_session_id)

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        print("\nOptimization tools are working correctly!")

        return 0

    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
