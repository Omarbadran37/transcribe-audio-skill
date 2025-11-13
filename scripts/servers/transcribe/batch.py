"""Batch transcription using Google Gemini Batch API.

Process multiple podcast episodes in a single batch at 50% cost reduction.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.podcast_helpers import download_audio_file
from utils.gemini_helpers import get_gemini_api_key
from utils.cache_helpers import get_cache_key, save_to_cache
from utils.constants import CACHE_DIR, OUTPUT_DIR

try:
    from google import genai
except ImportError:
    genai = None


def create_batch_transcription(
    episodes: List[Dict],
    batch_name: Optional[str] = None,
    speaker_diarization: bool = True,
    include_timestamps: bool = True,
    wait_for_completion: bool = False
) -> Dict:
    """
    Create a batch transcription job for multiple episodes.

    Uses Google Gemini Batch API to process multiple episodes at 50% cost
    with 24-hour processing time. Ideal for transcribing 5+ episodes.

    Args:
        episodes: List of episode dicts with 'audio_url' and 'title'
        batch_name: Optional name for the batch job
        speaker_diarization: Identify speakers in transcripts
        include_timestamps: Include timestamps
        wait_for_completion: Block until batch completes (can take hours)

    Returns:
        Dictionary with batch job info and status

    Example:
        >>> episodes = [
        ...     {'audio_url': 'https://...mp3', 'title': 'Episode 1'},
        ...     {'audio_url': 'https://...mp3', 'title': 'Episode 2'}
        ... ]
        >>> batch = create_batch_transcription(episodes)
        >>> print(f"Batch job: {batch['job_name']}")
        >>> print(f"Status: {batch['state']}")
    """
    if genai is None:
        raise ImportError("google-genai not installed. Run: pip install google-genai")

    if not episodes:
        raise ValueError("episodes list cannot be empty")

    # Get API key
    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)

    # Download all audio files
    print(f"Downloading {len(episodes)} audio files...")
    audio_files = []

    for i, ep in enumerate(episodes, 1):
        print(f"  [{i}/{len(episodes)}] {ep.get('title', 'Unknown')}")

        audio_path = download_audio_file(
            ep['audio_url'],
            CACHE_DIR,
            ep.get('title')
        )

        audio_files.append({
            'path': audio_path,
            'title': ep.get('title', f'Episode {i}'),
            'audio_url': ep['audio_url']
        })

    # Upload audio files to Gemini Files API
    print(f"\nUploading {len(audio_files)} files to Gemini...")
    uploaded_files = []

    for i, af in enumerate(audio_files, 1):
        print(f"  [{i}/{len(audio_files)}] {af['title']}")

        # Determine MIME type
        mime_type = "audio/mpeg"
        if af['path'].suffix.lower() == '.m4a':
            mime_type = "audio/mp4"
        elif af['path'].suffix.lower() == '.wav':
            mime_type = "audio/wav"

        # Upload file
        uploaded = genai.upload_file(
            path=str(af['path']),
            mime_type=mime_type
        )

        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(2)
            uploaded = genai.get_file(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            raise Exception(f"File upload failed for {af['title']}")

        uploaded_files.append({
            'file': uploaded,
            'title': af['title'],
            'audio_url': af['audio_url'],
            'local_path': af['path']
        })

    # Create JSONL input file for batch API
    print(f"\nCreating batch input file...")

    # Create prompt
    if include_timestamps and speaker_diarization:
        prompt = """Transcribe this audio accurately with speaker diarization.
Include timestamps in [MM:SS] format showing actual time in the recording.
Format: [MM:SS] Speaker A/B/C: <text>

Use Speaker A, Speaker B, etc. to identify different speakers.
Ensure timestamps correspond to actual positions in the audio."""
    elif include_timestamps:
        prompt = """Transcribe this audio accurately with timestamps.
Include timestamps in [MM:SS] format showing actual time in the recording.
Format: [MM:SS] <text>"""
    elif speaker_diarization:
        prompt = """Please transcribe this audio file with speaker diarization.
Format output with Speaker A, Speaker B, etc. to identify different speakers."""
    else:
        prompt = "Please transcribe this audio file accurately."

    # Create batch requests
    jsonl_lines = []

    for i, uf in enumerate(uploaded_files):
        request_obj = {
            "key": f"episode-{i}",
            "request": {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "file_data": {
                                    "file_uri": uf['file'].uri
                                }
                            }
                        ]
                    }
                ]
            }
        }
        jsonl_lines.append(json.dumps(request_obj))

    # Write JSONL file
    jsonl_content = '\n'.join(jsonl_lines)
    jsonl_path = CACHE_DIR / f"batch_input_{int(time.time())}.jsonl"
    jsonl_path.write_text(jsonl_content)

    # Upload JSONL input file
    print(f"Uploading batch input file...")
    input_file = genai.upload_file(path=str(jsonl_path))

    # Wait for input file processing
    while input_file.state.name == "PROCESSING":
        time.sleep(1)
        input_file = genai.get_file(name=input_file.name)

    # Create batch job
    print(f"Creating batch job...")

    batch_config = {
        'display_name': batch_name or f'transcribe-batch-{int(time.time())}'
    }

    client = genai.Client(api_key=api_key)
    batch_job = client.batches.create(
        model='gemini-1.5-flash',
        src=input_file.name,
        config=batch_config
    )

    job_info = {
        'job_name': batch_job.name,
        'state': batch_job.state.name,
        'create_time': batch_job.create_time.isoformat() if batch_job.create_time else None,
        'episode_count': len(episodes),
        'episodes': [
            {
                'title': uf['title'],
                'audio_url': uf['audio_url']
            }
            for uf in uploaded_files
        ],
        'display_name': batch_config['display_name']
    }

    print(f"\n✓ Batch job created!")
    print(f"  Job name: {batch_job.name}")
    print(f"  Status: {batch_job.state.name}")
    print(f"  Episodes: {len(episodes)}")
    print(f"\nUse check_batch_status('{batch_job.name}') to monitor progress")

    # Clean up local audio files
    for uf in uploaded_files:
        try:
            uf['local_path'].unlink()
        except Exception:
            pass

    # Wait for completion if requested
    if wait_for_completion:
        print(f"\nWaiting for batch completion (this may take hours)...")
        job_info = wait_for_batch(batch_job.name)

    return job_info


def check_batch_status(job_name: str) -> Dict:
    """
    Check the status of a batch transcription job.

    Args:
        job_name: Job name from create_batch_transcription()

    Returns:
        Dictionary with current status and progress

    Example:
        >>> status = check_batch_status("batches/abc123")
        >>> print(status['state'])
        JOB_STATE_RUNNING
    """
    if genai is None:
        raise ImportError("google-genai not installed")

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    batch_job = client.batches.get(name=job_name)

    return {
        'job_name': batch_job.name,
        'state': batch_job.state.name,
        'create_time': batch_job.create_time.isoformat() if batch_job.create_time else None,
        'request_count': batch_job.request_count,
        'output_uri': batch_job.output_uri if hasattr(batch_job, 'output_uri') else None
    }


def wait_for_batch(job_name: str, poll_interval: int = 60) -> Dict:
    """
    Wait for batch job to complete.

    Args:
        job_name: Job name from create_batch_transcription()
        poll_interval: Seconds between status checks (default: 60)

    Returns:
        Final job status when complete

    Example:
        >>> result = wait_for_batch("batches/abc123")
        >>> print(result['state'])
        JOB_STATE_SUCCEEDED
    """
    if genai is None:
        raise ImportError("google-genai not installed")

    print(f"Polling batch job every {poll_interval} seconds...")

    while True:
        status = check_batch_status(job_name)

        print(f"  Status: {status['state']} ({datetime.now().strftime('%H:%M:%S')})")

        if status['state'] == 'JOB_STATE_SUCCEEDED':
            print(f"✓ Batch job completed!")
            return status
        elif status['state'] in ['JOB_STATE_FAILED', 'JOB_STATE_CANCELLED', 'JOB_STATE_EXPIRED']:
            raise Exception(f"Batch job {status['state']}")

        time.sleep(poll_interval)


def get_batch_results(job_name: str, save_to_disk: bool = True) -> List[Dict]:
    """
    Retrieve transcripts from completed batch job.

    Args:
        job_name: Job name from create_batch_transcription()
        save_to_disk: Save transcripts to files

    Returns:
        List of transcript dictionaries with titles and content

    Example:
        >>> results = get_batch_results("batches/abc123")
        >>> for r in results:
        ...     print(f"{r['title']}: {len(r['transcript'])} chars")
    """
    if genai is None:
        raise ImportError("google-genai not installed")

    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)
    client = genai.Client(api_key=api_key)

    # Get batch job
    batch_job = client.batches.get(name=job_name)

    if batch_job.state.name != 'JOB_STATE_SUCCEEDED':
        raise Exception(f"Batch job not completed yet. Status: {batch_job.state.name}")

    # Download output file
    if not hasattr(batch_job, 'output_uri') or not batch_job.output_uri:
        raise Exception("Batch job has no output file")

    # Extract file name from URI
    output_file_name = batch_job.output_uri.split('/')[-1]
    output_file = genai.get_file(name=output_file_name)

    # Download JSONL results
    import requests
    response = requests.get(output_file.uri)
    response.raise_for_status()

    # Parse JSONL results
    results = []

    for line in response.text.strip().split('\n'):
        if not line:
            continue

        result_obj = json.loads(line)
        key = result_obj.get('key', '')
        response_data = result_obj.get('response', {})

        # Extract transcript from response
        transcript = ""
        if 'candidates' in response_data:
            for candidate in response_data['candidates']:
                if 'content' in candidate:
                    for part in candidate['content'].get('parts', []):
                        if 'text' in part:
                            transcript += part['text']

        # Extract episode index from key
        episode_idx = int(key.split('-')[-1]) if '-' in key else 0

        results.append({
            'key': key,
            'episode_index': episode_idx,
            'transcript': transcript,
            'title': f"Episode {episode_idx + 1}"  # Will be updated with actual title
        })

    # Sort by episode index
    results = sorted(results, key=lambda x: x['episode_index'])

    # Save to disk if requested
    if save_to_disk:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for i, result in enumerate(results):
            safe_title = f"batch_episode_{i+1:03d}"
            transcript_path = OUTPUT_DIR / f"{safe_title}_{timestamp}.txt"

            with open(transcript_path, 'w', encoding='utf-8') as f:
                header = f"""{'='*80}
BATCH TRANSCRIPTION
{'='*80}
Episode: {result['title']}
Transcribed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Batch Job: {job_name}
{'='*80}

"""
                f.write(header)
                f.write(result['transcript'])

            result['saved_to'] = str(transcript_path)
            print(f"  Saved: {transcript_path.name}")

    print(f"\n✓ Retrieved {len(results)} transcripts")
    return results


def cancel_batch(job_name: str) -> Dict:
    """
    Cancel a running batch job.

    Args:
        job_name: Job name from create_batch_transcription()

    Returns:
        Updated job status

    Example:
        >>> status = cancel_batch("batches/abc123")
        >>> print(status['state'])
        JOB_STATE_CANCELLED
    """
    if genai is None:
        raise ImportError("google-genai not installed")

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    # Cancel job
    batch_job = client.batches.cancel(name=job_name)

    return {
        'job_name': batch_job.name,
        'state': batch_job.state.name,
        'message': 'Batch job cancelled'
    }


def list_batch_jobs(limit: int = 10) -> List[Dict]:
    """
    List recent batch transcription jobs.

    Args:
        limit: Maximum number of jobs to return

    Returns:
        List of job status dictionaries

    Example:
        >>> jobs = list_batch_jobs(limit=5)
        >>> for job in jobs:
        ...     print(f"{job['display_name']}: {job['state']}")
    """
    if genai is None:
        raise ImportError("google-genai not installed")

    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    # List batches
    batches = client.batches.list(page_size=limit)

    jobs = []
    for batch in batches:
        jobs.append({
            'job_name': batch.name,
            'display_name': batch.display_name if hasattr(batch, 'display_name') else '',
            'state': batch.state.name,
            'create_time': batch.create_time.isoformat() if batch.create_time else None,
            'request_count': batch.request_count
        })

    return jobs
