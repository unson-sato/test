"""
Phase 9 Runner: Final Rendering with Remotion

Renders the final music video using Remotion with effects.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core import (
    SharedState,
    get_session_dir,
    ensure_dir,
    write_json,
    get_iso_timestamp,
)
from core.remotion_renderer import RemotionRenderer, RenderConfig


logger = logging.getLogger(__name__)


def run_phase9(
    session_id: str,
    remotion_project_dir: Optional[Path] = None,
    output_filename: str = "final_output.mp4",
    render_config: Optional[RenderConfig] = None,
    mock_mode: bool = True,
) -> Dict[str, Any]:
    """
    Run Phase 9: Final rendering with Remotion.

    Args:
        session_id: Session identifier
        remotion_project_dir: Path to Remotion project (if None, creates in session dir)
        output_filename: Name of output video file
        render_config: Render configuration (if None, uses defaults)
        mock_mode: If True, simulate rendering without actual Remotion calls

    Returns:
        Phase 9 results dictionary
    """
    logger.info("=" * 70)
    logger.info("PHASE 9: Final Rendering (Remotion)")
    logger.info("=" * 70)

    # Load session
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Get Phase 0 audio analysis
    phase0_data = session.get_phase_data(0)
    if not phase0_data or "audio_file" not in phase0_data:
        raise ValueError("Phase 0 data not found. Need original audio file.")

    audio_path = Path(phase0_data["audio_file"])
    if not audio_path.exists():
        raise ValueError(f"Audio file not found: {audio_path}")

    # Get Phase 7 video sequence
    phase7_data = session.get_phase_data(7)
    if not phase7_data or "final_sequence" not in phase7_data:
        raise ValueError("Phase 7 data not found. Run Phase 7 first.")

    sequence_info = phase7_data["final_sequence"]
    sequence_path = Path(sequence_info["path"]) if sequence_info["path"] else None

    if not sequence_path or not sequence_path.exists():
        raise ValueError(f"Video sequence not found: {sequence_path}")

    # Get Phase 8 effects code
    phase8_data = session.get_phase_data(8)
    if not phase8_data or "final_code_file" not in phase8_data:
        raise ValueError("Phase 8 data not found. Run Phase 8 first.")

    effects_code_path = Path(phase8_data["final_code_file"])
    if not effects_code_path.exists():
        raise ValueError(f"Effects code not found: {effects_code_path}")

    logger.info("\nInput files:")
    logger.info(f"  Audio: {audio_path}")
    logger.info(f"  Video sequence: {sequence_path} ({sequence_info['duration']:.1f}s)")
    logger.info(f"  Effects code: {effects_code_path}")

    # Create output directory
    output_dir = session_dir / "phase9"
    ensure_dir(output_dir)

    # Set up Remotion project directory
    if remotion_project_dir is None:
        remotion_project_dir = output_dir / "remotion_project"

    ensure_dir(remotion_project_dir)

    # Create render config if not provided
    if render_config is None:
        # Calculate duration in frames
        duration_seconds = sequence_info.get("duration", 180.0)
        fps = 30
        duration_frames = int(duration_seconds * fps)

        render_config = RenderConfig(
            composition_id="MVOrchestra",
            width=1920,
            height=1080,
            fps=fps,
            duration_in_frames=duration_frames,
            crf=18,
            video_bitrate="8M",
        )

    logger.info("\nRender configuration:")
    logger.info(f"  Resolution: {render_config.width}x{render_config.height}")
    logger.info(f"  FPS: {render_config.fps}")
    logger.info(f"  Duration: {render_config.duration_in_frames} frames")
    logger.info(f"  Codec: {render_config.codec}")
    logger.info(f"  CRF: {render_config.crf}")

    # Initialize Remotion renderer
    renderer = RemotionRenderer(remotion_project_dir=remotion_project_dir, mock_mode=mock_mode)

    # Setup Remotion project
    logger.info("\nSetting up Remotion project at {}...".format(remotion_project_dir))

    setup_success = asyncio.run(
        renderer.setup_project(
            project_dir=remotion_project_dir,
            video_sequence_path=sequence_path,
            effects_code_path=effects_code_path,
            audio_path=audio_path,
            config=render_config,
        )
    )

    if not setup_success:
        raise RuntimeError("Failed to setup Remotion project")

    logger.info("✓ Remotion project setup complete")

    # Render final video
    output_path = output_dir / output_filename

    logger.info("\nRendering final video...")
    logger.info(f"  Output: {output_path}")

    render_result = asyncio.run(
        renderer.render(
            project_dir=remotion_project_dir, output_path=output_path, config=render_config
        )
    )

    if not render_result.success:
        logger.error(f"Rendering failed: {render_result.error}")
        raise RuntimeError(f"Rendering failed: {render_result.error}")

    # Log results
    logger.info("\n" + "=" * 70)
    logger.info("FINAL RENDER COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Output file: {render_result.output_path}")
    logger.info(f"Duration: {render_result.duration:.1f}s")
    logger.info(f"File size: {render_result.file_size / 1024 / 1024:.1f} MB")
    logger.info(f"Render time: {render_result.render_time:.1f}s")

    # Save results
    phase9_results = {
        "output_file": str(render_result.output_path),
        "duration": render_result.duration,
        "file_size_mb": render_result.file_size / 1024 / 1024,
        "render_time_seconds": render_result.render_time,
        "render_config": {
            "composition_id": render_config.composition_id,
            "width": render_config.width,
            "height": render_config.height,
            "fps": render_config.fps,
            "duration_frames": render_config.duration_in_frames,
            "codec": render_config.codec,
            "crf": render_config.crf,
            "video_bitrate": render_config.video_bitrate,
        },
        "input_files": {
            "audio": str(audio_path),
            "video_sequence": str(sequence_path),
            "effects_code": str(effects_code_path),
        },
        "remotion_project_dir": str(remotion_project_dir),
        "success": render_result.success,
        "timestamp": get_iso_timestamp(),
    }

    # Save results
    result_file = output_dir / "results.json"
    write_json(result_file, phase9_results)

    # Save render logs
    logs_file = output_dir / "render_logs.txt"
    with open(logs_file, "w") as f:
        f.write(render_result.logs)

    # Update session state
    session.mark_phase_started(9)
    session.mark_phase_completed(9, phase9_results)

    logger.info("\n✓ Phase 9 completed")
    logger.info(f"  Results saved to: {result_file}")
    logger.info(f"  Logs saved to: {logs_file}")

    logger.info("\n" + "=" * 70)
    logger.info("🎬 MUSIC VIDEO GENERATION COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"Final output: {render_result.output_path}")

    return phase9_results
