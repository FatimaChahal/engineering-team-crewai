"""
agents/qa_tester.py
─────────────────────────────────────────────────────────────────────────────
The QA Tester agent reviews the Developer's code, writes a pytest test suite,
executes it in the Docker sandbox, and produces a final QA report.
"""

import os
from crewai import Agent
from tools import DockerCodeExecutor


def create_qa_tester() -> Agent:
    """
    Returns a CrewAI Agent configured as a QA Engineer.

    Responsibilities:
    - Critically review the Developer's code for bugs and edge cases
    - Write a comprehensive pytest test suite
    - Execute code and tests via the DockerCodeExecutor tool
    - Produce a structured QA report with pass/fail results and recommendations
    """
    executor = DockerCodeExecutor()

    return Agent(
        role="QA Engineer",
        goal=(
            "Validate the developer's code by writing a thorough pytest test "
            "suite covering happy paths, edge cases, and error conditions. "
            "Execute the tests using the DockerCodeExecutor tool and produce "
            "a QA report that clearly states: what was tested, what passed, "
            "what failed, and what should be fixed before release."
        ),
        backstory=(
            "You are a meticulous QA engineer who has prevented countless "
            "production incidents. You approach every codebase with healthy "
            "scepticism — if it can break, it will break. "
            "You write pytest tests that are thorough but readable: each test "
            "has a clear name that describes what it verifies, uses fixtures "
            "for shared setup, and covers both valid and invalid inputs. "
            "You use the DockerCodeExecutor tool to actually run the code and "
            "tests in a sandboxed environment — you never just read code and "
            "assume it works. Your QA reports are concise but complete."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[executor],
        llm=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
    )
