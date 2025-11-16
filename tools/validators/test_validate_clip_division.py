"""
Tests for Phase 3 Clip Division Validator

Tests validation functionality for clip division output including:
- Valid data passes all checks
- Invalid data is correctly detected
- Edge cases are handled properly
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.validators.validation_utils import (
    validate_unique_ids,
    validate_timing_consistency,
    validate_timeline_coverage,
    validate_duration_sanity
)
from tools.validators.validate_clip_division import (
    validate_section_coverage,
    validate_beat_alignment,
    validate_base_allocation,
    validate_creative_adjustments
)


class TestClipIDUniqueness:
    """Test clip ID uniqueness validation."""

    def test_unique_ids_pass(self):
        """Test that unique IDs pass validation."""
        clips = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002'},
            {'clip_id': 'clip_003'}
        ]
        result = validate_unique_ids(clips, 'clip_id')
        assert result['passed'] is True
        assert len(result['duplicate_ids']) == 0

    def test_duplicate_ids_fail(self):
        """Test that duplicate IDs are detected."""
        clips = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002'},
            {'clip_id': 'clip_001'}  # Duplicate
        ]
        result = validate_unique_ids(clips, 'clip_id')
        assert result['passed'] is False
        assert 'clip_001' in result['duplicate_ids']


class TestTimingConsistency:
    """Test timing consistency validation."""

    def test_valid_timing_pass(self):
        """Test that valid timing passes."""
        clips = [
            {
                'clip_id': 'clip_001',
                'start_time': 0.0,
                'end_time': 3.0,
                'duration': 3.0
            },
            {
                'clip_id': 'clip_002',
                'start_time': 3.0,
                'end_time': 6.0,
                'duration': 3.0
            }
        ]
        result = validate_timing_consistency(clips)
        assert result['passed'] is True
        assert len(result['issues']) == 0

    def test_start_after_end_fail(self):
        """Test that start >= end is detected."""
        clips = [
            {
                'clip_id': 'clip_001',
                'start_time': 5.0,
                'end_time': 3.0,  # Invalid
                'duration': -2.0
            }
        ]
        result = validate_timing_consistency(clips)
        assert result['passed'] is False
        assert len(result['issues']) > 0

    def test_duration_mismatch_fail(self):
        """Test that duration mismatch is detected."""
        clips = [
            {
                'clip_id': 'clip_001',
                'start_time': 0.0,
                'end_time': 3.0,
                'duration': 5.0  # Should be 3.0
            }
        ]
        result = validate_timing_consistency(clips)
        assert result['passed'] is False
        assert any('duration mismatch' in issue.lower() for issue in result['issues'])

    def test_negative_timing_fail(self):
        """Test that negative times are detected."""
        clips = [
            {
                'clip_id': 'clip_001',
                'start_time': -1.0,  # Invalid
                'end_time': 3.0,
                'duration': 4.0
            }
        ]
        result = validate_timing_consistency(clips)
        assert result['passed'] is False


class TestTimelineCoverage:
    """Test timeline coverage validation."""

    def test_full_coverage_pass(self):
        """Test that full coverage passes."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 3.0},
            {'clip_id': 'clip_002', 'start_time': 3.0, 'end_time': 6.0},
            {'clip_id': 'clip_003', 'start_time': 6.0, 'end_time': 10.0}
        ]
        result = validate_timeline_coverage(clips, total_duration=10.0)
        assert result['passed'] is True
        assert len(result['gaps']) == 0
        assert len(result['overlaps']) == 0
        assert result['coverage_percentage'] >= 99.0

    def test_gap_detection(self):
        """Test that gaps are detected."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 3.0},
            {'clip_id': 'clip_002', 'start_time': 5.0, 'end_time': 10.0}  # Gap 3.0-5.0
        ]
        result = validate_timeline_coverage(clips, total_duration=10.0, gap_tolerance=0.5)
        assert result['passed'] is False
        assert len(result['gaps']) > 0
        assert result['gaps'][0]['start'] == 3.0
        assert result['gaps'][0]['end'] == 5.0

    def test_overlap_detection(self):
        """Test that overlaps are detected."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 5.0},
            {'clip_id': 'clip_002', 'start_time': 4.0, 'end_time': 8.0}  # Overlap 4.0-5.0
        ]
        result = validate_timeline_coverage(clips, total_duration=10.0)
        assert result['passed'] is False
        assert len(result['overlaps']) > 0


class TestSectionCoverage:
    """Test section coverage validation."""

    def test_valid_sections_pass(self):
        """Test that valid section assignments pass."""
        clips = [
            {'clip_id': 'clip_001', 'section': 'Intro'},
            {'clip_id': 'clip_002', 'section': 'Verse 1'},
            {'clip_id': 'clip_003', 'section': 'Chorus'}
        ]
        sections = ['Intro', 'Verse 1', 'Chorus']
        result = validate_section_coverage(clips, sections)
        assert result['passed'] is True

    def test_missing_section_fail(self):
        """Test that missing sections are detected."""
        clips = [
            {'clip_id': 'clip_001'},  # No section
            {'clip_id': 'clip_002', 'section': 'Intro'}
        ]
        sections = ['Intro', 'Verse 1']
        result = validate_section_coverage(clips, sections)
        assert result['passed'] is False
        assert 'clip_001' in result['unassigned_clips']

    def test_invalid_section_fail(self):
        """Test that invalid sections are detected."""
        clips = [
            {'clip_id': 'clip_001', 'section': 'Unknown Section'}
        ]
        sections = ['Intro', 'Verse 1']
        result = validate_section_coverage(clips, sections)
        assert result['passed'] is False
        assert len(result['invalid_sections']) > 0


class TestBeatAlignment:
    """Test beat alignment validation."""

    def test_aligned_clips_pass(self):
        """Test that beat-aligned clips pass."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 2.0},
            {'clip_id': 'clip_002', 'start_time': 2.0, 'end_time': 4.0}
        ]
        beat_times = [0.0, 1.0, 2.0, 3.0, 4.0]
        result = validate_beat_alignment(clips, beat_times, tolerance=0.1)
        assert result['passed'] is True
        assert result['alignment_percentage'] == 100.0

    def test_misaligned_clips_warning(self):
        """Test that misaligned clips generate warnings."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.5, 'end_time': 2.5, 'beat_aligned': True}
        ]
        beat_times = [0.0, 1.0, 2.0, 3.0, 4.0]
        result = validate_beat_alignment(clips, beat_times, tolerance=0.1)
        # This clip claims to be beat aligned but isn't
        assert 'clip_001' in result.get('misaligned_clips', [])

    def test_no_beat_data(self):
        """Test behavior when no beat data is available."""
        clips = [
            {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 3.0}
        ]
        result = validate_beat_alignment(clips, beat_times=None)
        assert result['passed'] is True  # Should pass with warning


class TestBaseAllocation:
    """Test base allocation validation."""

    def test_all_clips_have_allocation(self):
        """Test that clips with allocation pass."""
        clips = [
            {'clip_id': 'clip_001', 'base_allocation': 3.0},
            {'clip_id': 'clip_002', 'base_allocation': 2.5}
        ]
        result = validate_base_allocation(clips)
        assert result['passed'] is True
        assert result['clips_with_allocation'] == 2
        assert result['clips_without_allocation'] == 0

    def test_missing_allocation_fail(self):
        """Test that missing allocation is detected."""
        clips = [
            {'clip_id': 'clip_001', 'base_allocation': 3.0},
            {'clip_id': 'clip_002'}  # Missing allocation
        ]
        result = validate_base_allocation(clips)
        assert result['passed'] is False
        assert result['clips_without_allocation'] == 1


class TestCreativeAdjustments:
    """Test creative adjustments validation."""

    def test_creative_adjustments_optional(self):
        """Test that creative adjustments are optional."""
        clips = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002', 'creative_adjustments': {}}
        ]
        result = validate_creative_adjustments(clips)
        assert result['passed'] is True
        assert result['clips_with_adjustments'] == 1


class TestDurationSanity:
    """Test duration sanity validation."""

    def test_reasonable_durations_pass(self):
        """Test that reasonable durations pass."""
        clips = [
            {'clip_id': 'clip_001', 'duration': 2.5},
            {'clip_id': 'clip_002', 'duration': 3.0},
            {'clip_id': 'clip_003', 'duration': 4.5}
        ]
        result = validate_duration_sanity(clips)
        assert result['passed'] is True
        assert len(result['warnings']) == 0

    def test_too_short_warning(self):
        """Test that too-short clips generate warnings."""
        clips = [
            {'clip_id': 'clip_001', 'duration': 0.3}  # Too short
        ]
        result = validate_duration_sanity(clips, min_duration=0.5)
        assert result['passed'] is False
        assert len(result['warnings']) > 0
        assert 'too short' in result['warnings'][0]

    def test_too_long_warning(self):
        """Test that too-long clips generate warnings."""
        clips = [
            {'clip_id': 'clip_001', 'duration': 35.0}  # Too long
        ]
        result = validate_duration_sanity(clips, max_duration=30.0)
        assert result['passed'] is False
        assert len(result['warnings']) > 0
        assert 'too long' in result['warnings'][0]

    def test_statistics_calculation(self):
        """Test duration statistics."""
        clips = [
            {'clip_id': 'clip_001', 'duration': 2.0},
            {'clip_id': 'clip_002', 'duration': 3.0},
            {'clip_id': 'clip_003', 'duration': 4.0}
        ]
        result = validate_duration_sanity(clips)
        assert result['min_duration'] == 2.0
        assert result['max_duration'] == 4.0
        assert result['avg_duration'] == 3.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
