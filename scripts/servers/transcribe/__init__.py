"""
Transcribe Server - Code Execution API

Provides importable functions for YouTube and podcast transcription
following the Anthropic code execution framework.

Quick Start:
    >>> from servers.transcribe import get_transcript, find_rss, transcribe_episode
    >>>
    >>> # YouTube
    >>> transcript = get_transcript("dQw4w9WgXcQ")
    >>>
    >>> # Podcast
    >>> feed = find_rss("Lex Fridman Podcast")
    >>> episodes = parse_rss(feed['rss_url'])
    >>> transcript = transcribe_episode(episodes[0]['audio_url'])
    >>>
    >>> # Batch (50% cost reduction)
    >>> from servers.transcribe import create_batch_transcription, get_batch_results
    >>> batch = create_batch_transcription(episodes)
    >>> results = get_batch_results(batch['job_name'])
"""

from .youtube import get_transcript
from .podcast import find_rss, parse_rss, transcribe_episode
from .cache import get_cached, list_cache
from .format import format_transcript
from .batch import (
    create_batch_transcription,
    check_batch_status,
    wait_for_batch,
    get_batch_results,
    cancel_batch,
    list_batch_jobs
)

__all__ = [
    # YouTube
    'get_transcript',

    # Podcast
    'find_rss',
    'parse_rss',
    'transcribe_episode',

    # Cache
    'get_cached',
    'list_cache',

    # Formatting
    'format_transcript',

    # Batch (50% cost reduction)
    'create_batch_transcription',
    'check_batch_status',
    'wait_for_batch',
    'get_batch_results',
    'cancel_batch',
    'list_batch_jobs',
]
