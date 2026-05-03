"""
crew.py
─────────────────────────────────────────────────────────────────────────────
Assembles the 4-agent engineering crew and orchestrates the sequential
pipeline: PM → Architect → Developer → QA Tester.

Handles:
- Agent and task creation
- Crew kickoff with the user's request
- Output extraction and saving to the outputs/ directory
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from crewai import Crew, Process

from agents import (
    create_project_manager,
    create_architect,
    create_developer,
    create_qa_tester,
)
from tasks import (
    create_requirements_task,
    create_architecture_task,
    create_implementation_task,
    create_qa_task,
)

# Output directory (created alongside this file)
OUTPUTS_DIR = Path(__file__).parent / "outputs"


class EngineeringTeam:
    """
    Orchestrates the 4-agent software engineering pipeline.

    Usage:
        team = EngineeringTeam()
        results = team.build("A FastAPI todo list REST API")
    """

    def __init__(self):
        OUTPUTS_DIR.mkdir(exist_ok=True)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ─────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────

    def build(self, user_request: str) -> dict:
        """
        Run the full engineering pipeline for the given user request.

        Args:
            user_request: Plain-English description of the app to build.

        Returns:
            A dict with keys: brief, architecture, code, qa_report,
            and output_dir pointing to where files were saved.
        """
        print(self._banner())

        # ── Instantiate agents ──────────────────────────────────────────
        pm        = create_project_manager()
        architect = create_architect()
        developer = create_developer()
        qa        = create_qa_tester()

        # ── Instantiate tasks ───────────────────────────────────────────
        t1_requirements  = create_requirements_task(pm, user_request)
        t2_architecture  = create_architecture_task(architect)
        t3_implementation = create_implementation_task(developer)
        t4_qa            = create_qa_task(qa)

        # ── Assemble crew ───────────────────────────────────────────────
        crew = Crew(
            agents=[pm, architect, developer, qa],
            tasks=[t1_requirements, t2_architecture, t3_implementation, t4_qa],
            process=Process.sequential,   # tasks run in order, output → context
            verbose=True,
        )

        # ── Kick off ────────────────────────────────────────────────────
        print(f"\n🚀  Starting engineering pipeline for:\n    \"{user_request}\"\n")
        raw_result = crew.kickoff()

        # ── Extract individual outputs ───────────────────────────────────
        outputs = self._extract_outputs(crew, raw_result)

        # ── Save to disk ────────────────────────────────────────────────
        session_dir = OUTPUTS_DIR / self._session_id
        session_dir.mkdir(exist_ok=True)
        self._save_outputs(outputs, session_dir, user_request)

        print(f"\n✅  Pipeline complete! Outputs saved to: {session_dir}")
        return {**outputs, "output_dir": str(session_dir)}

    # ─────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────

    def _extract_outputs(self, crew: Crew, raw_result) -> dict:
        """
        Pull individual task outputs from the completed crew.
        Falls back gracefully if the CrewAI version returns outputs differently.
        """
        outputs = {
            "brief":        "",
            "architecture": "",
            "code":         "",
            "qa_report":    "",
            "raw":          str(raw_result),
        }

        try:
            task_outputs = crew.tasks
            if len(task_outputs) >= 1 and hasattr(task_outputs[0], "output"):
                outputs["brief"]        = str(task_outputs[0].output or "")
                outputs["architecture"] = str(task_outputs[1].output or "") if len(task_outputs) > 1 else ""
                outputs["code"]         = str(task_outputs[2].output or "") if len(task_outputs) > 2 else ""
                outputs["qa_report"]    = str(task_outputs[3].output or "") if len(task_outputs) > 3 else ""
        except Exception:
            # If individual task outputs aren't accessible, use the full result
            outputs["qa_report"] = outputs["raw"]

        return outputs

    def _save_outputs(self, outputs: dict, session_dir: Path, user_request: str) -> None:
        """Write each artifact to disk in the session directory."""

        # Metadata
        meta = {
            "session_id":   self._session_id,
            "user_request": user_request,
            "timestamp":    datetime.now().isoformat(),
        }
        (session_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False)
        )

        # Technical brief
        if outputs["brief"]:
            (session_dir / "1_technical_brief.md").write_text(outputs["brief"])

        # Architecture document
        if outputs["architecture"]:
            (session_dir / "2_architecture.md").write_text(outputs["architecture"])

        # Generated code — extract Python files if delimited
        if outputs["code"]:
            (session_dir / "3_app_code.py").write_text(outputs["code"])
            self._extract_code_files(outputs["code"], session_dir)

        # QA report
        if outputs["qa_report"]:
            (session_dir / "4_qa_report.md").write_text(outputs["qa_report"])
        elif outputs["raw"]:
            (session_dir / "4_qa_report.md").write_text(outputs["raw"])

    def _extract_code_files(self, code_output: str, session_dir: Path) -> None:
        """
        Parse the developer output for '# === FILE: path ===' delimiters
        and write each file to disk individually.
        """
        pattern = r"# === FILE: (.+?) ===\n(.*?)(?=# === FILE:|$)"
        matches = re.findall(pattern, code_output, re.DOTALL)

        if not matches:
            return

        code_dir = session_dir / "src"
        for file_path, file_content in matches:
            full_path = code_dir / file_path.strip()
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(file_content.strip())

        print(f"    📁  Extracted {len(matches)} source file(s) to {code_dir}/")

    @staticmethod
    def _banner() -> str:
        return """
╔══════════════════════════════════════════════════════════════╗
║          🤖  4-Agent AI Engineering Team                     ║
║                                                              ║
║  PM → Architect → Developer → QA Tester                     ║
║  Powered by CrewAI + Docker sandbox                         ║
╚══════════════════════════════════════════════════════════════╝"""
