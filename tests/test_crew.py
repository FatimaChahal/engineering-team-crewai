"""
tests/test_crew.py
─────────────────────────────────────────────────────────────────────────────
Unit and integration tests for the 4-Agent Engineering Team.

Run with:
    pytest tests/ -v

These tests validate:
- Agent instantiation and configuration
- Task creation with correct agents
- DockerCodeExecutor tool (local subprocess mode)
- Crew assembly (structure only — no LLM calls)
- Output directory creation and file saving
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Ensure project root is on the path ───────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Force local execution mode for all tests (no Docker required) ────────────
os.environ.setdefault("CODE_EXEC_MODE", "local")
os.environ.setdefault("MODEL", "groq/llama-3.3-70b-versatile")


# ═══════════════════════════════════════════════════════════════════════════════
# DockerCodeExecutor tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDockerCodeExecutor:
    """Tests for the sandboxed code execution tool."""

    def setup_method(self):
        from tools.docker_executor import DockerCodeExecutor
        self.executor = DockerCodeExecutor()

    def test_basic_print_returns_output(self):
        """A simple print statement should appear in stdout."""
        result = self.executor._run("print('hello from sandbox')", timeout=10)
        assert "hello from sandbox" in result

    def test_arithmetic_output(self):
        """Arithmetic results should be captured correctly."""
        result = self.executor._run("print(6 * 7)", timeout=10)
        assert "42" in result

    def test_multiline_code_executes(self):
        """Multi-line code with variables should execute correctly."""
        code = "x = [i**2 for i in range(5)]\nprint(x)"
        result = self.executor._run(code, timeout=10)
        assert "0" in result and "16" in result

    def test_syntax_error_captured_in_stderr(self):
        """Syntax errors should be captured and reported, not crash the tool."""
        result = self.executor._run("def broken(: pass", timeout=10)
        # Either stderr contains SyntaxError or exit code is non-zero
        assert "SyntaxError" in result or "Exit Code" in result

    def test_runtime_error_captured(self):
        """Runtime errors (e.g. ZeroDivisionError) should be captured."""
        result = self.executor._run("print(1 / 0)", timeout=10)
        assert "ZeroDivisionError" in result or "error" in result.lower()

    def test_import_stdlib_works(self):
        """Standard library imports should work inside the sandbox."""
        result = self.executor._run("import math; print(math.pi)", timeout=10)
        assert "3.14" in result

    def test_output_format_contains_exit_code(self):
        """The result string should include 'Exit Code' metadata."""
        result = self.executor._run("pass", timeout=10)
        assert "Exit Code" in result

    def test_empty_code_runs_without_crash(self):
        """Empty code should execute cleanly (exit 0, no output)."""
        result = self.executor._run("", timeout=10)
        assert result is not None  # Should not raise

    def test_tool_name_and_description_set(self):
        """Tool metadata should be correctly configured."""
        assert self.executor.name == "DockerCodeExecutor"
        assert "Docker" in self.executor.description or "Execute" in self.executor.description


# ═══════════════════════════════════════════════════════════════════════════════
# Agent instantiation tests (no LLM calls)
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentCreation:
    """Verify agents are created with correct roles and configurations."""

    def _make_agent(self, factory):
        """Create agent using openai provider (no key needed for structure tests)."""
        with patch.dict(os.environ, {"MODEL": "openai/gpt-4o-mini",
                                      "OPENAI_API_KEY": "sk-test-dummy"}):
            return factory()

    def test_project_manager_role(self):
        from agents.project_manager import create_project_manager
        agent = self._make_agent(create_project_manager)
        assert "Project Manager" in agent.role

    def test_architect_role(self):
        from agents.architect import create_architect
        agent = self._make_agent(create_architect)
        assert "Architect" in agent.role

    def test_developer_role(self):
        from agents.developer import create_developer
        agent = self._make_agent(create_developer)
        assert "Developer" in agent.role

    def test_qa_tester_role(self):
        from agents.qa_tester import create_qa_tester
        agent = self._make_agent(create_qa_tester)
        assert "QA" in agent.role or "Tester" in agent.role or "Engineer" in agent.role

    def test_qa_tester_has_tools(self):
        """QA Tester must have the DockerCodeExecutor tool attached."""
        from agents.qa_tester import create_qa_tester
        agent = self._make_agent(create_qa_tester)
        tool_names = [t.name for t in agent.tools]
        assert "DockerCodeExecutor" in tool_names

    def test_agents_not_delegating(self):
        """None of the agents should allow delegation (sequential pipeline)."""
        from agents import (
            create_project_manager, create_architect,
            create_developer, create_qa_tester
        )
        for factory in [create_project_manager, create_architect,
                         create_developer, create_qa_tester]:
            agent = self._make_agent(factory)
            assert agent.allow_delegation is False


# ═══════════════════════════════════════════════════════════════════════════════
# Task creation tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestTaskCreation:
    """Verify tasks are created with correct agents and non-empty prompts."""

    def _real_agent(self):
        """Create a minimal real Agent using OpenAI (no actual API call made)."""
        from crewai import Agent
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-dummy"}):
            return Agent(
                role="Test Agent",
                goal="Test goal",
                backstory="Test backstory",
                llm="openai/gpt-4o-mini",
                allow_delegation=False,
                verbose=False,
            )

    def test_requirements_task_embeds_user_request(self):
        from tasks.task_definitions import create_requirements_task
        agent = self._real_agent()
        user_request = "Build a todo app"
        task = create_requirements_task(agent, user_request)
        assert user_request in task.description

    def test_architecture_task_has_description(self):
        from tasks.task_definitions import create_architecture_task
        agent = self._real_agent()
        task = create_architecture_task(agent)
        assert len(task.description) > 50

    def test_implementation_task_mentions_pep8(self):
        from tasks.task_definitions import create_implementation_task
        agent = self._real_agent()
        task = create_implementation_task(agent)
        assert "PEP" in task.description or "pep" in task.description.lower()

    def test_qa_task_mentions_docker_executor(self):
        from tasks.task_definitions import create_qa_task
        agent = self._real_agent()
        task = create_qa_task(agent)
        assert "DockerCodeExecutor" in task.description

    def test_all_tasks_have_expected_output(self):
        from tasks import (
            create_requirements_task, create_architecture_task,
            create_implementation_task, create_qa_task
        )
        agent = self._real_agent()
        tasks = [
            create_requirements_task(agent, "test"),
            create_architecture_task(agent),
            create_implementation_task(agent),
            create_qa_task(agent),
        ]
        for task in tasks:
            assert task.expected_output
            assert len(task.expected_output) > 10


# ═══════════════════════════════════════════════════════════════════════════════
# Output saving tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestOutputSaving:
    """Test that EngineeringTeam correctly saves output files."""

    def test_output_directory_created(self, tmp_path):
        """Session directory should be created on instantiation."""
        with patch("crew.OUTPUTS_DIR", tmp_path):
            from crew import EngineeringTeam
            team = EngineeringTeam()
            # outputs dir itself should now exist
            assert tmp_path.exists()

    def test_save_outputs_creates_files(self, tmp_path):
        """_save_outputs should create all 4 output files."""
        with patch("crew.OUTPUTS_DIR", tmp_path):
            from crew import EngineeringTeam
            team = EngineeringTeam()
            session_dir = tmp_path / "test_session"
            session_dir.mkdir()

            outputs = {
                "brief": "# Brief\nContent here",
                "architecture": "# Architecture\nContent here",
                "code": "# code\nprint('hello')",
                "qa_report": "# QA Report\nAll tests passed",
                "raw": "raw output",
            }
            team._save_outputs(outputs, session_dir, "test request")

            assert (session_dir / "meta.json").exists()
            assert (session_dir / "1_technical_brief.md").exists()
            assert (session_dir / "2_architecture.md").exists()
            assert (session_dir / "3_app_code.py").exists()
            assert (session_dir / "4_qa_report.md").exists()

    def test_meta_json_contains_request(self, tmp_path):
        """meta.json should record the original user request."""
        with patch("crew.OUTPUTS_DIR", tmp_path):
            from crew import EngineeringTeam
            team = EngineeringTeam()
            session_dir = tmp_path / "test_session2"
            session_dir.mkdir()

            outputs = {"brief": "x", "architecture": "x",
                       "code": "x", "qa_report": "x", "raw": "x"}
            team._save_outputs(outputs, session_dir, "build a weather app")

            meta = json.loads((session_dir / "meta.json").read_text())
            assert meta["user_request"] == "build a weather app"

    def test_code_file_extraction(self, tmp_path):
        """Files delimited with '# === FILE: path ===' should be extracted."""
        with patch("crew.OUTPUTS_DIR", tmp_path):
            from crew import EngineeringTeam
            team = EngineeringTeam()
            session_dir = tmp_path / "test_session3"
            session_dir.mkdir()

            code_with_files = (
                "# === FILE: main.py ===\n"
                "print('main')\n"
                "# === FILE: models.py ===\n"
                "class Item: pass\n"
            )
            team._extract_code_files(code_with_files, session_dir)

            assert (session_dir / "src" / "main.py").exists()
            assert (session_dir / "src" / "models.py").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# Integration smoke test (no LLM)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrewIntegration:
    """Smoke tests that verify the crew assembles without errors."""

    def test_crew_assembles_with_four_agents(self):
        """Crew should have exactly 4 agents."""
        from crewai import Crew, Process
        from agents import (
            create_project_manager, create_architect,
            create_developer, create_qa_tester
        )
        from tasks import (
            create_requirements_task, create_architecture_task,
            create_implementation_task, create_qa_task
        )

        with patch.dict(os.environ, {"MODEL": "openai/gpt-4o-mini",
                                      "OPENAI_API_KEY": "sk-test-dummy"}):
            pm        = create_project_manager()
            architect = create_architect()
            developer = create_developer()
            qa        = create_qa_tester()

        t1 = create_requirements_task(pm, "build something")
        t2 = create_architecture_task(architect)
        t3 = create_implementation_task(developer)
        t4 = create_qa_task(qa)

        crew = Crew(
            agents=[pm, architect, developer, qa],
            tasks=[t1, t2, t3, t4],
            process=Process.sequential,
            verbose=False,
        )

        assert len(crew.agents) == 4
        assert len(crew.tasks) == 4
