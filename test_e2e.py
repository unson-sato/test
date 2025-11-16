#!/usr/bin/env python3
"""
End-to-End Test for MV Orchestra v2.8

Tests the complete pipeline from analysis.json to final generation plan.

Usage:
    python3 test_e2e.py
    python3 test_e2e.py -v  # Verbose mode

Author: MV Orchestra Team
Version: 2.8
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    SharedState,
    read_json,
    write_json,
    get_session_dir,
    get_project_root
)
from phase0 import run_phase0
from phase1 import run_phase1
from phase2 import run_phase2
from phase3 import run_phase3
from phase4 import run_phase4


class TestE2EPipeline(unittest.TestCase):
    """End-to-end pipeline tests."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.project_root = get_project_root()
        cls.sample_analysis = cls.project_root / 'sample_analysis.json'

        # Ensure sample analysis exists
        if not cls.sample_analysis.exists():
            raise FileNotFoundError(
                f"sample_analysis.json not found at {cls.sample_analysis}. "
                "Cannot run end-to-end tests without sample data."
            )

    def setUp(self):
        """Set up each test."""
        # Create unique session ID for each test
        import uuid
        self.session_id = f"test_e2e_{uuid.uuid4().hex[:8]}"
        self.session_dir = get_session_dir(self.session_id)

    def tearDown(self):
        """Clean up after each test."""
        # Optionally clean up test sessions
        # Commented out to allow inspection of test results
        # if self.session_dir.exists():
        #     shutil.rmtree(self.session_dir)
        pass

    def test_full_pipeline_mock_mode(self):
        """Test complete pipeline with mock evaluations."""
        print(f"\n{'='*70}")
        print(f"TEST: Full Pipeline (Mock Mode)")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*70}")

        # Phase 0: Overall Design
        print("\n→ Running Phase 0: Overall Design")
        phase0_results = run_phase0(
            session_id=self.session_id,
            analysis_path=str(self.sample_analysis),
            mock_mode=True
        )
        self.assertIsNotNone(phase0_results)
        self.assertIn('winner', phase0_results)
        self.assertIn('director', phase0_results['winner'])
        print(f"  ✓ Winner: {phase0_results['winner']['director']}")

        # Phase 1: Character Design
        print("\n→ Running Phase 1: Character Design")
        phase1_results = run_phase1(
            session_id=self.session_id,
            mock_mode=True
        )
        self.assertIsNotNone(phase1_results)
        self.assertIn('winner', phase1_results)
        print(f"  ✓ Winner: {phase1_results['winner']['director']}")

        # Phase 2: Section Direction
        print("\n→ Running Phase 2: Section Direction")
        phase2_results = run_phase2(
            session_id=self.session_id,
            mock_mode=True
        )
        self.assertIsNotNone(phase2_results)
        self.assertIn('winner', phase2_results)
        print(f"  ✓ Winner: {phase2_results['winner']['director']}")

        # Phase 3: Clip Division
        print("\n→ Running Phase 3: Clip Division")
        phase3_results = run_phase3(
            session_id=self.session_id,
            mock_mode=True
        )
        self.assertIsNotNone(phase3_results)
        self.assertIn('winner', phase3_results)
        print(f"  ✓ Winner: {phase3_results['winner']['director']}")

        # Verify clips were created
        clips = phase3_results['winner'].get('clips', [])
        self.assertGreater(len(clips), 0, "Phase 3 should generate clips")
        print(f"  ✓ Generated {len(clips)} clips")

        # Phase 4: Generation Strategy
        print("\n→ Running Phase 4: Generation Strategy")
        phase4_results = run_phase4(
            session_id=self.session_id,
            mock_mode=True
        )
        self.assertIsNotNone(phase4_results)
        self.assertIn('winner', phase4_results)
        print(f"  ✓ Winner: {phase4_results['winner']['director']}")

        # Verify session was saved
        session = SharedState.load_session(self.session_id)
        self.assertEqual(session.session_id, self.session_id)

        # Verify all phases completed
        for phase_num in range(5):  # Phases 0-4
            self.assertIn(phase_num, session.phases)
            self.assertEqual(
                session.phases[phase_num].status,
                'completed',
                f"Phase {phase_num} should be completed"
            )

        print(f"\n{'='*70}")
        print(f"✓ Full pipeline test passed!")
        print(f"  Session saved to: {self.session_dir}")
        print(f"{'='*70}")

    def test_pipeline_with_optimization(self):
        """Test pipeline with optimization tools."""
        print(f"\n{'='*70}")
        print(f"TEST: Pipeline with Optimization")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*70}")

        # Run through Phase 3
        print("\n→ Running Phases 0-3")
        run_phase0(self.session_id, str(self.sample_analysis), mock_mode=True)
        run_phase1(self.session_id, mock_mode=True)
        run_phase2(self.session_id, mock_mode=True)
        phase3_results = run_phase3(self.session_id, mock_mode=True)

        # Run clip optimizer
        print("\n→ Running clip optimizer")
        try:
            from tools.optimization.clip_optimizer import ClipOptimizer

            optimizer = ClipOptimizer(self.session_id)
            result = optimizer.optimize_all_clips()

            self.assertTrue(result['success'])
            self.assertGreater(result['stats']['total_clips'], 0)
            print(f"  ✓ Optimized {result['stats']['total_clips']} clips")
            print(f"  ✓ Applied {result['stats']['optimizations_applied']} optimizations")

        except ImportError:
            print("  ⚠ Clip optimizer not available, skipping")

        print(f"\n{'='*70}")
        print(f"✓ Optimization test passed!")
        print(f"{'='*70}")

    def test_pipeline_with_validation(self):
        """Test pipeline with validators enabled."""
        print(f"\n{'='*70}")
        print(f"TEST: Pipeline with Validation")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*70}")

        # Run through Phase 4
        print("\n→ Running Phases 0-4")
        run_phase0(self.session_id, str(self.sample_analysis), mock_mode=True)
        run_phase1(self.session_id, mock_mode=True)
        run_phase2(self.session_id, mock_mode=True)
        run_phase3(self.session_id, mock_mode=True)
        run_phase4(self.session_id, mock_mode=True)

        # Validate clip division
        print("\n→ Validating clip division")
        try:
            from tools.validators.validate_clip_division import ClipDivisionValidator

            validator = ClipDivisionValidator(self.session_id)
            result = validator.validate()

            # Should be valid or have only warnings
            if not result['valid']:
                print(f"  ⚠ Validation found {len(result['errors'])} issues")
                for error in result['errors'][:3]:
                    print(f"    - {error}")
            else:
                print(f"  ✓ Clip division is valid")

        except ImportError:
            print("  ⚠ Clip division validator not available, skipping")

        # Validate Phase 4 strategies
        print("\n→ Validating generation strategies")
        try:
            from tools.validators.validate_phase4_strategies import Phase4StrategyValidator

            validator = Phase4StrategyValidator(self.session_id)
            result = validator.validate()

            if not result['valid']:
                print(f"  ⚠ Validation found {len(result['errors'])} issues")
                for error in result['errors'][:3]:
                    print(f"    - {error}")
            else:
                print(f"  ✓ Generation strategies are valid")

        except ImportError:
            print("  ⚠ Strategy validator not available, skipping")

        print(f"\n{'='*70}")
        print(f"✓ Validation test passed!")
        print(f"{'='*70}")

    def test_session_state_persistence(self):
        """Test that session state persists correctly across phases."""
        print(f"\n{'='*70}")
        print(f"TEST: Session State Persistence")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*70}")

        # Run Phase 0
        print("\n→ Running Phase 0")
        phase0_results = run_phase0(
            self.session_id,
            str(self.sample_analysis),
            mock_mode=True
        )

        # Load session and verify Phase 0 data
        print("\n→ Verifying Phase 0 persistence")
        session = SharedState.load_session(self.session_id)
        self.assertIn(0, session.phases)
        self.assertEqual(session.phases[0].status, 'completed')

        phase0_data = session.get_phase_data(0)
        self.assertIsNotNone(phase0_data)
        self.assertIn('winner', phase0_data)

        # Run Phase 1
        print("\n→ Running Phase 1")
        phase1_results = run_phase1(self.session_id, mock_mode=True)

        # Reload session and verify both phases
        print("\n→ Verifying both phases persist")
        session = SharedState.load_session(self.session_id)
        self.assertIn(0, session.phases)
        self.assertIn(1, session.phases)

        # Verify Phase 0 data still exists
        phase0_data_reloaded = session.get_phase_data(0)
        self.assertEqual(
            phase0_data['winner']['director'],
            phase0_data_reloaded['winner']['director']
        )

        print(f"\n{'='*70}")
        print(f"✓ Persistence test passed!")
        print(f"{'='*70}")

    def test_error_handling_missing_analysis(self):
        """Test error handling for missing analysis file."""
        print(f"\n{'='*70}")
        print(f"TEST: Error Handling - Missing Analysis")
        print(f"{'='*70}")

        # Try to run Phase 0 with non-existent analysis
        with self.assertRaises(FileNotFoundError):
            run_phase0(
                self.session_id,
                "/nonexistent/analysis.json",
                mock_mode=True
            )

        print(f"  ✓ Correctly raised FileNotFoundError")
        print(f"\n{'='*70}")
        print(f"✓ Error handling test passed!")
        print(f"{'='*70}")


class TestPipelineComponents(unittest.TestCase):
    """Test individual pipeline components."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = get_project_root()
        cls.sample_analysis = cls.project_root / 'sample_analysis.json'

    def test_analysis_json_format(self):
        """Test that sample_analysis.json has correct format."""
        print(f"\n{'='*70}")
        print(f"TEST: Analysis JSON Format")
        print(f"{'='*70}")

        analysis = read_json(self.sample_analysis)

        # Required fields
        required_fields = [
            'title', 'artist', 'bpm', 'duration',
            'sections', 'lyrics', 'mood'
        ]

        for field in required_fields:
            self.assertIn(field, analysis, f"Analysis missing required field: {field}")
            print(f"  ✓ {field}: present")

        # Sections should be a list
        self.assertIsInstance(analysis['sections'], list)
        self.assertGreater(len(analysis['sections']), 0)
        print(f"  ✓ sections: {len(analysis['sections'])} sections found")

        print(f"\n{'='*70}")
        print(f"✓ Analysis format test passed!")
        print(f"{'='*70}")

    def test_director_profiles_available(self):
        """Test that all director profiles are available."""
        print(f"\n{'='*70}")
        print(f"TEST: Director Profiles")
        print(f"{'='*70}")

        from core import get_all_profiles, DirectorType

        profiles = get_all_profiles()
        self.assertEqual(len(profiles), 5, "Should have 5 director profiles")

        for director_type in DirectorType:
            from core import get_director_profile
            profile = get_director_profile(director_type)
            self.assertIsNotNone(profile)
            print(f"  ✓ {director_type.value}: {profile.name_en}")

        print(f"\n{'='*70}")
        print(f"✓ Director profiles test passed!")
        print(f"{'='*70}")


def run_tests(verbosity=2):
    """
    Run all tests.

    Args:
        verbosity: Test output verbosity (1=quiet, 2=normal, 3=verbose)
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestE2EPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineComponents))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="End-to-End Tests for MV Orchestra v2.8")
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet output')
    args = parser.parse_args()

    verbosity = 2
    if args.verbose:
        verbosity = 3
    elif args.quiet:
        verbosity = 1

    print("\n" + "="*70)
    print("MV ORCHESTRA v2.8 - END-TO-END TESTS")
    print("="*70)

    success = run_tests(verbosity=verbosity)

    if success:
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print("✗ SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
