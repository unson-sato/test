"""
MCP Client for Kamuicode integration

Provides interface to Kamuicode MCP servers via Claude Code CLI in headless mode.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Claude Code MCP client for Kamuicode servers.

    Uses Claude Code CLI in headless/non-interactive mode to call MCP servers.
    Requires .mcp.json configuration file with MCP server definitions.
    """

    def __init__(self, claude_cli: str = "claude", mcp_config: str = ".mcp.json"):
        """
        Initialize MCP client.

        Args:
            claude_cli: Path to Claude CLI executable
            mcp_config: Path to MCP configuration file (.mcp.json)
        """
        self.claude_cli = claude_cli
        self.mcp_config = mcp_config
        self.models_config = self._load_models_config()

    def _load_models_config(self) -> Dict[str, Any]:
        """Load Kamuicode models metadata from config file."""
        config_path = Path("config/kamuicode_models.json")
        if not config_path.exists():
            logger.warning(
                f"Models config not found: {config_path}. " "Model metadata will not be available."
            )
            return {"models": []}

        with open(config_path, encoding="utf-8") as f:
            return json.load(f)

    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for specific model.

        Args:
            model_id: Kamuicode model ID

        Returns:
            Model configuration dict or None if not found
        """
        for model in self.models_config.get("models", []):
            if model["id"] == model_id:
                return model
        return None

    async def generate_video(
        self, model_id: str, prompt: str, duration: float, **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using Kamuicode MCP server.

        Args:
            model_id: Kamuicode model ID (e.g., "anime-diffusion-v3")
            prompt: Generation prompt
            duration: Video duration in seconds
            **kwargs: Model-specific additional parameters

        Returns:
            {
                "success": bool,
                "video_url": str (if success),
                "error": str (if failed),
                "raw_response": dict (full MCP response)
            }
        """
        model_config = self.get_model_config(model_id)
        if not model_config:
            logger.warning(f"Model config not found for {model_id}, proceeding anyway")

        # Build MCP tool name from model_id
        # Convert "anime-diffusion-v3" -> "mcp__kamuicode_anime_diffusion_v3"
        mcp_tool = f"mcp__kamuicode_{model_id.replace('-', '_')}"

        # Build generation request prompt
        request_prompt = self._build_request_prompt(model_id, prompt, duration, kwargs)

        # Call MCP via Claude CLI
        result = await self._call_claude_mcp(mcp_tool, request_prompt)

        return result

    def _build_request_prompt(
        self,
        model_id: str,
        prompt: str,
        duration: float,
        extra_params: Dict[str, Any],
    ) -> str:
        """
        Build request prompt for Claude MCP call.

        Args:
            model_id: Model ID
            prompt: Generation prompt
            duration: Duration in seconds
            extra_params: Additional parameters

        Returns:
            Formatted prompt string
        """
        # Combine all parameters
        params = {
            "prompt": prompt,
            "duration": duration,
            **extra_params,
        }

        # Build prompt asking Claude to use MCP tool
        request = f"""Generate a video using the Kamuicode MCP server.

Model: {model_id}
Parameters:
{json.dumps(params, indent=2)}

Please call the MCP tool to generate the video and return the result in JSON format
with the following structure:
{{
    "video_url": "https://...",
    "duration": {duration},
    "model_id": "{model_id}"
}}
"""
        return request

    async def _call_claude_mcp(self, mcp_tool: str, request_prompt: str) -> Dict[str, Any]:
        """
        Call Claude CLI in headless mode with MCP.

        Command format:
            claude -p "<prompt>" \\
                --mcp-config .mcp.json \\
                --allowedTools "mcp__..." \\
                --dangerously-skip-permissions \\
                --output-format json

        Args:
            mcp_tool: MCP tool name (e.g., "mcp__kamuicode_anime_diffusion_v3")
            request_prompt: Request prompt

        Returns:
            {
                "success": bool,
                "video_url": str (if success),
                "error": str (if failed),
                "raw_response": dict
            }
        """
        cmd = [
            self.claude_cli,
            "-p",
            request_prompt,
            "--mcp-config",
            self.mcp_config,
            "--allowedTools",
            mcp_tool,
            "--dangerously-skip-permissions",
            "--output-format",
            "json",
        ]

        logger.info(f"Calling MCP tool: {mcp_tool}")
        logger.debug(f"Command: {' '.join(cmd[:4])}...")  # Log first few args only

        try:
            # Security: Using create_subprocess_exec (not shell) to prevent command injection
            # All arguments are passed as separate list items
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"MCP call failed: {error_msg}")
                return {"success": False, "error": error_msg}

            # Parse JSON response
            response_text = stdout.decode()
            logger.debug(f"MCP response: {response_text[:200]}...")

            result = json.loads(response_text)

            # Extract video URL from response
            video_url = self._extract_video_url(result)

            if not video_url:
                return {
                    "success": False,
                    "error": "No video_url in MCP response",
                    "raw_response": result,
                }

            return {
                "success": True,
                "video_url": video_url,
                "raw_response": result,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response as JSON: {e}")
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            logger.error(f"MCP call exception: {e}")
            return {"success": False, "error": str(e)}

    def _extract_video_url(self, mcp_response: Dict[str, Any]) -> Optional[str]:
        """
        Extract video URL from MCP server response.

        Tries multiple common patterns for video URL in response.

        Args:
            mcp_response: MCP server response dict

        Returns:
            Video URL string or None if not found
        """
        # Try common patterns for video URL
        if "video_url" in mcp_response:
            return mcp_response["video_url"]
        elif "url" in mcp_response:
            return mcp_response["url"]
        elif "output" in mcp_response:
            output = mcp_response["output"]
            if isinstance(output, dict):
                if "video_url" in output:
                    return output["video_url"]
                elif "url" in output:
                    return output["url"]
        elif "result" in mcp_response:
            result = mcp_response["result"]
            if isinstance(result, dict):
                if "video_url" in result:
                    return result["video_url"]
                elif "url" in result:
                    return result["url"]

        logger.warning(
            f"Could not find video URL in response. " f"Response keys: {list(mcp_response.keys())}"
        )
        return None
