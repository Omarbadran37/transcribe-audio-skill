"""Automatic .env file loader for transcribe skill."""

import os
from pathlib import Path


def load_env():
    """
    Load environment variables from .env file if it exists.

    Looks for .env file in the skill root directory:
    ~/.claude/skills/transcribe-audio/.env
    """
    # Get skill root directory (parent of scripts/)
    skill_root = Path(__file__).parent.parent
    env_file = skill_root / ".env"

    if not env_file.exists():
        return

    # Read .env file and set environment variables
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key and value and value != 'your-api-key-here':
                        if key not in os.environ:
                            os.environ[key] = value
    except Exception:
        # Silently ignore errors reading .env file
        pass


# Auto-load on import
load_env()
