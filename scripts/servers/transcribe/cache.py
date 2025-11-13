"""Cache management tools for transcripts."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.cache_helpers import get_cached_transcript, list_cached_transcripts


def get_cached(cache_key: str) -> dict | None:
    """
    Retrieve a cached transcript by its cache key.

    Args:
        cache_key: 32-character MD5 hash cache key

    Returns:
        Dictionary with transcript and metadata, or None if not found

    Example:
        >>> cached = get_cached("abc123...")
        >>> if cached:
        ...     print(cached['transcript'])
    """
    cached = get_cached_transcript(cache_key)

    if not cached:
        return {
            "found": False,
            "cache_key": cache_key,
            "message": f"No cached transcript found with key '{cache_key}'. Use list_cache() to see available transcripts."
        }

    return {
        "found": True,
        "cache_key": cache_key,
        "cached_at": cached.get('cached_at', 'Unknown'),
        "source_type": cached.get('metadata', {}).get('source_type', 'unknown'),
        "title": cached.get('metadata', {}).get('title', 'Unknown'),
        "source": cached.get('metadata', {}).get('source', 'Unknown'),
        "transcript": cached.get('transcript', '')
    }


def list_cache(limit: int = 20) -> list:
    """
    List all cached transcripts.

    Args:
        limit: Maximum number of results to return (1-100)

    Returns:
        List of dictionaries with cache metadata

    Example:
        >>> cached = list_cache(limit=10)
        >>> for item in cached:
        ...     print(f"{item['title']}: {item['cache_key']}")
    """
    transcripts = list_cached_transcripts(limit)

    if not transcripts:
        return []

    return transcripts
