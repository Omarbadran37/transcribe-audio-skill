# Transcribe Audio - Code Execution Workflows

Complete workflow examples using the code execution framework.

## Basic Setup (Required for All Workflows)

```python
import sys
import os
from pathlib import Path

# Add skill to path
skill_path = Path.home() / ".claude/skills/transcribe-audio/scripts"
sys.path.insert(0, str(skill_path))

# Set API key
os.environ['GOOGLE_API_KEY'] = 'your-api-key'

# Import functions
from servers.transcribe import (
    get_transcript, find_rss, parse_rss,
    transcribe_episode, get_cached, list_cache
)
```

## Workflow 1: YouTube Transcript Extraction and Analysis

Extract YouTube transcript and process locally.

```python
# Get transcript
video_id = "i43kYARbSGM"
transcript = get_transcript(video_id)

# Process in execution environment (no token cost)
lines = transcript.split('\n')
timestamped = [l for l in lines if '[' in l and ']' in l]

# Find AI mentions
ai_mentions = [l for l in timestamped if 'ai' in l.lower()]

print(f"Total entries: {len(timestamped)}")
print(f"AI mentions: {len(ai_mentions)}")
```

## Workflow 2: Find and Transcribe Latest Podcast

Discover podcast, list episodes, transcribe.

```python
# Find RSS
feed = find_rss("How I Built This")
if not feed['found']:
    print(feed['message'])
    exit()

# List episodes
episodes = parse_rss(feed['rss_url'], max_episodes=5)
for i, ep in enumerate(episodes, 1):
    print(f"{i}. {ep['title']} ({ep['duration']})")

# Transcribe first
transcript = transcribe_episode(
    episodes[0]['audio_url'],
    episode_title=episodes[0]['title']
)

# Save
Path("/tmp/transcript.txt").write_text(transcript)
```

## Workflow 3: Batch Process Episodes

Transcribe multiple episodes efficiently.

```python
rss_url = "https://feeds.megaphone.fm/podcast"
episodes = parse_rss(rss_url, max_episodes=3)

results = []
for i, ep in enumerate(episodes, 1):
    print(f"[{i}/{len(episodes)}] {ep['title']}")
    transcript = transcribe_episode(
        ep['audio_url'],
        episode_title=ep['title']
    )
    results.append({'title': ep['title'], 'transcript': transcript})

print(f"Processed {len(results)} episodes")
```

## Workflow 4: Search Cached Transcripts

Find and filter cached transcripts.

```python
# List all
cached = list_cache(limit=100)

# Filter YouTube
youtube = [c for c in cached if c['source_type'] == 'youtube']

# Filter by keyword
keyword = "built"
matching = [c for c in cached if keyword in c['title'].lower()]

print(f"Found {len(matching)} matching transcripts")

# Retrieve specific one
if matching:
    result = get_cached(matching[0]['cache_key'])
    if result['found']:
        print(result['transcript'][:500])
```

## Workflow 5: Extract Speaker Content

Get speaker-specific content from podcast.

```python
transcript = transcribe_episode(
    audio_url,
    speaker_diarization=True
)

lines = transcript.split('\n')
speaker_a = [l for l in lines if 'Speaker A:' in l]
speaker_b = [l for l in lines if 'Speaker B:' in l]

print(f"Speaker A: {len(speaker_a)} statements")
print(f"Speaker B: {len(speaker_b)} statements")

# Save separately
Path("/tmp/speaker_a.txt").write_text('\n'.join(speaker_a))
Path("/tmp/speaker_b.txt").write_text('\n'.join(speaker_b))
```

## Workflow 6: Check Cache Before Fetching

Efficient caching pattern.

```python
video_id = "dQw4w9WgXcQ"

# Check cache
cached = list_cache()
cache_hit = [c for c in cached if c['source'] == video_id]

if cache_hit:
    print("Using cache")
    result = get_cached(cache_hit[0]['cache_key'])
    transcript = result['transcript']
else:
    print("Fetching fresh")
    transcript = get_transcript(video_id)

print(f"Length: {len(transcript)} chars")
```

## Workflow 7: Custom Analysis

Extract insights programmatically.

```python
transcript = get_transcript("video-id", include_timestamps=False)

# Analyze
sentences = transcript.split('. ')
words = transcript.split()
word_count = len(words)

# Find long sentences
long = sorted([(len(s.split()), s) for s in sentences], reverse=True)[:5]

# Find key terms
key_terms = set([w.strip('.,\!?') for w in words if len(w) > 10])

print(f"Words: {word_count}")
print(f"Sentences: {len(sentences)}")
print(f"Key terms: {len(key_terms)}")
```

## Workflow 8: Generate Metadata JSON

Create structured metadata.

```python
import json
from datetime import datetime

transcript = get_transcript("video-id")
lines = transcript.split('\n')

metadata = {
    "video_id": "video-id",
    "transcript_length": len(transcript),
    "word_count": len(transcript.split()),
    "extracted_at": datetime.now().isoformat(),
    "has_timestamps": '[00:' in transcript
}

Path("/tmp/metadata.json").write_text(json.dumps(metadata, indent=2))
```

## Best Practices

### 1. Check Cache First
```python
cached = list_cache()
if target_key in [c['cache_key'] for c in cached]:
    use_cached()
else:
    fetch_fresh()
```

### 2. Process Locally
```python
# Efficient
transcript = get_transcript(vid)
relevant = [l for l in transcript.split('\n') if 'keyword' in l]
print('\n'.join(relevant))  # Return only relevant

# Inefficient
print(transcript)  # Returns all 50KB
```

### 3. Error Handling
```python
try:
    transcript = get_transcript(video_id)
except Exception as e:
    print(f"Error: {e}")
```
