"""
MCP Clip Generator for MV Orchestra v3.0

Generates video clips via Kamuicode MCP servers.
Handles:
- MCP server communication
- Parallel clip generation
- Retry logic
- Result storage
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mcp_selector import MCPSelector, MCPServer
from .utils import ensure_dir, get_iso_timestamp

logger = logging.getLogger(__name__)


class MCPGenerationError(Exception):
    """Raised when MCP generation fails"""

    pass


@dataclass
class VideoClip:
    """Generated video clip"""

    clip_id: int
    path: Path
    design: Dict[str, Any]
    mcp_server: str
    generation_time: float
    timestamp: str = field(default_factory=get_iso_timestamp)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Result of clip generation"""

    clip_id: int
    success: bool
    clip: Optional[VideoClip] = None
    error: Optional[str] = None
    attempts: int = 1
    total_time: float = 0.0


class MCPClipGenerator:
    """
    Generates video clips using MCP servers.

    Features:
    - Dynamic MCP selection
    - Parallel generation (with concurrency limit)
    - Automatic retry on failure
    - Progress tracking
    """

    def __init__(
        self,
        mcp_config: Dict[str, Any],
        output_dir: Path,
        max_parallel: int = 3,
        max_retries: int = 2,
    ):
        """
        Initialize MCP Clip Generator.

        Args:
            mcp_config: MCP configuration
            output_dir: Output directory for generated clips
            max_parallel: Maximum parallel generations
            max_retries: Maximum retry attempts per clip
        """
        self.mcp_selector = MCPSelector(mcp_config)
        self.output_dir = Path(output_dir)
        self.max_parallel = max_parallel
        self.max_retries = max_retries

        ensure_dir(self.output_dir)

        logger.info(
            f"MCPClipGenerator initialized: output={self.output_dir}, max_parallel={max_parallel}"
        )

    async def generate_clip(
        self,
        clip_design: Dict[str, Any],
        clip_index: int,
        strategy: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """
        Generate a single clip.

        Args:
            clip_design: Clip design from Phase 3
            clip_index: Clip index
            strategy: Optional generation strategy from Phase 4

        Returns:
            GenerationResult
        """
        start_time = time.time()
        clip_id = clip_design.get("clip_id", clip_index)

        logger.info(f"Generating clip {clip_id}...")

        # Determine MCP server
        preferred_mcp = None
        if strategy:
            preferred_mcp = strategy.get("mcp_server")

        mcp_server = self.mcp_selector.select_best_mcp(clip_design, preferred_mcp)

        # Attempt generation with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Clip {clip_id}: Attempt {attempt}/{self.max_retries} using {mcp_server.name}"
                )

                # Generate clip via MCP
                clip_path = await self._call_mcp_server(
                    mcp_server=mcp_server,
                    clip_design=clip_design,
                    strategy=strategy,
                    clip_id=clip_id,
                )

                # Create VideoClip object
                generation_time = time.time() - start_time
                clip = VideoClip(
                    clip_id=clip_id,
                    path=clip_path,
                    design=clip_design,
                    mcp_server=mcp_server.name,
                    generation_time=generation_time,
                    metadata={
                        "attempt": attempt,
                        "duration": clip_design.get("duration", 0),
                        "aspect_ratio": clip_design.get("technical_specs", {}).get(
                            "aspect_ratio", "16:9"
                        ),
                    },
                )

                logger.info(f"✓ Clip {clip_id} generated successfully ({generation_time:.1f}s)")

                return GenerationResult(
                    clip_id=clip_id,
                    success=True,
                    clip=clip,
                    attempts=attempt,
                    total_time=generation_time,
                )

            except Exception as e:
                logger.warning(f"Clip {clip_id} attempt {attempt} failed: {e}")

                if attempt < self.max_retries:
                    # Try fallback MCP if available
                    if strategy and "fallback_strategy" in strategy:
                        fallback_mcp_name = strategy["fallback_strategy"].get("alternative_mcp")
                        if fallback_mcp_name:
                            fallback_server = self.mcp_selector.get_server_by_name(
                                fallback_mcp_name
                            )
                            if fallback_server:
                                logger.info(f"Trying fallback MCP: {fallback_mcp_name}")
                                mcp_server = fallback_server
                else:
                    # Final attempt failed
                    total_time = time.time() - start_time
                    logger.error(
                        f"✗ Clip {clip_id} generation failed after {self.max_retries} attempts"
                    )

                    return GenerationResult(
                        clip_id=clip_id,
                        success=False,
                        error=str(e),
                        attempts=attempt,
                        total_time=total_time,
                    )

        # Should not reach here
        return GenerationResult(
            clip_id=clip_id,
            success=False,
            error="Max retries exceeded",
            attempts=self.max_retries,
            total_time=time.time() - start_time,
        )

    async def _call_mcp_server(
        self,
        mcp_server: MCPServer,
        clip_design: Dict[str, Any],
        strategy: Optional[Dict[str, Any]],
        clip_id: int,
    ) -> Path:
        """
        Call MCP server to generate clip.

        This is a placeholder for actual MCP integration.
        In production, this would call the actual MCP API.

        Args:
            mcp_server: MCP server to use
            clip_design: Clip design
            strategy: Generation strategy
            clip_id: Clip ID

        Returns:
            Path to generated video file
        """
        # Extract generation parameters
        prompt = clip_design.get("ai_generation_prompt", clip_design.get("visual_description", ""))
        duration = clip_design.get("duration", 4.0)

        logger.debug(
            f"MCP Request to {mcp_server.endpoint}: prompt='{prompt[:50]}...', duration={duration}"
        )

        # TODO: Actual MCP API call
        # For now, simulate generation with delay
        await asyncio.sleep(2.0)  # Simulate generation time

        # In production, this would be the actual generated file from MCP
        # For now, create a placeholder path
        output_filename = f"clip_{clip_id:03d}_{mcp_server.name}.mp4"
        output_path = self.output_dir / output_filename

        # TODO: Save actual generated video from MCP response
        # For now, just create the path (file doesn't exist yet)

        logger.debug(f"Generated clip saved to: {output_path}")

        return output_path

    async def generate_all_clips(
        self, clip_designs: List[Dict[str, Any]], strategies: Optional[List[Dict[str, Any]]] = None
    ) -> List[GenerationResult]:
        """
        Generate all clips with parallel execution limit.

        Args:
            clip_designs: List of clip designs from Phase 3
            strategies: Optional list of generation strategies from Phase 4

        Returns:
            List of GenerationResult
        """
        total_clips = len(clip_designs)
        logger.info(
            f"Starting generation of {total_clips} clips (max {self.max_parallel} parallel)..."
        )

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def generate_with_limit(clip_design, index):
            async with semaphore:
                strategy = strategies[index] if strategies and index < len(strategies) else None
                return await self.generate_clip(clip_design, index, strategy)

        # Create tasks for all clips
        tasks = [generate_with_limit(design, i) for i, design in enumerate(clip_designs)]

        # Execute with progress tracking
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            logger.info(f"  Progress: {len(results)}/{total_clips} clips completed")

        # Sort results by clip_id
        results.sort(key=lambda r: r.clip_id)

        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = total_clips - successful

        logger.info(
            f"\nGeneration complete: {successful}/{total_clips} successful, {failed} failed"
        )

        return results

    def get_successful_clips(self, results: List[GenerationResult]) -> List[VideoClip]:
        """Extract successful clips from results"""
        return [r.clip for r in results if r.success and r.clip]

    async def generate_all_clips_sync(
        self, clip_designs: List[Dict[str, Any]], strategies: Optional[List[Dict[str, Any]]] = None
    ) -> List[GenerationResult]:
        """
        Synchronous wrapper for generate_all_clips.

        Use this when calling from synchronous code.
        """
        return await self.generate_all_clips(clip_designs, strategies)
