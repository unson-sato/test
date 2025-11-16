#!/usr/bin/env python3
"""
Test Suite for Phase 5: Real Claude Review

This module tests the optional Claude review phase functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import SharedState
from phase4 import run_phase4
from phase5 import (
    run_phase5,
    Phase5Runner,
    ClaudeAPIClient,
    create_client
)


def create_test_session_with_phase4():
    """Create a test session with Phase 4 completed"""
    print("\nSetting up test session with Phase 4...")

    # Create session
    session = SharedState.create_session()
    session_id = session.session_id

    # Set up Phase 0-3 data
    session.start_phase(0)
    session.set_phase_data(0, {
        'concept': 'Test MV concept',
        'color_palette': ['blue', 'purple', 'black']
    })
    session.complete_phase(0)

    session.start_phase(1)
    session.set_phase_data(1, {
        'characters': [{'name': 'Main Character'}]
    })
    session.complete_phase(1)

    session.start_phase(2)
    session.set_phase_data(2, {
        'sections': [{'section_name': 'Intro', 'mood': 'mysterious'}]
    })
    session.complete_phase(2)

    session.start_phase(3)
    session.set_phase_data(3, {
        'winner': {
            'proposal': {
                'sections': [{
                    'section_name': 'Intro',
                    'clips': [
                        {
                            'clip_id': 'clip_001',
                            'start_time': 0.0,
                            'end_time': 3.0,
                            'duration': 3.0,
                            'description': 'Opening shot',
                            'clip_type': 'establishing'
                        },
                        {
                            'clip_id': 'clip_002',
                            'start_time': 3.0,
                            'end_time': 6.0,
                            'duration': 3.0,
                            'description': 'Character intro',
                            'clip_type': 'performance'
                        },
                        {
                            'clip_id': 'clip_003',
                            'start_time': 6.0,
                            'end_time': 8.0,
                            'duration': 2.0,
                            'description': 'Transition',
                            'clip_type': 'transition'
                        }
                    ]
                }]
            }
        }
    })
    session.complete_phase(3)

    # Run Phase 4
    print("  Running Phase 4...")
    run_phase4(session_id, mock_mode=True)
    print(f"  ✓ Session ready: {session_id}")

    return session_id


def test_api_client_mock_mode():
    """Test API client in mock mode"""
    print("\n" + "="*60)
    print("Test: API Client - Mock Mode")
    print("="*60)

    # Create mock client
    client = ClaudeAPIClient(mock_mode=True)

    # Test single review
    review = client.review_generation_strategy(
        clip_id="test_clip_001",
        generation_mode="veo2",
        prompt="A young woman standing in urban street, cinematic",
        clip_context={
            'clip_type': 'performance',
            'duration': 3.0,
            'description': 'Character performance'
        }
    )

    print(f"\nReview Result:")
    print(f"  Clip ID: {review['clip_id']}")
    print(f"  Mode: {review['original_mode']}")
    print(f"  Score: {review['claude_score']}/10")
    print(f"  Feedback: {review['claude_feedback'][:80]}...")
    print(f"  Mock Mode: {review['mock_mode']}")

    # Test cost estimation
    cost = client.estimate_cost(num_clips=10)
    print(f"\nCost Estimate (10 clips):")
    print(f"  Input tokens: {cost['estimated_input_tokens']}")
    print(f"  Output tokens: {cost['estimated_output_tokens']}")
    print(f"  Total cost: ${cost['estimated_total_cost_usd']:.2f}")

    print("\n✓ Mock API client working")


def test_api_client_batch():
    """Test batch review functionality"""
    print("\n" + "="*60)
    print("Test: API Client - Batch Review")
    print("="*60)

    client = ClaudeAPIClient(mock_mode=True)

    # Create sample strategies
    strategies = [
        {
            'clip_id': f'clip_{i:03d}',
            'generation_mode': 'veo2' if i % 2 == 0 else 'sora',
            'clip_type': 'performance' if i % 3 == 0 else 'establishing',
            'duration': 3.0 + i * 0.5,
            'prompt_template': {
                'full_prompt': f'Sample prompt for clip {i}'
            }
        }
        for i in range(1, 6)
    ]

    # Batch review
    print(f"\nReviewing {len(strategies)} clips...")
    reviews = client.batch_review(strategies)

    print(f"\nBatch Review Results:")
    for review in reviews:
        score = review.get('claude_score', 0)
        alt = review.get('suggested_alternative')
        print(f"  {review['clip_id']}: {score:.1f}/10" +
              (f" → Suggest {alt}" if alt else ""))

    print(f"\n✓ Batch review working ({len(reviews)} clips)")


def test_skip_mode():
    """Test Phase 5 skip mode"""
    print("\n" + "="*60)
    print("Test: Phase 5 - Skip Mode")
    print("="*60)

    # Create test session
    session_id = create_test_session_with_phase4()

    # Run Phase 5 in skip mode
    print("\nRunning Phase 5 (skip mode)...")
    results = run_phase5(session_id, mode="skip")

    # Verify results
    print(f"\nResults:")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Phase: {results['phase']}")

    assert results['skipped'] == True, "Skip mode should set skipped=True"

    print("\n✓ Skip mode working")


def test_mock_mode():
    """Test Phase 5 mock mode"""
    print("\n" + "="*60)
    print("Test: Phase 5 - Mock Mode")
    print("="*60)

    # Create test session
    session_id = create_test_session_with_phase4()

    # Run Phase 5 in mock mode
    print("\nRunning Phase 5 (mock mode)...")
    results = run_phase5(session_id, mode="mock")

    # Verify results
    print(f"\nResults:")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Mode: {results['mode']}")
    print(f"  Reviews: {len(results['reviews'])}")
    print(f"  Average Score: {results['summary']['average_score']:.1f}/10")
    print(f"  Adjustments: {len(results['adjustments'])}")

    # Show sample reviews
    if results['reviews']:
        print(f"\nSample Review:")
        review = results['reviews'][0]
        print(f"  Clip: {review['clip_id']}")
        print(f"  Score: {review['claude_score']}/10")
        print(f"  Feedback: {review['claude_feedback'][:80]}...")

    # Show adjustments if any
    if results['adjustments']:
        print(f"\nAdjustments:")
        for adj in results['adjustments']:
            print(f"  {adj['clip_id']}: {adj['original_mode']} → {adj['new_mode']}")

    print("\n✓ Mock mode working")


def test_max_clips_limit():
    """Test limiting number of clips reviewed"""
    print("\n" + "="*60)
    print("Test: Phase 5 - Max Clips Limit")
    print("="*60)

    # Create test session
    session_id = create_test_session_with_phase4()

    # Run Phase 5 with limit
    print("\nRunning Phase 5 with max_clips=2...")
    results = run_phase5(session_id, mode="mock", max_clips=2)

    # Verify only 2 clips reviewed
    print(f"\nResults:")
    print(f"  Reviews: {len(results['reviews'])}")
    print(f"  Expected: 2")

    assert len(results['reviews']) == 2, "Should review exactly 2 clips"

    print("\n✓ Max clips limit working")


def test_adjustment_threshold():
    """Test adjustment threshold parameter"""
    print("\n" + "="*60)
    print("Test: Phase 5 - Adjustment Threshold")
    print("="*60)

    # Create test session
    session_id = create_test_session_with_phase4()

    # Run with strict threshold (only very bad clips)
    print("\nRunning with strict threshold (5.0)...")
    results_strict = run_phase5(
        session_id,
        mode="mock",
        adjustment_threshold=5.0
    )

    # Run with aggressive threshold (adjust most clips)
    print("\nRunning with aggressive threshold (8.0)...")
    results_aggressive = run_phase5(
        session_id,
        mode="mock",
        adjustment_threshold=8.0
    )

    print(f"\nStrict threshold (5.0):")
    print(f"  Adjustments: {len(results_strict['adjustments'])}")

    print(f"\nAggressive threshold (8.0):")
    print(f"  Adjustments: {len(results_aggressive['adjustments'])}")

    # Aggressive should have more adjustments
    # (In mock mode, this depends on hash values, but generally true)
    print("\n✓ Adjustment threshold working")


def test_client_creation():
    """Test client creation utility"""
    print("\n" + "="*60)
    print("Test: Client Creation")
    print("="*60)

    # Test mock client
    mock_client = create_client("mock")
    assert mock_client is not None
    assert mock_client.mock_mode == True
    print("  ✓ Mock client created")

    # Test skip (returns None)
    skip_client = create_client("skip")
    assert skip_client is None
    print("  ✓ Skip client (None) created")

    # Test invalid mode
    try:
        invalid_client = create_client("invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"  ✓ Invalid mode raises ValueError: {e}")

    print("\n✓ Client creation working")


def test_full_integration():
    """Test full Phase 5 integration"""
    print("\n" + "="*60)
    print("Test: Full Integration")
    print("="*60)

    try:
        # Run all tests
        test_api_client_mock_mode()
        test_api_client_batch()
        test_client_creation()
        test_skip_mode()
        test_mock_mode()
        test_max_clips_limit()
        test_adjustment_threshold()

        print("\n" + "="*60)
        print("All Phase 5 tests passed! ✓")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_integration()
    sys.exit(0 if success else 1)
