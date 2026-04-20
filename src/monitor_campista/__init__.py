"""Thin entry point for `uv run dashboard`. Invokes streamlit via subprocess
to avoid importing dashboard.py (which has module-level Streamlit calls)."""

import subprocess
import sys
from pathlib import Path


def run_dashboard():
    dashboard = Path(__file__).parent / "dashboard.py"
    raise SystemExit(
        subprocess.call([sys.executable, "-m", "streamlit", "run", str(dashboard)])
    )

