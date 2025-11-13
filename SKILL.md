---
name: transcribe-audio
description: Extract transcripts from YouTube videos and podcasts via importable Python functions. Use when users mention YouTube transcripts, podcast transcription, audio transcription, video captions, batch processing audio, or need to programmatically process transcripts in Python code execution environment. Functions follow the Anthropic code execution framework for data processing and state management.
---

# Transcribe Audio (Code Execution)

## Overview

This skill provides Python functions for transcribing YouTube videos and podcast episodes through direct code execution. Functions can be imported and called like any Python module, enabling data processing, filtering, and state management in the execution environment.

**Key Benefits:**
- **No MCP required** - Direct function imports
- **Data processing** - Filter/transform transcripts before returning
- **Privacy-preserving** - Data stays in execution environment
- **Token efficient** - Process results locally
- **State persistent** - Save intermediate results to files
- **Batch processing** - 50% cost reduction on large transcription jobs

**When to use this skill:**
- User asks for a YouTube video transcript
- User wants to transcribe a podcast episode
- User needs to find podcast RSS feeds or episodes
- User wants to process or filter transcripts programmatically
- User needs to manage transcript cache
- User needs to transcribe multiple episodes/videos (use batch API for cost savings)

## Installation

Set up the skill's Python environment:

```python
import sys
import os
from pathlib import Path

# Add skill scripts to path
skill_path = Path.home() / ".claude/skills/transcribe-audio/scripts"
sys.path.insert(0, str(skill_path))

# Set Google Gemini API key (required for podcast transcription)
os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
```

Install dependencies (if not already installed):

```bash
cd ~/.claude/skills/transcribe-audio/scripts
pip install -r requirements.txt
```

## Quick Start

### Import Functions

```python
from servers.transcribe import (
    # YouTube & Podcast
    get_transcript,           # YouTube transcription
    find_rss,                 # Find podcast RSS feeds
    parse_rss,                # List podcast episodes
    transcribe_episode,       # Transcribe podcast audio

    # Cache Management
    get_cached,               # Retrieve cached transcript
    list_cache,               # List all cached transcripts

    # Batch Processing (50% cost reduction)
    create_batch_transcription,  # Submit batch job
    check_batch_status,          # Check job progress
    wait_for_batch,              # Wait for completion
    get_batch_results,           # Retrieve results
    cancel_batch,                # Cancel job
    list_batch_jobs              # List all batch jobs
)
```

### Basic Examples

**YouTube Transcription:**
```python
# Extract YouTube transcript
transcript = get_transcript("dQw4w9WgXcQ")
print(transcript)

# With custom options
transcript = get_transcript(
    "https://youtube.com/watch?v=i43kYARbSGM",
    include_timestamps=True,
    use_cache=True
)
```

**Podcast Transcription:**
```python
# Find podcast RSS feed
feed = find_rss("Lex Fridman Podcast")
if feed['found']:
    # List episodes
    episodes = parse_rss(feed['rss_url'], max_episodes=5)

    # Transcribe first episode
    transcript = transcribe_episode(
        episodes[0]['audio_url'],
        episode_title=episodes[0]['title'],
        speaker_diarization=True
    )
    print(transcript)
```

**Batch Transcription (50% Cost Reduction):**
```python
# Create batch job for multiple episodes
episodes = parse_rss(feed['rss_url'], max_episodes=10)

# Submit batch
batch = create_batch_transcription(
    audio_items=[
        {
            'audio_url': ep['audio_url'],
            'episode_title': ep['title']
        }
        for ep in episodes
    ]
)

print(f"Batch job created: {batch['job_name']}")

# Wait for completion (processes asynchronously)
results = wait_for_batch(batch['job_name'], timeout_hours=24)

# Access results
for result in results:
    print(f"{result['title']}: {len(result['transcript'])} chars")
```

**Cache Management:**
```python
# List cached transcripts
cached = list_cache(limit=10)
for item in cached:
    print(f"{item['title']}: {item['cache_key']}")

# Retrieve cached transcript
if cached:
    result = get_cached(cached[0]['cache_key'])
    if result['found']:
        print(result['transcript'])
```

## Function Overview

### YouTube & Podcast
- `get_transcript()` - Extract YouTube transcripts with timestamps
- `find_rss()` - Find podcast RSS feeds by name
- `parse_rss()` - List podcast episodes from RSS feed
- `transcribe_episode()` - Transcribe podcast audio with speaker diarization

### Cache Management
- `get_cached()` - Retrieve cached transcript by cache key
- `list_cache()` - List all cached transcripts with metadata

### Batch Processing (50% Cost Savings)
- `create_batch_transcription()` - Submit batch transcription job
- `check_batch_status()` - Check batch job status
- `wait_for_batch()` - Wait for batch completion and retrieve results
- `get_batch_results()` - Retrieve results from completed batch
- `cancel_batch()` - Cancel running batch job
- `list_batch_jobs()` - List all batch jobs with status

**For complete API documentation with all parameters, return types, and examples**, see [references/api_reference.md](references/api_reference.md).

## Key Features

### Batch Processing
Process multiple episodes with **50% cost reduction** using Google's Batch API. Ideal for transcribing 10+ episodes or entire podcast series.

**Cost Comparison:**
- Individual calls: $0.04 per minute of audio
- Batch API: $0.02 per minute of audio (50% savings)

**When to use batch:**
- Transcribing 5+ episodes
- Not time-sensitive (24-hour processing window)
- Processing entire podcast series
- Running overnight jobs

See [references/batch_transcription.md](references/batch_transcription.md) for complete batch processing guide.

### Caching
Automatic caching prevents redundant processing:
- Cache location: `~/.cache/transcribe_mcp/`
- Persists across sessions
- Default: `use_cache=True` for all functions

### Speaker Diarization
Identify and label different speakers in podcast transcripts:
```python
transcript = transcribe_episode(
    audio_url,
    speaker_diarization=True  # Enable speaker labels
)
```

Output includes speaker labels:
```
[00:00] Speaker A: Welcome to the show...
[00:15] Speaker B: Thanks for having me...
```

### Token Efficient Processing
Process and filter transcripts in execution environment before returning results:
```python
# Get full transcript
transcript = get_transcript("video-id")

# Extract only lines with specific keywords (processed locally)
relevant_lines = [
    line for line in transcript.split('\n')
    if 'keyword' in line.lower()
]

# Return only relevant content (saves tokens)
print('\n'.join(relevant_lines))
```

## Reference Documentation

For detailed information, see:

- **[api_reference.md](references/api_reference.md)** - Complete API documentation with all parameters, return types, examples, and error handling
- **[batch_transcription.md](references/batch_transcription.md)** - Comprehensive batch processing guide with cost analysis, workflows, and use cases
- **[workflows.md](references/workflows.md)** - Common workflow patterns and step-by-step guides for typical use cases
- **[workflows_code_exec.md](references/workflows_code_exec.md)** - Code execution framework patterns and data processing examples
- **[troubleshooting.md](references/troubleshooting.md)** - Debugging guide with common errors, solutions, and workarounds

## Best Practices

### Dependency Management
Install dependencies before using functions:
```bash
pip install youtube-transcript-api google-genai httpx pydantic requests beautifulsoup4
```

### API Key Setup
Set `GOOGLE_API_KEY` environment variable (required for podcast transcription):
```python
import os
os.environ['GOOGLE_API_KEY'] = 'your-api-key'
```

Get your API key from: https://aistudio.google.com/app/apikey

### Caching Strategy
- Always use `use_cache=True` (default) to avoid redundant processing
- Check cache with `list_cache()` before transcribing
- Cache persists across sessions

### Batch Processing
Use batch API for **50% cost reduction** on multiple transcriptions:
- **Good for:** 10+ episodes, large collections, bulk processing
- **Processing time:** 24-hour window (asynchronous)
- **Cost savings:** 50% compared to individual calls

### Error Handling
Wrap function calls in try/except:
```python
try:
    transcript = get_transcript("video-id")
except Exception as e:
    print(f"Error: {e}")
```

### Processing Large Results
Process transcripts in execution environment to reduce token usage:
```python
# Get full transcript
transcript = get_transcript("video-id")

# Extract only relevant sections (processed locally)
relevant_lines = [
    line for line in transcript.split('\n')
    if 'keyword' in line.lower()
]

# Return only relevant content
print('\n'.join(relevant_lines))
```

For complete best practices, common workflows, and advanced usage patterns, see [references/workflows.md](references/workflows.md) and [references/workflows_code_exec.md](references/workflows_code_exec.md).

## Troubleshooting

For detailed troubleshooting, see [references/troubleshooting.md](references/troubleshooting.md).

**Common quick fixes:**

### Import Errors
Ensure skill path is added:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))
```

### YouTube Errors
- **"TranscriptsDisabled"** - Video has captions disabled
- **"VideoUnavailable"** - Invalid video ID/URL
- **"NoTranscriptFound"** - No transcript available

### Podcast Errors
- **"Google API key is required"** - Set `GOOGLE_API_KEY` environment variable
- **"RSS feed parsing failed"** - Invalid RSS URL
- **Rate limit exceeded** - Wait and retry

### Batch Processing Errors
- **"Job timeout exceeded"** - Increase `timeout_hours` parameter
- **"Batch quota exceeded"** - Wait for jobs to complete or cancel non-critical jobs
- **"Invalid audio URL"** - Verify URL is publicly accessible

### Cache Issues
Clear cache if needed:
```bash
rm -rf ~/.cache/transcribe_mcp/*.json
```

For detailed error messages, solutions, and debugging steps, see [references/troubleshooting.md](references/troubleshooting.md).
