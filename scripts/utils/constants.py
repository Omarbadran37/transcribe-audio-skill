"""Constants and configuration for transcription operations."""

from pathlib import Path

# Directory constants
CACHE_DIR = Path.home() / ".cache" / "transcribe_mcp"
OUTPUT_DIR = CACHE_DIR / "transcripts"
CHARACTER_LIMIT = 25000

# Gemini constants
GEMINI_FILE_SIZE_THRESHOLD = 20 * 1024 * 1024  # 20MB

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
