"""Custom exception classes for the YouTube interaction system."""


class YouTubeInteractionError(Exception):
    """Base exception for YouTube interaction errors."""
    pass


class YouTubeToolError(YouTubeInteractionError):
    """Base exception for YouTube tool errors."""
    pass


class VideoNotFoundError(YouTubeToolError):
    """Raised when a video is not found."""
    pass


class TranscriptNotFoundError(YouTubeToolError):
    """Raised when a transcript is not available."""
    pass


class InvalidVideoURLError(YouTubeToolError):
    """Raised when a video URL is invalid."""
    pass


class ConfigurationError(YouTubeInteractionError):
    """Raised when there's a configuration error."""
    pass


class ToolExecutionError(YouTubeInteractionError):
    """Raised when a tool execution fails."""
    pass
