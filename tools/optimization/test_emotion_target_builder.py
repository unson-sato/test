"""
Tests for Emotion Target Builder

Run with: python -m pytest tools/optimization/test_emotion_target_builder.py -v
Or: python tools/optimization/test_emotion_target_builder.py
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
from tools.optimization.emotion_target_builder import (
    EmotionTargetBuilder,
    build_target_curve
)
from tools.optimization.emotion_utils import (
    map_emotion_to_value,
    get_emotion_statistics
)


# Only define pytest-based tests if pytest is available
if pytest is not None:
    class TestEmotionTargetBuilder:
        """Test suite for EmotionTargetBuilder."""

    @pytest.fixture
    def test_session_id(self):
        """
        Get a test session ID that has Phase 0, 1, and 2 completed.
        This uses an existing test session from the test suite.
        """
        # Use the latest session that has Phase 2 completed
        return "mvorch_20251114_163545_d1c7c8d0"

    def test_emotion_mapping(self):
        """Test emotion keyword to value mapping."""
        # Test exact matches
        value, label = map_emotion_to_value("mysterious")
        assert value == 0.4
        assert label == "mysterious"

        value, label = map_emotion_to_value("intense")
        assert value == 1.0
        assert label == "intense"

        value, label = map_emotion_to_value("calm")
        assert value == 0.2
        assert label == "calm"

    def test_emotion_mapping_composite(self):
        """Test mapping of composite emotion descriptions."""
        value, label = map_emotion_to_value("emotional, artistic intro")
        assert 0.5 <= value <= 0.7  # Should match "emotional"

        value, label = map_emotion_to_value("upbeat and energetic")
        assert value == 0.8  # Should match "upbeat" or "energetic"

    def test_builder_initialization(self, test_session_id):
        """Test builder initialization."""
        builder = EmotionTargetBuilder(test_session_id, sampling_rate=0.5)
        assert builder.session_id == test_session_id
        assert builder.sampling_rate == 0.5
        assert builder.session is not None

    def test_load_phase2_data(self, test_session_id):
        """Test loading Phase 2 data."""
        builder = EmotionTargetBuilder(test_session_id)
        proposal = builder.load_phase2_data()

        assert 'sections' in proposal
        assert len(proposal['sections']) > 0

    def test_build_section_metadata(self, test_session_id):
        """Test building section metadata with emotion values."""
        builder = EmotionTargetBuilder(test_session_id)
        proposal = builder.load_phase2_data()
        sections = proposal['sections']

        metadata = builder.build_section_metadata(sections)

        assert len(metadata) == len(sections)
        for section in metadata:
            assert 'section_name' in section
            assert 'start_time' in section
            assert 'end_time' in section
            assert 'target_emotion' in section
            assert 'emotion_label' in section
            assert 0.0 <= section['target_emotion'] <= 1.0

    def test_build_emotion_curve(self, test_session_id):
        """Test building the emotion curve."""
        builder = EmotionTargetBuilder(test_session_id, sampling_rate=1.0)
        proposal = builder.load_phase2_data()
        sections = proposal['sections']

        total_duration = max(s.get('end_time', 0.0) for s in sections)
        section_metadata = builder.build_section_metadata(sections)
        curve = builder.build_emotion_curve(section_metadata, total_duration)

        # Verify curve properties
        assert len(curve) > 0
        assert curve[0]['time'] == 0.0

        # Check all required fields
        for point in curve:
            assert 'time' in point
            assert 'emotion' in point
            assert 'source_section' in point
            assert 'label' in point
            assert 0.0 <= point['emotion'] <= 1.0

        # Verify time spacing matches sampling rate
        if len(curve) > 1:
            time_diff = curve[1]['time'] - curve[0]['time']
            assert abs(time_diff - builder.sampling_rate) < 0.01

    def test_emotion_statistics(self, test_session_id):
        """Test emotion curve statistics calculation."""
        builder = EmotionTargetBuilder(test_session_id)
        proposal = builder.load_phase2_data()
        sections = proposal['sections']

        total_duration = max(s.get('end_time', 0.0) for s in sections)
        section_metadata = builder.build_section_metadata(sections)
        curve = builder.build_emotion_curve(section_metadata, total_duration)

        stats = get_emotion_statistics(curve)

        assert 'min_emotion' in stats
        assert 'max_emotion' in stats
        assert 'avg_emotion' in stats
        assert 'total_samples' in stats
        assert stats['total_samples'] == len(curve)
        assert stats['min_emotion'] <= stats['avg_emotion'] <= stats['max_emotion']

    def test_full_build_process(self, test_session_id):
        """Test the complete build process."""
        result = build_target_curve(test_session_id, sampling_rate=0.5)

        assert 'curve' in result
        assert 'sections' in result
        assert 'statistics' in result
        assert 'curve_path' in result

        # Verify file was created
        curve_path = Path(result['curve_path'])
        assert curve_path.exists()

        # Verify file contents
        curve_data = read_json(str(curve_path))
        assert 'metadata' in curve_data
        assert 'curve' in curve_data
        assert 'sections' in curve_data
        assert 'statistics' in curve_data

        # Verify metadata
        assert curve_data['metadata']['session_id'] == test_session_id
        assert curve_data['metadata']['source_phase'] == 2
        assert curve_data['metadata']['sampling_rate'] == 0.5

    def test_interpolation_at_section_boundaries(self, test_session_id):
        """Test that interpolation works correctly at section boundaries."""
        builder = EmotionTargetBuilder(test_session_id, sampling_rate=0.1)
        proposal = builder.load_phase2_data()
        sections = proposal['sections']

        total_duration = max(s.get('end_time', 0.0) for s in sections)
        section_metadata = builder.build_section_metadata(sections)
        curve = builder.build_emotion_curve(section_metadata, total_duration)

        # Find points near section boundaries and verify smooth transitions
        for i in range(len(section_metadata) - 1):
            section_end = section_metadata[i]['end_time']

            # Find curve points near this boundary
            nearby_points = [
                p for p in curve
                if abs(p['time'] - section_end) < 2.0
            ]

            # Should have multiple points for smooth transition
            assert len(nearby_points) > 0


def test_emotion_utils():
    """Test emotion utilities independently."""
    from tools.optimization.emotion_utils import (
        map_emotion_to_value,
        interpolate_linear,
        interpolate_smooth,
        normalize_emotion_curve
    )

    # Test linear interpolation
    value = interpolate_linear(0.2, 0.8, 0.0, 10.0, 5.0)
    assert abs(value - 0.5) < 0.01  # Midpoint

    # Test smooth interpolation
    value = interpolate_smooth(0.2, 0.8, 0.0, 10.0, 5.0)
    assert 0.4 < value < 0.6  # Should be near midpoint but smoothed

    # Test normalization
    test_curve = [
        {'time': 0.0, 'emotion': 0.3},
        {'time': 1.0, 'emotion': 0.5},
        {'time': 2.0, 'emotion': 0.7}
    ]
    normalized = normalize_emotion_curve(test_curve, 0.0, 1.0)
    assert normalized[0]['emotion'] == 0.0  # Min maps to 0
    assert normalized[-1]['emotion'] == 1.0  # Max maps to 1
    assert 0.0 < normalized[1]['emotion'] < 1.0  # Middle value


def main():
    """Run tests manually if not using pytest."""
    print("Running Emotion Target Builder Tests...\n")

    # Test session ID (use existing test session)
    test_session_id = "mvorch_20251114_163545_d1c7c8d0"

    # Verify session exists
    session_dir = get_session_dir(test_session_id)
    if not session_dir.exists():
        print(f"✗ Test session not found: {test_session_id}")
        print("  Please run Phase 0-2 tests first to create test data")
        return 1

    try:
        # Test 1: Emotion mapping
        print("Test 1: Emotion mapping...")
        test_emotion_utils()
        print("✓ Passed\n")

        # Test 2: Builder initialization
        print("Test 2: Builder initialization...")
        builder = EmotionTargetBuilder(test_session_id)
        print(f"✓ Passed - Session: {builder.session_id}\n")

        # Test 3: Load Phase 2 data
        print("Test 3: Load Phase 2 data...")
        proposal = builder.load_phase2_data()
        print(f"✓ Passed - Loaded {len(proposal['sections'])} sections\n")

        # Test 4: Build section metadata
        print("Test 4: Build section metadata...")
        metadata = builder.build_section_metadata(proposal['sections'])
        print(f"✓ Passed - Built metadata for {len(metadata)} sections")
        for sec in metadata[:3]:
            print(f"  - {sec['section_name']}: emotion={sec['target_emotion']:.2f} ({sec['emotion_label']})")
        print()

        # Test 5: Build emotion curve
        print("Test 5: Build emotion curve...")
        result = build_target_curve(test_session_id, sampling_rate=0.5)
        print(f"✓ Passed - Built curve with {result['statistics']['total_samples']} samples")
        print(f"  Curve path: {result['curve_path']}")
        print(f"  Emotion range: {result['statistics']['min_emotion']:.2f} - {result['statistics']['max_emotion']:.2f}")
        print(f"  Average emotion: {result['statistics']['avg_emotion']:.2f}\n")

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
