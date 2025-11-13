"""YouTube transcript extraction tool."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.youtube_helpers import (
    extract_video_id,
    format_youtube_transcript_markdown,
    format_youtube_transcript_json
)
from utils.cache_helpers import get_cache_key, get_cached_transcript, save_to_cache

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None


def get_transcript(
    video_url_or_id: str,
    include_timestamps: bool = True,
    use_cache: bool = True,
    format_json: bool = False
) -> str:
    """
    Extract transcript from a YouTube video.

    Args:
        video_url_or_id: YouTube video URL or 11-character ID
        include_timestamps: Include timestamps in markdown format
        use_cache: Check cache before fetching from YouTube
        format_json: Return JSON format instead of markdown

    Returns:
        Formatted transcript as markdown or JSON string

    Raises:
        ImportError: If youtube-transcript-api not installed
        ValueError: If video ID format is invalid
        Exception: If transcript extraction fails

    Example:
        >>> transcript = get_transcript("dQw4w9WgXcQ")
        >>> print(transcript)
        # YouTube Transcript
        **Video ID**: dQw4w9WgXcQ
        ...
    """
    if YouTubeTranscriptApi is None:
        raise ImportError(
            "youtube-transcript-api not installed. "
            "Install with: pip install youtube-transcript-api"
        )

    try:
        # Extract video ID from URL or validate ID
        video_id = extract_video_id(video_url_or_id)

        # Check cache if requested
        cache_key = get_cache_key(video_id, "youtube")

        if use_cache:
            cached = get_cached_transcript(cache_key)
            if cached:
                # Return cached transcript
                if format_json:
                    import json
                    return json.dumps({
                        "video_id": video_id,
                        "transcript": cached.get("transcript", ""),
                        "cache_key": cache_key,
                        "cached_at": cached.get("cached_at", ""),
                        "metadata": cached.get("metadata", {})
                    }, indent=2)
                else:
                    return f"# YouTube Transcript (Cached)\n\n**Video ID**: {video_id}\n**Cache Key**: {cache_key}\n**Cached At**: {cached.get('cached_at', 'Unknown')}\n\n## Transcript\n\n{cached.get('transcript', '')}"

        # Fetch transcript from YouTube
        api = YouTubeTranscriptApi()
        transcript_raw = api.fetch(video_id)

        # Convert to dict format
        transcript_list = [
            {
                'text': entry.text,
                'start': entry.start,
                'duration': entry.duration
            }
            for entry in transcript_raw
        ]

        # Format transcript
        if format_json:
            formatted = format_youtube_transcript_json(transcript_list, video_id)
        else:
            formatted = format_youtube_transcript_markdown(
                transcript_list,
                video_id,
                include_timestamps
            )

        # Save to cache
        save_to_cache(
            cache_key,
            formatted,
            {
                "source_type": "youtube",
                "source": video_id,
                "title": f"YouTube Video {video_id}",
                "format": "json" if format_json else "markdown"
            }
        )

        # Add cache key to response
        if format_json:
            import json
            data = json.loads(formatted)
            data['cache_key'] = cache_key
            return json.dumps(data, indent=2)
        else:
            return f"{formatted}\n\n---\n**Cache Key**: `{cache_key}`"

    except Exception as e:
        error_type = type(e).__name__

        if "TranscriptsDisabled" in error_type:
            raise Exception("This video has captions disabled. Please try a different video with captions enabled.")
        elif "VideoUnavailable" in error_type:
            raise Exception("Video not found. Please check the video ID/URL is correct and the video exists.")
        elif "NoTranscriptFound" in error_type:
            raise Exception("No transcript available for this video in any language.")
        else:
            raise Exception(f"YouTube transcript extraction failed: {error_type} - {str(e)}")
