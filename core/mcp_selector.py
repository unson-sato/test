"""
MCP Selector for MV Orchestra v3.0

Dynamically selects the best MCP server for each clip based on:
- Clip visual characteristics
- Style requirements
- Motion intensity
- Server capabilities
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    """MCP Server configuration"""
    name: str
    endpoint: str
    capabilities: List[str]
    priority: int
    available: bool = True
    cost_per_clip: float = 1.0


@dataclass
class ClipRequirements:
    """Requirements extracted from clip design"""
    style: str
    motion_intensity: str
    visual_complexity: str
    aspect_ratio: str
    duration: float


class MCPSelector:
    """
    Selects optimal MCP server for clip generation.

    Selection logic:
    1. Filter servers by capability match
    2. Rank by priority and availability
    3. Return best match
    """

    def __init__(self, mcp_config: Dict[str, Any]):
        """
        Initialize MCP Selector.

        Args:
            mcp_config: MCP configuration from orchestrator_config.json
        """
        self.servers = self._load_servers(mcp_config)
        logger.info(f"MCPSelector initialized with {len(self.servers)} servers")

    def _load_servers(self, config: Dict[str, Any]) -> Dict[str, MCPServer]:
        """Load MCP servers from config"""
        servers = {}

        for name, server_config in config.get("servers", {}).items():
            servers[name] = MCPServer(
                name=name,
                endpoint=server_config.get("endpoint", ""),
                capabilities=server_config.get("capabilities", []),
                priority=server_config.get("priority", 10),
                cost_per_clip=server_config.get("cost_per_clip", 1.0)
            )

        return servers

    def select_best_mcp(
        self,
        clip_design: Dict[str, Any],
        preferred_mcp: Optional[str] = None
    ) -> MCPServer:
        """
        Select best MCP server for clip.

        Args:
            clip_design: Clip design from Phase 3
            preferred_mcp: Optional preferred MCP from Phase 4 strategy

        Returns:
            Selected MCPServer
        """
        # If preferred MCP specified in strategy, use it
        if preferred_mcp and preferred_mcp in self.servers:
            server = self.servers[preferred_mcp]
            if server.available:
                logger.debug(f"Using preferred MCP: {preferred_mcp}")
                return server

        # Extract clip requirements
        requirements = self._extract_requirements(clip_design)

        # Find matching servers
        candidates = self._find_matching_servers(requirements)

        if not candidates:
            logger.warning("No matching MCP found, using default")
            return self.servers.get("default", list(self.servers.values())[0])

        # Select best candidate
        best_server = self._rank_candidates(candidates, requirements)

        logger.debug(f"Selected MCP: {best_server.name} for clip")
        return best_server

    def _extract_requirements(self, clip_design: Dict[str, Any]) -> ClipRequirements:
        """Extract requirements from clip design"""
        # Extract from visual description and metadata
        visual_desc = clip_design.get("visual_description", "").lower()

        # Determine style
        style = "realistic"
        if "anime" in visual_desc or "illustration" in visual_desc:
            style = "anime"
        elif "abstract" in visual_desc or "surreal" in visual_desc:
            style = "experimental"
        elif "cinematic" in visual_desc:
            style = "cinematic"

        # Determine motion intensity
        camera_movement = clip_design.get("camera_movement", "").lower()
        motion_intensity = "medium"
        if "static" in camera_movement or "slow" in camera_movement:
            motion_intensity = "low"
        elif "fast" in camera_movement or "dynamic" in camera_movement:
            motion_intensity = "high"

        # Visual complexity
        visual_complexity = "medium"
        if len(visual_desc) > 200 or "complex" in visual_desc:
            visual_complexity = "high"
        elif len(visual_desc) < 100:
            visual_complexity = "low"

        return ClipRequirements(
            style=style,
            motion_intensity=motion_intensity,
            visual_complexity=visual_complexity,
            aspect_ratio=clip_design.get("technical_specs", {}).get("aspect_ratio", "16:9"),
            duration=clip_design.get("duration", 4.0)
        )

    def _find_matching_servers(self, requirements: ClipRequirements) -> List[MCPServer]:
        """Find servers matching requirements"""
        candidates = []

        for server in self.servers.values():
            if not server.available:
                continue

            # Check capability match
            if self._matches_capabilities(server, requirements):
                candidates.append(server)

        return candidates

    def _matches_capabilities(
        self,
        server: MCPServer,
        requirements: ClipRequirements
    ) -> bool:
        """Check if server capabilities match requirements"""
        # Check style match
        style_match = (
            requirements.style in server.capabilities or
            "general" in server.capabilities
        )

        # Check motion match
        motion_keywords = {
            "high": ["high_motion", "dynamic", "fast"],
            "medium": ["general"],
            "low": ["general", "static"]
        }

        motion_match = any(
            keyword in server.capabilities
            for keyword in motion_keywords.get(requirements.motion_intensity, ["general"])
        )

        return style_match or motion_match or "general" in server.capabilities

    def _rank_candidates(
        self,
        candidates: List[MCPServer],
        requirements: ClipRequirements
    ) -> MCPServer:
        """Rank candidates and return best"""
        # Sort by priority (lower number = higher priority)
        sorted_candidates = sorted(candidates, key=lambda s: s.priority)

        # Return highest priority available server
        return sorted_candidates[0]

    def get_server_by_name(self, name: str) -> Optional[MCPServer]:
        """Get server by name"""
        return self.servers.get(name)

    def mark_server_unavailable(self, name: str):
        """Mark server as unavailable (e.g., after failure)"""
        if name in self.servers:
            self.servers[name].available = False
            logger.warning(f"MCP server marked unavailable: {name}")

    def mark_server_available(self, name: str):
        """Mark server as available"""
        if name in self.servers:
            self.servers[name].available = True
            logger.info(f"MCP server marked available: {name}")
