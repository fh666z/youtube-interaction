"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock

from src.config.settings import Settings


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    settings = Settings(
        google_api_key="test_api_key",
        model_name="test-model",
        model_provider="test_provider",
        log_level="DEBUG"
    )
    return settings


@pytest.fixture
def sample_video_id():
    """Sample YouTube video ID for testing."""
    return "dQw4w9WgXcQ"


@pytest.fixture
def sample_video_url():
    """Sample YouTube video URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
