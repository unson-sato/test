#!/usr/bin/env python3
"""
Complete Integration Example

Combines all approaches:
1. File-based workflow orchestration
2. Declarative YAML configuration
3. Message history persistence (Hybrid: SQLite + JSONL)
4. Error handling and retry mechanisms
5. Non-interactive mode support (claude -p)

This is a production-ready template for Claude Code automation
"""

import yaml
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import our strategies
# (In a real project, these would be separate modules)
from message_history_persistence import HybridMessageStore, Message
from error_handling_retry import (
    exponential_backoff_retry,
    CircuitBreaker,
    ErrorRecoveryStrategy,
    GracefulDegradation
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Complete Workflow Engine
# ============================================================================

class ProductionWorkflowEngine:
    """
    Production-ready workflow engine with all features
    """

    def __init__(
        self,
        workspace_dir: str = "./production_workspace",
        enable_persistence: bool = True,
        enable_circuit_breaker: bool = True
    ):
        """
        Initialize workflow engine

        Args:
            workspace_dir: Directory for workflow artifacts
            enable_persistence: Enable message history persistence
            enable_circuit_breaker: Enable circuit breaker protection
        """
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.prompts_dir = self.workspace / "prompts"
        self.responses_dir = self.workspace / "responses"
        self.state_dir = self.workspace / "state"
        self.logs_dir = self.workspace / "logs"

        for d in [self.prompts_dir, self.responses_dir, self.state_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Message store (Hybrid: SQLite + JSONL)
        self.message_store = None
        if enable_persistence:
            self.message_store = HybridMessageStore(
                db_path=str(self.state_dir / "messages.db"),
                jsonl_path=str(self.state_dir / "messages.jsonl")
            )

        # Circuit breaker for API calls
        self.circuit_breaker = None
        if enable_circuit_breaker:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60.0
            )

        # Execution context
        self.context = {}
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def load_workflow_from_yaml(self, yaml_file: str) -> Dict[str, Any]:
        """
        Load workflow definition from YAML

        Args:
            yaml_file: Path to YAML file

        Returns:
            Workflow configuration
        """
        with open(yaml_file, 'r') as f:
            workflow = yaml.safe_load(f)

        logger.info(f"Loaded workflow: {workflow.get('name', 'Unnamed')}")
        return workflow

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render prompt template with context

        Args:
            template: Template string
            context: Context variables

        Returns:
            Rendered template
        """
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing variable in template: {e}")

    @exponential_backoff_retry(max_retries=4, base_delay=2.0)
    def execute_claude(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Execute Claude Code with exponential backoff retry

        Args:
            prompt_file: Path to prompt file

        Returns:
            Response data
        """
        logger.info(f"Executing: claude -p {prompt_file}")

        # Run claude command
        result = subprocess.run(
            ["claude", "-p", str(prompt_file), "--dangerously-skip-permission"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            raise Exception(f"Claude execution failed: {result.stderr}")

        # Parse output
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback: treat as text
            response = {
                "type": "text",
                "content": result.stdout,
                "raw": True
            }

        return response

    def execute_claude_with_protection(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Execute Claude with circuit breaker and fallback

        Args:
            prompt_file: Path to prompt file

        Returns:
            Response data
        """
        def primary():
            if self.circuit_breaker:
                return self.circuit_breaker.call(self.execute_claude, prompt_file)
            else:
                return self.execute_claude(prompt_file)

        def fallback():
            logger.warning("Using fallback response due to repeated failures")
            return {
                "type": "fallback",
                "content": "Service temporarily unavailable. Using cached/default response.",
                "fallback": True
            }

        return GracefulDegradation.with_fallback(primary, fallback)

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tool execution result
        """
        # TODO: Implement actual tool execution
        logger.info(f"Executing tool: {tool_name} with {tool_input}")

        # Placeholder
        return f"[Tool {tool_name} executed successfully]"

    def save_message(self, role: str, content: Any, iteration: int):
        """Save message to history"""
        if self.message_store:
            message = Message(
                session_id=self.session_id,
                iteration=iteration,
                role=role,
                content=content,
                timestamp=datetime.now().isoformat()
            )
            self.message_store.save_message(message)

    def execute_workflow_step(
        self,
        step: Dict[str, Any],
        step_index: int,
        iteration: int
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step

        Args:
            step: Step configuration
            step_index: Step index
            iteration: Current iteration

        Returns:
            Execution result
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Step {step_index + 1}: {step['name']}")
        logger.info(f"{'='*70}")

        # Render prompt
        prompt = self.render_template(step['prompt'], self.context)

        # Save prompt
        prompt_file = self.prompts_dir / f"step{step_index:02d}_iter{iteration:03d}.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        logger.info(f"Prompt file: {prompt_file}")

        # Save user message
        self.save_message("user", prompt, iteration)

        # Execute Claude
        try:
            response = self.execute_claude_with_protection(prompt_file)

            # Save response
            response_file = self.responses_dir / f"step{step_index:02d}_iter{iteration:03d}.json"
            with open(response_file, 'w') as f:
                json.dump(response, f, indent=2)

            logger.info(f"Response file: {response_file}")

            # Save assistant message
            self.save_message("assistant", response, iteration)

            # Extract tool uses
            tool_uses = self._extract_tool_uses(response)

            # Execute tools
            tool_results = []
            for tool_use in tool_uses:
                result = self.execute_tool(
                    tool_use['name'],
                    tool_use.get('input', {})
                )
                tool_results.append({
                    "tool_use_id": tool_use.get('id'),
                    "tool_name": tool_use['name'],
                    "result": result
                })

            # Store output variable
            if step.get('output_variable'):
                self.context[step['output_variable']] = response

            return {
                "status": "success",
                "response": response,
                "tool_results": tool_results
            }

        except Exception as e:
            error_context = ErrorRecoveryStrategy.classify_error(e)
            logger.error(f"Step failed: {error_context.message}")

            if not step.get('continue_on_error', False):
                raise

            return {
                "status": "error",
                "error": str(e),
                "error_context": asdict(error_context)
            }

    def _extract_tool_uses(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool uses from response"""
        # TODO: Implement based on actual response format
        tool_uses = []

        if isinstance(response.get('content'), list):
            for block in response['content']:
                if isinstance(block, dict) and block.get('type') == 'tool_use':
                    tool_uses.append(block)

        return tool_uses

    def execute_workflow(self, yaml_file: str, max_iterations: int = 10):
        """
        Execute complete workflow from YAML file

        Args:
            yaml_file: Path to workflow YAML file
            max_iterations: Maximum iterations per step
        """
        # Load workflow
        workflow = self.load_workflow_from_yaml(yaml_file)

        logger.info(f"\n{'#'*70}")
        logger.info(f"WORKFLOW: {workflow['name']}")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"{'#'*70}")

        # Initialize context with workflow variables
        self.context = workflow.get('variables', {}).copy()
        self.context['session_id'] = self.session_id
        self.context['start_time'] = datetime.now().isoformat()

        # Execute steps
        iteration = 0
        for step_index, step in enumerate(workflow.get('steps', [])):
            iteration += 1

            try:
                result = self.execute_workflow_step(step, step_index, iteration)

                if result['status'] == 'error' and not step.get('continue_on_error'):
                    logger.error("Workflow stopped due to error")
                    break

            except Exception as e:
                logger.error(f"Unhandled exception: {e}")
                raise

        # Save final stats
        if self.message_store:
            stats = self.message_store.get_session_stats(self.session_id)
            logger.info(f"\nSession Stats: {stats}")

        logger.info(f"\n{'#'*70}")
        logger.info("WORKFLOW COMPLETED")
        logger.info(f"{'#'*70}")

    def close(self):
        """Cleanup resources"""
        if self.message_store:
            self.message_store.close()


# ============================================================================
# Example Workflow YAML
# ============================================================================

def create_example_workflow_yaml():
    """Create an example production workflow"""
    workflow_yaml = """
name: Production Data Pipeline
description: Complete data processing workflow with error handling
version: 2.0

variables:
  input_file: "data/input.csv"
  output_dir: "data/output"
  notification_email: "user@example.com"

steps:
  - name: Initialize Environment
    prompt: |
      Initialize the data processing environment.

      Input file: {input_file}
      Output directory: {output_dir}

      Please verify that:
      1. Input file exists and is readable
      2. Output directory can be created
      3. Required Python packages are available

      Return a JSON summary of the environment status.
    tools:
      - read_file
      - execute_python
    max_iterations: 3
    output_variable: env_status
    continue_on_error: false

  - name: Process Data
    prompt: |
      Process the data file.

      Environment status:
      {env_status}

      Tasks:
      1. Load data from {input_file}
      2. Clean and validate data
      3. Apply transformations
      4. Calculate statistics

      Save intermediate results to {output_dir}/processed.csv
    tools:
      - read_file
      - write_file
      - execute_python
    max_iterations: 5
    output_variable: processing_result
    continue_on_error: false

  - name: Generate Report
    prompt: |
      Generate analysis report.

      Processing result:
      {processing_result}

      Create a markdown report with:
      - Data summary
      - Key findings
      - Visualizations
      - Recommendations

      Save to {output_dir}/report.md
    tools:
      - write_file
      - execute_python
    max_iterations: 3
    output_variable: report_path
    continue_on_error: true

  - name: Send Notification
    prompt: |
      Send completion notification.

      Report: {report_path}
      Email: {notification_email}

      Generate a notification email (simulate sending).
    tools:
      - write_file
    max_iterations: 2
    continue_on_error: true
"""

    output_file = Path("./examples/production_workflow.yaml")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(workflow_yaml)

    logger.info(f"Example workflow created: {output_file}")
    return output_file


# ============================================================================
# Main
# ============================================================================

def main():
    """Main execution"""

    logger.info("\n" + "="*70)
    logger.info("PRODUCTION WORKFLOW ENGINE - COMPLETE EXAMPLE")
    logger.info("="*70)

    # Create example workflow
    workflow_file = create_example_workflow_yaml()

    # Create engine
    engine = ProductionWorkflowEngine(
        workspace_dir="./production_workspace",
        enable_persistence=True,
        enable_circuit_breaker=True
    )

    try:
        # Execute workflow
        engine.execute_workflow(str(workflow_file), max_iterations=10)

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

    finally:
        # Cleanup
        engine.close()


if __name__ == "__main__":
    main()
