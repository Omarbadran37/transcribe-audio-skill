# Transcribe Audio - API Reference

Complete API documentation for all transcription functions.

## Setup

```python
import sys
from pathlib import Path

# Add skill to path
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))

# Import functions
from servers.transcribe import (
    get_transcript,
    find_rss,
    parse_rss,
    transcribe_episode,
    get_cached,
    list_cache,
    format_transcript
)
```

## YouTube Transcription

### `get_transcript()`

Extract transcript from a YouTube video.

**Signature:**
```python
def get_transcript(
    video_url_or_id: str,
    include_timestamps: bool = True,
    use_cache: bool = True,
    format_json: bool = False
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_url_or_id` | str | *required* | YouTube video URL or 11-character video ID |
| `include_timestamps` | bool | `True` | Include [MM:SS] timestamps in markdown format |
| `use_cache` | bool | `True` | Check cache before fetching from YouTube API |
| `format_json` | bool | `False` | Return JSON format instead of markdown |

**Returns:** `str` - Formatted transcript (markdown or JSON)

**Raises:**
- `ImportError` - If youtube-transcript-api package not installed
- `ValueError` - If video ID format is invalid
- `Exception` - If video has captions disabled, video unavailable, or no transcript found

**Example:**
```python
# Basic usage
transcript = get_transcript("dQw4w9WgXcQ")

# Full URL
transcript = get_transcript("https://youtube.com/watch?v=i43kYARbSGM")

# JSON format
transcript = get_transcript("dQw4w9WgXcQ", format_json=True)
```

**Output Format (Markdown):**
```markdown
# YouTube Transcript

**Video ID**: dQw4w9WgXcQ
**Total Entries**: 1353
**Duration**: 52:36

## Transcript

**[00:00]** Introduction text here...
**[00:15]** More transcript content...

---
**Cache Key**: `abc123...`
```

**Output Format (JSON):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "total_entries": 1353,
  "duration_seconds": 3156,
  "transcript": [...],
  "cache_key": "abc123..."
}
```

---

## Podcast Discovery

### `find_rss()`

Find RSS feed URL for a podcast by name.

**Signature:**
```python
def find_rss(podcast_name: str) -> dict
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `podcast_name` | str | *required* | Podcast name to search for |

**Returns:** `dict` - Feed information or error message

**Success Response:**
```python
{
    "found": True,
    "podcast_name": "How I Built This",
    "rss_url": "https://feeds.megaphone.fm/...",
    "title": "How I Built This with Guy Raz",
    "description": "Brief description...",
    "source": "Podcastindex"  # or "Apple Podcasts", "Megaphone", etc.
}
```

**Failure Response:**
```python
{
    "found": False,
    "podcast_name": "Unknown Podcast",
    "message": "Could not find RSS feed for 'Unknown Podcast'. Try:..."
}
```

**Search Strategy:**
1. Podcastindex.org API
2. Apple Podcasts API
3. Common hosting platforms (Megaphone, Anchor, Podbean)

**Example:**
```python
feed = find_rss("Lex Fridman Podcast")
if feed['found']:
    print(feed['rss_url'])
else:
    print(feed['message'])
```

---

### `parse_rss()`

Parse podcast RSS feed and list episodes.

**Signature:**
```python
def parse_rss(
    rss_url: str,
    max_episodes: int = 10
) -> list
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rss_url` | str | *required* | RSS feed URL |
| `max_episodes` | int | `10` | Maximum episodes to return (1-50) |

**Returns:** `list[dict]` - List of episode dictionaries

**Episode Dictionary Format:**
```python
{
    "title": "Episode Title",
    "audio_url": "https://audio.megaphone.fm/...",
    "pub_date": "Mon, 01 Jan 2024 12:00:00 GMT",
    "duration": "1:23:45",
    "description": "Episode description (first 200 chars)..."
}
```

**Raises:**
- `Exception` - If RSS feed URL is invalid or parsing fails

**Example:**
```python
episodes = parse_rss("https://feeds.megaphone.fm/lexfridmanpodcast", max_episodes=5)

for i, ep in enumerate(episodes):
    print(f"{i+1}. {ep['title']}")
    print(f"   Duration: {ep['duration']}")
    print(f"   Audio: {ep['audio_url']}")
```

---

## Podcast Transcription

### `transcribe_episode()`

Transcribe podcast episode using Google Gemini.

**Signature:**
```python
def transcribe_episode(
    audio_url: str,
    episode_title: str | None = None,
    include_timestamps: bool = True,
    speaker_diarization: bool = True,
    save_to_disk: bool = True,
    use_cache: bool = True
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_url` | str | *required* | Direct URL to audio file (.mp3, .m4a, .wav) |
| `episode_title` | str | `None` | Episode title for metadata and filename |
| `include_timestamps` | bool | `True` | Include [MM:SS] timestamps in output |
| `speaker_diarization` | bool | `True` | Identify speakers (Speaker A, B, C, etc.) |
| `save_to_disk` | bool | `True` | Save transcript to ~/.cache/transcribe_mcp/transcripts/ |
| `use_cache` | bool | `True` | Check cache before processing |

**Returns:** `str` - Markdown formatted transcript with metadata

**Raises:**
- `ValueError` - If GOOGLE_API_KEY environment variable not set
- `Exception` - If download fails, transcription fails, or API error

**Processing Time:** 2-5 minutes for 60-minute episodes

**Environment Requirements:**
```python
import os
os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
```

**Example:**
```python
transcript = transcribe_episode(
    "https://audio.megaphone.fm/episode.mp3",
    episode_title="Episode 1: Building Babylist",
    include_timestamps=True,
    speaker_diarization=True
)
```

**Output Format:**
```markdown
# Podcast Transcript

**Episode**: Episode 1: Building Babylist
**Audio URL**: https://audio.megaphone.fm/episode.mp3
**Transcribed**: 2024-01-15 10:30:00
**Saved To**: /Users/name/.cache/transcribe_mcp/transcripts/Episode_1_20240115_103000.txt
**Cache Key**: `abc123...`

## Transcript

[00:00] Speaker A: Welcome to How I Built This...
[00:15] Speaker B: Thank you for having me...
[02:30] Speaker A: So let's start from the beginning...
```

---

## Cache Management

### `get_cached()`

Retrieve cached transcript by cache key.

**Signature:**
```python
def get_cached(cache_key: str) -> dict | None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cache_key` | str | *required* | 32-character MD5 hash cache key |

**Returns:** `dict` - Cached transcript data or error message

**Success Response:**
```python
{
    "found": True,
    "cache_key": "abc123...",
    "cached_at": "2024-01-15T10:30:00",
    "source_type": "youtube",  # or "podcast"
    "title": "YouTube Video dQw4w9WgXcQ",
    "source": "dQw4w9WgXcQ",
    "transcript": "Full transcript text..."
}
```

**Failure Response:**
```python
{
    "found": False,
    "cache_key": "invalid123...",
    "message": "No cached transcript found with key 'invalid123...'"
}
```

**Example:**
```python
result = get_cached("abc123...")
if result['found']:
    print(result['transcript'])
else:
    print(result['message'])
```

---

### `list_cache()`

List all cached transcripts.

**Signature:**
```python
def list_cache(limit: int = 20) -> list
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | `20` | Maximum results to return (1-100) |

**Returns:** `list[dict]` - List of cache metadata dictionaries (most recent first)

**Cache Item Format:**
```python
{
    "cache_key": "abc123...",
    "cached_at": "2024-01-15T10:30:00",
    "source_type": "youtube",
    "title": "YouTube Video dQw4w9WgXcQ",
    "source": "dQw4w9WgXcQ"
}
```

**Example:**
```python
cached = list_cache(limit=10)

for item in cached:
    print(f"[{item['source_type']}] {item['title']}")
    print(f"  Key: {item['cache_key']}")
    print(f"  Cached: {item['cached_at']}")
```

---

## Transcript Formatting

### `format_transcript()`

Format raw transcript into clean, professional document using Google Gemini.

**Signature:**
```python
def format_transcript(
    raw_transcript: str,
    api_key: str = None,
    title: str = None,
    include_timestamps: bool = True,
    clean_filler_words: bool = True,
    detect_sections: bool = True
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `raw_transcript` | str | *required* | Raw transcript text to format |
| `api_key` | str | `None` | Google AI API key (uses GOOGLE_API_KEY env if not provided) |
| `title` | str | `None` | Document title (auto-generated if None) |
| `include_timestamps` | bool | `True` | Include [MM:SS] timestamps in output |
| `clean_filler_words` | bool | `True` | Remove filler words (um, uh, you know) |
| `detect_sections` | bool | `True` | Insert section headings based on topics |

**Returns:** `str` - Formatted markdown document

**Raises:**
- `ImportError` - If google-genai package not installed
- `ValueError` - If GOOGLE_API_KEY not set and api_key not provided

**Features:**
- Creates descriptive title (auto-generated or custom)
- Identifies all speakers (e.g., Alex, Michael, John)
- Formats dialogue as bullet points with bold speaker names
- Inserts section headings based on conversation flow
- Corrects grammar, spelling, and punctuation
- Removes filler words while preserving meaning
- Preserves timestamps in [MM:SS] format

**Example:**
```python
# Get raw transcript
raw = get_transcript("video-id")

# Format with all options
formatted = format_transcript(
    raw,
    title="MCP Server Discussion",
    include_timestamps=True,
    clean_filler_words=True,
    detect_sections=True
)

print(formatted)
```

**Output Format:**
```markdown
# MCP Server Discussion

## Introduction

* **Alex:** [00:00] Welcome everyone to today's discussion about MCP servers.
* **Michael:** [00:15] Thanks for having me. I'm excited to talk about this topic.

## What is MCP?

* **Alex:** [01:30] Let's start with the basics. What exactly is MCP?
* **Michael:** [01:45] MCP stands for Model Context Protocol. It's a way to...

## Implementation Details

* **John:** [05:20] How would someone get started implementing this?
* **Alex:** [05:35] Great question. The first step is to...

## Future of MCP

* **Michael:** [15:20] Where do you see this technology going?
* **Alex:** [15:35] I think we'll see widespread adoption in the next year...
```

**Use Cases:**
- Clean up messy transcripts for sharing
- Create professional documentation from interviews
- Format podcast transcripts for blog posts
- Generate readable meeting notes
- Prepare transcripts for publication

**Integration Example:**
```python
# Transcribe and format in one workflow
raw_transcript = transcribe_episode(
    audio_url,
    speaker_diarization=True,
    include_timestamps=True
)

# Format the result
formatted = format_transcript(
    raw_transcript,
    title="Podcast Episode 42",
    clean_filler_words=True,
    detect_sections=True
)

# Save to file
with open('formatted_transcript.md', 'w') as f:
    f.write(formatted)
```

**Tips:**
- Use `title=None` to let Gemini generate a descriptive title
- Set `clean_filler_words=False` to preserve exact wording
- Set `detect_sections=False` for simple, flat transcripts
- Works with both YouTube and podcast transcripts

---

## Error Handling

### Common Errors

#### YouTube Errors

**TranscriptsDisabled:**
```python
try:
    transcript = get_transcript("video-id")
except Exception as e:
    if "TranscriptsDisabled" in str(e):
        print("This video has captions disabled")
```

**VideoUnavailable:**
```python
try:
    transcript = get_transcript("invalid-id")
except Exception as e:
    if "VideoUnavailable" in str(e):
        print("Video not found")
```

**NoTranscriptFound:**
```python
try:
    transcript = get_transcript("video-id")
except Exception as e:
    if "NoTranscriptFound" in str(e):
        print("No transcript available")
```

#### Podcast Errors

**Missing API Key:**
```python
try:
    transcript = transcribe_episode(audio_url)
except ValueError as e:
    if "Google API key is required" in str(e):
        import os
        os.environ['GOOGLE_API_KEY'] = 'your-key'
```

**RSS Parsing Failed:**
```python
try:
    episodes = parse_rss("invalid-rss-url")
except Exception as e:
    if "RSS feed parsing failed" in str(e):
        print("Invalid RSS feed URL")
```

#### Cache Errors

**Not Found:**
```python
result = get_cached("nonexistent-key")
if not result['found']:
    print("Cache miss - transcript not cached")
```

---

## Best Practices

### 1. Always Check Cache First

```python
# Check cache before expensive operations
cached = list_cache()
cache_keys = [c['cache_key'] for c in cached]

if target_cache_key in cache_keys:
    result = get_cached(target_cache_key)
else:
    # Process fresh transcript
    transcript = get_transcript(video_id)
```

### 2. Error Handling

```python
try:
    transcript = get_transcript(video_id)
except ImportError:
    print("Install: pip install youtube-transcript-api")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### 3. Environment Setup

```python
import os
from pathlib import Path

# API key
if 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = Path.home() / ".env"

# Path setup
import sys
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))
```

### 4. Processing Large Transcripts

```python
# Get transcript
transcript = get_transcript(video_id, include_timestamps=False)

# Process in chunks
lines = transcript.split('\n')
chunks = [lines[i:i+100] for i in range(0, len(lines), 100)]

# Return only relevant parts
for chunk in chunks:
    relevant = [l for l in chunk if 'keyword' in l.lower()]
    if relevant:
        print('\n'.join(relevant))
```

---

## Cache Details

### Cache Location
`~/.cache/transcribe_mcp/`

### Cache Structure
```
~/.cache/transcribe_mcp/
├── abc123...json  # Cached YouTube transcript
├── def456...json  # Cached podcast transcript
└── transcripts/
    ├── Episode_1_20240115_103000.txt
    └── Episode_2_20240115_110000.txt
```

### Cache File Format
```json
{
  "transcript": "Full transcript text...",
  "metadata": {
    "source_type": "youtube",
    "source": "dQw4w9WgXcQ",
    "title": "YouTube Video dQw4w9WgXcQ",
    "format": "markdown"
  },
  "cached_at": "2024-01-15T10:30:00",
  "cache_key": "abc123..."
}
```

### Clear Cache
```bash
# Clear all cached transcripts
rm -rf ~/.cache/transcribe_mcp/*.json

# Clear saved transcript files
rm -rf ~/.cache/transcribe_mcp/transcripts/*
```
