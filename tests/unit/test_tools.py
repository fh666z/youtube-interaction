"""Unit tests for YouTube tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.tools.youtube import (
    extract_video_id,
    fetch_transcript,
    search_youtube,
    get_full_metadata,
    get_thumbnails,
    get_channel_info,
    get_playlist_info,
    get_playlist_videos,
    fetch_transcript_with_timestamps,
    list_transcript_languages,
    _format_upload_date,
    _extract_info_with_ytdlp,
)
from src.utils.exceptions import (
    InvalidVideoURLError,
    TranscriptNotFoundError,
    VideoNotFoundError,
    ToolExecutionError,
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


class TestExtractVideoIDEdgeCases:
    """Additional edge-case tests for extract_video_id tool."""

    def test_too_short_video_id_raises_error(self):
        """URL with v= but too-short ID should raise InvalidVideoURLError."""
        url = "https://www.youtube.com/watch?v=short_id"
        with pytest.raises(InvalidVideoURLError):
            extract_video_id.invoke({"url": url})

    def test_missing_video_id_raises_error(self):
        """URL with v= but missing ID should raise InvalidVideoURLError."""
        url = "https://www.youtube.com/watch?v="
        with pytest.raises(InvalidVideoURLError):
            extract_video_id.invoke({"url": url})


class TestGetThumbnailsEdgeCases:
    """Edge-case tests for get_thumbnails tool."""

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_get_thumbnails_empty_list(self, mock_ydl_class):
        """No thumbnails should return empty list."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {'thumbnails': []}
        mock_ydl_class.return_value = mock_ydl

        result = get_thumbnails.invoke({"url": "https://youtube.com/watch?v=test"})
        assert result == []

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_get_thumbnails_missing_thumbnails_key(self, mock_ydl_class):
        """Missing thumbnails key should return empty list."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {}
        mock_ydl_class.return_value = mock_ydl

        result = get_thumbnails.invoke({"url": "https://youtube.com/watch?v=test"})
        assert result == []

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_get_thumbnails_error_raises_tool_execution_error(self, mock_ydl_class):
        """Generic extraction error should raise ToolExecutionError."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Extraction failed")
        mock_ydl_class.return_value = mock_ydl

        with pytest.raises(ToolExecutionError):
            get_thumbnails.invoke({"url": "https://youtube.com/watch?v=test"})


class TestFormatUploadDate:
    """Tests for _format_upload_date helper function."""

    def test_format_valid_date(self):
        """Test formatting a valid date string."""
        result = _format_upload_date("20231225")
        assert result == "2023-12-25"

    def test_format_invalid_date_returns_none(self):
        """Test that invalid date format returns None."""
        assert _format_upload_date("invalid") is None
        assert _format_upload_date("2023122") is None  # Too short
        assert _format_upload_date("202312251") is None  # Too long
        assert _format_upload_date(None) is None
        assert _format_upload_date("") is None

    def test_format_invalid_date_value_returns_none(self):
        """Test that invalid date value returns None."""
        assert _format_upload_date("20231301") is None  # Invalid month
        assert _format_upload_date("20231232") is None  # Invalid day


class TestExtractInfoWithYtDlp:
    """Tests for _extract_info_with_ytdlp helper function."""

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_extract_info_success(self, mock_ydl_class):
        """Test successful info extraction."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {'title': 'Test Video', 'id': 'test123'}
        mock_ydl_class.return_value = mock_ydl

        result = _extract_info_with_ytdlp("https://youtube.com/watch?v=test")
        assert result['title'] == 'Test Video'
        assert result['id'] == 'test123'

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_extract_info_not_found(self, mock_ydl_class):
        """Test VideoNotFoundError when content not found."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = None
        mock_ydl_class.return_value = mock_ydl

        with pytest.raises(VideoNotFoundError):
            _extract_info_with_ytdlp("https://youtube.com/watch?v=invalid")

    @patch('src.tools.youtube.yt_dlp.YoutubeDL')
    def test_extract_info_error(self, mock_ydl_class):
        """Test ToolExecutionError on extraction failure."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Extraction failed")
        mock_ydl_class.return_value = mock_ydl

        with pytest.raises(ToolExecutionError):
            _extract_info_with_ytdlp("https://youtube.com/watch?v=test")


class TestGetFullMetadataEnhanced:
    """Enhanced tests for get_full_metadata tool."""

    @patch('src.tools.youtube._extract_info_with_ytdlp')
    def test_get_metadata_with_enhanced_fields(self, mock_extract):
        """Test metadata retrieval with enhanced fields and formatting."""
        mock_extract.return_value = {
            'title': 'Test Video',
            'view_count': 1000,
            'duration': 120,
            'uploader': 'Test Channel',
            'like_count': 100,
            'comment_count': 50,
            'chapters': [],
            'description': 'Test description',
            'tags': ['tag1', 'tag2'],
            'categories': ['Education'],
            'upload_date': '20231225',
            'release_date': '20231220',
            'channel_id': 'UCtest123',
            'channel_url': 'https://youtube.com/channel/UCtest123',
            'channel_follower_count': 5000,
            'uploader_id': 'test_uploader',
            'uploader_url': 'https://youtube.com/user/test_uploader',
            'age_limit': 0,
            'is_live': False,
            'was_live': False,
            'live_status': 'not_live',
            'language': 'en',
            'license': 'youtube',
            'availability': 'public',
            'webpage_url': 'https://youtube.com/watch?v=test',
            'original_url': None,
        }

        result = get_full_metadata.invoke({"url": "https://youtube.com/watch?v=test"})

        # Basic fields
        assert result['title'] == 'Test Video'
        assert result['views'] == 1000
        assert result['duration'] == 120

        # Enhanced metadata
        assert result['description'] == 'Test description'
        assert result['tags'] == ['tag1', 'tag2']
        assert result['categories'] == ['Education']
        assert result['upload_date'] == '2023-12-25'
        assert result['upload_date_raw'] == '20231225'
        assert result['release_date'] == '2023-12-20'

        # Channel information
        assert result['channel_id'] == 'UCtest123'
        assert result['channel_url'] == 'https://youtube.com/channel/UCtest123'
        assert result['channel_follower_count'] == 5000

        # Content details
        assert result['age_limit'] == 0
        assert result['is_live'] is False
        assert result['language'] == 'en'
        assert result['license'] == 'youtube'

    @patch('src.tools.youtube._extract_info_with_ytdlp')
    def test_get_metadata_with_missing_fields(self, mock_extract):
        """Test metadata retrieval handles missing optional fields."""
        mock_extract.return_value = {
            'title': 'Test Video',
            'view_count': 1000,
        }

        result = get_full_metadata.invoke({"url": "https://youtube.com/watch?v=test"})
        assert result['title'] == 'Test Video'
        assert result['tags'] == []
        assert result['chapters'] == []
        assert result['description'] is None
        assert result['upload_date'] is None

    @patch('src.tools.youtube._extract_info_with_ytdlp')
    def test_get_metadata_video_not_found(self, mock_extract):
        """VideoNotFoundError from helper should propagate."""
        mock_extract.side_effect = VideoNotFoundError("Video not found")

        with pytest.raises(VideoNotFoundError):
            get_full_metadata.invoke({"url": "https://youtube.com/watch?v=missing"})

    @patch('src.tools.youtube._extract_info_with_ytdlp')
    def test_get_metadata_generic_error(self, mock_extract):
        """Generic error should raise ToolExecutionError."""
        mock_extract.side_effect = Exception("Unexpected error")

        with pytest.raises(ToolExecutionError):
            get_full_metadata.invoke({"url": "https://youtube.com/watch?v=test"})


class TestSearchYouTubeEnhanced:
    """Tests for enhanced search_youtube with max_results."""

    @patch('src.tools.youtube.youtube_search')
    def test_search_with_max_results(self, mock_search):
        """Test search with max_results parameter."""
        mock_results = [Mock(title=f"Video {i}", video_id=f"id{i}") for i in range(10)]
        mock_search.return_value.results = mock_results

        result = search_youtube.invoke({"query": "test", "max_results": 3})
        assert len(result) == 3
        assert result[0]["title"] == "Video 0"
        assert result[2]["title"] == "Video 2"

    @patch('src.tools.youtube.youtube_search')
    def test_search_without_max_results(self, mock_search):
        """Test search without max_results returns all results."""
        mock_results = [Mock(title=f"Video {i}", video_id=f"id{i}") for i in range(5)]
        mock_search.return_value.results = mock_results

        result = search_youtube.invoke({"query": "test"})
        assert len(result) == 5

    @patch('src.tools.youtube.youtube_search')
    def test_search_with_zero_max_results(self, mock_search):
        """Test search with max_results=0 returns empty list."""
        mock_results = [Mock(title="Video", video_id="id") for _ in range(5)]
        mock_search.return_value.results = mock_results

        result = search_youtube.invoke({"query": "test", "max_results": 0})
        assert result == []
