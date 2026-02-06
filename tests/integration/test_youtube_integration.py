"""Integration tests for YouTube tools (require network access)."""

import pytest

from src.tools.youtube import (
    extract_video_id,
    search_youtube
)


@pytest.mark.integration
class TestYouTubeIntegration:
    """Integration tests that require network access."""
    
    def test_extract_video_id_real_url(self):
        """Test extracting video ID from a real YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id.invoke({"url": url})
        assert result == "dQw4w9WgXcQ"
        assert len(result) == 11
    
    @pytest.mark.skip(reason="Requires network and may be rate limited")
    def test_search_youtube_real_query(self):
        """Test YouTube search with a real query."""
        result = search_youtube.invoke({"query": "python programming"})
        assert isinstance(result, list)
        if result:  # If not rate limited
            assert "title" in result[0]
            assert "video_id" in result[0]
            assert "url" in result[0]
