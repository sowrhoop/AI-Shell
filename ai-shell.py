"""
Backward-compatible entry point. Prefer running `ai-shell` or `python -m ai_shell`.
"""

from ai_shell.cli import app

if __name__ == "__main__":
    app()
