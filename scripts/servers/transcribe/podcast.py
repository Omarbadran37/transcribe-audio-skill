"""Podcast RSS discovery and transcription tools."""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.podcast_helpers import (
    find_podcast_rss_feed,
    parse_rss_feed,
    download_audio_file
)
from utils.gemini_helpers import get_gemini_api_key, transcribe_audio_gemini
from utils.cache_helpers import get_cache_key, get_cached_transcript, save_to_cache
from utils.constants import CACHE_DIR, OUTPUT_DIR


def find_rss(podcast_name: str) -> dict:
    """
    Find RSS feed URL for a podcast by name.

    Searches multiple sources: Podcastindex, Apple Podcasts, common hosting platforms.

    Args:
        podcast_name: Name of the podcast (e.g., "Lex Fridman Podcast")

    Returns:
        Dictionary with RSS feed info or error message

    Example:
        >>> feed = find_rss("How I Built This")
        >>> print(feed['rss_url'])
        https://feeds.megaphone.fm/...
    """
    result = find_podcast_rss_feed(podcast_name)

    if not result:
        return {
            "found": False,
            "podcast_name": podcast_name,
            "message": f"Could not find RSS feed for '{podcast_name}'. Try:\n1. Checking the exact podcast name\n2. Searching on Apple Podcasts or Spotify first\n3. Using a different search term"
        }

    return {
        "found": True,
        "podcast_name": podcast_name,
        "rss_url": result['rss_url'],
        "title": result.get('title', podcast_name),
        "description": result.get('description', ''),
        "source": result.get('source', 'Unknown')
    }


def parse_rss(rss_url: str, max_episodes: int = 10) -> list:
    """
    Parse podcast RSS feed and list episodes.

    Args:
        rss_url: URL to podcast RSS feed
        max_episodes: Maximum number of episodes to return (1-50)

    Returns:
        List of episode dictionaries with title, audio_url, pub_date, duration

    Example:
        >>> episodes = parse_rss("https://feeds.megaphone.fm/lexfridmanpodcast")
        >>> print(episodes[0]['title'])
        Latest Episode Title
    """
    try:
        episodes = parse_rss_feed(rss_url, max_episodes)

        if not episodes:
            return []

        return episodes

    except Exception as e:
        raise Exception(f"RSS feed parsing failed: {str(e)}")


def transcribe_episode(
    audio_url: str,
    episode_title: Optional[str] = None,
    include_timestamps: bool = True,
    speaker_diarization: bool = True,
    save_to_disk: bool = True,
    use_cache: bool = True
) -> str:
    """
    Transcribe a podcast episode from audio URL.

    Uses Google Gemini for transcription with speaker diarization.
    Processing time: 2-5 minutes for 60-minute episodes.

    Args:
        audio_url: Direct URL to audio file (.mp3, .m4a, .wav)
        episode_title: Optional episode title for metadata
        include_timestamps: Include [MM:SS] timestamps
        speaker_diarization: Identify speakers (Speaker A, B, C, etc.)
        save_to_disk: Save transcript to ~/.cache/transcribe_mcp/transcripts/
        use_cache: Check cache before processing

    Returns:
        Formatted transcript with metadata

    Raises:
        ValueError: If GOOGLE_API_KEY not set
        Exception: If download or transcription fails

    Example:
        >>> transcript = transcribe_episode(
        ...     "https://audio.megaphone.fm/episode.mp3",
        ...     episode_title="Episode 1"
        ... )
        >>> print(transcript)
        # Podcast Transcript
        **Episode**: Episode 1
        ...
        [00:00] Speaker A: Introduction...
    """
    try:
        # Check cache if requested
        cache_key = get_cache_key(audio_url, "podcast")

        if use_cache:
            cached = get_cached_transcript(cache_key)
            if cached:
                return f"# Podcast Transcript (Cached)\n\n**Episode**: {cached.get('metadata', {}).get('title', 'Unknown')}\n**Cache Key**: {cache_key}\n**Cached At**: {cached.get('cached_at', 'Unknown')}\n\n## Transcript\n\n{cached.get('transcript', '')}"

        # Get Gemini API key
        api_key = get_gemini_api_key()

        # Download audio file
        print(f"Downloading audio from {audio_url}...")
        audio_path = download_audio_file(
            audio_url,
            CACHE_DIR,
            episode_title
        )

        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"Downloaded {file_size_mb:.1f} MB audio file")

        # Transcribe audio
        print(f"Transcribing with Google Gemini (this may take 2-5 minutes)...")
        transcript = transcribe_audio_gemini(
            audio_path,
            api_key,
            include_timestamps,
            speaker_diarization
        )

        # Save to disk if requested
        saved_path = None
        if save_to_disk:
            if episode_title:
                safe_title = "".join(c for c in episode_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:100]
            else:
                safe_title = f"podcast_{int(time.time())}"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_path = OUTPUT_DIR / f"{safe_title}_{timestamp}.txt"

            with open(transcript_path, 'w', encoding='utf-8') as f:
                header = f"""{'='*80}
PODCAST TRANSCRIPTION
{'='*80}
Title: {episode_title or 'Unknown'}
Audio URL: {audio_url}
Transcribed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Timestamps: {include_timestamps}
Speaker Diarization: {speaker_diarization}
{'='*80}

"""
                f.write(header)
                f.write(transcript)

            saved_path = str(transcript_path)
            print(f"Transcript saved to: {saved_path}")

        # Save to cache
        save_to_cache(
            cache_key,
            transcript,
            {
                "source_type": "podcast",
                "source": audio_url,
                "title": episode_title or "Unknown",
                "format": "markdown",
                "include_timestamps": include_timestamps,
                "speaker_diarization": speaker_diarization,
                "saved_to": saved_path
            }
        )

        # Clean up downloaded audio file
        try:
            audio_path.unlink()
        except Exception:
            pass

        # Format response
        lines = [
            f"# Podcast Transcript",
            f"",
            f"**Episode**: {episode_title or 'Unknown'}",
            f"**Audio URL**: {audio_url}",
            f"**Transcribed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if saved_path:
            lines.append(f"**Saved To**: {saved_path}")

        lines.extend([
            f"**Cache Key**: `{cache_key}`",
            f"",
            f"## Transcript",
            f"",
            transcript
        ])

        return "\n".join(lines)

    except Exception as e:
        raise Exception(f"Podcast transcription failed: {str(e)}")
