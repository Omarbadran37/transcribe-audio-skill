# Example Queries

Common requests and how they'll be handled by the skill.

## YouTube Examples

### Query 1: YouTube Video Transcript
```
User: "Get the transcript for this YouTube video: https://youtube.com/watch?v=i43kYARbSGM"

Response:
✅ Extracted transcript from video
📄 1,353 entries found
⏱️ Duration: 52 minutes 36 seconds

Video: [Title]
Date: [Date]

[00:00] Speaker 1: Introduction...
[01:15] Speaker 1: The main topic...
[05:30] Speaker 1: Key point...

... (full transcript) ...

✅ This transcript is cached for instant retrieval next time!
```

### Query 2: Short YouTube URL
```
User: "Transcribe this video: https://youtu.be/dQw4w9WgXcQ"

Response:
✅ Video found and transcribed
📊 Transcript length: 847 words
⏱️ Duration: 3:33

[00:00] Full transcript...
[00:15] ...continues...

💡 Tip: Show different formats with ?format=json or ?format=markdown
```

### Query 3: Multiple Formats
```
User: "Can I get this as JSON?"

Response:
```json
{
  "video_id": "i43kYARbSGM",
  "title": "...",
  "duration": 3156,
  "entries": [
    {"start": 0, "duration": 2.5, "text": "..."},
    {"start": 2.5, "duration": 3.2, "text": "..."}
  ]
}
```
```

---

## Podcast Examples

### Query 1: Find and Transcribe Latest
```
User: "Find the latest episode of How I Built This and transcribe it"

Response:
🔍 Searching for "How I Built This"...
✅ Found! How I Built This with Guy Raz

📺 Latest 5 episodes:
1. Babylist: Natalie Gordon (1h 7m) - Oct 24, 2024
2. Bridgewater: Ray Dalio (1h 12m) - Oct 17, 2024
3. Airbnb: Brian Chesky (1h 15m) - Oct 10, 2024
4. Slack: Stewart Butterfield (58m) - Oct 3, 2024
5. Uber: Travis Kalanick (1h 8m) - Sep 26, 2024

🎤 Transcribing latest episode: Babylist: Natalie Gordon
⏳ This will take 2-5 minutes for a 67-minute episode...
📥 Downloading audio (67.7 MB)...
🤖 Processing with Google Gemini AI...

✅ Transcription complete!

[00:00] Speaker A: Wondery Plus subscribers...
[00:10] Speaker A: If you've shopped online...
[01:31] Speaker C: This message comes from Capital One...
[02:15] Speaker D: [Natalie Gordon, Guest]
[05:30] Speaker E: [Guy Raz, Host]

... (full speaker-separated transcript with timestamps) ...

📊 Summary:
  • Episode: Babylist: Natalie Gordon
  • Duration: 1h 7m 43s
  • Speakers identified: 5
  • Transcript length: 60,282 characters
  • Processing time: 2 min 23 sec

✅ This transcript is cached for instant future retrieval!
💡 Use transcribe_list_cache to see all your transcripts
```

### Query 2: Direct Audio URL
```
User: "Transcribe this podcast: https://cdn.example.com/episode.mp3"

Response:
📥 Downloading audio...
✅ File size: 45.3 MB
🤖 Transcribing with Google Gemini...
⏳ Processing (approx 45 seconds of audio)...

✅ Complete!

[00:00] Speaker A: Introduction...
... (continues) ...

📊 Cached: Yes | Cache ID: abc123def456...
```

### Query 3: Direct RSS Feed
```
User: "Get the latest episode of This American Life"

Response:
🔍 Searching for "This American Life"...
✅ Found RSS feed

📺 Latest episodes:
1. [Episode Title] (52m) - Nov 3, 2024
2. [Episode Title] (58m) - Nov 2, 2024
3. [Episode Title] (48m) - Oct 31, 2024

User: "Transcribe the first one"

🎤 Transcribing...
⏳ 2-5 minutes...

✅ Done!
```

---

## Cache Examples

### Query 1: View Cache
```
User: "Show me what's in the transcript cache"

Response:
📚 Your transcript cache:

1. Babylist: Natalie Gordon (Podcast)
   Duration: 1h 7m | Cached: Nov 3, 2024
   Content: 60,282 characters | ID: e86692a9...

2. [YouTube Video Title] (YouTube)
   Duration: 52m | Cached: Nov 3, 2024
   Content: 15,400 characters | ID: abc123de...

3. [Another Podcast] (Podcast)
   Duration: 42m | Cached: Nov 2, 2024
   Content: 42,500 characters | ID: xyz789ab...

Total: 3 cached transcripts (118 KB)
```

### Query 2: Retrieve Cached Transcript
```
User: "Get the cached transcript for How I Built This"

Response:
⚡ Loading from cache (instant)...

✅ Babylist: Natalie Gordon
📅 Cached: Nov 3, 2024
⏱️ Duration: 1h 7m 43s

[00:00] Speaker A: Wondery Plus...
[00:10] Speaker A: If you've shopped...
... (full transcript instantly) ...
```

### Query 3: Cache Hit on Re-request
```
User: "Transcribe this again: https://youtube.com/watch?v=i43kYARbSGM"

Response:
⚡ Found in cache! (instant retrieval)

[00:00] Speaker 1: Introduction...
... (returns immediately) ...

💡 Processing time: 0 ms (cached result from Nov 3)
```

---

## Multi-step Examples

### Example 1: Complete Workflow
```
User: "Find a podcast about AI and transcribe the latest episode"

Step 1: Search
🔍 "AI" is too generic. Which podcast?
- Artificial Intelligence Podcast (Lex Fridman)
- AI in Industry
- AI Daily Brief

User: "The one by Lex Fridman"

Step 2: Get Episodes
✅ Found: Artificial Intelligence Podcast

📺 Latest episodes:
1. [Recent episode] (2h 15m)
2. [Previous episode] (1h 48m)
...

User: "The first one"

Step 3: Transcribe
⏳ Downloading and transcribing...
✅ Complete!
```

### Example 2: Comparison Request
```
User: "Get transcripts for the last 3 episodes of How I Built This"

Response:
📚 Getting latest 3 episodes...

1️⃣ Latest episode (already cached - instant)
2️⃣ Previous episode (downloading...) ⏳
3️⃣ Two weeks ago (downloading...) ⏳

✅ All done!
Total processing: 5-10 minutes for 3 episodes
Total content: ~180,000 characters across all three
```

---

## Error Recovery Examples

### Example 1: Podcast Not Found
```
User: "Transcribe the latest episode of that new podcast about climate"

Tool: Podcast not found

Response:
❌ Couldn't find that podcast. Let me help:

Could you be more specific?
• Climate Now
• Our Changing Climate
• Talking Points Climate Podcast
• The Climate Question

Which one?
```

### Example 2: No Transcript Available
```
User: "Get the transcript for this video: [URL]"

Tool: No transcript available

Response:
❌ This YouTube video doesn't have captions available.

Options:
1. Contact the creator to enable captions
2. If it's a podcast, use the audio URL with podcast transcription
3. Try a different video from the same creator

Would any of these work?
```

### Example 3: Invalid URL
```
User: "Transcribe this: https://example.com/something"

Tool: Invalid URL

Response:
❌ This doesn't look like a valid audio URL.

I need:
• Direct link to YouTube video (youtube.com/watch?v=...)
• Direct link to podcast audio (.mp3 or similar)
• Podcast name (I'll find the episode)

What do you have?
```

---

## Performance Examples

### YouTube (Fast)
```
User: "Get transcript"
⏱️ 0.3 seconds - Instant!
```

### Podcast from Cache (Very Fast)
```
User: "Show me that How I Built This episode again"
⏱️ 0.05 seconds - Instant!
```

### New Podcast (Slow)
```
User: "Transcribe this podcast"
⏱️ 2-5 minutes - Normal
⏱️ 10-15 minutes - Very long episode (2+ hours)
```

### Discovery + Transcription (Medium)
```
User: "Find and transcribe latest episode"
⏱️ 10 seconds - Discovery
⏱️ 3-5 minutes - Transcription
⏱️ ~5-6 minutes - Total
```
