# Tool Reference

All 6 tools are available through the transcribe MCP server.

## Tool: transcribe_get_youtube_transcript

Extracts transcript from YouTube videos with timestamps.

**When to use:** User provides a YouTube URL and wants the full transcript

**Parameters:**
- `url` (string, required): YouTube video URL
  - Accepts: Full URL (`https://youtube.com/watch?v=...`)
  - Accepts: Short URL (`https://youtu.be/...`)
  - Accepts: Raw video ID (`dQw4w9WgXcQ`)
- `format` (string, optional): Output format
  - `text`: Plain text (default)
  - `json`: JSON with timestamps
  - `markdown`: Markdown with sections

**Returns:**
```json
{
  "video_id": "i43kYARbSGM",
  "title": "Video Title",
  "duration": 3156,
  "language": "en",
  "transcript": "Full transcript text...",
  "entries": [
    {
      "text": "Entry text",
      "start": 0.5,
      "duration": 2.5
    }
  ],
  "cached": false,
  "cache_key": "abc123def456..."
}
```

**Error Handling:**
- Invalid URL: Returns 400 with error message
- Video not found: Returns 404
- No transcript available: Returns 404 with message "Video has no transcript"

**Caching:** Automatically cached by video ID

**Processing time:** Instant (cached results) to <1 second (fresh fetch)

---

## Tool: transcribe_find_podcast_rss

Finds RSS feed for a podcast by name using multiple search strategies.

**When to use:** User provides podcast name, need to find the RSS feed URL

**Parameters:**
- `podcast_name` (string, required): Name of the podcast
  - Example: "How I Built This with Guy Raz"
  - Example: "Joe Rogan Experience"
  - Partial matches work

**Returns:**
```json
{
  "found": true,
  "podcast_name": "How I Built This with Guy Raz",
  "rss_url": "https://rss.art19.com/how-i-built-this",
  "description": "Guy Raz interviews founders...",
  "author": "Wondery",
  "image_url": "https://...",
  "language": "en",
  "search_strategy": "apple_podcasts"
}
```

**Search strategies** (tried in order):
1. Podcastindex.org API (most comprehensive)
2. Apple Podcasts API (large catalog)
3. Common hosting platforms (Megaphone, Anchor, Podbean)
4. Listen Notes scraping (fallback)

**Error Handling:**
- Not found: Returns `{"found": false, "message": "Podcast not found"}`
- Network issues: Retries with exponential backoff

**Processing time:** 2-10 seconds

---

## Tool: transcribe_parse_rss_feed

Lists episodes from a podcast RSS feed.

**When to use:** Have RSS URL, need to see available episodes

**Parameters:**
- `rss_url` (string, required): RSS feed URL
  - Example: "https://rss.art19.com/how-i-built-this"
- `limit` (integer, optional): Number of episodes to return (default: 20)
- `order` (string, optional): `newest` (default) or `oldest`

**Returns:**
```json
{
  "podcast_name": "How I Built This with Guy Raz",
  "total_episodes": 487,
  "episodes": [
    {
      "title": "Babylist: Natalie Gordon",
      "description": "Episode description...",
      "pub_date": "2024-10-24",
      "duration": 4063,
      "audio_url": "https://rss.art19.com/episodes/...",
      "episode_number": 487,
      "season": 1,
      "guid": "unique-id"
    }
  ]
}
```

**Error Handling:**
- Invalid RSS URL: Returns 400
- Network issues: Returns 500 with retry suggestion

**Processing time:** 1-3 seconds

---

## Tool: transcribe_podcast_episode

Downloads and transcribes podcast audio with speaker diarization.

**When to use:** User provides podcast episode audio URL, wants full transcript

**Parameters:**
- `audio_url` (string, required): Direct link to MP3 or audio file
  - Example: "https://rss.art19.com/episodes/..."
- `podcast_name` (string, optional): Podcast name for metadata
- `episode_title` (string, optional): Episode title for saving
- `output_format` (string, optional): `text` (default), `json`, or `markdown`

**Returns:**
```json
{
  "podcast_name": "How I Built This with Guy Raz",
  "episode_title": "Babylist: Natalie Gordon",
  "duration_seconds": 4063,
  "processed_seconds": 4063,
  "transcript": "[00:00] Speaker A: Introduction...",
  "speakers": {
    "Speaker A": "Narrator/Commercial",
    "Speaker D": "Natalie Gordon",
    "Speaker E": "Guy Raz"
  },
  "model": "gemini-flash-latest",
  "processing_time_seconds": 143,
  "cache_key": "e86692a9f742af2c5751e8ec139f9191",
  "cached": false
}
```

**Features:**
- Speaker diarization: Automatically identifies up to 5 speakers
- Timestamps: [MM:SS] format for each speaker turn
- Large files: Automatically handles >20MB via Gemini File API
- Language: Supports 100+ languages

**Error Handling:**
- Invalid URL: Returns 400
- Download failure: Returns 503 with retry suggestion
- API rate limit: Returns 429 (usually cached)

**Processing time:** 2-5 minutes for 60-70 minute episodes

**Caching:** Automatically cached, same URL returns instant result

---

## Tool: transcribe_get_cached_transcript

Retrieves a previously transcribed and cached transcript.

**When to use:** User wants to reuse a transcript without re-processing

**Parameters:**
- `cache_key` (string, required): Hash key from previous transcription
  - Obtained from `transcribe_list_cache`
  - Format: MD5 hash (32 characters)

**Returns:**
```json
{
  "found": true,
  "cache_key": "e86692a9f742af2c5751e8ec139f9191",
  "source_url": "https://rss.art19.com/episodes/...",
  "transcript": "Full transcript...",
  "metadata": {
    "title": "Babylist: Natalie Gordon",
    "duration": 4063,
    "created_at": "2024-11-03T14:02:43Z",
    "format": "markdown"
  }
}
```

**Error Handling:**
- Not found: Returns `{"found": false}`
- Invalid cache key: Returns 400

**Processing time:** Instant (<100ms)

---

## Tool: transcribe_list_cache

Lists all cached transcriptions.

**When to use:** User wants to see what transcripts are already cached

**Parameters:**
- `limit` (integer, optional): Max results (default: 50)
- `sort_by` (string, optional): `created_at` (default), `title`, or `duration`

**Returns:**
```json
{
  "cache_size": 12,
  "total_items": 12,
  "items": [
    {
      "cache_key": "e86692a9f742af2c5751e8ec139f9191",
      "title": "Babylist: Natalie Gordon",
      "source_url": "https://rss.art19.com/episodes/...",
      "source_type": "podcast",
      "duration": 4063,
      "transcript_length": 60282,
      "created_at": "2024-11-03T14:02:43Z"
    },
    {
      "cache_key": "abc123def456...",
      "title": "YouTube Video Title",
      "source_url": "https://youtube.com/watch?v=...",
      "source_type": "youtube",
      "duration": 3156,
      "transcript_length": 15400,
      "created_at": "2024-11-03T10:15:22Z"
    }
  ]
}
```

**Error Handling:**
- No cache: Returns empty items array `{"cache_size": 0, "items": []}`

**Processing time:** <500ms
