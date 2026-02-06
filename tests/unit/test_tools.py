"""Unit tests for YouTube tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.tools.youtube import (
    extract_video_id,
    fetch_transcript,
    search_youtube,
    get_full_metadata,
    get_thumbnails
)
from src.utils.exceptions import (
    InvalidVideoURLError,
    TranscriptNotFoundError,
    ToolExecutionError
)


class TestExtractVideoID:
    """Tests for extract_video_id tool."""
    
    def test_extract_from_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id.invoke({"url": url})
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_from_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = extract_video_id.invoke({"url": url})
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_from_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = extract_video_id.invoke({"url": url})
        assert result == "dQw4w9WgXcQ"
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises InvalidVideoURLError."""
        url = "https://example.com/not-youtube"
        with pytest.raises(InvalidVideoURLError):
            extract_video_id.invoke({"url": url})


class TestFetchTranscript:
    """Tests for fetch_transcript tool."""
    
    @patch('src.tools.youtube.YouTubeTranscriptApi')
    def test_fetch_transcript_success(self, mock_api_class):
        """Test successful transcript fetching."""
        mock_api = Mock()
        mock_snippet = Mock()
        mock_snippet.text = "Hello world"
        mock_transcript = Mock()
        mock_transcript.snippets = [mock_snippet]
        mock_api.fetch.return_value = mock_transcript
        mock_api_class.return_value = mock_api
        
        result = fetch_transcript.invoke({"video_id": "test123", "language": "en"})
        assert "Hello world" in result
    
    @patch('src.tools.youtube.YouTubeTranscriptApi')
    def test_fetch_transcript_not_found(self, mock_api_class):
        """Test transcript not found error."""
        mock_api = Mock()
        mock_api.fetch.side_effect = Exception("No transcripts were found")
        mock_api_class.return_value = mock_api
        
        with pytest.raises(TranscriptNotFoundError):
            fetch_transcript.invoke({"video_id": "test123"})


class TestSearchYouTube:
    """Tests for search_youtube tool."""
    
    @patch('src.tools.youtube.youtube_search')
    def test_search_youtube_success(self, mock_search):
        """Test successful YouTube search."""
        mock_result = Mock()
        mock_result.title = "Test Video"
        mock_result.video_id = "test123"
        mock_search.return_value.results = [mock_result]
        
        result = search_youtube.invoke({"query": "test query"})
        assert len(result) == 1
        assert result[0]["title"] == "Test Video"
        assert result[0]["video_id"] == "test123"
    
    @patch('src.tools.youtube.youtube_search')
    def test_search_youtube_error(self, mock_search):
        """Test YouTube search error handling."""
        mock_search.side_effect = Exception("Search failed")
        
        with pytest.raises(ToolExecutionError):
            search_youtube.invoke({"query": "test query"})


class TestGetFullMetadata:
    """Tests for get_full_metadata tool."""
    
    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_get_metadata_success(self, mock_ydl_class):
        """Test successful metadata retrieval."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'title': 'Test Video',
            'view_count': 1000,
            'duration': 120,
            'uploader': 'Test Channel',
            'like_count': 100,
            'comment_count': 50,
            'chapters': []
        }
        mock_ydl_class.return_value = mock_ydl
        
        result = get_full_metadata.invoke({"url": "https://youtube.com/watch?v=test"})
        assert result['title'] == 'Test Video'
        assert result['views'] == 1000


class TestGetThumbnails:
    """Tests for get_thumbnails tool."""
    
    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_get_thumbnails_success(self, mock_ydl_class):
        """Test successful thumbnail retrieval."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'thumbnails': [
                {'url': 'http://example.com/thumb.jpg', 'width': 320, 'height': 180}
            ]
        }
        mock_ydl_class.return_value = mock_ydl
        
        result = get_thumbnails.invoke({"url": "https://youtube.com/watch?v=test"})
        assert len(result) == 1
        assert result[0]['url'] == 'http://example.com/thumb.jpg'
