"""Google Gemini transcription utilities."""

import os
import time
from pathlib import Path

try:
    from google import genai
except ImportError:
    genai = None

from .constants import GEMINI_FILE_SIZE_THRESHOLD


def get_gemini_api_key() -> str:
    """
    Get Google Gemini API key from environment.

    Returns:
        Google AI API key

    Raises:
        ValueError: If API key cannot be obtained
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        return api_key

    raise ValueError(
        "Google API key is required. Please set the GOOGLE_API_KEY environment variable."
    )


def transcribe_audio_gemini(
    audio_path: Path,
    api_key: str,
    include_timestamps: bool = True,
    speaker_diarization: bool = True
) -> str:
    """
    Transcribe audio using Google Gemini Flash.

    Args:
        audio_path: Path to audio file
        api_key: Google AI API key
        include_timestamps: Include timestamps in output
        speaker_diarization: Identify different speakers

    Returns:
        Transcription text
    """
    if genai is None:
        raise ImportError("google-genai package not installed. Run: pip install google-genai")

    genai.configure(api_key=api_key)

    file_size = audio_path.stat().st_size

    # Determine MIME type
    mime_type = "audio/mpeg"
    if audio_path.suffix.lower() == '.m4a':
        mime_type = "audio/mp4"
    elif audio_path.suffix.lower() == '.wav':
        mime_type = "audio/wav"

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

    # For large files (>20MB), use File API
    if file_size > GEMINI_FILE_SIZE_THRESHOLD:
        uploaded_file = genai.upload_file(path=str(audio_path))

        # Wait for file processing
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise Exception("File processing failed")

        # Generate transcription
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content([prompt, uploaded_file])

        # Clean up uploaded file
        genai.delete_file(name=uploaded_file.name)
    else:
        # For smaller files, send inline
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(
            [
                prompt,
                {
                    'mime_type': mime_type,
                    'data': audio_path.read_bytes()
                }
            ]
        )

    return response.text
