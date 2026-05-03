"""
agents/developer.py
─────────────────────────────────────────────────────────────────────────────
The Developer agent reads the Architect's design and writes production-ready
Python code that implements the specified application.
"""

import os
from crewai import Agent


def create_developer() -> Agent:
    """
    Returns a CrewAI Agent configured as a Senior Python Developer.

    Responsibilities:
    - Implement the architecture faithfully in clean Python
    - Follow PEP 8 and include docstrings
    - Handle errors gracefully with informative messages
    - Structure code so the QA Tester can import and test it easily
    - Output complete, runnable source code (no placeholders)
    """
    return Agent(
        role="Senior Python Developer",
        goal=(
            "Write clean, complete, production-ready Python code that fully "
            "implements the provided architecture. The code must be immediately "
            "runnable, PEP 8 compliant, well-documented with docstrings, and "
            "structured so each logical unit can be tested independently."
        ),
        backstory=(
            "You are a senior Python engineer with expertise in building "
            "everything from REST APIs to data pipelines. You write code "
            "that is readable first, performant second. You never leave "
            "placeholder comments like 'TODO: implement this' — when you "
            "write code, it works. "
            "You take pride in clean error handling, meaningful variable "
            "names, and docstrings that actually explain WHY, not just WHAT. "
            "Your output is always complete, executable Python source."
        ),
        verbose=True,
        allow_delegation=False,
        llm=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
    )
