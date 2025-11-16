"""
Video Editor for MV Orchestra v3.0

Trims and merges video clips based on clip designs.
Uses ffmpeg for video editing operations.
"""

import asyncio
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import get_iso_timestamp

logger = logging.getLogger(__name__)


class VideoEditError(Exception):
    """Raised when video editing fails"""
    pass


@dataclass
class TrimSpec:
    """Specification for trimming a clip"""
    clip_id: int
    input_path: Path
    output_path: Path
    start_time: float  # seconds
    duration: float  # seconds
    design: Dict[str, Any]


@dataclass
class MergeSpec:
    """Specification for merging clips"""
    clips: List[Path]
    output_path: Path
    transition_duration: float = 0.0  # seconds
    transition_type: str = "none"  # none, crossfade, fade


@dataclass
class EditResult:
    """Result of video editing operation"""
    success: bool
    output_path: Optional[Path] = None
    duration: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(default_factory=get_iso_timestamp)


class VideoEditor:
    """
    Edits video clips using ffmpeg.

    Supports:
    - Trimming clips to exact durations
    - Merging multiple clips
    - Adding transitions between clips
    """

    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
        mock_mode: bool = True
    ):
        """
        Initialize Video Editor.

        Args:
            ffmpeg_path: Path to ffmpeg executable
            ffprobe_path: Path to ffprobe executable
            mock_mode: If True, simulate video editing without actual ffmpeg calls
        """
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.mock_mode = mock_mode

        if not mock_mode:
            # Verify ffmpeg is available
            try:
                subprocess.run(
                    [ffmpeg_path, "-version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.warning(f"ffmpeg not available: {e}. Falling back to mock mode.")
                self.mock_mode = True

        logger.info(f"VideoEditor initialized: mock_mode={self.mock_mode}")

    async def trim_clip(self, spec: TrimSpec) -> EditResult:
        """
        Trim a clip to specified duration.

        Args:
            spec: Trim specification

        Returns:
            EditResult
        """
        logger.debug(f"Trimming clip {spec.clip_id}: {spec.duration}s from {spec.input_path}")

        if self.mock_mode:
            return self._mock_trim(spec)

        try:
            # Build ffmpeg command for trimming
            # ffmpeg -i input.mp4 -ss start_time -t duration -c copy output.mp4
            cmd = [
                self.ffmpeg_path,
                "-i", str(spec.input_path),
                "-ss", str(spec.start_time),
                "-t", str(spec.duration),
                "-c", "copy",  # Copy codec for fast trimming
                "-y",  # Overwrite output
                str(spec.output_path)
            ]

            # Run ffmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"ffmpeg trim failed: {error_msg}")
                return EditResult(
                    success=False,
                    error=f"ffmpeg trim failed: {error_msg}"
                )

            # Verify output exists
            if not spec.output_path.exists():
                return EditResult(
                    success=False,
                    error="Output file not created"
                )

            # Get actual duration
            actual_duration = await self._get_video_duration(spec.output_path)

            return EditResult(
                success=True,
                output_path=spec.output_path,
                duration=actual_duration
            )

        except Exception as e:
            logger.error(f"Trim failed: {e}")
            return EditResult(
                success=False,
                error=str(e)
            )

    async def merge_clips(self, spec: MergeSpec) -> EditResult:
        """
        Merge multiple clips into one.

        Args:
            spec: Merge specification

        Returns:
            EditResult
        """
        logger.debug(f"Merging {len(spec.clips)} clips to {spec.output_path}")

        if self.mock_mode:
            return self._mock_merge(spec)

        try:
            if spec.transition_type == "none":
                # Simple concatenation without transitions
                return await self._concat_clips(spec)
            else:
                # Merge with transitions (crossfade, fade, etc.)
                return await self._merge_with_transitions(spec)

        except Exception as e:
            logger.error(f"Merge failed: {e}")
            return EditResult(
                success=False,
                error=str(e)
            )

    async def _concat_clips(self, spec: MergeSpec) -> EditResult:
        """Concatenate clips without transitions using concat demuxer"""
        # Create concat file
        concat_file = spec.output_path.parent / f"{spec.output_path.stem}_concat.txt"

        with open(concat_file, 'w') as f:
            for clip_path in spec.clips:
                f.write(f"file '{clip_path.absolute()}'\n")

        # Build ffmpeg concat command
        # ffmpeg -f concat -safe 0 -i concat.txt -c copy output.mp4
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-y",
            str(spec.output_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Clean up concat file
        concat_file.unlink(missing_ok=True)

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"ffmpeg concat failed: {error_msg}")
            return EditResult(
                success=False,
                error=f"ffmpeg concat failed: {error_msg}"
            )

        if not spec.output_path.exists():
            return EditResult(
                success=False,
                error="Output file not created"
            )

        # Get total duration
        total_duration = await self._get_video_duration(spec.output_path)

        return EditResult(
            success=True,
            output_path=spec.output_path,
            duration=total_duration
        )

    async def _merge_with_transitions(self, spec: MergeSpec) -> EditResult:
        """Merge clips with transitions (crossfade, fade, etc.)"""
        # This is more complex and requires filter_complex
        # For now, implement simple crossfade between clips

        if len(spec.clips) < 2:
            # No transitions needed for single clip
            return await self._concat_clips(spec)

        transition_dur = spec.transition_duration

        # Build filter_complex for crossfade
        # Example for 2 clips: [0][1]xfade=transition=fade:duration=1:offset=5[out]
        filter_parts = []

        # TODO: Implement full crossfade logic for multiple clips
        # This is a simplified version for demonstration

        logger.warning("Transitions not fully implemented, falling back to concat")
        return await self._concat_clips(spec)

    async def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return 0.0

        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 0.0

    def _mock_trim(self, spec: TrimSpec) -> EditResult:
        """Mock trim operation"""
        logger.debug(f"MOCK: Trimming clip {spec.clip_id} to {spec.duration}s")
        return EditResult(
            success=True,
            output_path=spec.output_path,
            duration=spec.duration
        )

    def _mock_merge(self, spec: MergeSpec) -> EditResult:
        """Mock merge operation"""
        total_duration = sum(5.0 for _ in spec.clips)  # Assume 5s per clip
        logger.debug(f"MOCK: Merging {len(spec.clips)} clips, total duration: {total_duration}s")
        return EditResult(
            success=True,
            output_path=spec.output_path,
            duration=total_duration
        )

    async def trim_all_clips(
        self,
        trim_specs: List[TrimSpec],
        max_parallel: int = 3
    ) -> List[EditResult]:
        """
        Trim multiple clips in parallel.

        Args:
            trim_specs: List of trim specifications
            max_parallel: Maximum parallel trim operations

        Returns:
            List of EditResult
        """
        logger.info(f"Trimming {len(trim_specs)} clips (max {max_parallel} parallel)...")

        semaphore = asyncio.Semaphore(max_parallel)

        async def trim_with_limit(spec: TrimSpec) -> EditResult:
            async with semaphore:
                return await self.trim_clip(spec)

        tasks = [trim_with_limit(spec) for spec in trim_specs]

        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)

            if (i + 1) % 10 == 0:
                logger.info(f"  Trimmed {i + 1}/{len(trim_specs)} clips")

        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        logger.info(f"\nTrim complete: {successful}/{len(results)} successful")
        if failed > 0:
            logger.warning(f"  {failed} clips failed to trim")

        return results

    def create_trim_specs(
        self,
        clips: List[Dict[str, Any]],
        designs: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[TrimSpec]:
        """
        Create trim specifications from clip data and designs.

        Args:
            clips: List of clip data from Phase 6
            designs: List of clip designs from Phase 3
            output_dir: Output directory for trimmed clips

        Returns:
            List of TrimSpec
        """
        specs = []

        # Create design lookup
        designs_by_id = {d["clip_id"]: d for d in designs}

        for clip_data in clips:
            clip_id = clip_data["clip_id"]
            design = designs_by_id.get(clip_id)

            if not design:
                logger.warning(f"No design found for clip {clip_id}, skipping")
                continue

            # Get clip path
            clip_path = Path(clip_data["clip_path"])
            if not clip_path.exists() and "path" in clip_data:
                clip_path = Path(clip_data["path"])

            # Get duration from design
            duration = design.get("duration", 5.0)
            start_time = design.get("start_time", 0.0)

            # Create output path
            output_path = output_dir / f"clip_{clip_id:03d}_trimmed.mp4"

            spec = TrimSpec(
                clip_id=clip_id,
                input_path=clip_path,
                output_path=output_path,
                start_time=start_time,
                duration=duration,
                design=design
            )

            specs.append(spec)

        return specs
