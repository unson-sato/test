#!/usr/bin/env python3
"""
Declarative Workflow System

Define workflows in YAML, execute them with Claude Code in non-interactive mode
"""

import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """
    A single step in the workflow
    """
    name: str
    prompt_template: str
    tools: List[str]
    max_iterations: int = 5
    continue_on_error: bool = False
    output_variable: Optional[str] = None
    condition: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """
    Complete workflow definition
    """
    name: str
    description: str
    version: str
    variables: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)


class DeclarativeWorkflowEngine:
    """
    Execute workflows defined in YAML
    """

    def __init__(self, workspace_dir: str = "./workflow_workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Execution context (variables available to templates)
        self.context = {}

    def load_workflow(self, yaml_file: str) -> WorkflowDefinition:
        """
        Load workflow from YAML file

        Args:
            yaml_file: Path to YAML workflow definition

        Returns:
            WorkflowDefinition object
        """
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                name=step_data['name'],
                prompt_template=step_data['prompt'],
                tools=step_data.get('tools', []),
                max_iterations=step_data.get('max_iterations', 5),
                continue_on_error=step_data.get('continue_on_error', False),
                output_variable=step_data.get('output_variable'),
                condition=step_data.get('condition')
            )
            steps.append(step)

        return WorkflowDefinition(
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0'),
            variables=data.get('variables', {}),
            steps=steps
        )

    def evaluate_condition(self, condition: Optional[str]) -> bool:
        """
        Evaluate step condition

        Args:
            condition: Condition expression (e.g., "previous_step_success")

        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return True

        # Simple condition evaluation
        # TODO: Implement proper expression parser
        try:
            return eval(condition, {"__builtins__": {}}, self.context)
        except Exception:
            return False

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render prompt template with context variables

        Args:
            template: Template string with {variable} placeholders
            context: Context dictionary

        Returns:
            Rendered template
        """
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing variable in context: {e}")

    def execute_step(self, step: WorkflowStep, step_index: int) -> Dict[str, Any]:
        """
        Execute a single workflow step

        Args:
            step: WorkflowStep to execute
            step_index: Index of this step

        Returns:
            Execution result
        """
        print(f"\n{'='*70}")
        print(f"Step {step_index + 1}: {step.name}")
        print(f"{'='*70}")

        # Check condition
        if not self.evaluate_condition(step.condition):
            print(f"Condition not met, skipping step: {step.condition}")
            return {"status": "skipped", "reason": "condition_not_met"}

        # Render prompt
        try:
            prompt = self.render_template(step.prompt_template, self.context)
        except ValueError as e:
            print(f"Error rendering template: {e}")
            if not step.continue_on_error:
                raise
            return {"status": "error", "error": str(e)}

        # Save prompt
        prompt_file = self.workspace / f"step_{step_index:02d}_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        print(f"Prompt: {prompt_file}")
        print(f"Tools available: {', '.join(step.tools)}")

        # Execute with Claude (placeholder - would call actual claude command)
        result = self._execute_claude(prompt_file, step)

        # Save result
        result_file = self.workspace / f"step_{step_index:02d}_result.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"Result: {result_file}")

        # Store output variable
        if step.output_variable:
            self.context[step.output_variable] = result.get('output', '')
            print(f"Stored result in: {step.output_variable}")

        return result

    def _execute_claude(self, prompt_file: Path, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute Claude with the given prompt

        Args:
            prompt_file: Path to prompt file
            step: WorkflowStep configuration

        Returns:
            Execution result
        """
        # Placeholder implementation
        # In reality, would run: claude -p prompt_file --dangerously-skip-permission

        print(f"[Simulated] Running: claude -p {prompt_file}")

        # Simulated response
        return {
            "status": "success",
            "output": f"Result from {step.name}",
            "iterations": 2
        }

    def execute_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """
        Execute complete workflow

        Args:
            workflow: WorkflowDefinition to execute

        Returns:
            Execution summary
        """
        print(f"\n{'#'*70}")
        print(f"Workflow: {workflow.name}")
        print(f"Description: {workflow.description}")
        print(f"Version: {workflow.version}")
        print(f"{'#'*70}")

        # Initialize context with workflow variables
        self.context = workflow.variables.copy()
        self.context['workflow_name'] = workflow.name
        self.context['start_time'] = datetime.now().isoformat()

        results = []
        for i, step in enumerate(workflow.steps):
            try:
                result = self.execute_step(step, i)
                results.append({
                    "step": step.name,
                    "result": result
                })

                # Stop on error if not continuing
                if result.get('status') == 'error' and not step.continue_on_error:
                    print(f"\nWorkflow stopped due to error in step: {step.name}")
                    break

            except Exception as e:
                print(f"\nException in step {step.name}: {e}")
                if not step.continue_on_error:
                    raise

        # Summary
        summary = {
            "workflow": workflow.name,
            "total_steps": len(workflow.steps),
            "executed_steps": len(results),
            "results": results,
            "final_context": self.context
        }

        return summary


def create_example_workflow():
    """Create an example workflow YAML file"""
    workflow_yaml = """
name: Data Analysis Pipeline
description: Analyze data files and generate reports
version: 1.0

variables:
  data_file: "data.csv"
  output_dir: "./reports"

steps:
  - name: Read and Validate Data
    prompt: |
      Please read the data file: {data_file}

      Validate that it contains the following columns:
      - timestamp
      - value
      - category

      If valid, provide a summary of the data shape and basic statistics.
    tools:
      - read_file
      - execute_python
    max_iterations: 3
    output_variable: data_summary

  - name: Analyze Trends
    prompt: |
      Based on the data summary:
      {data_summary}

      Analyze trends in the data and identify:
      - Overall patterns
      - Anomalies
      - Key insights

      Use Python for calculations if needed.
    tools:
      - execute_python
    max_iterations: 5
    output_variable: trends_analysis
    condition: "data_summary is not None"

  - name: Generate Report
    prompt: |
      Generate a markdown report based on:

      Data Summary:
      {data_summary}

      Trends Analysis:
      {trends_analysis}

      Save the report to: {output_dir}/analysis_report.md
    tools:
      - write_file
    max_iterations: 2
    continue_on_error: false

  - name: Create Visualizations
    prompt: |
      Create visualization plots for the analysis.

      Generate:
      - Time series plot
      - Category distribution
      - Anomaly highlights

      Save plots to: {output_dir}/
    tools:
      - execute_python
      - write_file
    max_iterations: 5
    continue_on_error: true
"""

    output_file = Path("./examples/workflow_example.yaml")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(workflow_yaml)

    print(f"Example workflow created: {output_file}")
    return output_file


def main():
    """Example usage"""

    # Create example workflow
    workflow_file = create_example_workflow()

    # Create engine
    engine = DeclarativeWorkflowEngine(workspace_dir="./workflow_workspace")

    # Load workflow
    workflow = engine.load_workflow(str(workflow_file))

    # Execute
    summary = engine.execute_workflow(workflow)

    # Print summary
    print(f"\n{'#'*70}")
    print("WORKFLOW EXECUTION SUMMARY")
    print(f"{'#'*70}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
