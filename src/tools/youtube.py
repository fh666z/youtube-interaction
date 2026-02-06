"""YouTube-specific tool definitions."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from pytube import Search as youtube_search, Playlist
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


def _extract_info_with_ytdlp(url: str) -> Dict[str, Any]:
    """
    Helper function to extract info using yt-dlp.
    
    Args:
        url: YouTube URL (video, playlist, or channel)
        
    Returns:
        Dictionary containing extracted info
        
    Raises:
        VideoNotFoundError: If content is not found.
        ToolExecutionError: If extraction fails.
    """
    yt_dlp_logger = _get_suppressed_yt_dlp_logger()
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'logger': yt_dlp_logger}) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise VideoNotFoundError(f"Content not found: {url}")
            return info
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to extract info for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


def _format_upload_date(date_str: Optional[str]) -> Optional[str]:
    """
    Convert YYYYMMDD format date string to readable format.
    
    Args:
        date_str: Date string in YYYYMMDD format
        
    Returns:
        Formatted date string (YYYY-MM-DD) or None if invalid
    """
    if not date_str or len(date_str) != 8:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None


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
def search_youtube(query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Search YouTube for videos matching the query.
    
    Args:
        query: The search term to look for on YouTube
        max_results: Maximum number of results to return (optional, defaults to all results)
        
    Returns:
        List of dictionaries containing video titles, IDs, and URLs.
        
    Raises:
        ToolExecutionError: If search fails.
    """
    try:
        s = youtube_search(query)
        results = [
            {
                "title": yt.title,
                "video_id": yt.video_id,
                "url": f"https://youtu.be/{yt.video_id}"
            }
            for yt in s.results
        ]
        
        if max_results is not None and max_results > 0:
            return results[:max_results]
        
        return results
    except Exception as e:
        error_msg = f"Failed to search YouTube for '{query}': {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_full_metadata(url: str) -> dict:
    """
    Extract comprehensive metadata given a YouTube URL, including title, views, 
    duration, channel, likes, comments, chapters, description, tags, categories, 
    upload date, and more.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing comprehensive video metadata.
        
    Raises:
        VideoNotFoundError: If video is not found.
        ToolExecutionError: If metadata extraction fails.
    """
    try:
        info = _extract_info_with_ytdlp(url)
        
        # Format upload date if available
        upload_date_formatted = _format_upload_date(info.get('upload_date'))
        
        return {
            # Basic info
            'title': info.get('title'),
            'views': info.get('view_count'),
            'duration': info.get('duration'),
            'channel': info.get('uploader'),
            'likes': info.get('like_count'),
            'comments': info.get('comment_count'),
            'chapters': info.get('chapters', []),
            
            # Enhanced metadata
            'description': info.get('description'),
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'upload_date': upload_date_formatted,
            'upload_date_raw': info.get('upload_date'),
            'release_date': _format_upload_date(info.get('release_date')),
            
            # Channel information
            'channel_id': info.get('channel_id'),
            'channel_url': info.get('channel_url'),
            'channel_follower_count': info.get('channel_follower_count'),
            'uploader_id': info.get('uploader_id'),
            'uploader_url': info.get('uploader_url'),
            
            # Content details
            'age_limit': info.get('age_limit'),
            'is_live': info.get('is_live', False),
            'was_live': info.get('was_live', False),
            'live_status': info.get('live_status'),
            'language': info.get('language'),
            'license': info.get('license'),
            
            # Additional metadata
            'availability': info.get('availability'),
            'webpage_url': info.get('webpage_url'),
            'original_url': info.get('original_url'),
        }
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get metadata for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_channel_info(url: str) -> Dict[str, Any]:
    """
    Get channel information from a YouTube video URL or channel URL.
    
    Args:
        url: YouTube video URL or channel URL
        
    Returns:
        Dictionary containing channel information including name, ID, URL, 
        subscriber count, and description.
        
    Raises:
        VideoNotFoundError: If video/channel is not found.
        ToolExecutionError: If channel info extraction fails.
    """
    try:
        info = _extract_info_with_ytdlp(url)
        
        return {
            'channel_name': info.get('uploader') or info.get('channel'),
            'channel_id': info.get('channel_id'),
            'channel_url': info.get('channel_url'),
            'channel_follower_count': info.get('channel_follower_count'),
            'uploader_id': info.get('uploader_id'),
            'uploader_url': info.get('uploader_url'),
            'channel_description': info.get('channel_description'),
        }
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get channel info for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_playlist_info(url: str) -> Dict[str, Any]:
    """
    Get playlist information from a YouTube playlist URL.
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        Dictionary containing playlist information including title, ID, URL, 
        video count, and description.
        
    Raises:
        VideoNotFoundError: If playlist is not found.
        ToolExecutionError: If playlist info extraction fails.
    """
    try:
        info = _extract_info_with_ytdlp(url)
        
        # For playlists, yt-dlp returns entries as a list
        entries = info.get('entries', [])
        video_count = len(entries) if entries else info.get('playlist_count')
        
        return {
            'playlist_title': info.get('title') or info.get('playlist'),
            'playlist_id': info.get('id') or info.get('playlist_id'),
            'playlist_url': info.get('webpage_url') or url,
            'video_count': video_count,
            'playlist_description': info.get('description'),
            'playlist_uploader': info.get('uploader'),
            'playlist_uploader_id': info.get('uploader_id'),
        }
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get playlist info for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def get_playlist_videos(url: str) -> List[Dict[str, Any]]:
    """
    Get list of videos in a YouTube playlist.
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        List of dictionaries containing video information (title, ID, URL, position).
        
    Raises:
        VideoNotFoundError: If playlist is not found.
        ToolExecutionError: If playlist video extraction fails.
    """
    try:
        info = _extract_info_with_ytdlp(url)
        entries = info.get('entries', [])
        
        if not entries:
            # Try using pytube as fallback
            try:
                playlist = Playlist(url)
                return [
                    {
                        'title': video.title,
                        'video_id': video.video_id,
                        'url': video.watch_url,
                        'position': idx + 1
                    }
                    for idx, video in enumerate(playlist.videos)
                ]
            except Exception as pytube_error:
                logger.warning(f"Pytube fallback failed: {pytube_error}")
                return []
        
        videos = []
        for idx, entry in enumerate(entries):
            if entry:
                videos.append({
                    'title': entry.get('title'),
                    'video_id': entry.get('id'),
                    'url': entry.get('webpage_url') or entry.get('url'),
                    'position': idx + 1,
                    'duration': entry.get('duration'),
                    'channel': entry.get('uploader') or entry.get('channel'),
                })
        
        return videos
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_msg = f"Failed to get playlist videos for {url}: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def fetch_transcript_with_timestamps(video_id: str, language: str = YouTubeConfig.DEFAULT_TRANSCRIPT_LANGUAGE) -> List[Dict[str, Any]]:
    """
    Fetches the transcript of a YouTube video with timestamps.
    
    Args:
        video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ").
        language: Language code for the transcript (e.g., "en", "es").
    
    Returns:
        List of dictionaries containing transcript segments with text, start time, and duration.
        
    Raises:
        TranscriptNotFoundError: If transcript is not available.
        ToolExecutionError: If transcript fetching fails.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list_transcripts(video_id)
        
        # Try to get transcript in requested language
        try:
            transcript = transcript_list.find_transcript([language])
        except:
            # Fallback to any available transcript
            transcript = transcript_list.find_transcript(transcript_list.manually_created_transcript_language_codes + 
                                                         transcript_list.generated_transcript_language_codes)
        
        # Get transcript with timestamps using get_transcript() which returns list of dicts
        transcript_data = transcript.fetch()
        
        # Convert TranscriptSnippet objects to dictionaries
        return [
            {
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            }
            for snippet in transcript_data
        ]
    except Exception as e:
        error_msg = f"Failed to fetch transcript with timestamps for video {video_id}: {str(e)}"
        logger.error(error_msg)
        if "No transcripts were found" in str(e) or "TranscriptsDisabled" in str(e):
            raise TranscriptNotFoundError(error_msg)
        raise ToolExecutionError(error_msg)


@tool
def list_transcript_languages(video_id: str) -> List[Dict[str, Any]]:
    """
    List all available transcript/caption languages for a YouTube video.
    
    Args:
        video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ").
    
    Returns:
        List of dictionaries containing language information (code, name, is_generated, is_translatable).
        
    Raises:
        TranscriptNotFoundError: If no transcripts are available.
        ToolExecutionError: If language listing fails.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list_transcripts(video_id)
        
        languages = []
        
        # Add manually created transcripts
        for transcript in transcript_list.manually_created_transcripts.values():
            languages.append({
                'language_code': transcript.language_code,
                'language': transcript.language,
                'is_generated': False,
                'is_translatable': transcript.is_translatable,
            })
        
        # Add auto-generated transcripts
        for transcript in transcript_list.generated_transcripts.values():
            languages.append({
                'language_code': transcript.language_code,
                'language': transcript.language,
                'is_generated': True,
                'is_translatable': transcript.is_translatable,
            })
        
        return languages
    except Exception as e:
        error_msg = f"Failed to list transcript languages for video {video_id}: {str(e)}"
        logger.error(error_msg)
        if "No transcripts were found" in str(e) or "TranscriptsDisabled" in str(e):
            raise TranscriptNotFoundError(error_msg)
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
