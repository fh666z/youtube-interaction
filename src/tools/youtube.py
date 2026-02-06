"""YouTube-specific tool definitions."""

import re
from typing import List, Dict, Any
import logging

from pytube import Search as youtube_search
from langchain.tools import tool
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from src.core.constants import YouTubeConfig
from src.utils.exceptions import (
    InvalidVideoURLError,
    TranscriptNotFoundError,
    VideoNotFoundError,
    ToolExecutionError
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _get_suppressed_yt_dlp_logger() -> logging.Logger:
    """Get a yt-dlp logger with warnings suppressed."""
    yt_dlp_logger = logging.getLogger('yt_dlp')
    yt_dlp_logger.setLevel(logging.ERROR)
    return yt_dlp_logger


@tool
def extract_video_id(url: str) -> str:
    """
    Extracts the 11-character YouTube video ID from a URL.
    
    Args:
        url: A YouTube URL containing a video ID.

    Returns:
        Extracted video ID or error message if parsing fails.
        
    Raises:
        InvalidVideoURLError: If the URL format is invalid.
    """
    try:
        match = re.search(YouTubeConfig.VIDEO_ID_PATTERN, url)
        if match:
            return match.group(1)
        raise InvalidVideoURLError(f"Invalid YouTube URL format: {url}")
    except InvalidVideoURLError:
        raise
    except Exception as e:
        logger.error(f"Error extracting video ID from {url}: {e}")
        raise InvalidVideoURLError(f"Failed to extract video ID: {str(e)}")


@tool
def fetch_transcript(video_id: str, language: str = YouTubeConfig.DEFAULT_TRANSCRIPT_LANGUAGE) -> str:
    """
    Fetches the transcript of a YouTube video.
    
    Args:
        video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ").
        language: Language code for the transcript (e.g., "en", "es").
    
    Returns:
        The transcript text.
        
    Raises:
        TranscriptNotFoundError: If transcript is not available.
        ToolExecutionError: If transcript fetching fails.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=[language])
        return " ".join([snippet.text for snippet in transcript.snippets])
    except Exception as e:
        error_msg = f"Failed to fetch transcript for video {video_id}: {str(e)}"
        logger.error(error_msg)
        if "No transcripts were found" in str(e) or "TranscriptsDisabled" in str(e):
            raise TranscriptNotFoundError(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def search_youtube(query: str) -> List[Dict[str, str]]:
    """
    Search YouTube for videos matching the query.
    
    Args:
        query: The search term to look for on YouTube
        
    Returns:
        List of dictionaries containing video titles, IDs, and URLs.
        
    Raises:
        ToolExecutionError: If search fails.
    """
    try:
        s = youtube_search(query)
        return [
            {
                "title": yt.title,
                "video_id": yt.video_id,
                "url": f"https://youtu.be/{yt.video_id}"
            }
            for yt in s.results
        ]
    except Exception as e:
        error_msg = f"Failed to search YouTube for '{query}': {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_full_metadata(url: str) -> dict:
    """
    Extract metadata given a YouTube URL, including title, views, duration, 
    channel, likes, comments, and chapters.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing video metadata.
        
    Raises:
        VideoNotFoundError: If video is not found.
        ToolExecutionError: If metadata extraction fails.
    """
    yt_dlp_logger = _get_suppressed_yt_dlp_logger()
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'logger': yt_dlp_logger}) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise VideoNotFoundError(f"Video not found: {url}")
            
            return {
                'title': info.get('title'),
                'views': info.get('view_count'),
                'duration': info.get('duration'),
                'channel': info.get('uploader'),
                'likes': info.get('like_count'),
                'comments': info.get('comment_count'),
                'chapters': info.get('chapters', [])
            }
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get metadata for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_thumbnails(url: str) -> List[Dict[str, Any]]:
    """
    Get available thumbnails for a YouTube video using its URL.
    
    Args:
        url: YouTube video URL (any format)
        
    Returns:
        List of dictionaries with thumbnail URLs and resolutions.
        
    Raises:
        VideoNotFoundError: If video is not found.
        ToolExecutionError: If thumbnail extraction fails.
    """
    yt_dlp_logger = _get_suppressed_yt_dlp_logger()

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'logger': yt_dlp_logger}) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise VideoNotFoundError(f"Video not found: {url}")
            
            thumbnails = []
            for t in info.get('thumbnails', []):
                if 'url' in t:
                    thumbnails.append({
                        "url": t['url'],
                        "width": t.get('width'),
                        "height": t.get('height'),
                        "resolution": f"{t.get('width', '')}x{t.get('height', '')}".strip('x')
                    })
            
            return thumbnails
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get thumbnails for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)
