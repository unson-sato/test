#!/usr/bin/env python3
"""
Test real AI integration with Claude API.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 test_real_ai.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import SharedState, DirectorType
from core.codex_runner import CodexRunner, EvaluationRequest


def test_real_evaluation():
    """Test a single real evaluation."""

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("=" * 70)
        print("ERROR: ANTHROPIC_API_KEY not set")
        print("=" * 70)
        print("\nTo use real AI evaluations, you need an Anthropic API key.")
        print("\nSteps:")
        print("1. Get your API key from: https://console.anthropic.com/")
        print("2. Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("3. Run this script again")
        print("\n" + "=" * 70)
        return False

    print("=" * 70)
    print("Testing Real AI Evaluation")
    print("=" * 70)
    print("\nThis will make a real API call to Claude and incur costs.")
    print("Estimated cost: ~$0.01-0.05 per evaluation")

    # Create test session
    session = SharedState.create_session("test_real_ai")

    # Create evaluation request
    request = EvaluationRequest(
        session_id=session.session_id,
        phase_number=0,
        director_type=DirectorType.FREELANCER,
        evaluation_type="overall_design",
        context={
            'proposals': [
                {
                    'director': 'corporate',
                    'concept_theme': 'Modern urban romance',
                    'visual_style': 'Clean, cinematic, commercial aesthetic',
                    'narrative_structure': 'Linear story progression with clear beginning, middle, end',
                    'target_audience': 'Young adults 18-35, mainstream appeal',
                    'key_selling_points': [
                        'High production value',
                        'Relatable storyline',
                        'Instagram-worthy visuals',
                        'Radio-friendly approach'
                    ],
                    'commercial_viability': 'Very high - designed for mass appeal and streaming success'
                }
            ],
            'previous_phases': {}
        }
    )

    # Run real evaluation
    print("\n" + "=" * 70)
    print("Calling Claude API...")
    print("=" * 70)
    print(f"\nDirector: {request.director_type.value}")
    print(f"Phase: {request.phase_number}")
    print(f"Evaluation Type: {request.evaluation_type}")
    print("\nPlease wait...")

    try:
        runner = CodexRunner(mock_mode=False)
        result = runner.execute_evaluation(request)

        # Display results
        print("\n" + "=" * 70)
        print("EVALUATION RESULTS")
        print("=" * 70)
        print(f"\nDirector: {result.director_type.value}")
        print(f"Score: {result.score:.1f}/100")
        print(f"\nFeedback:")
        print("-" * 70)
        print(result.feedback)

        if result.suggestions:
            print(f"\n{'Suggestions:'}")
            print("-" * 70)
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"{i}. {suggestion}")

        if result.highlights:
            print(f"\n{'Highlights:'}")
            print("-" * 70)
            for i, highlight in enumerate(result.highlights, 1):
                print(f"{i}. {highlight}")

        if result.concerns:
            print(f"\n{'Concerns:'}")
            print("-" * 70)
            for i, concern in enumerate(result.concerns, 1):
                print(f"{i}. {concern}")

        print("\n" + "=" * 70)
        print("✓ Real AI evaluation successful!")
        print("=" * 70)

        # Show where results were saved
        print(f"\nResults saved to:")
        print(f"  shared-workspace/sessions/{session.session_id}/evaluations/")

        return True

    except ImportError as e:
        print("\n" + "=" * 70)
        print("ERROR: Missing dependency")
        print("=" * 70)
        print(f"\n{e}")
        print("\nTo fix this, run:")
        print("  pip install anthropic")
        print("\n" + "=" * 70)
        return False

    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR: Evaluation failed")
        print("=" * 70)
        print(f"\n{e}")
        print("\n" + "=" * 70)
        return False


def test_all_directors():
    """Test evaluation with all 5 directors."""

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return False

    print("=" * 70)
    print("Testing All 5 Directors")
    print("=" * 70)
    print("\nThis will make 5 API calls (one per director).")
    print("Estimated cost: ~$0.05-0.25 total")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")

    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return False

    # Create test session
    session = SharedState.create_session("test_all_directors")

    # Test proposal
    proposal = {
        'concept_theme': 'Urban nightlife and self-discovery',
        'visual_style': 'Neon-lit, energetic, contemporary',
        'narrative_structure': 'Non-linear, dream-like progression',
        'target_audience': 'Young adults 20-30, club culture',
        'key_elements': [
            'Dynamic camera work',
            'Color symbolism',
            'Character transformation',
            'Urban exploration'
        ]
    }

    directors = [
        DirectorType.CORPORATE,
        DirectorType.FREELANCER,
        DirectorType.VETERAN,
        DirectorType.AWARD_WINNER,
        DirectorType.NEWCOMER
    ]

    results = {}

    for director in directors:
        print(f"\n{'='*70}")
        print(f"Evaluating with: {director.value}")
        print(f"{'='*70}")

        request = EvaluationRequest(
            session_id=session.session_id,
            phase_number=0,
            director_type=director,
            evaluation_type="overall_design",
            context={'proposals': [proposal]}
        )

        try:
            runner = CodexRunner(mock_mode=False)
            result = runner.execute_evaluation(request)
            results[director.value] = result.score

            print(f"Score: {result.score:.1f}/100")
            print(f"Feedback: {result.feedback[:200]}...")

        except Exception as e:
            print(f"ERROR: {e}")
            results[director.value] = None

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for director, score in results.items():
        if score is not None:
            print(f"{director:15s}: {score:5.1f}/100")
        else:
            print(f"{director:15s}: FAILED")

    avg_score = sum(s for s in results.values() if s is not None) / len([s for s in results.values() if s is not None])
    print(f"\nAverage Score: {avg_score:.1f}/100")

    print("\n" + "=" * 70)
    print("✓ All evaluations complete!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        success = test_all_directors()
    else:
        success = test_real_evaluation()

    sys.exit(0 if success else 1)
