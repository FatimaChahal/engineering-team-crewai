"""
main.py
─────────────────────────────────────────────────────────────────────────────
Entry point for the 4-Agent Engineering Team.

Run:
    python main.py                    # interactive prompt
    python main.py "your app idea"    # direct from CLI argument
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv


def main():
    # ── Load environment ──────────────────────────────────────────────────
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅  Loaded config from .env  (MODEL={os.getenv('MODEL', 'not set')})")
    else:
        print("⚠️   No .env file found. Copy .env.example → .env and set your API key.")
        print("    Using default MODEL from environment (if set).\n")

    # ── Import crew (after env is loaded) ────────────────────────────────
    from crew import EngineeringTeam

    # ── Get user request ─────────────────────────────────────────────────
    if len(sys.argv) > 1:
        # Passed as CLI argument
        user_request = " ".join(sys.argv[1:])
    else:
        # Interactive prompt
        print("\n" + "─" * 60)
        print("  🤖  4-Agent AI Engineering Team")
        print("─" * 60)
        print("  Describe the app you want to build.")
        print("  Examples:")
        print("    • A FastAPI REST API for managing a book collection")
        print("    • A CLI tool to monitor CPU/RAM usage in real time")
        print("    • A Python script that scrapes Hacker News top stories")
        print("─" * 60)
        user_request = input("\n  Your app idea: ").strip()

    if not user_request:
        print("❌  No request provided. Exiting.")
        sys.exit(1)

    # ── Run the pipeline ─────────────────────────────────────────────────
    team = EngineeringTeam()
    results = team.build(user_request)

    # ── Final summary ─────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  📦  Pipeline Complete!")
    print("═" * 60)
    print(f"  Output directory : {results['output_dir']}")
    print(f"  Files generated  :")
    output_dir = Path(results["output_dir"])
    for f in sorted(output_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(output_dir)
            print(f"    ├── {rel}")
    print("═" * 60)


if __name__ == "__main__":
    main()
