"""
Phase 5 Runner: Clip Generation via MCP

Generates video clips using MCP servers.
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
    read_json,
    get_iso_timestamp,
    get_project_root
)
from core.mcp_clip_generator import MCPClipGenerator, GenerationResult


logger = logging.getLogger(__name__)


def run_phase5(
    session_id: str,
    mcp_config: Optional[Dict[str, Any]] = None,
    mock_mode: bool = True
) -> Dict[str, Any]:
    """
    Run Phase 5: Generate clips via MCP.

    Args:
        session_id: Session identifier
        mcp_config: Optional MCP configuration (from orchestrator_config.json)
        mock_mode: If True, simulate generation without actual MCP calls

    Returns:
        Phase 5 results dictionary
    """
    logger.info("=" * 70)
    logger.info("PHASE 5: Clip Generation (MCP)")
    logger.info("=" * 70)

    # Load session
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Get Phase 3 clip division
    phase3_data = session.get_phase_data(3)
    if not phase3_data or "winner" not in phase3_data:
        raise ValueError("Phase 3 data not found. Run Phase 3 first.")

    clip_designs = phase3_data["winner"].get("clips", [])
    if not clip_designs:
        raise ValueError("No clips found in Phase 3 winner")

    logger.info(f"Found {len(clip_designs)} clips to generate")

    # Get Phase 4 generation strategies (if available)
    strategies = None
    phase4_data = session.get_phase_data(4)
    if phase4_data and "winner" in phase4_data:
        strategies = phase4_data["winner"].get("clip_strategies", [])
        logger.info(f"Using {len(strategies)} strategies from Phase 4")

    # Load MCP config
    if mcp_config is None:
        config_file = get_project_root() / "config" / "orchestrator_config.json"
        if config_file.exists():
            full_config = read_json(config_file)
            mcp_config = full_config.get("mcp", {})
        else:
            logger.warning("No MCP config found, using defaults")
            mcp_config = {
                "servers": {
                    "default": {
                        "endpoint": "http://localhost:8000",
                        "capabilities": ["general"],
                        "priority": 10
                    }
                },
                "max_parallel_generations": 3
            }

    # Create output directory
    output_dir = session_dir / "phase5" / "generated_clips"
    ensure_dir(output_dir)

    # Initialize MCP Clip Generator
    max_parallel = mcp_config.get("max_parallel_generations", 3)
    max_retries = mcp_config.get("max_retries_per_clip", 2)

    generator = MCPClipGenerator(
        mcp_config=mcp_config,
        output_dir=output_dir,
        max_parallel=max_parallel,
        max_retries=max_retries
    )

    # Generate clips
    if mock_mode:
        logger.info("Running in MOCK MODE - simulating clip generation")
        results = _mock_generate_clips(clip_designs, output_dir)
    else:
        logger.info("Generating clips via MCP...")
        results = asyncio.run(
            generator.generate_all_clips(clip_designs, strategies)
        )

    # Process results
    successful_clips = [r for r in results if r.success]
    failed_clips = [r for r in results if not r.success]

    logger.info(f"\nGeneration Summary:")
    logger.info(f"  Total clips: {len(results)}")
    logger.info(f"  Successful: {len(successful_clips)}")
    logger.info(f"  Failed: {len(failed_clips)}")

    if failed_clips:
        logger.warning(f"  Failed clip IDs: {[r.clip_id for r in failed_clips]}")

    # Save results
    phase5_results = {
        "total_clips": len(results),
        "successful_clips": len(successful_clips),
        "failed_clips": len(failed_clips),
        "clips": [
            {
                "clip_id": r.clip_id,
                "success": r.success,
                "path": str(r.clip.path) if r.clip else None,
                "mcp_server": r.clip.mcp_server if r.clip else None,
                "generation_time": r.total_time,
                "attempts": r.attempts,
                "error": r.error
            }
            for r in results
        ],
        "output_directory": str(output_dir),
        "timestamp": get_iso_timestamp()
    }

    # Save to session
    result_file = session_dir / "phase5" / "results.json"
    ensure_dir(result_file.parent)
    write_json(result_file, phase5_results)

    # Update session state
    session.mark_phase_started(5)
    session.mark_phase_completed(5, phase5_results)

    logger.info(f"\n✓ Phase 5 completed")
    logger.info(f"  Results saved to: {result_file}")

    return phase5_results


def _mock_generate_clips(
    clip_designs: list,
    output_dir: Path
) -> list:
    """
    Mock clip generation for testing.

    Creates placeholder GenerationResult objects without actual video files.
    """
    import time

    results = []

    for i, clip_design in enumerate(clip_designs):
        clip_id = clip_design.get("clip_id", i)

        # Simulate generation time
        time.sleep(0.1)

        # Create mock result
        from core.mcp_clip_generator import GenerationResult, VideoClip

        mock_path = output_dir / f"clip_{clip_id:03d}_mock.mp4"

        clip = VideoClip(
            clip_id=clip_id,
            path=mock_path,
            design=clip_design,
            mcp_server="mock_server",
            generation_time=0.1,
            metadata={"mock": True}
        )

        result = GenerationResult(
            clip_id=clip_id,
            success=True,
            clip=clip,
            attempts=1,
            total_time=0.1
        )

        results.append(result)

        if (i + 1) % 10 == 0:
            logger.info(f"  Mock generation progress: {i + 1}/{len(clip_designs)}")

    return results
