# Batch Transcription Guide

Process multiple podcast episodes efficiently using Google's Gemini Batch API at **50% cost reduction** with 24-hour processing time.

## When to Use Batch Transcription

### ✅ Use Batch When:
- Transcribing 5+ episodes
- Not time-sensitive (24-hour SLO acceptable)
- Want 50% cost savings
- Processing entire podcast series
- Running overnight jobs

### ❌ Use Regular Transcription When:
- Need results immediately (2-5 minutes)
- Processing 1-4 episodes
- Interactive use case
- Time-sensitive transcription

## Quick Start

```python
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))

# Import functions
from servers.transcribe import (
    find_rss,
    parse_rss,
    create_batch_transcription,
    check_batch_status,
    get_batch_results
)

# 1. Find podcast and get episodes
feed = find_rss("How I Built This")
episodes = parse_rss(feed['rss_url'], max_episodes=10)

# 2. Create batch job
batch = create_batch_transcription(
    episodes,
    batch_name="hibt-batch-jan2024",
    speaker_diarization=True
)

print(f"Batch job created: {batch['job_name']}")
print(f"Status: {batch['state']}")

# 3. Check status later
status = check_batch_status(batch['job_name'])
print(f"Current status: {status['state']}")

# 4. Get results when complete
if status['state'] == 'JOB_STATE_SUCCEEDED':
    results = get_batch_results(batch['job_name'])
    for r in results:
        print(f"{r['title']}: {len(r['transcript'])} chars")
```

## Complete Workflow

### Step 1: Prepare Episodes

```python
from servers.transcribe import find_rss, parse_rss

# Option A: From RSS feed
feed = find_rss("Lex Fridman Podcast")
episodes = parse_rss(feed['rss_url'], max_episodes=20)

# Option B: Manual list
episodes = [
    {'audio_url': 'https://...mp3', 'title': 'Episode 1'},
    {'audio_url': 'https://...mp3', 'title': 'Episode 2'},
    {'audio_url': 'https://...mp3', 'title': 'Episode 3'}
]
```

### Step 2: Create Batch Job

```python
from servers.transcribe import create_batch_transcription

batch = create_batch_transcription(
    episodes=episodes,
    batch_name="my-podcast-batch",
    speaker_diarization=True,    # Identify speakers
    include_timestamps=True,     # Add timestamps
    wait_for_completion=False    # Return immediately
)

# Save job name for later
job_name = batch['job_name']
print(f"Job: {job_name}")
```

**Output:**
```
Downloading 10 audio files...
  [1/10] Episode 1
  [2/10] Episode 2
  ...
  
Uploading 10 files to Gemini...
  [1/10] Episode 1
  ...

Creating batch input file...
Uploading batch input file...
Creating batch job...

✓ Batch job created\!
  Job name: batches/abc123def456
  Status: JOB_STATE_PENDING
  Episodes: 10

Use check_batch_status('batches/abc123def456') to monitor progress
```

### Step 3: Monitor Progress

```python
from servers.transcribe import check_batch_status

# Check status anytime
status = check_batch_status(job_name)
print(f"Status: {status['state']}")
print(f"Requests: {status['request_count']}")

# Possible states:
# - JOB_STATE_PENDING: Waiting to start
# - JOB_STATE_RUNNING: Processing
# - JOB_STATE_SUCCEEDED: Complete
# - JOB_STATE_FAILED: Failed
# - JOB_STATE_CANCELLED: Cancelled
# - JOB_STATE_EXPIRED: Expired (48 hours)
```

### Step 4: Wait for Completion (Optional)

```python
from servers.transcribe import wait_for_batch

# Block until complete (can take hours)
final_status = wait_for_batch(
    job_name,
    poll_interval=60  # Check every 60 seconds
)

print(f"Final status: {final_status['state']}")
```

**Output:**
```
Polling batch job every 60 seconds...
  Status: JOB_STATE_PENDING (10:30:00)
  Status: JOB_STATE_RUNNING (10:31:00)
  Status: JOB_STATE_RUNNING (10:32:00)
  ...
  Status: JOB_STATE_SUCCEEDED (14:25:00)
✓ Batch job completed\!
```

### Step 5: Retrieve Results

```python
from servers.transcribe import get_batch_results

# Get all transcripts
results = get_batch_results(
    job_name,
    save_to_disk=True  # Save to ~/.cache/transcribe_mcp/transcripts/
)

# Process results
for r in results:
    print(f"\n{r['title']}")
    print(f"  Transcript: {len(r['transcript'])} characters")
    print(f"  Saved to: {r['saved_to']}")
    
    # Show preview
    print(f"  Preview: {r['transcript'][:200]}...")
```

**Output:**
```
  Saved: batch_episode_001_20240112_142500.txt
  Saved: batch_episode_002_20240112_142500.txt
  ...
  
✓ Retrieved 10 transcripts

Episode 1
  Transcript: 58234 characters
  Saved to: /Users/name/.cache/transcribe_mcp/transcripts/batch_episode_001_20240112_142500.txt
  Preview: [00:00] Speaker A: Welcome to the show...
```

## Advanced Usage

### List All Batch Jobs

```python
from servers.transcribe import list_batch_jobs

jobs = list_batch_jobs(limit=10)

for job in jobs:
    print(f"{job['display_name']}")
    print(f"  Status: {job['state']}")
    print(f"  Created: {job['create_time']}")
    print(f"  Requests: {job['request_count']}\n")
```

### Cancel Running Job

```python
from servers.transcribe import cancel_batch

status = cancel_batch(job_name)
print(f"Job cancelled: {status['state']}")
```

### Batch with Custom Options

```python
batch = create_batch_transcription(
    episodes=episodes[:5],           # First 5 episodes
    batch_name="test-batch",         # Custom name
    speaker_diarization=False,       # No speaker labels
    include_timestamps=False,        # No timestamps
    wait_for_completion=True         # Block until done
)
```

## Cost Comparison

### Regular Transcription
```python
# Process 10 episodes individually
for ep in episodes[:10]:
    transcript = transcribe_episode(ep['audio_url'])
    # Takes: 2-5 min per episode
    # Cost: 100% standard rate
```

**Total Time:** 20-50 minutes  
**Total Cost:** 10 × $0.10 = **$1.00**

### Batch Transcription
```python
# Process 10 episodes in batch
batch = create_batch_transcription(episodes[:10])
results = get_batch_results(batch['job_name'])
# Takes: 24 hours (SLO), often faster
# Cost: 50% of standard rate
```

**Total Time:** Hours (asynchronous)  
**Total Cost:** 10 × $0.05 = **$0.50** (**50% savings**)

## Best Practices

### 1. Naming Convention

```python
from datetime import datetime

batch_name = f"{podcast_name}_{datetime.now().strftime('%Y%m%d')}"
batch = create_batch_transcription(episodes, batch_name=batch_name)
```

### 2. Save Job Names

```python
import json

# Save for later retrieval
jobs_file = Path.home() / ".claude/batch_jobs.json"

jobs = []
if jobs_file.exists():
    jobs = json.loads(jobs_file.read_text())

jobs.append({
    'job_name': batch['job_name'],
    'batch_name': batch['display_name'],
    'created': batch['create_time'],
    'episode_count': batch['episode_count']
})

jobs_file.write_text(json.dumps(jobs, indent=2))
```

### 3. Error Handling

```python
try:
    batch = create_batch_transcription(episodes)
except Exception as e:
    print(f"Batch creation failed: {e}")
    
    # Fallback to regular transcription
    for ep in episodes:
        transcript = transcribe_episode(ep['audio_url'])
```

### 4. Resume Failed Jobs

```python
# List recent jobs
jobs = list_batch_jobs()

# Find failed jobs
failed = [j for j in jobs if j['state'] == 'JOB_STATE_FAILED']

# Retry with subset
if failed:
    print(f"Found {len(failed)} failed jobs")
    # Manually retry those episodes
```

## Workflow Example: Complete Podcast Series

```python
from servers.transcribe import (
    find_rss,
    parse_rss,
    create_batch_transcription,
    wait_for_batch,
    get_batch_results
)

# 1. Find podcast
print("Finding podcast...")
feed = find_rss("How I Built This")

# 2. Get all episodes (or last 50)
print("Parsing RSS feed...")
episodes = parse_rss(feed['rss_url'], max_episodes=50)
print(f"Found {len(episodes)} episodes\n")

# 3. Create batch job
print("Creating batch job...")
batch = create_batch_transcription(
    episodes,
    batch_name=f"hibt-batch-{datetime.now().strftime('%Y%m%d')}"
)

print(f"\nBatch job created: {batch['job_name']}")
print(f"Processing {batch['episode_count']} episodes")
print(f"Cost savings: ~50% vs regular transcription\n")

# 4. Wait for completion (optional)
print("Waiting for completion (this will take hours)...")
final_status = wait_for_batch(batch['job_name'], poll_interval=300)  # Check every 5 min

# 5. Get results
print("\nRetrieving results...")
results = get_batch_results(batch['job_name'])

# 6. Process results
print(f"\n{'='*60}")
print(f"BATCH COMPLETE")
print(f"{'='*60}")

total_chars = sum(len(r['transcript']) for r in results)
print(f"Episodes transcribed: {len(results)}")
print(f"Total characters: {total_chars:,}")
print(f"Average per episode: {total_chars // len(results):,}")

# 7. Save summary
summary_file = Path(f"batch_summary_{datetime.now().strftime('%Y%m%d')}.txt")
with open(summary_file, 'w') as f:
    f.write(f"Batch Job: {batch['job_name']}\n")
    f.write(f"Episodes: {len(results)}\n")
    f.write(f"Total Characters: {total_chars:,}\n\n")
    
    for i, r in enumerate(results, 1):
        f.write(f"{i}. {r['title']}: {len(r['transcript']):,} chars\n")

print(f"\nSummary saved to: {summary_file}")
```

## Troubleshooting

### Job Taking Too Long

**Check status:**
```python
status = check_batch_status(job_name)
print(status)
```

**Normal processing time:** 24-hour SLO, but often completes in 2-8 hours

### Job Failed

```python
status = check_batch_status(job_name)

if status['state'] == 'JOB_STATE_FAILED':
    print("Job failed. Check:")
    print("1. Audio files are valid")
    print("2. API key is correct")
    print("3. Quota limits not exceeded")
```

### Can't Find Job

```python
# List all jobs
jobs = list_batch_jobs(limit=50)

# Find by name
my_jobs = [j for j in jobs if 'my-batch' in j['display_name']]
```

### Results Not Available

```python
status = check_batch_status(job_name)

if status['state'] \!= 'JOB_STATE_SUCCEEDED':
    print(f"Job not complete yet: {status['state']}")
    print("Wait for JOB_STATE_SUCCEEDED before retrieving results")
```

## API Reference

See `api_reference.md` for complete function signatures and parameters for:
- `create_batch_transcription()`
- `check_batch_status()`
- `wait_for_batch()`
- `get_batch_results()`
- `cancel_batch()`
- `list_batch_jobs()`

## Limitations

- **Processing Time:** 24-hour SLO (Service Level Objective)
- **File Size:** Individual audio files must be <2GB
- **Batch Size:** Up to 10,000 requests per batch
- **Expiration:** Jobs expire after 48 hours
- **No Immediate Results:** Not suitable for interactive use

## Pricing

**Regular Transcription:** $0.10 per 60-minute episode  
**Batch Transcription:** $0.05 per 60-minute episode (**50% discount**)

**Example:**
- 100 episodes × 60 minutes each
- Regular: 100 × $0.10 = $10.00
- Batch: 100 × $0.05 = **$5.00** (save $5.00)
