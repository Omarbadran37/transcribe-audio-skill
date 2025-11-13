"""YouTube transcript extraction and formatting utilities."""

import re
import json
from typing import List, Dict


def extract_video_id(url_or_id: str) -> str:
    """
    Extract YouTube video ID from URL or validate ID format.

    Supports multiple URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - Raw VIDEO_ID (11 characters)

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        Validated 11-character video ID

    Raises:
        ValueError: If URL/ID format is invalid
    """
    # Remove whitespace
    url_or_id = url_or_id.strip()

    # Patterns to match YouTube URLs
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',  # Standard watch URL
        r'youtu\.be/([0-9A-Za-z_-]{11})',   # Short URL
        r'embed/([0-9A-Za-z_-]{11})',        # Embed URL
        r'^([0-9A-Za-z_-]{11})$'             # Raw ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise ValueError(
        f"Invalid YouTube URL or video ID: '{url_or_id}'. "
        "Please provide either a valid YouTube URL or an 11-character video ID."
    )


def format_youtube_transcript_markdown(
    transcript_data: List[Dict],
    video_id: str,
    include_timestamps: bool
) -> str:
    """Format YouTube transcript as Markdown."""
    if not transcript_data:
        return f"# YouTube Transcript\n\n**Video ID**: {video_id}\n\nNo transcript data available."

    total_duration = transcript_data[-1]['start'] + transcript_data[-1]['duration']
    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)

    lines = [
        f"# YouTube Transcript",
        f"",
        f"**Video ID**: {video_id}",
        f"**Total Entries**: {len(transcript_data)}",
        f"**Duration**: {minutes}:{seconds:02d}",
        f"",
        f"## Transcript",
        f""
    ]

    for entry in transcript_data:
        entry_minutes = int(entry['start'] // 60)
        entry_seconds = int(entry['start'] % 60)

        if include_timestamps:
            lines.append(f"**[{entry_minutes:02d}:{entry_seconds:02d}]** {entry['text']}")
        else:
            lines.append(f"{entry['text']}")

    return "\n".join(lines)


def format_youtube_transcript_json(
    transcript_data: List[Dict],
    video_id: str
) -> str:
    """Format YouTube transcript as JSON."""
    total_duration = transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0

    return json.dumps({
        "video_id": video_id,
        "total_entries": len(transcript_data),
        "duration_seconds": total_duration,
        "transcript": transcript_data
    }, indent=2)
