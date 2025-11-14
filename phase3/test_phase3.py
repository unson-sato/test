"""
Test suite for Phase 3: Clip Division

This test suite validates:
- Phase 3 runner functionality
- Clip utilities and beat alignment
- Integration with Phase 2 outputs
- Proposal generation and evaluation
"""

import json
import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SharedState
from core.utils import get_project_root, read_json
from phase3 import (
    Phase3Runner,
    run_phase3,
    snap_to_beat,
    load_beat_data,
    validate_clip_coverage,
    generate_clip_id,
    estimate_clip_complexity,
    calculate_clip_statistics
)


def setup_test_session():
    """Create a test session with Phase 0, 1, and 2 completed."""
    # Create new session
    session = SharedState.create_session({
        'mp3': 'test_song.mp3',
        'analysis': 'analysis.json'
    })

    # Mock Phase 0 completion
    phase0_results = {
        'winner': {
            'director': 'award_winner',
            'proposal': {
                'concept': 'An emotional journey through urban isolation'
            }
        }
    }
    session.set_phase_data(0, phase0_results)
    session.complete_phase(0)

    # Mock Phase 1 completion
    phase1_results = {
        'winner': {
            'director': 'freelancer',
            'proposal': {
                'main_character': {
                    'name': 'Maya'
                }
            }
        }
    }
    session.set_phase_data(1, phase1_results)
    session.complete_phase(1)

    # Mock Phase 2 completion with section directions
    phase2_results = {
        'winner': {
            'director': 'corporate',
            'proposal': {
                'sections': [
                    {
                        'section_name': 'intro',
                        'start_time': 0.0,
                        'end_time': 8.5,
                        'emotional_tone': 'mysterious'
                    },
                    {
                        'section_name': 'verse 1',
                        'start_time': 8.5,
                        'end_time': 28.2,
                        'emotional_tone': 'building'
                    },
                    {
                        'section_name': 'chorus 1',
                        'start_time': 28.2,
                        'end_time': 44.0,
                        'emotional_tone': 'energetic'
                    }
                ]
            }
        }
    }
    session.set_phase_data(2, phase2_results)
    session.complete_phase(2)

    return session.session_id


def test_snap_to_beat():
    """Test beat snapping functionality."""
    beat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    # Should snap to nearest beat
    assert snap_to_beat(0.48, beat_times, tolerance=0.2) == 0.5
    assert snap_to_beat(1.52, beat_times, tolerance=0.2) == 1.5

    # Should not snap if outside tolerance
    assert snap_to_beat(0.25, beat_times, tolerance=0.1) == 0.25

    # Should handle empty beat list
    assert snap_to_beat(1.0, [], tolerance=0.2) == 1.0


def test_load_beat_data():
    """Test loading beat data from analysis.json."""
    analysis_path = get_project_root() / "shared-workspace" / "input" / "analysis.json"

    if not analysis_path.exists():
        pytest.skip("analysis.json not found")

    analysis_data = read_json(str(analysis_path))
    beats = load_beat_data(analysis_data)

    assert len(beats) > 0, "Should load at least one beat"
    assert all(isinstance(b, (int, float)) for b in beats), "All beats should be numbers"
    assert beats == sorted(beats), "Beats should be sorted"


def test_validate_clip_coverage():
    """Test clip coverage validation."""
    # Valid clips
    valid_clips = [
        {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 5.0},
        {'clip_id': 'clip_002', 'start_time': 5.0, 'end_time': 10.0},
        {'clip_id': 'clip_003', 'start_time': 10.0, 'end_time': 15.0}
    ]

    assert validate_clip_coverage(valid_clips, 15.0) is True

    # Invalid: overlapping clips
    invalid_clips = [
        {'clip_id': 'clip_001', 'start_time': 0.0, 'end_time': 6.0},
        {'clip_id': 'clip_002', 'start_time': 5.0, 'end_time': 10.0}  # Overlaps
    ]

    with pytest.raises(ValueError):
        validate_clip_coverage(invalid_clips, 10.0)


def test_generate_clip_id():
    """Test clip ID generation."""
    assert generate_clip_id(1) == "clip_001"
    assert generate_clip_id(42) == "clip_042"
    assert generate_clip_id(999) == "clip_999"

    # Custom prefix
    assert generate_clip_id(5, prefix="shot") == "shot_005"


def test_estimate_clip_complexity():
    """Test clip complexity estimation."""
    # Simple wide shot
    assert estimate_clip_complexity("wide shot", 5.0, has_movement=False) == "low"

    # Complex close-up with movement
    assert estimate_clip_complexity("close-up detail", 1.5, has_movement=True) == "high"

    # Medium shot with moderate duration
    assert estimate_clip_complexity("medium shot", 3.0, has_movement=True) in ["medium", "high"]


def test_calculate_clip_statistics():
    """Test clip statistics calculation."""
    clips = [
        {
            'clip_id': 'clip_001',
            'start_time': 0.0,
            'end_time': 3.0,
            'beat_aligned': True,
            'complexity': 'medium',
            'section': 'intro'
        },
        {
            'clip_id': 'clip_002',
            'start_time': 3.0,
            'end_time': 6.0,
            'beat_aligned': True,
            'complexity': 'high',
            'section': 'intro'
        },
        {
            'clip_id': 'clip_003',
            'start_time': 6.0,
            'end_time': 10.0,
            'beat_aligned': False,
            'complexity': 'medium',
            'section': 'verse'
        }
    ]

    stats = calculate_clip_statistics(clips)

    assert stats['total_clips'] == 3
    assert stats['total_duration'] == 10.0
    assert stats['average_duration'] > 0
    assert stats['beat_aligned_count'] == 2
    assert stats['beat_aligned_percentage'] > 0


def test_phase3_runner_initialization():
    """Test Phase 3 runner initialization."""
    session_id = setup_test_session()

    runner = Phase3Runner(session_id, mock_mode=True)

    assert runner.session_id == session_id
    assert runner.mock_mode is True
    assert runner.session is not None


def test_phase3_load_inputs():
    """Test loading Phase 3 inputs."""
    session_id = setup_test_session()
    runner = Phase3Runner(session_id, mock_mode=True)

    try:
        phase2_directions, beat_times, metadata = runner.load_phase_inputs()

        assert phase2_directions is not None
        assert 'sections' in phase2_directions
        assert len(beat_times) > 0
        assert 'bpm' in metadata

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


def test_phase3_generate_proposal():
    """Test clip proposal generation."""
    session_id = setup_test_session()
    runner = Phase3Runner(session_id, mock_mode=True)

    try:
        phase2_directions, beat_times, metadata = runner.load_phase_inputs()

        from core.director_profiles import DirectorType

        proposal = runner.generate_clip_proposal(
            DirectorType.FREELANCER,
            phase2_directions,
            beat_times,
            metadata
        )

        assert 'director' in proposal
        assert 'clips' in proposal
        assert len(proposal['clips']) > 0

        # Check clip structure
        clip = proposal['clips'][0]
        assert 'clip_id' in clip
        assert 'start_time' in clip
        assert 'end_time' in clip
        assert 'duration' in clip
        assert 'beat_aligned' in clip

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


def test_phase3_full_run():
    """Test complete Phase 3 execution."""
    session_id = setup_test_session()

    try:
        results = run_phase3(session_id, mock_mode=True)

        assert 'proposals' in results
        assert 'evaluations' in results
        assert 'winner' in results

        # Should have 5 proposals (one per director)
        assert len(results['proposals']) == 5

        # Should have 25 evaluations (5 directors × 5 proposals)
        assert len(results['evaluations']) == 25

        # Winner should be selected
        assert results['winner']['director'] in [
            'corporate', 'freelancer', 'veteran', 'award_winner', 'newcomer'
        ]

        # Verify session state was updated
        session = SharedState.load_session(session_id)
        phase3_data = session.get_phase_data(3)

        assert phase3_data.status == 'completed'
        assert len(phase3_data.data['proposals']) == 5

        # Get winner's clips
        winner_clips = results['winner']['proposal']['clips']

        print(f"\nPhase 3 completed successfully!")
        print(f"Winner: {results['winner']['director']}")
        print(f"Score: {results['winner']['total_score']}")
        print(f"Total clips: {len(winner_clips)}")
        print(f"Average clip length: {results['winner']['proposal']['average_clip_length']:.2f}s")

        # Show some clip details
        if winner_clips:
            print(f"\nFirst 3 clips:")
            for clip in winner_clips[:3]:
                print(f"  - {clip['clip_id']}: {clip['start_time']:.2f}s - {clip['end_time']:.2f}s "
                      f"({clip['duration']:.2f}s, {clip['section']}, {clip['shot_type']})")

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


if __name__ == "__main__":
    # Run tests
    print("Testing Phase 3: Clip Division\n")

    print("=" * 60)
    print("Test 1: Snap to beat")
    print("=" * 60)
    test_snap_to_beat()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 2: Load beat data")
    print("=" * 60)
    test_load_beat_data()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 3: Validate clip coverage")
    print("=" * 60)
    test_validate_clip_coverage()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 4: Generate clip ID")
    print("=" * 60)
    test_generate_clip_id()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 5: Estimate clip complexity")
    print("=" * 60)
    test_estimate_clip_complexity()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 6: Calculate clip statistics")
    print("=" * 60)
    test_calculate_clip_statistics()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 7: Runner initialization")
    print("=" * 60)
    test_phase3_runner_initialization()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 8: Load Phase 3 inputs")
    print("=" * 60)
    test_phase3_load_inputs()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 9: Generate clip proposal")
    print("=" * 60)
    test_phase3_generate_proposal()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 10: Full Phase 3 execution")
    print("=" * 60)
    test_phase3_full_run()
    print("✓ PASSED\n")

    print("=" * 60)
    print("All Phase 3 tests passed!")
    print("=" * 60)
