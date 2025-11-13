"""Transcript formatting utilities."""

import sys
from pathlib import Path

# Ensure parent paths are in sys.path for proper imports
scripts_path = Path(__file__).parent.parent.parent
utils_path = scripts_path / "utils"

for path in [str(scripts_path), str(utils_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Now import from utils with proper path setup
from utils.gemini_helpers import format_transcript

__all__ = ['format_transcript']
