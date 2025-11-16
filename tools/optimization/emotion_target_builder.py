"""
Emotion Target Builder for MV Orchestra v2.8

This tool builds a target emotion curve from Phase 2 section directions.
The curve is used by Phase 3 clip optimizer to match emotional intensity
with clip duration and creative parameters.

Usage:
    # Standalone
    python emotion_target_builder.py <session_id>

    # As module
    from tools.optimization.emotion_target_builder import build_target_curve
    build_target_curve(session_id)
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from core import SharedState
from core.utils import read_json, write_json, get_iso_timestamp
from .emotion_utils import (
    get_section_emotion_value,
    interpolate_smooth,
    get_emotion_statistics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmotionTargetBuilder:
    """
    Builds target emotion curve from Phase 2 section directions.

    The curve provides emotion intensity values at regular intervals
    throughout the song timeline, enabling optimization algorithms
    to match visual intensity with emotional content.
    """

    def __init__(self, session_id: str, sampling_rate: float = 0.5):
        """
        Initialize Emotion Target Builder.

        Args:
            session_id: The session identifier
            sampling_rate: Time interval between samples in seconds (default: 0.5s)
        """
        self.session_id = session_id
        self.sampling_rate = sampling_rate
        self.session = SharedState.load_session(session_id)

    def load_phase2_data(self) -> Dict[str, Any]:
        """
        Load Phase 2 section directions from session.

        Returns:
            Phase 2 winner proposal containing sections

        Raises:
            RuntimeError: If Phase 2 is not completed or data is missing
        """
        phase2_data = self.session.get_phase_data(2)

        if phase2_data.status != "completed":
            raise RuntimeError(
                f"Phase 2 must be completed before building emotion curve. "
                f"Current status: {phase2_data.status}"
            )

        winner_proposal = phase2_data.data.get('winner', {}).get('proposal', {})
        if not winner_proposal:
            raise RuntimeError("Phase 2 winner proposal not found")

        sections = winner_proposal.get('sections', [])
        if not sections:
            raise RuntimeError("No sections found in Phase 2 winner proposal")

        logger.info(f"Loaded {len(sections)} sections from Phase 2")
        return winner_proposal

    def build_section_metadata(self, sections: List[Dict]) -> List[Dict]:
        """
        Build section metadata with emotion values.

        Args:
            sections: List of section dictionaries from Phase 2

        Returns:
            List of section metadata with emotion values
        """
        section_metadata = []

        for section in sections:
            emotion_value, emotion_label = get_section_emotion_value(section)

            section_meta = {
                'section_name': section.get('section_name', 'unknown'),
                'start_time': section.get('start_time', 0.0),
                'end_time': section.get('end_time', 0.0),
                'target_emotion': round(emotion_value, 2),
                'emotion_label': emotion_label
            }

            section_metadata.append(section_meta)

        # Sort by start time
        section_metadata.sort(key=lambda s: s['start_time'])

        return section_metadata

    def build_emotion_curve(self, section_metadata: List[Dict],
                           total_duration: float) -> List[Dict]:
        """
        Build emotion curve by interpolating between section emotions.

        Args:
            section_metadata: List of sections with emotion values
            total_duration: Total duration of the song in seconds

        Returns:
            List of curve points with time and emotion values
        """
        curve = []
        current_time = 0.0

        # Generate samples at regular intervals
        while current_time <= total_duration:
            # Find which section this time belongs to
            current_section = self._find_section_at_time(
                current_time, section_metadata
            )

            if current_section is None:
                # Before first section or after last section
                if current_time < section_metadata[0]['start_time']:
                    # Use first section's emotion
                    emotion = section_metadata[0]['target_emotion']
                    label = section_metadata[0]['emotion_label']
                    section_name = section_metadata[0]['section_name']
                else:
                    # Use last section's emotion
                    emotion = section_metadata[-1]['target_emotion']
                    label = section_metadata[-1]['emotion_label']
                    section_name = section_metadata[-1]['section_name']
            else:
                # Within a section
                section_name = current_section['section_name']
                label = current_section['emotion_label']

                # Check if we're near a transition to next section
                next_section = self._find_next_section(
                    current_section, section_metadata
                )

                if next_section and self._is_in_transition_zone(
                    current_time, current_section, next_section
                ):
                    # Interpolate between current and next section
                    emotion = self._interpolate_between_sections(
                        current_time, current_section, next_section
                    )
                    label = f"{current_section['emotion_label']}→{next_section['emotion_label']}"
                else:
                    # Use current section's emotion
                    emotion = current_section['target_emotion']

            # Add curve point
            curve.append({
                'time': round(current_time, 2),
                'emotion': round(emotion, 3),
                'source_section': section_name,
                'label': label
            })

            current_time += self.sampling_rate

        logger.info(f"Built emotion curve with {len(curve)} samples")
        return curve

    def _find_section_at_time(self, time: float,
                              sections: List[Dict]) -> Dict | None:
        """Find the section that contains the given time."""
        for section in sections:
            if section['start_time'] <= time < section['end_time']:
                return section
        return None

    def _find_next_section(self, current_section: Dict,
                          sections: List[Dict]) -> Dict | None:
        """Find the section that comes after the current one."""
        current_idx = sections.index(current_section)
        if current_idx < len(sections) - 1:
            return sections[current_idx + 1]
        return None

    def _is_in_transition_zone(self, time: float,
                               current_section: Dict,
                               next_section: Dict,
                               transition_duration: float = 2.0) -> bool:
        """
        Check if time is in transition zone between sections.

        Args:
            time: Current time
            current_section: Current section
            next_section: Next section
            transition_duration: Duration of transition zone in seconds

        Returns:
            True if in transition zone
        """
        # Transition zone is the last N seconds of current section
        section_end = current_section['end_time']
        transition_start = max(
            current_section['start_time'],
            section_end - transition_duration
        )

        return transition_start <= time < section_end

    def _interpolate_between_sections(self, time: float,
                                      current_section: Dict,
                                      next_section: Dict) -> float:
        """Smoothly interpolate emotion between two sections."""
        return interpolate_smooth(
            current_section['target_emotion'],
            next_section['target_emotion'],
            current_section['end_time'] - 2.0,  # Start interpolating 2s before section end
            current_section['end_time'],
            time
        )

    def save_emotion_curve(self, curve: List[Dict],
                          section_metadata: List[Dict],
                          total_duration: float) -> Path:
        """
        Save emotion curve to session directory.

        Args:
            curve: Emotion curve data
            section_metadata: Section metadata
            total_duration: Total duration

        Returns:
            Path to saved file
        """
        # Calculate statistics
        statistics = get_emotion_statistics(curve)

        # Prepare output data
        output_data = {
            'metadata': {
                'session_id': self.session_id,
                'created_at': get_iso_timestamp(),
                'source_phase': 2,
                'sampling_rate': self.sampling_rate,
                'total_duration': total_duration
            },
            'curve': curve,
            'sections': section_metadata,
            'statistics': statistics
        }

        # Save to session directory
        session_dir = self.session.session_dir
        output_path = session_dir / "target_emotion_curve.json"

        write_json(str(output_path), output_data)
        logger.info(f"Saved emotion curve to {output_path}")

        return output_path

    def update_session_metadata(self, curve_path: Path,
                               statistics: Dict) -> None:
        """
        Update session metadata with emotion curve information.

        Args:
            curve_path: Path to saved curve file
            statistics: Curve statistics
        """
        # Add optimization log entry
        self.session.add_optimization_log({
            'tool': 'emotion_target_builder',
            'action': 'built_emotion_curve',
            'curve_path': str(curve_path),
            'statistics': statistics,
            'timestamp': get_iso_timestamp()
        })

        # Store curve path in global data
        self.session.set_global_data('target_emotion_curve_path', str(curve_path))

        logger.info("Updated session metadata with emotion curve info")

    def run(self) -> Dict[str, Any]:
        """
        Run the complete emotion target building process.

        Returns:
            Dictionary containing curve data and metadata

        Raises:
            RuntimeError: If building fails
        """
        try:
            logger.info(f"Building emotion target curve for session {self.session_id}")

            # Load Phase 2 data
            phase2_proposal = self.load_phase2_data()
            sections = phase2_proposal.get('sections', [])

            # Calculate total duration from sections
            total_duration = max(s.get('end_time', 0.0) for s in sections)

            # Build section metadata with emotion values
            section_metadata = self.build_section_metadata(sections)

            # Build emotion curve
            curve = self.build_emotion_curve(section_metadata, total_duration)

            # Save curve
            curve_path = self.save_emotion_curve(
                curve, section_metadata, total_duration
            )

            # Calculate statistics
            statistics = get_emotion_statistics(curve)

            # Update session metadata
            self.update_session_metadata(curve_path, statistics)

            logger.info("Emotion target curve built successfully")

            return {
                'curve': curve,
                'sections': section_metadata,
                'statistics': statistics,
                'curve_path': str(curve_path)
            }

        except Exception as e:
            logger.error(f"Failed to build emotion curve: {e}")
            raise


def build_target_curve(session_id: str, sampling_rate: float = 0.5) -> Dict[str, Any]:
    """
    Convenience function to build target emotion curve.

    Args:
        session_id: The session identifier
        sampling_rate: Time interval between samples in seconds

    Returns:
        Dictionary containing curve data and metadata
    """
    builder = EmotionTargetBuilder(session_id, sampling_rate)
    return builder.run()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build target emotion curve from Phase 2 section directions"
    )
    parser.add_argument(
        "session_id",
        help="Session ID to build emotion curve for"
    )
    parser.add_argument(
        "--sampling-rate",
        type=float,
        default=0.5,
        help="Sampling rate in seconds (default: 0.5)"
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
        result = build_target_curve(args.session_id, args.sampling_rate)
        print(f"\n✓ Emotion curve built successfully!")
        print(f"  Curve path: {result['curve_path']}")
        print(f"  Total samples: {result['statistics']['total_samples']}")
        print(f"  Emotion range: {result['statistics']['min_emotion']:.2f} - {result['statistics']['max_emotion']:.2f}")
        print(f"  Average emotion: {result['statistics']['avg_emotion']:.2f}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
