"""Application constants."""

from typing import List


class ModelConfig:
    """LLM model configuration constants."""
    
    DEFAULT_MODEL = "gemini-3-pro-preview"
    DEFAULT_PROVIDER = "google_genai"


class LoggingConfig:
    """Logging configuration constants."""
    
    DEFAULT_LEVEL = "INFO"
    THIRD_PARTY_LOGGERS: List[str] = ["pytube", "yt_dlp"]
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class YouTubeConfig:
    """YouTube-related configuration constants."""
    
    DEFAULT_TRANSCRIPT_LANGUAGE = "en"
    VIDEO_ID_PATTERN = r'(?:v=|be/|embed/)([a-zA-Z0-9_-]{11})'
