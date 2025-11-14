"""
Test suite for Phase 0: Overall Design
MV Orchestra v2.8

This module provides tests and examples for Phase 0 functionality.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SharedState, read_json, write_json
from phase0 import run_phase0, Phase0Runner


def create_sample_analysis() -> dict:
    """
    Create sample song analysis data for testing.

    Returns:
        Sample analysis dictionary
    """
    return {
        "title": "Summer Nights",
        "artist": "Test Artist",
        "genre": "Pop",
        "bpm": 128,
        "key": "C major",
        "duration": 180,
        "energy_profile": {
            "average": "high",
            "intro": "medium",
            "verse": "medium-high",
            "chorus": "high",
            "bridge": "medium",
            "outro": "medium"
        },
        "sections": [
            {"name": "intro", "start": 0, "end": 8, "mood": "anticipatory"},
            {"name": "verse1", "start": 8, "end": 24, "mood": "building"},
            {"name": "chorus1", "start": 24, "end": 40, "mood": "energetic"},
            {"name": "verse2", "start": 40, "end": 56, "mood": "reflective"},
            {"name": "chorus2", "start": 56, "end": 72, "mood": "energetic"},
            {"name": "bridge", "start": 72, "end": 88, "mood": "emotional"},
            {"name": "chorus3", "start": 88, "end": 104, "mood": "climactic"},
            {"name": "outro", "start": 104, "end": 120, "mood": "resolving"}
        ],
        "lyrics": {
            "verse1": "Walking down the street on a summer night...",
            "chorus": "Summer nights, dancing in the moonlight...",
            "verse2": "Remember when we used to dream...",
            "bridge": "And I know that time won't wait..."
        },
        "mood": "upbeat, nostalgic",
        "instruments": ["guitar", "drums", "synth", "bass"],
        "vocal_characteristics": "energetic, youthful",
        "target_demographic": "18-25, summer vibe enthusiasts"
    }


def test_phase0_basic():
    """
    Test basic Phase 0 functionality with mock mode.
    """
    print("=" * 60)
    print("TEST: Phase 0 Basic Functionality")
    print("=" * 60)

    # Create sample analysis
    analysis_data = create_sample_analysis()

    # Save to temp file
    analysis_path = "/tmp/test_analysis.json"
    write_json(analysis_path, analysis_data)
    print(f"\n✓ Created sample analysis: {analysis_path}")

    # Run Phase 0
    print("\n--- Running Phase 0 ---")
    results = run_phase0(
        session_id=None,  # Create new session
        analysis_path=analysis_path,
        mock_mode=True
    )

    # Check results
    print(f"\n✓ Phase 0 completed successfully")
    print(f"\n--- Results ---")
    print(f"Number of proposals: {len(results['proposals'])}")
    print(f"Number of evaluations: {len(results['evaluations'])}")
    print(f"Winner: {results['winner']['director']}")
    print(f"Winner Score: {results['winner']['total_score']:.2f}")

    print("\n--- All Proposal Scores ---")
    for director, score in results['winner']['all_scores'].items():
        print(f"  {director}: {score:.2f}")

    print("\n--- Winner's Proposal ---")
    winner_proposal = results['winner']['proposal']
    print(f"Concept: {winner_proposal['concept_theme']}")
    print(f"Visual Style: {winner_proposal['visual_style']}")
    print(f"Target Audience: {winner_proposal['target_audience']}")

    print("\n✓ Test passed!")
    return results


def test_phase0_with_session():
    """
    Test Phase 0 with explicit session management.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 0 with Session Management")
    print("=" * 60)

    # Create sample analysis
    analysis_data = create_sample_analysis()
    analysis_path = "/tmp/test_analysis_session.json"
    write_json(analysis_path, analysis_data)

    # Create session
    session = SharedState.create_session(
        input_files={"analysis": analysis_path}
    )
    print(f"\n✓ Created session: {session.session_id}")

    # Load config
    config = read_json("/home/user/test/config.json")
    print(f"✓ Loaded config")

    # Create runner
    runner = Phase0Runner(session, config, mock_mode=True)
    print(f"✓ Created Phase0Runner")

    # Run phase
    print("\n--- Running Phase 0 ---")
    results = runner.run(analysis_path)

    # Verify session state
    print(f"\n--- Session State ---")
    phase0_data = session.get_phase_data(0)
    print(f"Phase 0 Status: {phase0_data.status}")
    print(f"Started at: {phase0_data.started_at}")
    print(f"Completed at: {phase0_data.completed_at}")

    # Verify data saved to session
    assert phase0_data.status == "completed", "Phase should be completed"
    assert "winner" in phase0_data.data, "Winner should be in phase data"
    assert "proposals" in phase0_data.data, "Proposals should be in phase data"

    print("\n✓ Session state verified")
    print("✓ Test passed!")

    return session, results


def test_phase0_evaluation_details():
    """
    Test and display detailed evaluation information.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 0 Evaluation Details")
    print("=" * 60)

    # Create and run
    analysis_data = create_sample_analysis()
    analysis_path = "/tmp/test_analysis_eval.json"
    write_json(analysis_path, analysis_data)

    results = run_phase0(
        session_id=None,
        analysis_path=analysis_path,
        mock_mode=True
    )

    # Display detailed evaluations
    print("\n--- Detailed Evaluations ---")
    for evaluation in results['evaluations']:
        evaluator = evaluation['evaluator']
        print(f"\n{evaluator.upper()} Evaluations:")

        for director, score in evaluation['scores'].items():
            feedback = evaluation['feedback'].get(director, {})
            print(f"  → {director}: {score:.1f}/100")
            if isinstance(feedback, dict):
                print(f"    Feedback: {feedback.get('feedback', 'N/A')[:80]}...")
            else:
                print(f"    Feedback: {str(feedback)[:80]}...")

    print("\n✓ Test passed!")
    return results


def test_director_personalities():
    """
    Test that different directors produce different proposals.
    """
    print("\n" + "=" * 60)
    print("TEST: Director Personality Differences")
    print("=" * 60)

    # Create and run
    analysis_data = create_sample_analysis()
    analysis_path = "/tmp/test_analysis_personality.json"
    write_json(analysis_path, analysis_data)

    results = run_phase0(
        session_id=None,
        analysis_path=analysis_path,
        mock_mode=True
    )

    # Compare proposals
    print("\n--- Proposal Comparison ---")
    for proposal in results['proposals']:
        director = proposal['director']
        concept = proposal['concept_theme']
        style = proposal['visual_style']

        print(f"\n{director.upper()}:")
        print(f"  Concept: {concept[:60]}...")
        print(f"  Style: {style[:60]}...")

    # Verify uniqueness
    concepts = [p['concept_theme'] for p in results['proposals']]
    assert len(set(concepts)) == len(concepts), "Each director should have unique concept"

    print("\n✓ All directors have unique proposals")
    print("✓ Test passed!")
    return results


def run_all_tests():
    """
    Run all Phase 0 tests.
    """
    print("\n" + "=" * 70)
    print(" " * 20 + "PHASE 0 TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: Basic functionality
        test_phase0_basic()

        # Test 2: Session management
        session, results = test_phase0_with_session()

        # Test 3: Evaluation details
        test_phase0_evaluation_details()

        # Test 4: Director personalities
        test_director_personalities()

        print("\n" + "=" * 70)
        print(" " * 20 + "ALL TESTS PASSED ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
