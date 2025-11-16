# File-Based Non-Interactive Workflow Architecture

**Purpose**: Design a robust architecture for non-interactive Claude Code execution using file-based state management

**Target Use Case**: Script automation with `claude -p --dangerously-skip-permission`

---

## Core Concept

Instead of maintaining an in-memory conversation loop, use **files as the communication medium** between:
1. Orchestrator script
2. Claude Code process
3. Tool executors

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Script                       │
│                                                              │
│  while not done:                                            │
│    1. Generate prompt file                                  │
│    2. Run: claude -p prompt.txt > response.json            │
│    3. Parse response.json                                   │
│    4. Execute tools                                         │
│    5. Update state files                                    │
│    6. Generate next prompt                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
workspace/
├── state/
│   ├── session_id.json           # Current session state
│   ├── message_history.jsonl     # Line-delimited message log
│   └── tool_results.json         # Latest tool execution results
├── prompts/
│   ├── iteration_001.txt         # Generated prompts
│   ├── iteration_002.txt
│   └── ...
├── responses/
│   ├── iteration_001.json        # Claude responses
│   ├── iteration_002.json
│   └── ...
└── config/
    ├── workflow.yaml             # Workflow definition
    └── tools.yaml                # Tool definitions
```

---

## State Management

### session_id.json
```json
{
  "session_id": "sess_20251116_abc123",
  "created_at": "2025-11-16T12:00:00Z",
  "current_iteration": 5,
  "status": "running",
  "metadata": {
    "task": "Data analysis pipeline",
    "user": "unson-sato"
  }
}
```

### message_history.jsonl (JSON Lines format)
```jsonl
{"iteration": 1, "role": "user", "content": "Analyze data.csv", "timestamp": "2025-11-16T12:00:00Z"}
{"iteration": 1, "role": "assistant", "content": [...], "timestamp": "2025-11-16T12:00:05Z"}
{"iteration": 2, "role": "user", "content": "Tool results: ...", "timestamp": "2025-11-16T12:00:10Z"}
```

### tool_results.json
```json
{
  "iteration": 1,
  "results": [
    {
      "tool_use_id": "toolu_abc123",
      "tool_name": "read_file",
      "status": "success",
      "output": "...",
      "executed_at": "2025-11-16T12:00:08Z"
    }
  ]
}
```

---

## Prompt Generation Strategy

### Template-Based Approach

**Base Template** (`templates/base_prompt.txt`):
```
You are an AI assistant helping with: {task_description}

Current iteration: {iteration}
Previous iteration summary: {previous_summary}

{context}

{tool_results_section}

Please continue with the next step.
```

**Tool Results Section** (injected when tools were executed):
```
## Previous Tool Execution Results

Tool: {tool_name}
Status: {status}
Output:
{output}

---

Based on these results, please proceed.
```

---

## Implementation: Orchestrator Script

```python
#!/usr/bin/env python3
"""
File-based non-interactive workflow orchestrator
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class FileBasedOrchestrator:
    """
    Orchestrates non-interactive Claude Code execution using files
    """

    def __init__(self, workspace_dir: str, session_id: Optional[str] = None):
        self.workspace = Path(workspace_dir)
        self.session_id = session_id or self._generate_session_id()

        # Create directory structure
        self.state_dir = self.workspace / "state"
        self.prompts_dir = self.workspace / "prompts"
        self.responses_dir = self.workspace / "responses"
        self.config_dir = self.workspace / "config"

        for d in [self.state_dir, self.prompts_dir, self.responses_dir, self.config_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.state_file = self.state_dir / f"{self.session_id}.json"
        self.history_file = self.state_dir / "message_history.jsonl"
        self.tool_results_file = self.state_dir / "tool_results.json"

        # Initialize state
        self._init_state()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sess_{timestamp}"

    def _init_state(self):
        """Initialize session state"""
        if not self.state_file.exists():
            state = {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "current_iteration": 0,
                "status": "initialized",
                "metadata": {}
            }
            self._save_state(state)

    def _save_state(self, state: Dict[str, Any]):
        """Save session state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> Dict[str, Any]:
        """Load session state from file"""
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _append_to_history(self, role: str, content: Any, iteration: int):
        """Append message to history file (JSONL format)"""
        with open(self.history_file, 'a') as f:
            entry = {
                "iteration": iteration,
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            f.write(json.dumps(entry) + "\n")

    def generate_prompt(self, task: str, iteration: int,
                       tool_results: Optional[List[Dict]] = None) -> str:
        """
        Generate prompt for current iteration

        Args:
            task: Task description
            iteration: Current iteration number
            tool_results: Results from previous tool executions

        Returns:
            Generated prompt text
        """
        prompt = f"Task: {task}\n\n"
        prompt += f"Iteration: {iteration}\n\n"

        # Add tool results if available
        if tool_results:
            prompt += "## Previous Tool Execution Results\n\n"
            for result in tool_results:
                prompt += f"Tool: {result['tool_name']}\n"
                prompt += f"Status: {result['status']}\n"
                prompt += f"Output:\n{result['output']}\n"
                prompt += "-" * 60 + "\n\n"
            prompt += "Based on these results, please continue.\n\n"

        return prompt

    def save_prompt(self, prompt: str, iteration: int) -> Path:
        """Save prompt to file"""
        prompt_file = self.prompts_dir / f"iteration_{iteration:03d}.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        return prompt_file

    def run_claude(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Run Claude Code with prompt file

        Args:
            prompt_file: Path to prompt file

        Returns:
            Parsed response
        """
        # Run claude command
        result = subprocess.run(
            ["claude", "-p", str(prompt_file), "--dangerously-skip-permission"],
            capture_output=True,
            text=True
        )

        # Parse output as JSON
        # NOTE: This assumes Claude returns JSON. May need parsing logic.
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback: treat as text
            response = {"text": result.stdout, "raw": True}

        return response

    def save_response(self, response: Dict[str, Any], iteration: int) -> Path:
        """Save Claude response to file"""
        response_file = self.responses_dir / f"iteration_{iteration:03d}.json"
        with open(response_file, 'w') as f:
            json.dump(response, f, indent=2)
        return response_file

    def extract_tool_uses(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tool use requests from response

        Args:
            response: Claude response

        Returns:
            List of tool use requests
        """
        # TODO: Implement based on actual response format
        # This is a placeholder
        tool_uses = []

        if "content" in response:
            for block in response.get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_uses.append(block)

        return tool_uses

    def execute_tools(self, tool_uses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute requested tools

        Args:
            tool_uses: List of tool use requests

        Returns:
            List of tool execution results
        """
        results = []

        for tool_use in tool_uses:
            tool_name = tool_use.get("name")
            tool_input = tool_use.get("input", {})
            tool_use_id = tool_use.get("id")

            # Execute tool (placeholder - implement actual execution)
            try:
                output = self._execute_single_tool(tool_name, tool_input)
                status = "success"
            except Exception as e:
                output = f"Error: {str(e)}"
                status = "error"

            results.append({
                "tool_use_id": tool_use_id,
                "tool_name": tool_name,
                "status": status,
                "output": output,
                "executed_at": datetime.now().isoformat()
            })

        return results

    def _execute_single_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a single tool (placeholder)"""
        # TODO: Implement actual tool execution
        return f"[Executed {tool_name} with {tool_input}]"

    def run_workflow(self, task: str, max_iterations: int = 10):
        """
        Run complete workflow

        Args:
            task: Task description
            max_iterations: Maximum iterations
        """
        state = self._load_state()
        iteration = state["current_iteration"]

        tool_results = None

        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"Iteration {iteration}")
            print(f"{'='*70}")

            # 1. Generate prompt
            prompt = self.generate_prompt(task, iteration, tool_results)
            prompt_file = self.save_prompt(prompt, iteration)
            print(f"Prompt saved: {prompt_file}")

            # 2. Run Claude
            print("Running Claude...")
            response = self.run_claude(prompt_file)
            response_file = self.save_response(response, iteration)
            print(f"Response saved: {response_file}")

            # 3. Log to history
            self._append_to_history("user", prompt, iteration)
            self._append_to_history("assistant", response, iteration)

            # 4. Extract tool uses
            tool_uses = self.extract_tool_uses(response)

            if not tool_uses:
                print("No tools requested. Task complete.")
                break

            # 5. Execute tools
            print(f"Executing {len(tool_uses)} tools...")
            tool_results = self.execute_tools(tool_uses)

            # 6. Save tool results
            with open(self.tool_results_file, 'w') as f:
                json.dump({"iteration": iteration, "results": tool_results}, f, indent=2)

            # 7. Update state
            state["current_iteration"] = iteration
            state["status"] = "running"
            self._save_state(state)

        # Mark as complete
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        self._save_state(state)

        print(f"\nWorkflow completed in {iteration} iterations")


def main():
    """Example usage"""
    orchestrator = FileBasedOrchestrator(workspace_dir="./workspace")
    orchestrator.run_workflow(
        task="Analyze data.csv and generate a summary report",
        max_iterations=10
    )


if __name__ == "__main__":
    main()
```

---

## Advantages

1. **Debuggable**: All state is in files, easy to inspect
2. **Resumable**: Can pause and resume workflows
3. **Auditable**: Complete history in JSONL format
4. **Simple**: No complex in-memory state management
5. **Non-interactive friendly**: Perfect for `claude -p`

## Disadvantages

1. **I/O overhead**: Many file reads/writes
2. **Disk space**: Can grow large for long conversations
3. **Concurrency**: Needs locking for parallel workflows

---

## Next Steps

1. Implement actual tool execution logic
2. Add error handling and retries
3. Support workflow templates (YAML)
4. Add cleanup/archival strategies
5. Implement distributed locking for concurrent workflows
