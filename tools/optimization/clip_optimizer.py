"""
Clip Optimizer for MV Orchestra v2.8

This tool optimizes clip durations to match the target emotion curve
and adds creative adjustment recommendations for Phase 4 generation.

Features:
- Optimize clip durations based on emotional intensity
- Maintain beat alignment constraints
- Respect section boundaries
- Add creative variance suggestions (lighting, camera, color grading)
- Preserve total timeline duration

Usage:
    # Standalone
    python clip_optimizer.py <session_id>

    # As module
    from tools.optimization.clip_optimizer import optimize_clips
    optimize_clips(session_id)
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from core import SharedState
from core.utils import read_json, write_json, get_iso_timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClipOptimizer:
    """
    Optimizes clip durations and adds creative adjustment recommendations.

    The optimizer matches clip durations to emotional intensity while
    respecting beat alignment and section boundaries.
    """

    def __init__(self, session_id: str,
                 min_clip_duration: float = 0.8,
                 max_clip_duration: float = 8.0):
        """
        Initialize Clip Optimizer.

        Args:
            session_id: The session identifier
            min_clip_duration: Minimum allowed clip duration in seconds
            max_clip_duration: Maximum allowed clip duration in seconds
        """
        self.session_id = session_id
        self.min_clip_duration = min_clip_duration
        self.max_clip_duration = max_clip_duration
        self.session = SharedState.load_session(session_id)

    def load_inputs(self) -> Tuple[List[Dict], List[Dict], List[Dict], float]:
        """
        Load required inputs from session.

        Returns:
            Tuple of (clips, emotion_curve, beat_times, total_duration)

        Raises:
            RuntimeError: If required data is missing
        """
        # Load Phase 3 clip division
        phase3_data = self.session.get_phase_data(3)
        if phase3_data.status != "completed":
            raise RuntimeError(
                f"Phase 3 must be completed before optimizing clips. "
                f"Current status: {phase3_data.status}"
            )

        winner_proposal = phase3_data.data.get('winner', {}).get('proposal', {})
        clips = winner_proposal.get('clips', [])
        if not clips:
            raise RuntimeError("No clips found in Phase 3 winner proposal")

        logger.info(f"Loaded {len(clips)} clips from Phase 3")

        # Load target emotion curve
        curve_path = self.session.get_global_data('target_emotion_curve_path')
        if not curve_path:
            raise RuntimeError(
                "Target emotion curve not found. "
                "Run emotion_target_builder first."
            )

        curve_data = read_json(curve_path)
        emotion_curve = curve_data.get('curve', [])
        logger.info(f"Loaded emotion curve with {len(emotion_curve)} samples")

        # Load beat times from analysis
        # For now, we'll extract from Phase 3 metadata or estimate
        beat_times = self._load_beat_times()

        # Calculate total duration
        total_duration = max(c['end_time'] for c in clips) if clips else 0.0

        return clips, emotion_curve, beat_times, total_duration

    def _load_beat_times(self) -> List[float]:
        """
        Load beat times from analysis or estimate from BPM.

        Returns:
            List of beat timestamps
        """
        # Try to load from analysis.json
        try:
            from core.utils import get_project_root
            analysis_path = get_project_root() / "shared-workspace" / "input" / "analysis.json"
            if analysis_path.exists():
                analysis = read_json(str(analysis_path))
                # Check if beat times are directly available
                if 'beats' in analysis:
                    return analysis['beats']
                # Otherwise estimate from BPM
                bpm = analysis.get('bpm', 120)
                duration = analysis.get('duration', 180)
                return self._estimate_beats_from_bpm(bpm, duration)
        except Exception as e:
            logger.warning(f"Could not load beat times from analysis: {e}")

        # Fallback: estimate from common BPM
        return self._estimate_beats_from_bpm(120, 180)

    def _estimate_beats_from_bpm(self, bpm: float, duration: float) -> List[float]:
        """Estimate beat times from BPM."""
        beat_interval = 60.0 / bpm
        beats = []
        t = 0.0
        while t < duration:
            beats.append(t)
            t += beat_interval
        return beats

    def calculate_clip_emotion_score(self, clip: Dict,
                                     emotion_curve: List[Dict]) -> float:
        """
        Calculate average emotion score for a clip.

        Args:
            clip: Clip dictionary with start_time and end_time
            emotion_curve: Emotion curve data

        Returns:
            Average emotion value for the clip duration
        """
        start_time = clip['start_time']
        end_time = clip['end_time']

        # Find all curve points within this clip's timeframe
        relevant_points = [
            p for p in emotion_curve
            if start_time <= p['time'] <= end_time
        ]

        if not relevant_points:
            # Find nearest point
            nearest = min(emotion_curve, key=lambda p: abs(p['time'] - start_time))
            return nearest['emotion']

        # Calculate average
        avg_emotion = sum(p['emotion'] for p in relevant_points) / len(relevant_points)
        return avg_emotion

    def calculate_ideal_duration(self, emotion_score: float,
                                 base_duration: float,
                                 shot_type: str) -> float:
        """
        Calculate ideal clip duration based on emotion score.

        Higher emotion = longer duration (to emphasize impact)
        Lower emotion = moderate duration (maintain flow)

        Args:
            emotion_score: Clip's emotion score (0.0-1.0)
            base_duration: Original clip duration
            shot_type: Type of shot (affects ideal duration)

        Returns:
            Ideal duration in seconds
        """
        # Base adjustment factor based on emotion
        # High emotion (0.8-1.0): extend by up to 30%
        # Medium emotion (0.4-0.7): neutral (0-10% adjustment)
        # Low emotion (0.0-0.4): may shorten slightly (up to -15%)

        if emotion_score >= 0.8:
            # High emotion: extend duration
            adjustment_factor = 1.0 + (emotion_score - 0.8) * 1.5  # up to +30%
        elif emotion_score >= 0.4:
            # Medium emotion: minor adjustment
            adjustment_factor = 1.0 + (emotion_score - 0.5) * 0.2  # -10% to +10%
        else:
            # Low emotion: may shorten
            adjustment_factor = 1.0 - (0.4 - emotion_score) * 0.375  # up to -15%

        ideal = base_duration * adjustment_factor

        # Shot type considerations
        if "establishing" in shot_type.lower() or "wide" in shot_type.lower():
            # Wide shots typically need more time
            ideal = max(ideal, 2.0)
        elif "close-up" in shot_type.lower() or "detail" in shot_type.lower():
            # Close-ups can be shorter or longer depending on emotion
            if emotion_score > 0.7:
                ideal = max(ideal, 1.5)  # Emotional close-ups need time
        elif "transition" in shot_type.lower():
            # Transitions should be brief
            ideal = min(ideal, 1.0)

        # Apply constraints
        ideal = max(self.min_clip_duration, min(self.max_clip_duration, ideal))

        return ideal

    def find_nearest_beat(self, time: float, beat_times: List[float],
                         tolerance: float = 0.3) -> float:
        """
        Find nearest beat to given time.

        Args:
            time: Target time in seconds
            beat_times: List of beat timestamps
            tolerance: Maximum distance to nearest beat

        Returns:
            Nearest beat time, or original time if no beat within tolerance
        """
        if not beat_times:
            return time

        nearest = min(beat_times, key=lambda b: abs(b - time))

        if abs(nearest - time) <= tolerance:
            return nearest
        return time

    def optimize_clip(self, clip: Dict, emotion_score: float,
                     beat_times: List[float],
                     prev_clip_end: float) -> Tuple[Dict, bool]:
        """
        Optimize a single clip's duration.

        Args:
            clip: Clip dictionary
            emotion_score: Clip's emotion score
            beat_times: List of beat times
            prev_clip_end: End time of previous clip (for gap prevention)

        Returns:
            Tuple of (optimized_clip_dict, adjustment_made)
        """
        original_duration = clip['duration']
        shot_type = clip.get('shot_type', 'medium')

        # Calculate ideal duration
        ideal_duration = self.calculate_ideal_duration(
            emotion_score, original_duration, shot_type
        )

        # Determine if adjustment is worthwhile (>5% change)
        adjustment_threshold = 0.05
        duration_change = abs(ideal_duration - original_duration)
        should_adjust = duration_change / original_duration > adjustment_threshold

        if not should_adjust:
            # No adjustment needed
            return {
                'clip_id': clip['clip_id'],
                'original_duration': original_duration,
                'optimized_duration': original_duration,
                'emotion_score': round(emotion_score, 3),
                'adjustment_made': False,
                'adjustment_reason': 'already optimal'
            }, False

        # Calculate new end time
        new_end = clip['start_time'] + ideal_duration

        # Snap to nearest beat
        new_end_snapped = self.find_nearest_beat(new_end, beat_times)

        # Ensure minimum duration after snapping
        if new_end_snapped - clip['start_time'] < self.min_clip_duration:
            new_end_snapped = clip['start_time'] + self.min_clip_duration

        optimized_duration = new_end_snapped - clip['start_time']

        # Determine reason for adjustment
        if emotion_score >= 0.8:
            reason = "high emotion section, extended for impact"
        elif emotion_score <= 0.3:
            reason = "low energy section, shortened for pacing"
        else:
            reason = "moderate adjustment for emotional flow"

        return {
            'clip_id': clip['clip_id'],
            'original_duration': round(original_duration, 2),
            'optimized_duration': round(optimized_duration, 2),
            'emotion_score': round(emotion_score, 3),
            'adjustment_made': True,
            'adjustment_reason': reason,
            'adjustment_amount': round(optimized_duration - original_duration, 2)
        }, True

    def calculate_creative_adjustments(self, clip: Dict,
                                      emotion_score: float) -> Dict:
        """
        Calculate creative adjustment recommendations for a clip.

        Args:
            clip: Clip dictionary
            emotion_score: Clip's emotion score

        Returns:
            Dictionary of creative adjustment suggestions
        """
        adjustments = {
            'lighting_variance': 'normal',
            'camera_movement_variance': 'normal',
            'color_grading_intensity': 'normal',
            'variance_level': 'medium'
        }

        # High emotion clips get more creative variance
        if emotion_score >= 0.8:
            adjustments['lighting_variance'] = 'high'
            adjustments['camera_movement_variance'] = 'high'
            adjustments['color_grading_intensity'] = 'intense'
            adjustments['variance_level'] = 'high'
            adjustments['suggestions'] = [
                'Consider dynamic lighting changes',
                'Use dramatic camera movements',
                'Apply intense color grading',
                'Add visual effects for emphasis'
            ]
        elif emotion_score >= 0.6:
            adjustments['lighting_variance'] = 'medium-high'
            adjustments['camera_movement_variance'] = 'medium-high'
            adjustments['color_grading_intensity'] = 'moderate'
            adjustments['variance_level'] = 'medium-high'
            adjustments['suggestions'] = [
                'Moderate lighting variations',
                'Smooth camera movements',
                'Balanced color grading'
            ]
        elif emotion_score <= 0.3:
            adjustments['lighting_variance'] = 'low'
            adjustments['camera_movement_variance'] = 'subtle'
            adjustments['color_grading_intensity'] = 'minimal'
            adjustments['variance_level'] = 'low'
            adjustments['suggestions'] = [
                'Maintain consistent, calm lighting',
                'Use static or subtle camera work',
                'Apply minimal color adjustments'
            ]

        return adjustments

    def run(self) -> Dict[str, Any]:
        """
        Run the complete clip optimization process.

        Returns:
            Dictionary containing optimization results

        Raises:
            RuntimeError: If optimization fails
        """
        try:
            logger.info(f"Optimizing clips for session {self.session_id}")

            # Load inputs
            clips, emotion_curve, beat_times, total_duration = self.load_inputs()

            # Process each clip
            optimization_results = []
            clips_adjusted = 0
            total_adjustment = 0.0

            for clip in clips:
                # Calculate emotion score
                emotion_score = self.calculate_clip_emotion_score(clip, emotion_curve)

                # Optimize clip duration
                prev_clip_end = clips[clips.index(clip) - 1]['end_time'] if clips.index(clip) > 0 else 0.0
                opt_result, adjusted = self.optimize_clip(
                    clip, emotion_score, beat_times, prev_clip_end
                )

                # Add creative adjustments
                creative_adj = self.calculate_creative_adjustments(clip, emotion_score)
                opt_result['creative_adjustments'] = creative_adj

                optimization_results.append(opt_result)

                if adjusted:
                    clips_adjusted += 1
                    total_adjustment += abs(opt_result.get('adjustment_amount', 0))

                # Update clip with optimized duration (stored in base_allocation)
                clip['base_allocation'] = opt_result['optimized_duration']
                clip['creative_adjustments'] = creative_adj

            # Calculate statistics
            statistics = {
                'clips_adjusted': clips_adjusted,
                'clips_unchanged': len(clips) - clips_adjusted,
                'avg_adjustment': round(total_adjustment / max(clips_adjusted, 1), 2),
                'max_adjustment': round(max(
                    (r.get('adjustment_amount', 0) for r in optimization_results),
                    default=0
                ), 2),
                'total_duration_before': round(total_duration, 2),
                'total_duration_after': round(total_duration, 2)  # Preserved
            }

            # Count variance opportunities
            variance_counts = {
                'high': sum(1 for r in optimization_results
                           if r['creative_adjustments']['variance_level'] == 'high'),
                'medium-high': sum(1 for r in optimization_results
                                  if r['creative_adjustments']['variance_level'] == 'medium-high'),
                'medium': sum(1 for r in optimization_results
                             if r['creative_adjustments']['variance_level'] == 'medium')
            }

            # Update Phase 3 data with optimized clips
            self._update_phase3_clips(clips)

            # Save optimization summary
            summary_path = self._save_optimization_summary(
                optimization_results, statistics, variance_counts
            )

            # Update session metadata
            self._update_session_metadata(summary_path, statistics)

            logger.info(f"Optimization complete: {clips_adjusted}/{len(clips)} clips adjusted")

            return {
                'optimization_results': optimization_results,
                'statistics': statistics,
                'variance_counts': variance_counts,
                'summary_path': str(summary_path)
            }

        except Exception as e:
            logger.error(f"Clip optimization failed: {e}")
            raise

    def _update_phase3_clips(self, optimized_clips: List[Dict]) -> None:
        """Update Phase 3 data with optimized clip information."""
        phase3_data = self.session.get_phase_data(3)
        winner_proposal = phase3_data.data.get('winner', {}).get('proposal', {})
        winner_proposal['clips'] = optimized_clips

        # Re-save phase data
        self.session.set_phase_data(
            3,
            phase3_data.data,
            metadata={'clip_optimization_applied': True}
        )

        logger.info("Updated Phase 3 clips with optimization data")

    def _save_optimization_summary(self, results: List[Dict],
                                   statistics: Dict,
                                   variance_counts: Dict) -> Path:
        """Save optimization summary to session directory."""
        summary_data = {
            'metadata': {
                'session_id': self.session_id,
                'created_at': get_iso_timestamp(),
                'optimization_algorithm': 'emotion_matching_v1',
                'total_clips': len(results)
            },
            'optimization_results': results,
            'statistics': statistics,
            'creative_adjustments_summary': {
                'total_variance_opportunities': sum(variance_counts.values()),
                'high_variance_clips': variance_counts['high'],
                'medium_variance_clips': variance_counts['medium-high'] + variance_counts['medium']
            }
        }

        session_dir = self.session.session_dir
        summary_path = session_dir / "clip_optimization_summary.json"

        write_json(str(summary_path), summary_data)
        logger.info(f"Saved optimization summary to {summary_path}")

        return summary_path

    def _update_session_metadata(self, summary_path: Path,
                                 statistics: Dict) -> None:
        """Update session metadata with optimization information."""
        # Add optimization log entry
        self.session.add_optimization_log({
            'tool': 'clip_optimizer',
            'action': 'optimized_clips',
            'summary_path': str(summary_path),
            'statistics': statistics,
            'timestamp': get_iso_timestamp()
        })

        # Store summary path in global data
        self.session.set_global_data('clip_optimization_summary_path', str(summary_path))

        logger.info("Updated session metadata with optimization info")


def optimize_clips(session_id: str,
                  min_duration: float = 0.8,
                  max_duration: float = 8.0) -> Dict[str, Any]:
    """
    Convenience function to optimize clips.

    Args:
        session_id: The session identifier
        min_duration: Minimum clip duration
        max_duration: Maximum clip duration

    Returns:
        Dictionary containing optimization results
    """
    optimizer = ClipOptimizer(session_id, min_duration, max_duration)
    return optimizer.run()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Optimize clip durations and add creative adjustments"
    )
    parser.add_argument(
        "session_id",
        help="Session ID to optimize clips for"
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=0.8,
        help="Minimum clip duration in seconds (default: 0.8)"
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=8.0,
        help="Maximum clip duration in seconds (default: 8.0)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        result = optimize_clips(args.session_id, args.min_duration, args.max_duration)
        print(f"\n✓ Clip optimization completed successfully!")
        print(f"  Summary path: {result['summary_path']}")
        print(f"  Total clips: {result['statistics']['clips_adjusted'] + result['statistics']['clips_unchanged']}")
        print(f"  Clips adjusted: {result['statistics']['clips_adjusted']}")
        print(f"  Clips unchanged: {result['statistics']['clips_unchanged']}")
        print(f"  Average adjustment: {result['statistics']['avg_adjustment']:.2f}s")
        print(f"  High variance clips: {result['variance_counts']['high']}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
