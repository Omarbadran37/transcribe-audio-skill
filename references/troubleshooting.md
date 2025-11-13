# Transcribe Audio - Troubleshooting Guide

Common issues and solutions for the code execution framework.

## Setup Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'servers'`

**Solution:**
```python
import sys
from pathlib import Path

# Add skill scripts to path
skill_path = Path.home() / ".claude/skills/transcribe-audio/scripts"
sys.path.insert(0, str(skill_path))

# Now imports will work
from servers.transcribe import get_transcript
```

**Problem:** `ModuleNotFoundError: No module named 'youtube_transcript_api'`

**Solution:**
```bash
pip install youtube-transcript-api google-genai httpx pydantic requests beautifulsoup4
```

### API Key Issues

**Problem:** `ValueError: Google API key is required`

**Solution:**
```python
import os
os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
```

Get API key from: https://aistudio.google.com/app/apikey

**Problem:** API key not persisting across sessions

**Solution:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export GOOGLE_API_KEY='your-api-key-here'

# Or use .env file
echo "GOOGLE_API_KEY=your-api-key" > ~/.claude/skills/transcribe-audio/.env

# Load in Python
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path.home() / ".claude/skills/transcribe-audio/.env")
```

## YouTube Transcription Issues

### Video Not Found

**Problem:** `Exception: Video not found`

**Cause:** Invalid video ID or deleted video

**Solution:**
- Verify video ID is 11 characters
- Check video exists on YouTube
- Try different video

```python
try:
    transcript = get_transcript("invalid-id")
except Exception as e:
    if "VideoUnavailable" in str(e):
        print("Video doesn't exist or was deleted")
```

### Transcripts Disabled

**Problem:** `Exception: This video has captions disabled`

**Cause:** Video owner disabled captions

**Solution:**
- Choose different video with captions
- No workaround available

```python
try:
    transcript = get_transcript("video-id")
except Exception as e:
    if "TranscriptsDisabled" in str(e):
        print("This video has no captions available")
```

### No Transcript Found

**Problem:** `Exception: No transcript available for this video`

**Cause:** Video has no auto-generated or manual captions

**Solution:**
- Video must have captions/subtitles
- Check if captions exist on YouTube first

## Podcast Transcription Issues

### RSS Feed Not Found

**Problem:** `find_rss()` returns `found: False`

**Cause:** Podcast name doesn't match database entries

**Solution:**
- Try exact podcast name from Apple Podcasts
- Try different search terms
- Get RSS URL manually from podcast website

```python
# Alternative: Use RSS URL directly
feed_url = "https://feeds.megaphone.fm/podcast"
episodes = parse_rss(feed_url)
```

### RSS Parsing Failed

**Problem:** `Exception: RSS feed parsing failed`

**Cause:** Invalid RSS URL or feed format

**Solution:**
```python
# Verify RSS URL
import requests
try:
    r = requests.get(rss_url, timeout=10)
    r.raise_for_status()
    print("RSS feed accessible")
except Exception as e:
    print(f"RSS error: {e}")
```

### Audio Download Failed

**Problem:** `Exception: Audio download failed`

**Cause:** Network issue, invalid URL, or blocked access

**Solution:**
```python
# Test audio URL
import requests
try:
    r = requests.head(audio_url, timeout=10, allow_redirects=True)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
except Exception as e:
    print(f"Download error: {e}")
```

### Transcription Timeout

**Problem:** Transcription takes >10 minutes

**Cause:** Large audio file or API slowdown

**Solution:**
- Wait longer (some episodes take 5-10 minutes)
- Check file size: `audio_path.stat().st_size / (1024*1024)` MB
- Try smaller episode first

### Rate Limiting

**Problem:** `Exception: Rate limit exceeded`

**Cause:** Too many Gemini API requests

**Solution:**
- Wait 60 seconds
- Use cache to avoid re-processing
- Check Google Cloud Console for quotas

```python
import time

try:
    transcript = transcribe_episode(audio_url)
except Exception as e:
    if "rate limit" in str(e).lower():
        print("Waiting 60 seconds...")
        time.sleep(60)
        transcript = transcribe_episode(audio_url)
```

## Cache Issues

### Cache Not Working

**Problem:** Same transcript fetched repeatedly

**Cause:** `use_cache=False` or cache not checked

**Solution:**
```python
# Ensure caching is enabled (default)
transcript = get_transcript(video_id, use_cache=True)

# Verify cache
cached = list_cache()
print(f"Cached transcripts: {len(cached)}")
```

### Cache Key Not Found

**Problem:** `get_cached()` returns `found: False`

**Cause:** Invalid cache key or transcript not cached

**Solution:**
```python
# List cache to find correct key
cached = list_cache()
for c in cached:
    print(f"{c['title']}: {c['cache_key']}")

# Use correct key
result = get_cached(cached[0]['cache_key'])
```

### Clear Cache

**Problem:** Need to clear old transcripts

**Solution:**
```bash
# Clear all cached transcripts
rm -rf ~/.cache/transcribe_mcp/*.json

# Clear saved files
rm -rf ~/.cache/transcribe_mcp/transcripts/*

# Keep specific transcripts (example)
cd ~/.cache/transcribe_mcp
ls -lt *.json | tail -n +11 | awk '{print $9}' | xargs rm
```

## Performance Issues

### Slow Imports

**Problem:** Initial import takes 5+ seconds

**Cause:** Large dependency loading

**Solution:**
```python
# Import only what you need
from servers.transcribe.youtube import get_transcript  # Faster

# Instead of
from servers.transcribe import *  # Slower
```

### Memory Issues

**Problem:** Process runs out of memory

**Cause:** Large transcript in memory

**Solution:**
```python
# Stream to file instead of memory
transcript = get_transcript(video_id)

# Save immediately
Path("/tmp/transcript.txt").write_text(transcript)

# Process in chunks
with open("/tmp/transcript.txt") as f:
    for line in f:
        if 'keyword' in line:
            print(line)
```

### Disk Space Issues

**Problem:** Cache directory full

**Solution:**
```bash
# Check cache size
du -sh ~/.cache/transcribe_mcp

# Clear old cache (older than 30 days)
find ~/.cache/transcribe_mcp -name "*.json" -mtime +30 -delete
```

## Error Messages Reference

### YouTube Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `TranscriptsDisabled` | Captions disabled | Choose different video |
| `VideoUnavailable` | Video not found | Verify video ID |
| `NoTranscriptFound` | No captions exist | Video must have captions |
| `Invalid YouTube URL` | Bad URL format | Use valid YouTube URL or ID |

### Podcast Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Google API key is required` | Missing GOOGLE_API_KEY | Set environment variable |
| `RSS feed parsing failed` | Invalid RSS URL | Verify RSS feed URL |
| `Audio download failed` | Network/URL issue | Check audio URL accessibility |
| `Rate limit exceeded` | Too many API calls | Wait 60 seconds, use cache |

### Cache Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Cache key not found` | Invalid cache key | Use `list_cache()` to find valid keys |
| `Permission denied` | Cache directory not writable | Check `~/.cache/transcribe_mcp` permissions |

## Debugging Tips

### Enable Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now see detailed logs
transcript = get_transcript(video_id)
```

### Test Individual Components

```python
# Test YouTube API
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
result = api.fetch("dQw4w9WgXcQ")
print(f"Fetched {len(result)} entries")

# Test Gemini API
from google import genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)
```

### Verify File Paths

```python
from pathlib import Path

skill_path = Path.home() / ".claude/skills/transcribe-audio/scripts"
print(f"Skill path exists: {skill_path.exists()}")
print(f"Contents: {list(skill_path.iterdir())}")

cache_path = Path.home() / ".cache/transcribe_mcp"
print(f"Cache path exists: {cache_path.exists()}")
print(f"Cached files: {len(list(cache_path.glob('*.json')))}")
```

## Getting Help

### Check Versions

```python
import youtube_transcript_api
import google.genai
import httpx

print(f"youtube-transcript-api: {youtube_transcript_api.__version__}")
print(f"google-genai: {google.genai.__version__}")
print(f"httpx: {httpx.__version__}")
```

### Collect Error Info

When reporting issues, include:

1. Full error message
2. Python version: `python --version`
3. Operating system
4. Code that triggered error
5. Expected vs actual behavior

### Common Solutions Checklist

- [ ] Skill path added to sys.path
- [ ] Dependencies installed
- [ ] GOOGLE_API_KEY environment variable set
- [ ] Video/audio URL is valid
- [ ] Cache directory exists and is writable
- [ ] Network connection working
- [ ] Not hitting rate limits
