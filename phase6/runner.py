"""
Phase 6 Runner: Video Generation Execution

Handles actual video clip generation based on Phase 4 strategies.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from core import SharedState
from core.utils import read_json, write_json, get_iso_timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase6Runner:
    """
    Executes video generation for all clips.

    This runner:
    1. Loads generation strategies from Phase 4
    2. Prepares generation queue
    3. Submits clips to appropriate generation services
    4. Monitors progress and collects outputs
    5. Validates quality
    6. Saves results to SharedState
    """

    def __init__(self, session_id: str, mock_mode: bool = True):
        """
        Initialize Phase 6 Runner.

        Args:
            session_id: The session identifier
            mock_mode: If True, simulate generation without calling external APIs
        """
        self.session_id = session_id
        self.mock_mode = mock_mode
        self.session = SharedState.load_session(session_id)

        from core.utils import get_project_root
        self.project_root = get_project_root()

        # Setup output directory
        self.clips_dir = self.project_root / "shared-workspace" / "sessions" / session_id / "clips"
        self.clips_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> Dict[str, Any]:
        """
        Execute Phase 6 video generation.

        Returns:
            Dictionary with generation results
        """
        logger.info(f"Starting Phase 6: Video Generation Execution for session '{self.session_id}'")

        try:
            # Load inputs from Phase 4
            generation_strategies = self._load_phase4_strategies()
            clips_info = self._load_phase3_clips()

            # Execute generation
            generated_clips = self._generate_all_clips(generation_strategies, clips_info)

            # Generate execution summary
            execution_summary = self._generate_execution_summary(generated_clips)

            # Prepare results
            results = {
                'generated_clips': generated_clips,
                'execution_summary': execution_summary,
                'failed_clips': [c for c in generated_clips if c['status'] != 'completed']
            }

            # Save to SharedState
            self._save_results(results)

            logger.info(f"✓ Phase 6 completed: {execution_summary['completed']}/{execution_summary['total_clips']} clips generated")

            return results

        except Exception as e:
            logger.error(f"Phase 6 failed: {e}")
            raise

    def _load_phase4_strategies(self) -> Dict[str, Any]:
        """Load generation strategies from Phase 4"""
        phase4_data = self.session.get_phase_data(4)
        if phase4_data.status != "completed":
            raise RuntimeError("Phase 4 must be completed before running Phase 6")

        # Phase 4 winner contains proposal with generation_strategies
        winner = phase4_data.data.get('winner', {})
        proposal = winner.get('proposal', {})
        strategies = proposal.get('generation_strategies', [])

        if not strategies:
            raise RuntimeError("No generation strategies found in Phase 4")

        logger.info(f"Loaded {len(strategies)} generation strategies")
        return {s['clip_id']: s for s in strategies}

    def _load_phase3_clips(self) -> Dict[str, Any]:
        """Load clip division from Phase 3"""
        phase3_data = self.session.get_phase_data(3)
        if phase3_data.status != "completed":
            raise RuntimeError("Phase 3 must be completed before running Phase 6")

        clips = phase3_data.data.get('winner', {}).get('proposal', {}).get('clips', [])
        if not clips:
            raise RuntimeError("No clips found in Phase 3")

        logger.info(f"Loaded {len(clips)} clips from Phase 3")
        return {c['clip_id']: c for c in clips}

    def _generate_all_clips(
        self,
        strategies: Dict[str, Any],
        clips_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate all video clips.

        Args:
            strategies: Generation strategies by clip_id
            clips_info: Clip information by clip_id

        Returns:
            List of generated clip results
        """
        generated_clips = []

        for clip_id in sorted(strategies.keys()):
            strategy = strategies[clip_id]
            clip_info = clips_info.get(clip_id, {})

            logger.info(f"Generating {clip_id}...")

            result = self._generate_single_clip(clip_id, strategy, clip_info)
            generated_clips.append(result)

        return generated_clips

    def _generate_single_clip(
        self,
        clip_id: str,
        strategy: Dict[str, Any],
        clip_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a single video clip.

        Args:
            clip_id: Clip identifier
            strategy: Generation strategy from Phase 4
            clip_info: Clip information from Phase 3

        Returns:
            Generation result dictionary
        """
        if self.mock_mode:
            return self._mock_generate_clip(clip_id, strategy, clip_info)
        else:
            return self._real_generate_clip(clip_id, strategy, clip_info)

    def _mock_generate_clip(
        self,
        clip_id: str,
        strategy: Dict[str, Any],
        clip_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock clip generation for testing"""
        import random

        # Simulate generation success (90% success rate)
        success = random.random() > 0.1

        output_path = str(self.clips_dir / f"{clip_id}.mp4")

        # Create mock output file
        mock_file = Path(output_path)
        mock_file.write_text(f"Mock video clip: {clip_id}\nGenerated at: {get_iso_timestamp()}")

        duration = clip_info.get('duration', 3.0)

        if success:
            return {
                'clip_id': clip_id,
                'status': 'completed',
                'generation_mode': strategy.get('generation_mode', 'mock'),
                'output_path': output_path,
                'generation_time': get_iso_timestamp(),
                'actual_duration': duration + random.uniform(-0.2, 0.2),
                'quality_score': random.uniform(0.85, 0.98),
                'metadata': {
                    'prompt_used': strategy.get('prompt_template', {}).get('full_prompt', 'mock prompt'),
                    'model_version': 'mock-v1.0',
                    'seed': random.randint(1000, 9999),
                    'generation_params': strategy.get('variance_params', {})
                }
            }
        else:
            return {
                'clip_id': clip_id,
                'status': 'failed',
                'generation_mode': strategy.get('generation_mode', 'mock'),
                'output_path': None,
                'generation_time': get_iso_timestamp(),
                'actual_duration': 0.0,
                'quality_score': 0.0,
                'error': 'Mock generation failure (10% random failure)',
                'retry_count': 3
            }

    def _real_generate_clip(
        self,
        clip_id: str,
        strategy: Dict[str, Any],
        clip_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Real clip generation using external services"""
        # TODO: Implement real generation service integration
        # This would:
        # 1. Load appropriate client (Veo2/Sora/Runway/etc.)
        # 2. Format final prompt with assets
        # 3. Submit generation request
        # 4. Poll for completion
        # 5. Download and validate output
        # 6. Store with metadata

        logger.warning(f"Real generation not yet implemented for {clip_id}. Using mock.")
        return self._mock_generate_clip(clip_id, strategy, clip_info)

    def _generate_execution_summary(self, generated_clips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution summary statistics"""
        total_clips = len(generated_clips)
        completed = sum(1 for c in generated_clips if c['status'] == 'completed')
        failed = total_clips - completed

        completed_clips = [c for c in generated_clips if c['status'] == 'completed']
        quality_average = sum(c['quality_score'] for c in completed_clips) / len(completed_clips) if completed_clips else 0.0

        return {
            'total_clips': total_clips,
            'completed': completed,
            'failed': failed,
            'total_generation_time': f"{total_clips * 2.5} minutes (mock)",
            'total_cost': f"${total_clips * 10.0:.2f} (mock)",
            'quality_average': round(quality_average, 2)
        }

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save Phase 6 results to SharedState"""
        phase_data = {
            'phase': 6,
            'timestamp': get_iso_timestamp(),
            'results': results
        }

        self.session.set_phase_data(6, phase_data, auto_save=False)
        self.session.complete_phase(6)

        logger.info(f"Phase 6 results saved to SharedState")


def run_phase6(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 6.

    Args:
        session_id: The session identifier
        mock_mode: If True, use mock generation

    Returns:
        Phase 6 results dictionary
    """
    runner = Phase6Runner(session_id, mock_mode=mock_mode)
    return runner.run()
