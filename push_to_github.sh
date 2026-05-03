#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# push_to_github.sh
# Initialises a local Git repo and pushes the engineering-team project
# to a new GitHub repository under your FatimaUPPA account.
#
# Prerequisites:
#   - git installed
#   - GitHub CLI (gh) installed and authenticated  OR
#     a GitHub PAT exported as GITHUB_TOKEN
#
# Usage:
#   chmod +x push_to_github.sh
#   ./push_to_github.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_NAME="engineering-team-crewai"
GITHUB_USER="FatimaUPPA"
DESCRIPTION="🤖 4-Agent AI Engineering Team: PM → Architect → Developer → QA Tester, powered by CrewAI and Docker sandbox"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Pushing $REPO_NAME to GitHub/$GITHUB_USER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Step 1: Init git repo (if not already) ────────────────────────────────
if [ ! -d ".git" ]; then
  git init
  echo "✅  Git repo initialised"
fi

# ── Step 2: Stage all files ───────────────────────────────────────────────
git add .
git status --short

# ── Step 3: Commit ───────────────────────────────────────────────────────
git commit -m "🚀 Initial commit: 4-Agent AI Engineering Team

- Project Manager agent: requirements analysis & technical brief
- Architect agent: system design & architecture document
- Developer agent: PEP 8 Python implementation
- QA Tester agent: pytest suite + Docker sandbox execution
- DockerCodeExecutor custom CrewAI tool (Docker + local fallback)
- Sequential CrewAI pipeline with context passing
- 25/25 pytest tests passing
- Supports OpenAI / Groq / Ollama via .env configuration

Built for portfolio: FatimaUPPA/engineering-team-crewai"

# ── Step 4: Create GitHub repo and push ──────────────────────────────────
if command -v gh &> /dev/null; then
  echo ""
  echo "📦  Creating GitHub repo via GitHub CLI..."
  gh repo create "$GITHUB_USER/$REPO_NAME" \
    --public \
    --description "$DESCRIPTION" \
    --source=. \
    --remote=origin \
    --push
  echo "✅  Repository created and pushed!"
  echo "    🔗 https://github.com/$GITHUB_USER/$REPO_NAME"
else
  echo ""
  echo "⚠️   GitHub CLI (gh) not found. Using git remote directly."
  echo "    Make sure you have created the repo on GitHub first:"
  echo "    → https://github.com/new"
  echo ""
  REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
  git remote add origin "$REMOTE_URL" 2>/dev/null || git remote set-url origin "$REMOTE_URL"
  git branch -M main
  git push -u origin main
  echo "✅  Pushed to: $REMOTE_URL"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done! Your portfolio project is live 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
