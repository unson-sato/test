#!/usr/bin/env python3
"""
Method 2: tool_result を system メッセージ（正確にはAPIの標準形式）として送る実装例

Anthropic APIの標準的な使い方
"""

import anthropic
import json
from typing import List, Dict, Any, Optional


class Method2Runner:
    """
    方法2: tool_resultをAPIの標準形式で送る方式

    これがAnthropicの公式ドキュメントで推奨されている方法
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize runner

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.client = anthropic.Anthropic(api_key=api_key)

        # Tool definitions
        self.tools = [
            {
                "name": "execute_python",
                "description": "Execute Python code and return the result",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "read_file",
                "description": "Read contents of a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file"
                        }
                    },
                    "required": ["path"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool and return the result

        Args:
            tool_name: Name of the tool
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result as string
        """
        if tool_name == "execute_python":
            try:
                # Simplified: in reality, use safe execution
                result = eval(tool_input["code"])
                return f"Execution successful: {result}"
            except Exception as e:
                return f"Error: {str(e)}"

        elif tool_name == "read_file":
            try:
                with open(tool_input["path"], 'r') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error: {str(e)}"

        else:
            return f"Unknown tool: {tool_name}"

    def format_tool_results_standard(self, tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tool results in standard API format

        METHOD 2 の核心部分：
        tool_result を API の標準形式（tool_result content block）でフォーマット

        Args:
            tool_results: List of tool results with tool_use_id and content

        Returns:
            List of content blocks in API format
        """
        content_blocks = []

        for result in tool_results:
            content_blocks.append({
                "type": "tool_result",
                "tool_use_id": result["tool_use_id"],
                "content": result["content"]
            })

        return content_blocks

    def run(self, initial_prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the conversation loop with Method 2 approach

        Args:
            initial_prompt: Initial user prompt
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            Final response and conversation history
        """
        # Initialize message history
        messages = [
            {"role": "user", "content": initial_prompt}
        ]

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"Iteration {iteration}")
            print(f"{'='*70}")

            # API call
            print("Calling Claude API...")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=messages,
                tools=self.tools
            )

            print(f"Stop reason: {response.stop_reason}")

            # Add assistant response to message history
            # Important: Store the full response content (including tool_use blocks)
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Check if we're done
            if response.stop_reason == "end_turn":
                print("Conversation complete (end_turn)")
                break

            if response.stop_reason != "tool_use":
                print(f"Conversation complete ({response.stop_reason})")
                break

            # Extract and execute tools
            print("\nExecuting tools...")
            tool_results = []

            for content_block in response.content:
                if content_block.type == "tool_use":
                    print(f"  - Tool: {content_block.name}")
                    print(f"    Input: {json.dumps(content_block.input, indent=2)}")

                    # Execute tool
                    result = self.execute_tool(content_block.name, content_block.input)

                    print(f"    Result: {result[:100]}...")

                    tool_results.append({
                        "tool_use_id": content_block.id,
                        "content": result
                    })

            if not tool_results:
                print("No tools to execute, stopping")
                break

            # METHOD 2: Format tool results in standard API format
            tool_result_content = self.format_tool_results_standard(tool_results)

            # Add user message with tool results in standard format
            messages.append({
                "role": "user",
                "content": tool_result_content  # This is a list of content blocks
            })

            print(f"\nAdded {len(tool_result_content)} tool_result blocks to user message")

        if iteration >= max_iterations:
            print(f"\nReached maximum iterations ({max_iterations})")

        return {
            "final_response": response,
            "messages": messages,
            "iterations": iteration
        }


def main():
    """Example usage"""

    # Create runner
    runner = Method2Runner()

    # Run with a simple prompt
    prompt = """
    I need you to calculate 2 + 2 using Python.
    Then read the contents of README.md.
    """

    result = runner.run(prompt, max_iterations=5)

    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(f"Total iterations: {result['iterations']}")
    print(f"Total messages: {len(result['messages'])}")

    # Show final assistant response
    final_content = result['final_response'].content
    for block in final_content:
        if hasattr(block, 'text'):
            print(f"\nFinal text:\n{block.text}")


if __name__ == "__main__":
    main()
