"""
Phase 8 Runner: Effects & Lyric Motion
"""

import logging
from typing import Any, Dict

from core import SharedState
from core.shot_grammar import ShotGrammar
from core.utils import get_iso_timestamp, get_project_root

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase8Runner:
    """Applies visual effects and lyric motion"""

    def __init__(self, session_id: str, mock_mode: bool = True):
        self.session_id = session_id
        self.mock_mode = mock_mode
        self.session = SharedState.load_session(session_id)
        self.project_root = get_project_root()

        # Load shot grammar for fx rules
        try:
            grammar_path = self.project_root / "shot-grammar.json"
            self.shot_grammar = ShotGrammar(str(grammar_path))
        except Exception as e:
            logger.warning(f"Could not load shot grammar: {e}")
            self.shot_grammar = None

    def run(self) -> Dict[str, Any]:
        """Execute Phase 8"""
        logger.info(f"Starting Phase 8: Effects & Lyric Motion for session '{self.session_id}'")

        try:
            # Load timeline from Phase 7
            timeline = self._load_phase7_timeline()

            # Apply effects
            timeline = self._apply_effects(timeline)

            # Apply lyric motion (if lyrics available)
            lyric_data = self._apply_lyric_motion(timeline)

            results = {
                'timeline': timeline,
                'lyric_data': lyric_data,
                'effects_applied': self._count_effects(timeline)
            }

            self._save_results(results)

            logger.info(f"✓ Phase 8 completed: Effects applied")
            return results

        except Exception as e:
            logger.error(f"Phase 8 failed: {e}")
            raise

    def _load_phase7_timeline(self) -> Dict[str, Any]:
        """Load timeline from Phase 7"""
        phase7_data = self.session.get_phase_data(7)
        if phase7_data.status != "completed":
            raise RuntimeError("Phase 7 must be completed")
        return phase7_data.data.get('results', {}).get('timeline', {})

    def _apply_effects(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Apply visual effects from shot-grammar"""
        if not self.shot_grammar:
            return timeline

        fx_treatments = self.shot_grammar.get_section('fx_and_treatments')

        # Example: Apply color grading to sections
        for clip in timeline.get('clips', []):
            section = clip.get('metadata', {}).get('section', 'verse')

            if section == 'chorus':
                # Vibrant grading for chorus
                clip['effects'].append({
                    'type': 'color_grade_oversaturated',
                    'intensity': 1.2
                })
            elif section == 'intro':
                # Cool tones for intro
                clip['effects'].append({
                    'type': 'color_grade_teal_orange',
                    'intensity': 0.8
                })

        return timeline

    def _apply_lyric_motion(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Apply lyric motion graphics (mock)"""
        # TODO: Real lyric sync implementation
        return {
            'enabled': False,
            'format': 'srt',
            'style': 'modern_kinetic'
        }

    def _count_effects(self, timeline: Dict[str, Any]) -> int:
        """Count total effects applied"""
        return sum(len(clip.get('effects', [])) for clip in timeline.get('clips', []))

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save results"""
        phase_data = {
            'phase': 8,
            'status': 'completed',
            'timestamp': get_iso_timestamp(),
            'results': results
        }
        self.session.set_phase_data(8, phase_data)
        self.session.save()


def run_phase8(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """Run Phase 8"""
    runner = Phase8Runner(session_id, mock_mode=mock_mode)
    return runner.run()
