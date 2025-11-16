"""
Core components for MV Orchestra v3.0

This module contains all core components for the music video orchestration system.
"""

# Shared state and utilities
from .shared_state import SharedState, PhaseState, PhaseAttempt
from .utils import (
    get_project_root,
    get_session_dir,
    ensure_dir,
    read_json,
    write_json,
    get_iso_timestamp,
)

# Orchestrator components (Phase 0-4)
from .orchestrator_agent import OrchestratorAgent
from .agent_executor import AgentExecutor, AgentResult, PHASE_1_4_DIRECTORS
from .evaluation_agent import EvaluationAgent, SelectionResult
from .feedback_loop_manager import FeedbackLoopManager, IterationResult, FeedbackLoopResult
from .pipeline_state import PipelineState

# Phase 5-9 components
from .mcp_selector import MCPSelector
from .mcp_clip_generator import MCPClipGenerator, VideoClip, GenerationResult
from .clip_evaluator import CLIPEvaluator, EvaluationResult, TechnicalQuality
from .video_editor import VideoEditor, TrimSpec, MergeSpec, EditResult
from .effects_generator import EffectsGenerator, EffectsCode, EffectsEvaluation
from .remotion_renderer import RemotionRenderer, RenderConfig, RenderResult

__all__ = [
    # State and utilities
    "SharedState",
    "PhaseState",
    "PhaseAttempt",
    "get_project_root",
    "get_session_dir",
    "ensure_dir",
    "read_json",
    "write_json",
    "get_iso_timestamp",
    # Orchestrator components (Phase 0-4)
    "OrchestratorAgent",
    "AgentExecutor",
    "AgentResult",
    "PHASE_1_4_DIRECTORS",
    "EvaluationAgent",
    "SelectionResult",
    "FeedbackLoopManager",
    "IterationResult",
    "FeedbackLoopResult",
    "PipelineState",
    # Phase 5 - MCP Clip Generation
    "MCPSelector",
    "MCPClipGenerator",
    "VideoClip",
    "GenerationResult",
    # Phase 6 - CLIP Evaluation
    "CLIPEvaluator",
    "EvaluationResult",
    "TechnicalQuality",
    # Phase 7 - Video Editing
    "VideoEditor",
    "TrimSpec",
    "MergeSpec",
    "EditResult",
    # Phase 8 - Effects Generation
    "EffectsGenerator",
    "EffectsCode",
    "EffectsEvaluation",
    # Phase 9 - Remotion Rendering
    "RemotionRenderer",
    "RenderConfig",
    "RenderResult",
]
