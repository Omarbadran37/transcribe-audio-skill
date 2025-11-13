"""Podcast RSS feed discovery and parsing utilities."""

import time
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, List


def find_podcast_rss_feed(podcast_name: str) -> Optional[Dict[str, str]]:
    """
    Find RSS feed URL for a podcast using multiple search strategies.

    Strategies:
    1. Podcastindex API
    2. Apple Podcasts API
    3. Common hosting platforms (Megaphone, Anchor, Podbean, etc.)

    Args:
        podcast_name: Name of the podcast to search for

    Returns:
        Dict with 'rss_url', 'title', 'description' if found, None otherwise
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Strategy 1: Try Podcastindex API
    try:
        api_url = f"https://api.podcastindex.org/api/1.0/search/byterm?q={podcast_name.replace(' ', '+')}&type=podcast"
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'feeds' in data and len(data['feeds']) > 0:
                feed = data['feeds'][0]
                rss_url = feed.get('url')
                if rss_url:
                    return {
                        'rss_url': rss_url,
                        'title': feed.get('title', ''),
                        'description': feed.get('description', '')[:200],
                        'source': 'Podcastindex'
                    }
    except Exception:
        pass

    # Strategy 2: Try Apple Podcasts API
    try:
        api_url = f"https://itunes.apple.com/search?term={podcast_name.replace(' ', '+')}&media=podcast&limit=1"
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                podcast = data['results'][0]
                feed_url = podcast.get('feedUrl')
                if feed_url:
                    return {
                        'rss_url': feed_url,
                        'title': podcast.get('collectionName', ''),
                        'description': podcast.get('description', '')[:200],
                        'source': 'Apple Podcasts'
                    }
    except Exception:
        pass

    # Strategy 3: Try common hosting platforms
    common_hosts = [
        ('Megaphone', f"https://feeds.megaphone.fm/{podcast_name.lower().replace(' ', '')}"),
        ('Anchor', f"https://anchor.fm/s/{podcast_name.lower().replace(' ', '-')}/podcast/rss"),
        ('Podbean', f"https://{podcast_name.lower().replace(' ', '')}.podbean.com/feed.xml"),
    ]

    for host_name, feed_url in common_hosts:
        try:
            response = requests.head(feed_url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return {
                    'rss_url': feed_url,
                    'title': podcast_name,
                    'description': f'Found on {host_name}',
                    'source': host_name
                }
        except Exception:
            pass

    return None


def parse_rss_feed(rss_url: str, max_episodes: int = 10) -> List[Dict]:
    """
    Parse RSS feed and extract episode metadata.

    Args:
        rss_url: URL to RSS feed
        max_episodes: Maximum number of episodes to return

    Returns:
        List of episode dictionaries with title, audio_url, pub_date, duration
    """
    response = requests.get(rss_url, timeout=30)
    response.raise_for_status()

    # Parse XML
    root = ET.fromstring(response.content)

    # Find all items (episodes)
    episodes = []
    for item in root.findall('.//item')[:max_episodes]:
        episode = {}

        # Extract title
        title_elem = item.find('title')
        episode['title'] = title_elem.text if title_elem is not None else "Untitled"

        # Extract enclosure (audio URL)
        enclosure = item.find('enclosure')
        if enclosure is not None:
            episode['audio_url'] = enclosure.get('url')
        else:
            continue  # Skip if no audio

        # Extract publication date
        pub_date = item.find('pubDate')
        episode['pub_date'] = pub_date.text if pub_date is not None else ""

        # Extract duration
        duration = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
        episode['duration'] = duration.text if duration is not None else "Unknown"

        # Extract description
        desc = item.find('description')
        episode['description'] = desc.text[:200] if desc is not None else ""

        episodes.append(episode)

    return episodes


def download_audio_file(
    audio_url: str,
    output_dir: Path,
    episode_title: Optional[str] = None
) -> Path:
    """
    Download audio file from URL (synchronous).

    Args:
        audio_url: URL to audio file
        output_dir: Directory to save file
        episode_title: Optional episode title for filename

    Returns:
        Path to downloaded file
    """
    # Create safe filename
    if episode_title:
        safe_title = "".join(c for c in episode_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # Limit length
    else:
        safe_title = f"audio_{int(time.time())}"

    # Determine file extension from URL
    extension = '.mp3'  # Default
    if '.mp3' in audio_url.lower():
        extension = '.mp3'
    elif '.m4a' in audio_url.lower():
        extension = '.m4a'
    elif '.wav' in audio_url.lower():
        extension = '.wav'

    output_path = output_dir / f"{safe_title}{extension}"

    # Download file using requests (sync)
    response = requests.get(audio_url, timeout=60, stream=True, allow_redirects=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path
