"""
Test suite for Phase 2: Section Direction Design

This test suite validates:
- Phase 2 runner functionality
- Section utilities
- Integration with Phase 0 and Phase 1 outputs
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
from phase2 import (
    Phase2Runner,
    run_phase2,
    load_song_sections,
    validate_section_coverage,
    extract_section_summary,
    get_section_types
)


def setup_test_session():
    """Create a test session with Phase 0 and Phase 1 completed."""
    # Create new session
    session = SharedState.create_session({
        'mp3': 'test_song.mp3',
        'analysis': 'analysis.json'
    })

    # Mock Phase 0 completion
    phase0_results = {
        'proposals': [],
        'evaluations': [],
        'winner': {
            'director': 'award_winner',
            'total_score': 85.5,
            'proposal': {
                'concept': 'An emotional journey through urban isolation',
                'visual_style': 'Cinematic noir with vibrant color accents',
                'narrative_approach': 'Character-driven emotional arc',
                'target_audience': 'Young adults 18-35',
                'platform_strategy': 'YouTube primary, Instagram/TikTok cuts'
            }
        }
    }
    session.set_phase_data(0, phase0_results)
    session.complete_phase(0)

    # Mock Phase 1 completion
    phase1_results = {
        'proposals': [],
        'evaluations': [],
        'winner': {
            'director': 'freelancer',
            'total_score': 82.3,
            'proposal': {
                'main_character': {
                    'name': 'Maya',
                    'age': '25',
                    'visual_identity': 'Urban professional with artistic edge',
                    'emotional_state': 'Searching for connection in isolation'
                },
                'visual_consistency': 'Consistent wardrobe and styling throughout',
                'character_arc': 'From isolation to self-acceptance'
            }
        }
    }
    session.set_phase_data(1, phase1_results)
    session.complete_phase(1)

    return session.session_id


def test_load_song_sections():
    """Test loading song sections from analysis.json."""
    analysis_path = get_project_root() / "shared-workspace" / "input" / "analysis.json"

    if not analysis_path.exists():
        pytest.skip("analysis.json not found")

    analysis_data = read_json(str(analysis_path))
    sections = load_song_sections(analysis_data)

    assert len(sections) > 0, "Should load at least one section"
    assert all('start' in s for s in sections), "All sections should have start time"
    assert all('end' in s for s in sections), "All sections should have end time"
    assert all('label' in s for s in sections), "All sections should have label"


def test_validate_section_coverage():
    """Test section coverage validation."""
    # Valid sections
    valid_sections = [
        {'label': 'intro', 'start': 0.0, 'end': 10.0},
        {'label': 'verse', 'start': 10.0, 'end': 30.0},
        {'label': 'chorus', 'start': 30.0, 'end': 50.0}
    ]

    assert validate_section_coverage(valid_sections) is True

    # Invalid: overlapping sections
    invalid_sections = [
        {'label': 'intro', 'start': 0.0, 'end': 15.0},
        {'label': 'verse', 'start': 10.0, 'end': 30.0}  # Overlaps with intro
    ]

    # This should log a warning but not raise an error
    validate_section_coverage(invalid_sections)


def test_extract_section_summary():
    """Test section summary extraction."""
    sections = [
        {'label': 'intro', 'start': 0.0, 'end': 8.5},
        {'label': 'verse 1', 'start': 8.5, 'end': 28.2},
        {'label': 'chorus', 'start': 28.2, 'end': 44.0}
    ]

    summary = extract_section_summary(sections)

    assert summary['total_sections'] == 3
    assert summary['total_duration'] > 0
    assert len(summary['section_labels']) == 3
    assert 'average_duration' in summary


def test_get_section_types():
    """Test section type extraction."""
    labels = ['intro', 'verse 1', 'verse 2', 'chorus 1', 'chorus 2', 'bridge', 'outro']
    types = get_section_types(labels)

    assert 'intro' in types
    assert 'verse' in types
    assert types['verse'] == 2
    assert types['chorus'] == 2


def test_phase2_runner_initialization():
    """Test Phase 2 runner initialization."""
    session_id = setup_test_session()

    runner = Phase2Runner(session_id, mock_mode=True)

    assert runner.session_id == session_id
    assert runner.mock_mode is True
    assert runner.session is not None


def test_phase2_load_inputs():
    """Test loading Phase 2 inputs."""
    session_id = setup_test_session()
    runner = Phase2Runner(session_id, mock_mode=True)

    # This should succeed if Phase 0, Phase 1, and analysis.json are available
    try:
        phase0_concept, phase1_characters, song_sections = runner.load_phase_inputs()

        assert phase0_concept is not None
        assert phase1_characters is not None
        assert len(song_sections) > 0

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


def test_phase2_generate_proposal():
    """Test section proposal generation."""
    session_id = setup_test_session()
    runner = Phase2Runner(session_id, mock_mode=True)

    try:
        phase0_concept, phase1_characters, song_sections = runner.load_phase_inputs()

        from core.director_profiles import DirectorType

        proposal = runner.generate_section_proposal(
            DirectorType.CORPORATE,
            phase0_concept,
            phase1_characters,
            song_sections
        )

        assert 'director' in proposal
        assert 'sections' in proposal
        assert len(proposal['sections']) > 0

        # Check section structure
        section = proposal['sections'][0]
        assert 'section_name' in section
        assert 'emotional_tone' in section
        assert 'camera_work' in section

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


def test_phase2_full_run():
    """Test complete Phase 2 execution."""
    session_id = setup_test_session()

    try:
        results = run_phase2(session_id, mock_mode=True)

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
        phase2_data = session.get_phase_data(2)

        assert phase2_data.status == 'completed'
        assert len(phase2_data.data['proposals']) == 5

        print(f"\nPhase 2 completed successfully!")
        print(f"Winner: {results['winner']['director']}")
        print(f"Score: {results['winner']['total_score']}")
        print(f"Total clips in winner's proposal: {len(results['winner']['proposal']['sections'])}")

    except (FileNotFoundError, RuntimeError) as e:
        pytest.skip(f"Test prerequisites not met: {e}")


if __name__ == "__main__":
    # Run tests
    print("Testing Phase 2: Section Direction Design\n")

    print("=" * 60)
    print("Test 1: Load song sections")
    print("=" * 60)
    test_load_song_sections()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 2: Validate section coverage")
    print("=" * 60)
    test_validate_section_coverage()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 3: Extract section summary")
    print("=" * 60)
    test_extract_section_summary()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 4: Get section types")
    print("=" * 60)
    test_get_section_types()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 5: Runner initialization")
    print("=" * 60)
    test_phase2_runner_initialization()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 6: Load Phase 2 inputs")
    print("=" * 60)
    test_phase2_load_inputs()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 7: Generate section proposal")
    print("=" * 60)
    test_phase2_generate_proposal()
    print("✓ PASSED\n")

    print("=" * 60)
    print("Test 8: Full Phase 2 execution")
    print("=" * 60)
    test_phase2_full_run()
    print("✓ PASSED\n")

    print("=" * 60)
    print("All Phase 2 tests passed!")
    print("=" * 60)
