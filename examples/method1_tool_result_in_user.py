#!/usr/bin/env python3
"""
Method 1: tool_result を user メッセージに含める実装例

非対話モードでの使用を想定した、シンプルなループ構造
"""

import anthropic
import json
from typing import List, Dict, Any, Optional


class Method1Runner:
    """
    方法1: tool_resultをuserメッセージに含める方式

    非対話モード（claude -p --dangerously-skip-permission）との互換性を考慮
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

    def format_tool_results_for_user_message(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        Format tool results to embed in user message

        METHOD 1 の核心部分：
        tool_result を次の user メッセージのコンテンツとしてフォーマット

        Args:
            tool_results: List of tool results with tool_use_id and content

        Returns:
            Formatted string for user message
        """
        formatted = "Tool execution results:\n\n"

        for result in tool_results:
            formatted += f"Tool Use ID: {result['tool_use_id']}\n"
            formatted += f"Result:\n{result['content']}\n"
            formatted += "-" * 60 + "\n"

        formatted += "\nPlease continue based on these results."

        return formatted

    def run(self, initial_prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the conversation loop with Method 1 approach

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

            # METHOD 1: Format tool results as user message content
            tool_results_message = self.format_tool_results_for_user_message(tool_results)

            # Add user message with tool results
            messages.append({
                "role": "user",
                "content": tool_results_message
            })

            print(f"\nAdded tool results to user message")

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
    runner = Method1Runner()

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
