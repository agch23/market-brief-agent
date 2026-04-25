"""
Entry point. Run this to produce today's brief.
GitHub Actions will execute: python agent/main.py
"""

from agent import run_agent
from brief_writer import save_brief


def main():
    print("🚀 Starting market brief agent...")
    brief = run_agent()
    print("\n📝 Final brief generated. Saving...\n")
    save_brief(brief)
    print("✅ Done.")


if __name__ == "__main__":
    main()
