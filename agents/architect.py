"""
agents/architect.py
─────────────────────────────────────────────────────────────────────────────
The Architect agent reads the Project Manager's brief and produces a
detailed system design: modules, data flow, tech stack, and file structure.
"""

import os
from crewai import Agent


def create_architect() -> Agent:
    """
    Returns a CrewAI Agent configured as a Software Architect.

    Responsibilities:
    - Choose appropriate Python libraries and design patterns
    - Define the file/module structure
    - Describe data models and interfaces between components
    - Produce a clear architecture document for the Developer
    """
    return Agent(
        role="Software Architect",
        goal=(
            "Design a clean, pragmatic system architecture for the given "
            "requirements. Produce a detailed architecture document specifying "
            "modules, classes, data flow, chosen libraries, and file structure. "
            "The design must be simple enough to implement in a single session "
            "while being extensible and well-structured."
        ),
        backstory=(
            "You are a principal software architect specialising in Python "
            "back-end systems. You have designed everything from microservices "
            "to CLI tools to ML pipelines. You believe in simplicity over "
            "cleverness: choose boring technology when it works, and only "
            "introduce complexity when clearly justified. "
            "Your architecture documents are legendary for their clarity — "
            "any competent developer can implement from them without asking "
            "follow-up questions."
        ),
        verbose=True,
        allow_delegation=False,
        llm=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
    )
