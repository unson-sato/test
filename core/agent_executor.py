"""
Agent Executor for MV Orchestra v3.0

Executes director agents in parallel using subprocess + Claude CLI.
(Minimal implementation for Phase 8)
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import get_project_root


logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from agent execution"""
    director_type: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0


class AgentExecutor:
    """
    Executes director agents using subprocess + Claude CLI.

    This is a minimal implementation for Phase 8.
    Full implementation with parallel execution will be in Phase 0-4.
    """

    def __init__(self, claude_cli: str = "claude"):
        """
        Initialize Agent Executor.

        Args:
            claude_cli: Path to Claude CLI executable
        """
        self.claude_cli = claude_cli
        logger.info(f"AgentExecutor initialized: claude_cli={claude_cli}")

    async def run_director_async(
        self,
        director_type: str,
        phase_num: int,
        context: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Run a single director agent asynchronously.

        Args:
            director_type: Type of director (e.g., "minimalist", "creative", "balanced")
            phase_num: Phase number (8 for effects)
            context: Context data to pass to agent
            output_dir: Output directory for agent results

        Returns:
            Agent output as dictionary
        """
        # Get prompt file
        project_root = get_project_root()
        prompt_file = project_root / ".claude" / "prompts" / f"phase{phase_num}_{director_type}.md"

        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            return {
                "error": f"Prompt file not found: {prompt_file}"
            }

        # Create context file
        output_dir.mkdir(parents=True, exist_ok=True)
        context_file = output_dir / f"{director_type}_context.json"

        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)

        # Build Claude CLI command
        # claude -p prompt.md --dangerous-skip-permission --output-format json < context.json
        cmd = [
            self.claude_cli,
            "-p", str(prompt_file),
            "--dangerous-skip-permission",
            "--output-format", "json"
        ]

        logger.debug(f"Running {director_type} agent: {' '.join(cmd)}")

        try:
            # Run agent
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Pass context as stdin
            context_json = json.dumps(context).encode()
            stdout, stderr = await process.communicate(input=context_json)

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"{director_type} agent failed: {error_msg}")
                return {
                    "error": error_msg
                }

            # Parse output
            output_str = stdout.decode()
            try:
                output = json.loads(output_str)
                return output
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {director_type} output: {e}")
                # Try to extract JSON from output
                import re
                json_match = re.search(r'\{.*\}', output_str, re.DOTALL)
                if json_match:
                    try:
                        output = json.loads(json_match.group())
                        return output
                    except:
                        pass

                return {
                    "error": f"Invalid JSON output: {output_str[:200]}..."
                }

        except Exception as e:
            logger.error(f"Failed to run {director_type} agent: {e}")
            return {
                "error": str(e)
            }
