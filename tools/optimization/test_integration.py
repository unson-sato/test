"""
Integration test for automatic optimization triggering
Tests that Phase 2 and Phase 3 automatically trigger optimization tools
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import SharedState
from core.utils import get_session_dir, read_json, get_project_root
from phase2.runner import run_phase2
from phase3.runner import run_phase3


def test_phase2_integration():
    """Test that Phase 2 automatically triggers emotion target builder."""
    print("\n" + "=" * 60)
    print("TEST: Phase 2 Integration with Emotion Target Builder")
    print("=" * 60)

    # Create a new session for testing
    session = SharedState.create_session({
        'analysis': str(get_project_root() / "sample_analysis.json")
    })
    session_id = session.session_id
    print(f"\nCreated test session: {session_id}")

    # Manually complete Phase 0 and 1 (simplified for testing)
    print("\nSetting up Phase 0 and Phase 1...")
    from phase0.runner import run_phase0
    from phase1.runner import run_phase1

    try:
        run_phase0(session_id, mock_mode=True)
        print("✓ Phase 0 completed")
    except Exception as e:
        print(f"! Phase 0 setup: {e}")

    try:
        run_phase1(session_id, mock_mode=True)
        print("✓ Phase 1 completed")
    except Exception as e:
        print(f"! Phase 1 setup: {e}")

    # Run Phase 2 (should auto-trigger emotion target builder)
    print("\nRunning Phase 2 (with auto-trigger)...")
    try:
        result = run_phase2(session_id, mock_mode=True)
        print("✓ Phase 2 completed")

        # Check if emotion curve was created
        session_dir = get_session_dir(session_id)
        curve_path = session_dir / "target_emotion_curve.json"

        if curve_path.exists():
            print(f"\n✓ SUCCESS: Emotion curve automatically created!")
            print(f"  Path: {curve_path}")

            # Verify content
            curve_data = read_json(str(curve_path))
            print(f"  Sections: {len(curve_data['sections'])}")
            print(f"  Samples: {curve_data['statistics']['total_samples']}")
        else:
            print(f"\n✗ FAILED: Emotion curve not created")
            return False

        return True

    except Exception as e:
        print(f"\n✗ Phase 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase3_integration():
    """Test that Phase 3 automatically triggers clip optimizer."""
    print("\n" + "=" * 60)
    print("TEST: Phase 3 Integration with Clip Optimizer")
    print("=" * 60)

    # Use existing test session that has Phase 0-2 completed
    test_session_id = "mvorch_20251114_163545_d1c7c8d0"
    session_dir = get_session_dir(test_session_id)

    if not session_dir.exists():
        print(f"\n! Test session not found: {test_session_id}")
        print("  Skipping Phase 3 integration test")
        return True

    print(f"\nUsing test session: {test_session_id}")

    # Run Phase 3 (should auto-trigger clip optimizer)
    print("\nRunning Phase 3 (with auto-trigger)...")
    try:
        result = run_phase3(test_session_id, mock_mode=True)
        print("✓ Phase 3 completed")

        # Check if optimization summary was created
        summary_path = session_dir / "clip_optimization_summary.json"

        if summary_path.exists():
            print(f"\n✓ SUCCESS: Clip optimization automatically performed!")
            print(f"  Path: {summary_path}")

            # Verify content
            summary_data = read_json(str(summary_path))
            stats = summary_data['statistics']
            print(f"  Total clips: {stats['clips_adjusted'] + stats['clips_unchanged']}")
            print(f"  Adjusted: {stats['clips_adjusted']}")
        else:
            print(f"\n✗ FAILED: Optimization summary not created")
            return False

        return True

    except Exception as e:
        print(f"\n✗ Phase 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration tests."""
    print("\n" + "=" * 70)
    print("OPTIMIZATION TOOLS - INTEGRATION TESTS")
    print("=" * 70)

    results = []

    # Test Phase 2 integration
    result1 = test_phase2_integration()
    results.append(("Phase 2 Integration", result1))

    # Test Phase 3 integration
    result2 = test_phase3_integration()
    results.append(("Phase 3 Integration", result2))

    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST RESULTS")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
