"""
Saves the brief markdown to the briefs/ folder with a date-stamped filename.
"""

import os
from datetime import datetime
import pytz
from config import BRIEF_TIMEZONE


def save_brief(markdown_content):
    """
    Saves brief as briefs/YYYY-MM-DD.md.
    Returns the filepath written.
    """
    tz = pytz.timezone(BRIEF_TIMEZONE)
    today = datetime.now(tz).strftime("%Y-%m-%d")

    # Repo root is one level up from agent/
    briefs_dir = os.path.join(os.path.dirname(__file__), "..", "briefs")
    os.makedirs(briefs_dir, exist_ok=True)

    filepath = os.path.join(briefs_dir, f"{today}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"✅ Brief saved: {filepath}")
    return filepath
