# 🤖 4-Agent AI Engineering Team

> Automate software development with a fully orchestrated multi-agent pipeline: **Project Manager → Architect → Developer → QA Tester**, powered by [CrewAI](https://www.crewai.com/) and Docker-based code execution.

---

## 🧠 Architecture Overview

```
User Prompt (App Idea)
        │
        ▼
┌─────────────────────┐
│   Project Manager   │  ← Breaks down requirements, creates task plan
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Architect        │  ← Designs system structure, chooses tech stack
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Developer        │  ← Writes clean, documented Python code
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    QA Tester        │  ← Writes tests, validates code in Docker sandbox
└────────┬────────────┘
         │
         ▼
   Final Deliverable
   (code + tests + report)
```

---

## 🚀 Features

- **4 Specialized AI Agents** with distinct roles and expertise
- **Sequential pipeline** with context passing between agents
- **Docker-isolated code execution** for safe, sandboxed testing
- **Automatic output saving** — code, tests, and QA report written to `outputs/`
- **Modular design** — easy to extend with new agents or tools
- **`.env`-based LLM configuration** — works with OpenAI, Groq, or any LiteLLM-compatible provider

---

## 📁 Project Structure

```
engineering_team/
├── main.py                  # Entry point — run your engineering team here
├── crew.py                  # CrewAI Crew assembly and kickoff
├── agents/
│   ├── __init__.py
│   ├── project_manager.py   # PM agent definition
│   ├── architect.py         # Architect agent definition
│   ├── developer.py         # Developer agent definition
│   └── qa_tester.py         # QA Tester agent definition
├── tasks/
│   ├── __init__.py
│   └── task_definitions.py  # All 4 task definitions
├── tools/
│   ├── __init__.py
│   └── docker_executor.py   # Docker sandbox code execution tool
├── tests/
│   └── test_crew.py         # Unit tests for the crew pipeline
├── outputs/                 # Auto-generated: code, tests, QA reports
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/FatimaChahal/engineering-team-crewai.git
cd engineering-team-crewai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your LLM

```bash
cp .env.example .env
# Edit .env and add your API key
```

Supported providers (via LiteLLM):
- `openai/gpt-4o` — OpenAI
- `groq/llama-3.3-70b-versatile` — Groq (free tier available)
- `ollama/llama3` — Local Ollama

### 4. (Optional) Ensure Docker is running

The QA Tester uses Docker to execute code in an isolated sandbox. Make sure Docker Desktop or Docker Engine is running:

```bash
docker ps
```

If Docker is unavailable, the tool falls back to local subprocess execution with a warning.

---

## ▶️ Usage

```bash
python main.py
```

You'll be prompted to describe your app idea. Example inputs:

```
> A REST API for a simple todo list with FastAPI
> A CLI weather app that fetches data from OpenWeatherMap
> A Python script that scrapes headlines from Hacker News
```

The team will autonomously plan, design, build, and test your app.

---

## 📤 Outputs

After each run, find your deliverables in `outputs/`:

| File | Description |
|------|-------------|
| `architecture.md` | System design from the Architect |
| `app_code.py` | Implementation from the Developer |
| `test_suite.py` | Test suite from the QA Tester |
| `qa_report.md` | Full QA report with execution results |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent orchestration | [CrewAI](https://www.crewai.com/) 1.x |
| LLM backbone | OpenAI / Groq / Ollama (configurable) |
| Code execution sandbox | Docker (subprocess fallback) |
| Environment management | python-dotenv |
| Testing | pytest |

---

## 🤝 Contributing

Pull requests welcome! Ideas for extensions:
- Add a **DevOps agent** for Dockerfile/CI generation
- Integrate a **Code Review agent** between Developer and QA
- Add a **Documentation agent** for auto-generating API docs
- Connect to GitHub API for automatic repo creation

---

## 👩‍💻 Author

**Fatima Chahal** — AI Engineering  
[GitHub: FatimaChahal](https://github.com/FatimaChahal) | [LinkedIn](https://linkedin.com/in/fatima-chahal)

---

## 📄 License

MIT License — free to use and adapt.
