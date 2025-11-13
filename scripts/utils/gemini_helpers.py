"""Google Gemini transcription utilities."""

import os
import time
import mimetypes
from pathlib import Path

try:
    from google import genai
except ImportError:
    genai = None

from .constants import GEMINI_FILE_SIZE_THRESHOLD

# Model constants - centralized for easy updates
GEMINI_MODEL_FLASH = 'models/gemini-2.0-flash-exp'
GEMINI_MODEL_PRO = 'models/gemini-pro-latest'

# Default model for all operations
DEFAULT_MODEL = GEMINI_MODEL_FLASH


class GeminiTranscriptionError(Exception):
    """Base exception for Gemini transcription errors."""
    pass


class FileUploadError(GeminiTranscriptionError):
    """Exception raised when file upload to Gemini fails."""
    pass


class TranscriptionAPIError(GeminiTranscriptionError):
    """Exception raised when Gemini API call fails."""
    pass


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


def format_transcript(
    raw_transcript: str,
    api_key: str = None,
    title: str = None,
    include_timestamps: bool = True,
    clean_filler_words: bool = True,
    detect_sections: bool = True
) -> str:
    """
    Format raw transcript into clean, professional document using Google Gemini.

    Uses Google Gemini to:
    - Create descriptive title (if not provided)
    - Identify all speakers
    - Format dialogue as bullet points with bold speaker names
    - Insert section headings based on topic flow
    - Clean grammar, spelling, punctuation
    - Remove filler words (um, uh, you know)
    - Preserve timestamps in [MM:SS] format

    Args:
        raw_transcript: Raw transcript text to format
        api_key: Google AI API key (uses GOOGLE_API_KEY env if not provided)
        title: Document title (auto-generated if None)
        include_timestamps: Include [MM:SS] timestamps in output
        clean_filler_words: Remove filler words (um, uh, you know)
        detect_sections: Insert section headings based on topics

    Returns:
        Formatted markdown document

    Example:
        >>> raw = get_transcript("video-id")
        >>> formatted = format_transcript(raw, title="My Discussion")
        >>> print(formatted)
    """
    if genai is None:
        raise ImportError("google-genai package not installed. Run: pip install google-genai")

    # Get API key
    if api_key is None:
        api_key = get_gemini_api_key()

    # Create client with new API
    client = genai.Client(api_key=api_key)

    # Build prompt based on options
    title_instruction = f" (use this title: {title})" if title else ""
    timestamp_instruction = "Preserve all timestamps in [MM:SS] format." if include_timestamps else "Remove all timestamps."
    filler_instruction = 'Remove filler words (like "um," "uh," "you know") and repeated words to improve clarity, but do not change the original meaning or the speaker\'s tone.' if clean_filler_words else 'Keep all words as-is, only fix grammar and punctuation.'
    section_instruction = 'Analyze the flow of the conversation and insert logical section headings in bold to group related topics. Examples might be "**Introduction**", "**Main Discussion**", "**Conclusion**", etc.' if detect_sections else 'Do not add section headings.'

    prompt = f"""Please act as an editor and reformat the provided raw transcript into a clean, readable, and well-structured document. Here are the specific instructions:

1. **Title:** Create a concise and descriptive title for the conversation{title_instruction}.

2. **Speaker Identification:** Identify all speakers (e.g., Alex, Michael, John).

3. **Dialogue Formatting:**
   * Start each line of dialogue on a new bullet point.
   * Prefix each line with the speaker's name in bold, followed by a colon.
   * Example: `* **Alex:** This is the text of what I said.`

4. **Section Headings:** {section_instruction}

5. **Editing & Cleanup:**
   * Correct all spelling, grammar, and punctuation mistakes.
   * {filler_instruction}

6. **Timestamps:** {timestamp_instruction}

Ensure consistent formatting throughout the document.

Here is the raw transcript:

{raw_transcript}"""

    # Generate formatted output with error handling
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        raise TranscriptionAPIError(
            f"Failed to format transcript with Gemini API: {str(e)}"
        ) from e


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

    # Create client with new API
    client = genai.Client(api_key=api_key)

    file_size = audio_path.stat().st_size

    # Determine MIME type using mimetypes library for broader support
    mime_type, _ = mimetypes.guess_type(str(audio_path))
    if not mime_type or not mime_type.startswith('audio/'):
        # Fallback to common audio formats
        extension_map = {
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            '.aac': 'audio/aac'
        }
        mime_type = extension_map.get(audio_path.suffix.lower(), 'audio/mpeg')

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
        try:
            uploaded_file = client.files.upload(
                file=open(str(audio_path), 'rb'),
                config=genai.types.UploadFileConfig(mime_type=mime_type)
            )
        except Exception as e:
            raise FileUploadError(
                f"Failed to upload audio file to Gemini: {str(e)}"
            ) from e

        # Wait for file processing
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise FileUploadError(
                f"File processing failed for {audio_path.name}. "
                f"File state: {uploaded_file.state.name}"
            )

        # Generate transcription with error handling
        try:
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=[prompt, uploaded_file]
            )
        except Exception as e:
            raise TranscriptionAPIError(
                f"Failed to transcribe audio with Gemini API: {str(e)}"
            ) from e
        finally:
            # Always clean up uploaded file
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass  # Ignore cleanup errors

    else:
        # For smaller files, send inline with error handling
        try:
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=[
                    prompt,
                    {
                        'mime_type': mime_type,
                        'data': audio_path.read_bytes()
                    }
                ]
            )
        except Exception as e:
            raise TranscriptionAPIError(
                f"Failed to transcribe audio with Gemini API: {str(e)}"
            ) from e

    return response.text
