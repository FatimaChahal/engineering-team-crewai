"""
agents/project_manager.py
─────────────────────────────────────────────────────────────────────────────
The Project Manager agent is the first node in the pipeline.
It receives the raw user requirement and produces a structured technical
brief: scope, features, constraints, and an ordered task list.
"""

import os
from crewai import Agent


def create_project_manager() -> Agent:
    """
    Returns a CrewAI Agent configured as a Senior Project Manager.

    Responsibilities:
    - Parse ambiguous user requirements into a clear technical brief
    - Define MVP scope (what is in / out)
    - Break work into ordered tasks for downstream agents
    - Identify risks and assumptions
    """
    return Agent(
        role="Senior Project Manager",
        goal=(
            "Transform a raw app idea into a clear, actionable technical brief. "
            "Define scope, deliverables, and an ordered task plan that the "
            "Architect, Developer, and QA Tester can follow without ambiguity."
        ),
        backstory=(
            "You are a seasoned software project manager with 15 years of "
            "experience delivering Python-based applications in agile teams. "
            "You excel at cutting through vague requirements, identifying "
            "hidden complexity, and producing concise specs that keep "
            "engineering teams aligned. You always separate MVP features from "
            "nice-to-haves, and you flag risks before they become blockers."
        ),
        verbose=True,
        allow_delegation=False,
        llm=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
    )
