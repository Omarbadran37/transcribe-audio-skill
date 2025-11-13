# Environment Setup

## API Key Configuration

The transcribe skill requires a Google Gemini API key for podcast transcription (YouTube transcription works without an API key).

### Option 1: Using .env File (Recommended)

**1. Edit the .env file:**

```bash
# Open the .env file
nano ~/.claude/skills/transcribe-audio/.env

# Or with any text editor
open -e ~/.claude/skills/transcribe-audio/.env
```

**2. Replace the placeholder with your API key:**

```bash
# Before
GOOGLE_API_KEY=your-api-key-here

# After
GOOGLE_API_KEY=AIzaSyD...your-actual-key
```

**3. Save the file**

The API key will be automatically loaded when you import the skill\!

### Option 2: Environment Variable

Set the API key in your shell:

```bash
# Temporary (current session only)
export GOOGLE_API_KEY='your-api-key-here'

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo "export GOOGLE_API_KEY='your-api-key-here'" >> ~/.zshrc
source ~/.zshrc
```

### Option 3: Set in Code

```python
import os
os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'

# Then import skill
from servers.transcribe import transcribe_episode
```

## Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

## Verification

Test that your API key is loaded:

```python
import sys
from pathlib import Path

# Add skill to path
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))

# Import (will auto-load .env)
from servers.transcribe import transcribe_episode

# Check if key is loaded
import os
if os.getenv('GOOGLE_API_KEY'):
    print("✓ API key loaded successfully")
else:
    print("✗ API key not found")
```

## Security Notes

- **Never commit .env file to git** (already in .gitignore)
- **Don't share your API key** publicly
- **Rotate keys regularly** if exposed
- The .env file is only readable by you (file permissions)

## Troubleshooting

### API key not loading

**Check file exists:**
```bash
ls -la ~/.claude/skills/transcribe-audio/.env
```

**Check file contents:**
```bash
cat ~/.claude/skills/transcribe-audio/.env
```

**Manually load .env:**
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe-audio/scripts"))

# Manually trigger env loader
from env_loader import load_env
load_env()

# Verify
import os
print(f"API Key loaded: {bool(os.getenv('GOOGLE_API_KEY'))}")
```

### API key invalid

Error: `ValueError: Google API key is required`

**Solution:**
1. Verify key is correct (starts with `AIza`)
2. Check for extra spaces in .env file
3. Ensure no quotes around the key value
4. Try regenerating key in Google AI Studio

### Permission denied

Error: `Permission denied: .env`

**Solution:**
```bash
chmod 600 ~/.claude/skills/transcribe-audio/.env
```

## What Needs API Key

| Function | Requires API Key |
|----------|------------------|
| `get_transcript()` | ✗ No (uses YouTube API) |
| `find_rss()` | ✗ No (uses public APIs) |
| `parse_rss()` | ✗ No (parses XML) |
| `transcribe_episode()` | ✓ Yes (uses Gemini) |
| `get_cached()` | ✗ No (reads cache) |
| `list_cache()` | ✗ No (lists cache) |

Only podcast transcription requires the API key\!
