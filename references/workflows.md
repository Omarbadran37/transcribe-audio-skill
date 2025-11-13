# Transcription Workflows

Detailed guides for common transcription scenarios.

## Workflow 1: YouTube Transcript Extraction

**User Request:** "Get the transcript for this YouTube video: [URL]"

**Steps:**

1. **Extract Video ID**
   - Accept full URL, short URL, or raw ID
   - Tool handles all formats automatically

2. **Call Tool**
   - Use: `transcribe_get_youtube_transcript`
   - Parameters: `{"url": "[URL]"}`

3. **Check Result**
   - If success: Return formatted transcript
   - If not found: Check if video ID is correct
   - If no transcript: Explain that YouTube doesn't have captions for this video

4. **Format Output**
   - By default: Plain text with timestamps
   - Option: Offer JSON or Markdown formats
   - Suggestion: "Would you like this in a different format?"

5. **Caching**
   - Automatically stored
   - Same URL next time returns instant result
   - Shows: `✅ Loaded from cache` in response

**Example Output:**
```
Video: How to Build an MCP Server
Duration: 42:30

[00:00] This is the introduction to MCP servers...
[01:15] Today we'll explore the architecture...
[05:30] Let me show you the code structure...

(Full transcript continues...)

✅ This transcript is cached for instant retrieval next time!
```

**Common Issues:**
- "Video not found" → Verify video still exists
- "No transcript available" → Video has no captions/subtitles
- "Invalid URL" → Check URL format

---

## Workflow 2: Podcast Discovery and Transcription

**User Request:** "Find and transcribe the latest episode of [Podcast Name]"

**Steps:**

1. **Find Podcast RSS**
   - Call: `transcribe_find_podcast_rss`
   - Parameter: `{"podcast_name": "[Name]"}`
   - Shows search progress (searches multiple APIs)

2. **Parse RSS Feed**
   - Call: `transcribe_parse_rss_feed`
   - Parameters: `{"rss_url": "[URL]", "limit": 5}`
   - Shows latest 5 episodes

3. **Select Episode**
   - Present: Title, date, duration
   - Ask: "Which episode would you like to transcribe?" or assume latest
   - Extract: Audio URL from episode

4. **Transcribe Episode**
   - Call: `transcribe_podcast_episode`
   - Parameters: `{"audio_url": "[URL]"}`
   - Shows: Download progress, processing status
   - Wait: 2-5 minutes for audio processing

5. **Present Results**
   - Format: Speaker-separated transcript with timestamps
   - Summary: Episode title, duration, speakers identified
   - Option: "Save to file?" or "Different format?"

**Example Flow:**
- Find "How I Built This" → Get RSS
- Show latest 5 episodes → Select latest one
- Download and transcribe → Wait 2-5 minutes
- Return speaker-separated transcript with [HH:MM] timestamps

---

## Workflow 3: Direct Podcast Episode Transcription

**User Request:** "Transcribe this podcast episode: [Direct Audio URL]"

**Steps:**

1. **Validate URL**
   - Check: URL points to audio file (.mp3, .m4a, .wav, etc.)
   - Check: URL is accessible and valid

2. **Call Tool**
   - Use: `transcribe_podcast_episode`
   - Parameters: `{"audio_url": "[URL]"}`

3. **Processing**
   - Show: File size, download time estimate
   - Show: Transcription progress
   - Processing: 2-5 minutes typical

4. **Output**
   - Format: [MM:SS] Speaker A: Text
   - Summary: Duration, speakers found, transcript length
   - Caching: Automatic for future use

---

## Workflow 4: Cache Management

**User Request:** "Show me what's in the transcript cache"

**Steps:**

1. **List Cache**
   - Call: `transcribe_list_cache`
   - Shows: All cached transcripts with metadata

2. **Present Results**
   - Format: Table with title, type (YouTube/Podcast), date, duration
   - Enable: User to select and retrieve specific transcripts

**User Request:** "Get the cached transcript for [Title/URL]"

**Steps:**

1. **Find in Cache**
   - Call: `transcribe_list_cache` to find cache_key
   - OR parse cache_key from previous response

2. **Retrieve**
   - Call: `transcribe_get_cached_transcript`
   - Parameter: `{"cache_key": "[hash]"}`
   - Instant result (<100ms)

3. **Deliver**
   - Return full transcript immediately
   - Cite: "Cached on [date]"

---

## Best Practices for All Workflows

### 1. Error Handling

**Network Issues:**
- Tool automatically retries with exponential backoff
- If persistent: Suggest checking internet connection
- For podcasts: Try a different podcast

**API Limits:**
- Usually prevented by caching
- If hit: "Service temporarily busy, try again in a few minutes"

**Invalid URLs:**
- Verify URL format
- For YouTube: Show expected format examples
- For podcasts: Use podcast name discovery instead

### 2. Processing Time Management

**YouTube Transcripts:** Instant to <1 second
- User expectation: Immediate response
- Action: Return right away

**Podcast Transcription:** 2-5 minutes
- User expectation: Explain wait time upfront
- Action: Show progress, keep user informed
- Tip: "This will take 2-5 minutes for a 60-minute episode"

**Cache Retrieval:** <100ms
- User expectation: Instant
- Action: Deliver immediately, cite cache source

### 3. Output Formatting

**Default:** Plain text with timestamps
- Clean, easy to read
- Preserves speaker information

**Options:** Offer alternatives when appropriate
- JSON: For programmatic use
- Markdown: For documentation
- Plain text: For readability

### 4. Proactive Features

**Always Mention:**
- "This result is now cached for instant retrieval next time"
- "Use `transcribe_list_cache` to see all your transcripts"

**Offer When Relevant:**
- Different output formats
- Saving to specific location
- Further analysis of content

### 5. User Communication

**Be Transparent:**
- "Searching podcasts..." (shows progress)
- "Downloading audio (67.7 MB)..." (sets expectations)
- "Transcribing with AI..." (explains processing)

**Be Concise:**
- Skip technical details unless asked
- Focus on useful information
- Highlight key findings