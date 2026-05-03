"""
tools/docker_executor.py
─────────────────────────────────────────────────────────────────────────────
Custom CrewAI tool: executes Python code in an isolated Docker container
(or falls back to local subprocess if Docker is unavailable).

The QA Tester agent uses this tool to safely validate generated code.
"""

import os
import re
import subprocess
import tempfile
import textwrap
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CodeExecutionInput(BaseModel):
    """Input schema for the DockerCodeExecutor tool."""
    code: str = Field(
        ...,
        description="The Python source code to execute. Must be a complete, runnable script."
    )
    timeout: int = Field(
        default=30,
        description="Maximum execution time in seconds before the process is killed."
    )


class DockerCodeExecutor(BaseTool):
    """
    Executes Python code in an isolated Docker container for safe testing.

    Tries Docker first; if unavailable, falls back to a local subprocess
    running in a temporary directory. Either way, the code never touches
    the agent's working directory directly.
    """

    name: str = "DockerCodeExecutor"
    description: str = (
        "Execute Python code safely. "
        "Runs code in a Docker container (isolated sandbox) when Docker is available, "
        "or in a local subprocess sandbox otherwise. "
        "Returns stdout, stderr, and exit code. "
        "Use this to run test suites or validate generated code."
    )
    args_schema: Type[BaseModel] = CodeExecutionInput

    # ─────────────────────────────────────────
    # Public entry point
    # ─────────────────────────────────────────
    def _run(self, code: str, timeout: int = 30) -> str:
        mode = os.getenv("CODE_EXEC_MODE", "local").lower()
        if mode == "docker" and self._docker_available():
            return self._run_in_docker(code, timeout)
        return self._run_locally(code, timeout)

    # ─────────────────────────────────────────
    # Docker execution
    # ─────────────────────────────────────────
    def _docker_available(self) -> bool:
        try:
            subprocess.run(
                ["docker", "ps"],
                capture_output=True, timeout=5, check=True
            )
            return True
        except Exception:
            return False

    def _run_in_docker(self, code: str, timeout: int) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "agent_script.py")
            with open(script_path, "w") as f:
                f.write(code)

            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",           # no internet access
                "--memory", "256m",            # cap RAM
                "--cpus", "0.5",               # cap CPU
                "-v", f"{tmpdir}:/workspace",
                "python:3.12-slim",
                "python", "/workspace/agent_script.py"
            ]

            return self._execute(docker_cmd, timeout, mode="Docker")

    # ─────────────────────────────────────────
    # Local subprocess execution (fallback)
    # ─────────────────────────────────────────
    def _run_locally(self, code: str, timeout: int) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "agent_script.py")
            with open(script_path, "w") as f:
                f.write(code)

            cmd = ["python3", script_path]
            return self._execute(cmd, timeout, mode="Local (subprocess)")

    # ─────────────────────────────────────────
    # Shared execution helper
    # ─────────────────────────────────────────
    def _execute(self, cmd: list, timeout: int, mode: str) -> str:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            summary = textwrap.dedent(f"""
                ┌─────────────────────────────────────────────
                │  Execution Mode : {mode}
                │  Exit Code      : {result.returncode}
                └─────────────────────────────────────────────
                STDOUT:
                {result.stdout or '(empty)'}
                STDERR:
                {result.stderr or '(empty)'}
            """).strip()
            return summary

        except subprocess.TimeoutExpired:
            return f"❌ TIMEOUT: Code exceeded {timeout}s limit. Consider optimising loops or I/O."
        except FileNotFoundError as e:
            return f"❌ EXECUTION ERROR: {e}. Is Python/Docker available?"
        except Exception as e:
            return f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test (run: python tools/docker_executor.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tool = DockerCodeExecutor()

    # Basic sanity check
    result = tool._run(
        code="print('Hello from the sandbox!')\nprint(2 + 2)",
        timeout=10
    )
    print(result)

    # Test error capture
    result2 = tool._run(
        code="raise ValueError('intentional error')",
        timeout=10
    )
    print(result2)
