"""
Phase 7 Runner: Editing & Timeline Assembly

Assembles generated clips into cohesive timeline using shot-grammar editing rules.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core import SharedState
from core.shot_grammar import ShotGrammar
from core.utils import read_json, write_json, get_iso_timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase7Runner:
    """
    Assembles timeline with transitions and temporal techniques.

    This runner:
    1. Loads generated clips from Phase 6
    2. Loads clip timing from Phase 3
    3. Loads shot-grammar editing rules
    4. Selects transitions based on energy/emotion
    5. Applies temporal techniques
    6. Generates timeline structure
    7. Exports editing project files
    """

    def __init__(self, session_id: str, mock_mode: bool = True):
        """
        Initialize Phase 7 Runner.

        Args:
            session_id: The session identifier
            mock_mode: If True, simulate editing without processing files
        """
        self.session_id = session_id
        self.mock_mode = mock_mode
        self.session = SharedState.load_session(session_id)

        from core.utils import get_project_root
        self.project_root = get_project_root()

        # Load shot grammar for editing rules
        try:
            grammar_path = self.project_root / "shot-grammar.json"
            self.shot_grammar = ShotGrammar(str(grammar_path))
            logger.info("✓ Loaded shot-grammar editing rules")
        except Exception as e:
            logger.warning(f"Could not load shot grammar: {e}")
            self.shot_grammar = None

    def run(self) -> Dict[str, Any]:
        """
        Execute Phase 7 timeline assembly.

        Returns:
            Dictionary with timeline and editing results
        """
        logger.info(f"Starting Phase 7: Editing & Timeline Assembly for session '{self.session_id}'")

        try:
            # Load inputs
            generated_clips = self._load_phase6_clips()
            clip_timing = self._load_phase3_timing()
            beat_times = self._load_beat_data()

            # Build timeline
            timeline = self._build_timeline(generated_clips, clip_timing, beat_times)

            # Apply transitions
            timeline = self._apply_transitions(timeline)

            # Apply temporal techniques
            timeline = self._apply_temporal_techniques(timeline)

            # Generate project files
            project_files = self._generate_project_files(timeline)

            results = {
                'timeline': timeline,
                'project_files': project_files,
                'statistics': self._calculate_timeline_stats(timeline)
            }

            # Save results
            self._save_results(results)

            logger.info(f"✓ Phase 7 completed: Timeline with {len(timeline['clips'])} clips assembled")

            return results

        except Exception as e:
            logger.error(f"Phase 7 failed: {e}")
            raise

    def _load_phase6_clips(self) -> List[Dict[str, Any]]:
        """Load generated clips from Phase 6"""
        phase6_data = self.session.get_phase_data(6)
        if phase6_data.status != "completed":
            raise RuntimeError("Phase 6 must be completed before running Phase 7")

        clips = phase6_data.data.get('results', {}).get('generated_clips', [])
        # Filter to only completed clips
        completed_clips = [c for c in clips if c['status'] == 'completed']

        logger.info(f"Loaded {len(completed_clips)} generated clips")
        return completed_clips

    def _load_phase3_timing(self) -> List[Dict[str, Any]]:
        """Load clip timing from Phase 3"""
        phase3_data = self.session.get_phase_data(3)
        if phase3_data.status != "completed":
            raise RuntimeError("Phase 3 must be completed before running Phase 7")

        clips = phase3_data.data.get('winner', {}).get('proposal', {}).get('clips', [])
        logger.info(f"Loaded timing for {len(clips)} clips")
        return clips

    def _load_beat_data(self) -> List[float]:
        """Load beat timestamps from analysis.json"""
        analysis_path = self.project_root / "shared-workspace" / "input" / "analysis.json"
        if not analysis_path.exists():
            logger.warning("analysis.json not found, using mock beats")
            return [i * 0.5 for i in range(360)]  # Mock beats at 120 BPM

        analysis = read_json(str(analysis_path))
        beats = analysis.get('beats', [])
        if not beats:
            # Generate from BPM
            bpm = analysis.get('bpm', 120)
            duration = analysis.get('duration', 180)
            beat_interval = 60.0 / bpm
            beats = [i * beat_interval for i in range(int(duration / beat_interval) + 1)]

        return beats

    def _build_timeline(
        self,
        generated_clips: List[Dict[str, Any]],
        clip_timing: List[Dict[str, Any]],
        beat_times: List[float]
    ) -> Dict[str, Any]:
        """
        Build timeline structure from clips.

        Args:
            generated_clips: Clips from Phase 6
            clip_timing: Timing from Phase 3
            beat_times: Beat timestamps

        Returns:
            Timeline dictionary
        """
        # Create clip lookup by ID
        clip_files = {c['clip_id']: c for c in generated_clips}

        timeline_clips = []

        for timing in sorted(clip_timing, key=lambda x: x['start_time']):
            clip_id = timing['clip_id']

            if clip_id not in clip_files:
                logger.warning(f"Clip {clip_id} not found in generated clips, skipping")
                continue

            clip_file = clip_files[clip_id]

            timeline_clip = {
                'clip_id': clip_id,
                'track': 'video1',
                'start_time': timing['start_time'],
                'end_time': timing['end_time'],
                'source_file': clip_file['output_path'],
                'in_point': 0.0,
                'out_point': timing['duration'],
                'transition_in': None,
                'transition_out': None,
                'effects': [],
                'speed': 1.0,
                'metadata': {
                    'section': timing.get('section', 'unknown'),
                    'shot_type': timing.get('shot_type', 'unknown'),
                    'shot_size': timing.get('shot_size', 'medium_shot'),
                    'camera_movement': timing.get('camera_movement', 'static_locked'),
                    'beat_aligned': timing.get('beat_aligned', False)
                }
            }

            timeline_clips.append(timeline_clip)

        return {
            'clips': timeline_clips,
            'total_duration': timeline_clips[-1]['end_time'] if timeline_clips else 0.0,
            'frame_rate': 24,
            'resolution': '1920x1080',
            'audio_track': 'music.mp3'
        }

    def _apply_transitions(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transitions between clips using shot-grammar rules.

        Args:
            timeline: Timeline dictionary

        Returns:
            Timeline with transitions applied
        """
        if not self.shot_grammar:
            logger.warning("Shot grammar not available, using basic transitions")
            return self._apply_basic_transitions(timeline)

        clips = timeline['clips']
        editing_transitions = self.shot_grammar.get_section('editing_transitions')
        transition_logic = self.shot_grammar.get_section('scene_transition_logic')

        for i in range(len(clips) - 1):
            current_clip = clips[i]
            next_clip = clips[i + 1]

            # Select transition based on shot-grammar logic
            transition = self._select_transition(
                current_clip,
                next_clip,
                editing_transitions,
                transition_logic
            )

            current_clip['transition_out'] = transition
            next_clip['transition_in'] = transition

        return timeline

    def _select_transition(
        self,
        clip_a: Dict[str, Any],
        clip_b: Dict[str, Any],
        transitions: Dict[str, Any],
        logic: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Select appropriate transition using shot-grammar rules.

        Args:
            clip_a: Current clip
            clip_b: Next clip
            transitions: Available transitions from grammar
            logic: Transition logic rules from grammar

        Returns:
            Transition dictionary
        """
        # Calculate energy difference
        energy_a = self._estimate_clip_energy(clip_a)
        energy_b = self._estimate_clip_energy(clip_b)
        energy_diff = energy_b - energy_a

        # Check if section boundary
        section_change = clip_a['metadata']['section'] != clip_b['metadata']['section']

        # Apply transition logic
        if section_change:
            # Section boundary: use appropriate transition
            if energy_diff > 0.5:
                transition_type = 'smash_cut'  # Shock, contrast
            elif energy_diff < -0.5:
                transition_type = 'fade_to_black'  # Finality, pause
            else:
                transition_type = 'crossfade_dissolve'  # Gentle transition
        elif energy_diff > 0.7:
            # Large energy jump
            transition_type = 'whip_pan_transition'  # Dynamic
        elif energy_diff < -0.5:
            # Energy drop
            transition_type = 'crossfade_dissolve'  # Soft
        else:
            # Normal flow
            transition_type = 'hard_cut'  # Standard

        transition_data = transitions.get(transition_type, {})

        return {
            'type': transition_type,
            'duration': self._get_transition_duration(transition_data),
            'description': transition_data.get('description', '')
        }

    def _estimate_clip_energy(self, clip: Dict[str, Any]) -> float:
        """
        Estimate clip energy level (0.0 to 1.0).

        Based on:
        - Camera movement intensity
        - Shot size (wider = more energy)
        - Clip duration (shorter = more energy)
        """
        metadata = clip['metadata']

        # Camera movement contribution
        movement = metadata.get('camera_movement', 'static_locked')
        movement_energy = {
            'static_locked': 0.1,
            'slow_pan': 0.2,
            'dolly_push': 0.4,
            'steadicam': 0.5,
            'gimbal_flow': 0.6,
            'handheld': 0.7,
            'drone_aerial': 0.8,
            'whip_pan': 0.9,
            'fpv_drone_fast': 1.0
        }.get(movement, 0.5)

        # Duration contribution (shorter = higher energy)
        duration = clip['end_time'] - clip['start_time']
        duration_energy = max(0.0, 1.0 - (duration / 5.0))

        # Combine
        total_energy = (movement_energy * 0.6 + duration_energy * 0.4)

        return min(1.0, max(0.0, total_energy))

    def _get_transition_duration(self, transition_data: Dict[str, Any]) -> float:
        """Get transition duration in seconds"""
        duration_str = transition_data.get('duration', '0 frames')

        if 'frames' in duration_str:
            # Convert frames to seconds at 24fps
            frames = int(duration_str.split()[0]) if duration_str.split()[0].isdigit() else 0
            return frames / 24.0
        else:
            return 0.0

    def _apply_basic_transitions(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Apply basic hard cuts (fallback)"""
        clips = timeline['clips']

        for i in range(len(clips) - 1):
            transition = {'type': 'hard_cut', 'duration': 0.0}
            clips[i]['transition_out'] = transition
            clips[i + 1]['transition_in'] = transition

        return timeline

    def _apply_temporal_techniques(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply temporal techniques (slow-mo, speed ramps, etc.) from shot-grammar.

        Args:
            timeline: Timeline dictionary

        Returns:
            Timeline with temporal effects applied
        """
        if not self.shot_grammar:
            return timeline

        temporal_techniques = self.shot_grammar.get_section('temporal_techniques')

        # Apply slow-motion to emotional peaks (close-ups in key sections)
        for clip in timeline['clips']:
            metadata = clip['metadata']

            if metadata.get('shot_size') == 'close_up' and metadata.get('section') in ['chorus', 'bridge']:
                # Apply slow-motion
                slow_mo = {
                    'type': 'slow_motion',
                    'speed_factor': 0.8,
                    'description': temporal_techniques.get('slow_motion', {}).get('description', '')
                }
                clip['effects'].append(slow_mo)
                clip['speed'] = 0.8

        return timeline

    def _generate_project_files(self, timeline: Dict[str, Any]) -> Dict[str, str]:
        """Generate editing project files"""
        # For now, just save as JSON
        # TODO: Generate actual .drp, .xml, .edl files

        timeline_path = self.project_root / "shared-workspace" / "sessions" / self.session_id / "timeline.json"
        write_json(str(timeline_path), timeline)

        return {
            'json': str(timeline_path),
            'drp': 'Not yet implemented',
            'xml': 'Not yet implemented',
            'edl': 'Not yet implemented'
        }

    def _calculate_timeline_stats(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate timeline statistics"""
        clips = timeline['clips']

        transition_types = {}
        for clip in clips:
            if clip.get('transition_out'):
                t_type = clip['transition_out']['type']
                transition_types[t_type] = transition_types.get(t_type, 0) + 1

        effects_count = sum(len(clip.get('effects', [])) for clip in clips)

        return {
            'total_clips': len(clips),
            'total_duration': timeline['total_duration'],
            'transition_types': transition_types,
            'effects_applied': effects_count,
            'average_clip_length': timeline['total_duration'] / len(clips) if clips else 0.0
        }

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save Phase 7 results to SharedState"""
        phase_data = {
            'phase': 7,
            'status': 'completed',
            'timestamp': get_iso_timestamp(),
            'results': results
        }

        self.session.set_phase_data(7, phase_data)
        self.session.save()

        logger.info("Phase 7 results saved to SharedState")


def run_phase7(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run Phase 7.

    Args:
        session_id: The session identifier
        mock_mode: If True, simulate editing

    Returns:
        Phase 7 results dictionary
    """
    runner = Phase7Runner(session_id, mock_mode=mock_mode)
    return runner.run()
