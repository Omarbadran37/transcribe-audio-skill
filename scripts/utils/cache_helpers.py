"""Caching utilities for transcript storage and retrieval."""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from .constants import CACHE_DIR


def get_cache_key(source: str, source_type: str) -> str:
    """
    Generate cache key from source.

    Args:
        source: Video ID or audio URL
        source_type: 'youtube' or 'podcast'

    Returns:
        MD5 hash as cache key
    """
    content = f"{source_type}:{source}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_transcript(cache_key: str) -> Optional[Dict]:
    """
    Retrieve cached transcript by key.

    Args:
        cache_key: MD5 hash cache key

    Returns:
        Cached data dict or None if not found
    """
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        return cache_data
    except Exception:
        return None


def save_to_cache(
    cache_key: str,
    transcript: str,
    metadata: Dict
) -> None:
    """
    Save transcript to cache.

    Args:
        cache_key: MD5 hash cache key
        transcript: Transcript text
        metadata: Additional metadata (source, title, etc.)
    """
    cache_data = {
        "transcript": transcript,
        "metadata": metadata,
        "cached_at": datetime.now().isoformat(),
        "cache_key": cache_key
    }

    cache_file = CACHE_DIR / f"{cache_key}.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)


def list_cached_transcripts(limit: int = 20) -> List[Dict]:
    """
    List all cached transcripts.

    Args:
        limit: Maximum number of results

    Returns:
        List of cached transcript metadata
    """
    cache_files = sorted(
        CACHE_DIR.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]

    results = []
    for cache_file in cache_files:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            results.append({
                "cache_key": cache_data.get("cache_key", cache_file.stem),
                "cached_at": cache_data.get("cached_at", ""),
                "source_type": cache_data.get("metadata", {}).get("source_type", "unknown"),
                "title": cache_data.get("metadata", {}).get("title", "Unknown"),
                "source": cache_data.get("metadata", {}).get("source", "Unknown")
            })
        except Exception:
            continue

    return results
