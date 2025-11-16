"""
Agent Executor for MV Orchestra v3.0

Executes director agents in parallel using subprocess + Claude CLI.
Supports 5 director types for Phase 1-4 design phases.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import get_project_root


logger = logging.getLogger(__name__)


# Director types for Phase 1-4
PHASE_1_4_DIRECTORS = [
    "corporate",
    "freelancer",
    "veteran",
    "award_winner",
    "newcomer"
]


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

    Supports:
    - Parallel execution of multiple directors
    - Phase 1-4 design phases (5 directors)
    - Phase 8 effects generation (3 agents)
    """

    def __init__(self, claude_cli: str = "claude", max_parallel: int = 5):
        """
        Initialize Agent Executor.

        Args:
            claude_cli: Path to Claude CLI executable
            max_parallel: Maximum parallel agent executions
        """
        self.claude_cli = claude_cli
        self.max_parallel = max_parallel
        logger.info(f"AgentExecutor initialized: claude_cli={claude_cli}, max_parallel={max_parallel}")

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

    async def run_all_directors_parallel(
        self,
        phase_num: int,
        context: Dict[str, Any],
        output_dir: Path,
        directors: Optional[List[str]] = None
    ) -> List[AgentResult]:
        """
        Run all directors in parallel for a phase.

        Args:
            phase_num: Phase number (1-4)
            context: Context data to pass to agents
            output_dir: Output directory for agent results
            directors: List of director types (if None, uses PHASE_1_4_DIRECTORS)

        Returns:
            List of AgentResult
        """
        if directors is None:
            directors = PHASE_1_4_DIRECTORS

        logger.info(f"Running {len(directors)} directors in parallel for Phase {phase_num}...")

        # Create tasks for all directors
        tasks = []
        for director_type in directors:
            task = self._run_director_with_timing(
                director_type,
                phase_num,
                context,
                output_dir
            )
            tasks.append(task)

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        agent_results = []
        for i, result in enumerate(results):
            director_type = directors[i]

            if isinstance(result, Exception):
                logger.error(f"  ✗ {director_type}: {result}")
                agent_results.append(AgentResult(
                    director_type=director_type,
                    success=False,
                    output={},
                    error=str(result)
                ))
            elif isinstance(result, AgentResult):
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} {director_type}: {result.execution_time:.1f}s")
                agent_results.append(result)

        # Summary
        successful = sum(1 for r in agent_results if r.success)
        logger.info(f"Parallel execution complete: {successful}/{len(directors)} successful")

        return agent_results

    async def _run_director_with_timing(
        self,
        director_type: str,
        phase_num: int,
        context: Dict[str, Any],
        output_dir: Path
    ) -> AgentResult:
        """
        Run a director with execution time tracking.

        Args:
            director_type: Type of director
            phase_num: Phase number
            context: Context data
            output_dir: Output directory

        Returns:
            AgentResult with timing
        """
        start_time = time.time()

        try:
            output = await self.run_director_async(
                director_type=director_type,
                phase_num=phase_num,
                context=context,
                output_dir=output_dir
            )

            execution_time = time.time() - start_time

            # Check if output contains error
            if "error" in output:
                return AgentResult(
                    director_type=director_type,
                    success=False,
                    output=output,
                    error=output["error"],
                    execution_time=execution_time
                )

            return AgentResult(
                director_type=director_type,
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResult(
                director_type=director_type,
                success=False,
                output={},
                error=str(e),
                execution_time=execution_time
            )
