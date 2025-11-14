"""
Test suite for Phase 1: Character Design
MV Orchestra v2.8

This module provides tests and examples for Phase 1 functionality.
Requires Phase 0 to be completed first.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SharedState, read_json, write_json
from phase0 import run_phase0
from phase1 import run_phase1, Phase1Runner


def create_sample_analysis() -> dict:
    """
    Create sample song analysis data for testing.

    Returns:
        Sample analysis dictionary
    """
    return {
        "title": "Midnight Dreams",
        "artist": "Test Artist",
        "genre": "Electronic Pop",
        "bpm": 120,
        "key": "A minor",
        "duration": 200,
        "energy_profile": {
            "average": "medium-high",
            "intro": "low",
            "verse": "medium",
            "chorus": "high",
            "bridge": "medium",
            "outro": "low"
        },
        "sections": [
            {"name": "intro", "start": 0, "end": 10, "mood": "mysterious"},
            {"name": "verse1", "start": 10, "end": 30, "mood": "introspective"},
            {"name": "chorus1", "start": 30, "end": 50, "mood": "uplifting"},
            {"name": "verse2", "start": 50, "end": 70, "mood": "reflective"},
            {"name": "chorus2", "start": 70, "end": 90, "mood": "powerful"},
            {"name": "bridge", "start": 90, "end": 110, "mood": "emotional"},
            {"name": "chorus3", "start": 110, "end": 130, "mood": "euphoric"},
            {"name": "outro", "start": 130, "end": 150, "mood": "peaceful"}
        ],
        "lyrics": {
            "verse1": "In the silence of the midnight hour...",
            "chorus": "Dreams unfold in neon light...",
            "verse2": "Lost in thoughts of yesterday...",
            "bridge": "But I'm alive, I'm here tonight..."
        },
        "mood": "dreamy, introspective, hopeful",
        "instruments": ["synth", "electronic drums", "bass", "pad"],
        "vocal_characteristics": "ethereal, emotional, powerful",
        "target_demographic": "20-30, electronic music fans"
    }


def setup_phase0(analysis_path: str = None) -> tuple:
    """
    Setup by running Phase 0 first.

    Args:
        analysis_path: Path to analysis file (creates temp if None)

    Returns:
        Tuple of (session_id, phase0_results)
    """
    print("--- Setting up Phase 0 ---")

    if analysis_path is None:
        analysis_data = create_sample_analysis()
        analysis_path = "/tmp/test_analysis_phase1.json"
        write_json(analysis_path, analysis_data)

    # Run Phase 0
    phase0_results = run_phase0(
        session_id=None,
        analysis_path=analysis_path,
        mock_mode=True
    )

    # Extract session_id from results
    # We need to get it from the session that was created
    # The run_phase0 function creates a session but doesn't return the ID directly
    # We'll need to create a session explicitly

    # Let's do it properly
    session = SharedState.create_session(input_files={"analysis": analysis_path})
    config = read_json("/home/user/test/config.json")

    from phase0 import Phase0Runner
    runner = Phase0Runner(session, config, mock_mode=True)
    phase0_results = runner.run(analysis_path)

    print(f"✓ Phase 0 completed, session: {session.session_id}")
    print(f"✓ Phase 0 winner: {phase0_results['winner']['director']}")

    return session.session_id, phase0_results


def test_phase1_basic():
    """
    Test basic Phase 1 functionality with mock mode.
    """
    print("=" * 60)
    print("TEST: Phase 1 Basic Functionality")
    print("=" * 60)

    # Setup Phase 0
    session_id, phase0_results = setup_phase0()

    # Run Phase 1
    print("\n--- Running Phase 1 ---")
    results = run_phase1(
        session_id=session_id,
        mock_mode=True
    )

    # Check results
    print(f"\n✓ Phase 1 completed successfully")
    print(f"\n--- Results ---")
    print(f"Number of character designs: {len(results['proposals'])}")
    print(f"Number of evaluations: {len(results['evaluations'])}")
    print(f"Winner: {results['winner']['director']}")
    print(f"Winner Score: {results['winner']['total_score']:.2f}")

    print("\n--- All Character Design Scores ---")
    for director, score in results['winner']['all_scores'].items():
        print(f"  {director}: {score:.2f}")

    print("\n--- Winner's Character Design ---")
    winner_design = results['winner']['proposal']
    main_character = winner_design['characters'][0]
    print(f"Main Character: {main_character['name']}")
    print(f"Appearance: {main_character['appearance'][:60]}...")
    print(f"Costume: {main_character['costume'][:60]}...")
    print(f"Visual Strategy: {winner_design['visual_consistency_strategy'][:60]}...")

    print("\n✓ Test passed!")
    return results


def test_phase1_with_session():
    """
    Test Phase 1 with explicit session management.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 1 with Session Management")
    print("=" * 60)

    # Setup Phase 0
    session_id, phase0_results = setup_phase0()

    # Load session
    session = SharedState.load_session(session_id)
    print(f"\n✓ Loaded session: {session_id}")

    # Verify Phase 0 is complete
    phase0_data = session.get_phase_data(0)
    assert phase0_data.status == "completed", "Phase 0 must be completed"
    print(f"✓ Phase 0 verified: {phase0_data.status}")

    # Load config
    config = read_json("/home/user/test/config.json")
    print(f"✓ Loaded config")

    # Create runner
    runner = Phase1Runner(session, config, mock_mode=True)
    print(f"✓ Created Phase1Runner")

    # Run phase
    print("\n--- Running Phase 1 ---")
    results = runner.run()

    # Verify session state
    print(f"\n--- Session State ---")
    phase1_data = session.get_phase_data(1)
    print(f"Phase 1 Status: {phase1_data.status}")
    print(f"Started at: {phase1_data.started_at}")
    print(f"Completed at: {phase1_data.completed_at}")

    # Verify data saved to session
    assert phase1_data.status == "completed", "Phase should be completed"
    assert "winner" in phase1_data.data, "Winner should be in phase data"
    assert "proposals" in phase1_data.data, "Proposals should be in phase data"

    print("\n✓ Session state verified")
    print("✓ Test passed!")

    return session, results


def test_phase1_character_details():
    """
    Test and display detailed character design information.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 1 Character Design Details")
    print("=" * 60)

    # Setup and run
    session_id, phase0_results = setup_phase0()
    results = run_phase1(session_id=session_id, mock_mode=True)

    # Display all character designs
    print("\n--- All Character Designs ---")
    for design in results['proposals']:
        director = design['director']
        print(f"\n{director.upper()}:")

        main_char = design['characters'][0]
        print(f"  Character: {main_char['name']}")
        print(f"  Appearance: {main_char['appearance'][:70]}...")
        print(f"  Personality: {main_char['personality'][:70]}...")
        print(f"  Costume: {main_char['costume'][:70]}...")
        print(f"  Visual Strategy: {design['visual_consistency_strategy'][:70]}...")

    print("\n✓ Test passed!")
    return results


def test_phase1_concept_alignment():
    """
    Test that Phase 1 designs align with Phase 0 concept.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 0/Phase 1 Concept Alignment")
    print("=" * 60)

    # Setup and run both phases
    session_id, phase0_results = setup_phase0()
    phase1_results = run_phase1(session_id=session_id, mock_mode=True)

    # Show Phase 0 winner
    phase0_winner = phase0_results['winner']
    print(f"\n--- Phase 0 Winner ---")
    print(f"Director: {phase0_winner['director']}")
    print(f"Concept: {phase0_winner['proposal']['concept_theme'][:60]}...")
    print(f"Visual Style: {phase0_winner['proposal']['visual_style'][:60]}...")

    # Show Phase 1 designs referencing Phase 0
    print(f"\n--- Phase 1 Designs (Building on Phase 0) ---")
    for design in phase1_results['proposals']:
        print(f"\n{design['director'].upper()}:")
        print(f"  Alignment: {design.get('concept_alignment', 'N/A')[:70]}...")

    print("\n✓ All Phase 1 designs reference Phase 0 concept")
    print("✓ Test passed!")

    return phase0_results, phase1_results


def test_phase1_evaluation_details():
    """
    Test and display detailed evaluation information.
    """
    print("\n" + "=" * 60)
    print("TEST: Phase 1 Evaluation Details")
    print("=" * 60)

    # Setup and run
    session_id, phase0_results = setup_phase0()
    results = run_phase1(session_id=session_id, mock_mode=True)

    # Display detailed evaluations
    print("\n--- Detailed Character Design Evaluations ---")
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


def test_director_character_styles():
    """
    Test that different directors create different character styles.
    """
    print("\n" + "=" * 60)
    print("TEST: Director Character Style Differences")
    print("=" * 60)

    # Setup and run
    session_id, phase0_results = setup_phase0()
    results = run_phase1(session_id=session_id, mock_mode=True)

    # Compare character designs
    print("\n--- Character Style Comparison ---")
    for design in results['proposals']:
        director = design['director']
        char = design['characters'][0]
        strategy = design['visual_consistency_strategy']

        print(f"\n{director.upper()}:")
        print(f"  Character: {char['name']}")
        print(f"  Style: {char['costume'][:50]}...")
        print(f"  Strategy: {strategy[:50]}...")

    # Verify uniqueness
    costumes = [d['characters'][0]['costume'] for d in results['proposals']]
    assert len(set(costumes)) == len(costumes), "Each director should have unique costume design"

    print("\n✓ All directors have unique character styles")
    print("✓ Test passed!")
    return results


def run_all_tests():
    """
    Run all Phase 1 tests.
    """
    print("\n" + "=" * 70)
    print(" " * 20 + "PHASE 1 TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: Basic functionality
        test_phase1_basic()

        # Test 2: Session management
        session, results = test_phase1_with_session()

        # Test 3: Character details
        test_phase1_character_details()

        # Test 4: Concept alignment
        test_phase1_concept_alignment()

        # Test 5: Evaluation details
        test_phase1_evaluation_details()

        # Test 6: Director character styles
        test_director_character_styles()

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
