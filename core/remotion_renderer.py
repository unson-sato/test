"""
Remotion Renderer for MV Orchestra v3.0

Renders final music video using Remotion with generated effects code.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .utils import get_iso_timestamp

logger = logging.getLogger(__name__)


class RemotionRenderError(Exception):
    """Raised when Remotion rendering fails"""

    pass


@dataclass
class RenderConfig:
    """Configuration for Remotion rendering"""

    composition_id: str = "MVOrchestra"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    duration_in_frames: Optional[int] = None  # Auto-calculate from video
    output_format: str = "mp4"
    codec: str = "h264"
    audio_codec: str = "aac"
    audio_bitrate: str = "320k"
    video_bitrate: str = "8M"
    crf: int = 18  # Quality (lower = better, 18-23 is good)


@dataclass
class RenderResult:
    """Result of Remotion rendering"""

    success: bool
    output_path: Optional[Path] = None
    duration: float = 0.0
    render_time: float = 0.0
    file_size: int = 0  # bytes
    error: Optional[str] = None
    logs: str = ""
    timestamp: str = field(default_factory=get_iso_timestamp)


class RemotionRenderer:
    """
    Renders final music video using Remotion.

    Sets up Remotion project, integrates effects code and video sequence,
    and renders the final output.
    """

    def __init__(self, remotion_project_dir: Optional[Path] = None, mock_mode: bool = True):
        """
        Initialize Remotion Renderer.

        Args:
            remotion_project_dir: Path to Remotion project directory
            mock_mode: If True, simulate rendering without actual Remotion calls
        """
        self.remotion_project_dir = remotion_project_dir
        self.mock_mode = mock_mode

        if not mock_mode and remotion_project_dir:
            # Verify Remotion project exists
            package_json = remotion_project_dir / "package.json"
            if not package_json.exists():
                logger.warning(
                    f"No package.json found in {remotion_project_dir}. Falling back to mock mode."
                )
                self.mock_mode = True

        logger.info(f"RemotionRenderer initialized: mock_mode={self.mock_mode}")

    async def setup_project(
        self,
        project_dir: Path,
        video_sequence_path: Path,
        effects_code_path: Path,
        audio_path: Path,
        config: RenderConfig,
    ) -> bool:
        """
        Set up Remotion project with video, effects, and audio.

        Args:
            project_dir: Remotion project directory
            video_sequence_path: Path to merged video sequence
            effects_code_path: Path to effects code (TSX)
            audio_path: Path to audio file
            config: Render configuration

        Returns:
            True if setup successful, False otherwise
        """
        logger.info("Setting up Remotion project...")

        if self.mock_mode:
            logger.info("MOCK: Remotion project setup (skipped)")
            return True

        try:
            # Create project structure
            src_dir = project_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Copy effects code
            effects_dest = src_dir / "Effects.tsx"
            if effects_code_path.exists():
                import shutil

                shutil.copy(effects_code_path, effects_dest)
                logger.info(f"  ✓ Effects code copied to {effects_dest}")
            else:
                logger.error(f"  ✗ Effects code not found: {effects_code_path}")
                return False

            # Create Composition.tsx
            composition_code = self._generate_composition_code(
                video_sequence_path, audio_path, config
            )

            composition_file = src_dir / "Composition.tsx"
            with open(composition_file, "w") as f:
                f.write(composition_code)
            logger.info(f"  ✓ Composition created at {composition_file}")

            # Create Root.tsx
            root_code = self._generate_root_code(config)
            root_file = src_dir / "Root.tsx"
            with open(root_file, "w") as f:
                f.write(root_code)
            logger.info(f"  ✓ Root component created at {root_file}")

            # Copy assets
            public_dir = project_dir / "public"
            public_dir.mkdir(exist_ok=True)

            video_dest = public_dir / "sequence.mp4"
            audio_dest = public_dir / "audio.mp3"

            if video_sequence_path.exists():
                import shutil

                shutil.copy(video_sequence_path, video_dest)
                logger.info(f"  ✓ Video sequence copied to {video_dest}")

            if audio_path.exists():
                import shutil

                shutil.copy(audio_path, audio_dest)
                logger.info(f"  ✓ Audio copied to {audio_dest}")

            logger.info("✓ Remotion project setup complete")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Remotion project: {e}")
            return False

    async def render(
        self, project_dir: Path, output_path: Path, config: RenderConfig
    ) -> RenderResult:
        """
        Render final video using Remotion.

        Args:
            project_dir: Remotion project directory
            output_path: Output video path
            config: Render configuration

        Returns:
            RenderResult
        """
        logger.info("Starting Remotion render...")

        if self.mock_mode:
            return self._mock_render(output_path, config)

        import time

        start_time = time.time()

        try:
            # Build Remotion CLI command
            cmd = [
                "npx",
                "remotion",
                "render",
                config.composition_id,
                str(output_path),
                "--codec",
                config.codec,
                "--crf",
                str(config.crf),
                "--audio-codec",
                config.audio_codec,
                "--audio-bitrate",
                config.audio_bitrate,
                "--video-bitrate",
                config.video_bitrate,
            ]

            if config.duration_in_frames:
                cmd.extend(["--frames", str(config.duration_in_frames)])

            logger.info(f"Running: {' '.join(cmd)}")

            # Run Remotion render
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(project_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            # Collect output
            output_lines = []
            while True:
                if process.stdout is None:
                    break
                line = await process.stdout.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                output_lines.append(line_str)

                # Log progress
                if "Rendered" in line_str or "frame" in line_str.lower():
                    logger.info(f"  {line_str}")

            await process.wait()

            render_time = time.time() - start_time
            logs = "\n".join(output_lines)

            if process.returncode != 0:
                logger.error(f"Remotion render failed (exit code {process.returncode})")
                return RenderResult(
                    success=False,
                    error=f"Render failed with exit code {process.returncode}",
                    logs=logs,
                    render_time=render_time,
                )

            # Verify output exists
            if not output_path.exists():
                return RenderResult(
                    success=False,
                    error="Output file not created",
                    logs=logs,
                    render_time=render_time,
                )

            # Get file info
            file_size = output_path.stat().st_size
            duration = await self._get_video_duration(output_path)

            logger.info(f"✓ Render complete: {output_path}")
            logger.info(f"  Duration: {duration:.1f}s")
            logger.info(f"  File size: {file_size / 1024 / 1024:.1f} MB")
            logger.info(f"  Render time: {render_time:.1f}s")

            return RenderResult(
                success=True,
                output_path=output_path,
                duration=duration,
                render_time=render_time,
                file_size=file_size,
                logs=logs,
            )

        except Exception as e:
            render_time = time.time() - start_time
            logger.error(f"Render failed: {e}")
            return RenderResult(success=False, error=str(e), render_time=render_time)

    def _generate_composition_code(
        self, video_path: Path, audio_path: Path, config: RenderConfig
    ) -> str:
        """Generate Composition.tsx code"""
        return """import React from 'react';
import {{ AbsoluteFill, Video, Audio, useVideoConfig, useCurrentFrame }} from 'remotion';
import * as Effects from './Effects';

export const MVOrchestraComposition: React.FC = () => {{
  const {{ fps, durationInFrames }} = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      {{/* Video sequence */}}
      <Video
        src="/sequence.mp4"
        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
      />

      {{/* Audio */}}
      <Audio src="/audio.mp3" />

      {{/* Effects overlay - apply effects from Phase 8 here */}}
      {{/* Example: <Effects.FadeIn>...</Effects.FadeIn> */}}
    </AbsoluteFill>
  );
}};
"""

    def _generate_root_code(self, config: RenderConfig) -> str:
        """Generate Root.tsx code"""
        return f"""import {{ Composition }} from 'remotion';
import {{ MVOrchestraComposition }} from './Composition';

export const RemotionRoot: React.FC = () => {{
  return (
    <>
      <Composition
        id="{config.composition_id}"
        component={{MVOrchestraComposition}}
        durationInFrames={{{config.duration_in_frames or 'Math.floor(fps * 60)'}}}
        fps={{{config.fps}}}
        width={{{config.width}}}
        height={{{config.height}}}
      />
    </>
  );
}};
"""

    async def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()

            if process.returncode == 0:
                return float(stdout.decode().strip())
        except Exception:
            pass

        return 0.0

    def _mock_render(self, output_path: Path, config: RenderConfig) -> RenderResult:
        """Mock render operation"""
        import time

        logger.info("MOCK: Rendering final video...")
        time.sleep(1)  # Simulate render time

        # Create empty output file for mock
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()

        mock_duration = 180.0  # 3 minutes
        mock_size = 50 * 1024 * 1024  # 50 MB

        logger.info(f"MOCK: Render complete - {output_path}")

        return RenderResult(
            success=True,
            output_path=output_path,
            duration=mock_duration,
            render_time=1.0,
            file_size=mock_size,
            logs="MOCK render logs",
        )
