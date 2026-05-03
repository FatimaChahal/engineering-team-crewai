"""
tasks/task_definitions.py
─────────────────────────────────────────────────────────────────────────────
Defines the four sequential tasks that form the engineering pipeline:
  1. requirements_analysis   → Project Manager
  2. system_design           → Architect
  3. code_implementation     → Developer
  4. qa_and_testing          → QA Tester

Each task's output becomes the context for the next task in the chain.
"""

from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent


def create_requirements_task(agent: BaseAgent, user_request: str) -> Task:
    """
    Task 1 — Project Manager: analyse requirements and produce a technical brief.
    """
    return Task(
        description=f"""
You are the first agent in the pipeline. Your job is to take the following
raw user request and transform it into a structured technical brief.

USER REQUEST:
{user_request}

Your output MUST contain all of the following sections:

## 1. Project Summary
One paragraph describing what the application does and who it is for.

## 2. MVP Feature List
A numbered list of features to include in the first deliverable.
Mark any feature as [NICE-TO-HAVE] if it is not strictly necessary for MVP.

## 3. Technical Constraints & Assumptions
List any implicit constraints (Python version, no external DB, etc.)
and document the assumptions you are making.

## 4. Ordered Task Plan
A numbered list of implementation tasks for the Architect, Developer,
and QA Tester to execute in order.

## 5. Risk Register
A brief table of risks and mitigations (at least 3 rows).

Be concise and precise. This document will be passed directly to the
Software Architect — make sure it gives them everything they need.
        """.strip(),
        expected_output=(
            "A structured technical brief in Markdown with sections: "
            "Project Summary, MVP Feature List, Technical Constraints, "
            "Ordered Task Plan, and Risk Register."
        ),
        agent=agent,
    )


def create_architecture_task(agent: BaseAgent) -> Task:
    """
    Task 2 — Architect: design the system from the PM's brief.
    """
    return Task(
        description="""
You are the Software Architect. Using the technical brief produced by the
Project Manager (provided in your context), design a complete system
architecture for the application.

Your output MUST contain all of the following sections:

## 1. Technology Stack
List every Python library you will use and WHY (one sentence per library).

## 2. Module & File Structure
Show the complete file/directory tree with a one-line description per file.
Example:
    app/
    ├── main.py       # Entry point; CLI or FastAPI app launcher
    ├── models.py     # Pydantic data models
    └── ...

## 3. Core Components
For each module, describe:
- Its responsibilities
- Public functions/classes it exposes
- Its inputs and outputs

## 4. Data Flow Diagram (text-based)
Draw a simple ASCII diagram showing how data moves through the system.

## 5. Key Design Decisions
Explain 3–5 architectural decisions with alternatives considered.

## 6. Implementation Notes for the Developer
Any gotchas, ordering constraints, or patterns the developer must follow.

This document will be passed directly to the Senior Developer — it must
be detailed enough to implement from without asking questions.
        """.strip(),
        expected_output=(
            "A complete architecture document in Markdown with: "
            "Tech Stack, Module Structure, Component descriptions, "
            "Data Flow, Design Decisions, and Developer Notes."
        ),
        agent=agent,
    )


def create_implementation_task(agent: BaseAgent) -> Task:
    """
    Task 3 — Developer: implement the full application.
    """
    return Task(
        description="""
You are the Senior Python Developer. Using the architecture document from
the Architect (provided in your context), implement the full application.

STRICT REQUIREMENTS:
- Write complete, runnable Python code — NO placeholders, no "# TODO"
- Follow PEP 8 strictly (meaningful names, 88-char line limit)
- Add a module-level docstring to every file
- Add a docstring to every function and class
- Handle all errors with informative messages (no bare `except:`)
- Structure the code so the QA Tester can import individual functions
- Include a `if __name__ == "__main__":` block in the main entry point

FORMAT YOUR OUTPUT AS:
Start each file with a comment line:  # === FILE: path/to/file.py ===
Then the complete file content.
Repeat for every file in the project.

Example format:
# === FILE: main.py ===
\"\"\"Main entry point.\"\"\"
...

# === FILE: models.py ===
\"\"\"Data models.\"\"\"
...

Every line of code must be functional. The QA Tester will execute this
code directly — it must work.
        """.strip(),
        expected_output=(
            "Complete, runnable Python source code for all project files, "
            "each clearly delimited with '# === FILE: path/to/file.py ===', "
            "PEP 8 compliant, fully documented, with no placeholders."
        ),
        agent=agent,
    )


def create_qa_task(agent: BaseAgent) -> Task:
    """
    Task 4 — QA Tester: write tests, execute them, produce a report.
    """
    return Task(
        description="""
You are the QA Engineer. You have access to the Developer's code from the
previous step (in your context) and the DockerCodeExecutor tool.

YOUR PROCESS:
1. Review the Developer's code critically — identify potential bugs,
   missing edge case handling, and testability issues.

2. Write a complete pytest test suite that covers:
   - Happy path: normal inputs produce correct outputs
   - Edge cases: empty inputs, boundary values, None, etc.
   - Error cases: invalid inputs raise appropriate exceptions
   - At minimum 5 meaningful test functions

3. Use the DockerCodeExecutor tool to execute the developer's code
   combined with your tests. Construct a single Python script that
   includes BOTH the application code AND the test functions, then
   run it with DockerCodeExecutor.

4. Write a final QA report based on execution results.

FORMAT YOUR OUTPUT AS:

## QA Test Suite
```python
# Complete pytest test code here
```

## Execution Results
(paste the exact output from DockerCodeExecutor)

## QA Report

### Summary
- Total tests: N
- Passed: N
- Failed: N
- Coverage areas tested: [list]

### Issues Found
(list any bugs or problems discovered, or "None" if clean)

### Recommendations
(what should be improved before production release)

### Verdict
PASS ✅ or FAIL ❌ (with brief justification)
        """.strip(),
        expected_output=(
            "A QA document containing: the test suite code, "
            "actual execution results from DockerCodeExecutor, "
            "and a QA report with summary, issues, recommendations, and verdict."
        ),
        agent=agent,
    )
