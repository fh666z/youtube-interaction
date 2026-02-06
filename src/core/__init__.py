"""Core business logic module."""

# Import constants first to avoid circular imports
from src.core.constants import ModelConfig, LoggingConfig, YouTubeConfig

# Lazy imports to avoid circular dependency
# These are imported on-demand to prevent circular imports with tools.registry
def __getattr__(name: str):
    """Lazy import for chain and models to avoid circular imports."""
    if name in ("create_chain", "invoke_chain", "create_llm"):
        from src.core.chain import create_chain, invoke_chain, create_llm
        return {"create_chain": create_chain, "invoke_chain": invoke_chain, "create_llm": create_llm}[name]
    elif name in ("VideoMetadata", "Thumbnail", "VideoSearchResult", "QueryRequest"):
        from src.core.models import VideoMetadata, Thumbnail, VideoSearchResult, QueryRequest
        return {"VideoMetadata": VideoMetadata, "Thumbnail": Thumbnail, 
                "VideoSearchResult": VideoSearchResult, "QueryRequest": QueryRequest}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "create_chain",
    "invoke_chain",
    "create_llm",
    "VideoMetadata",
    "Thumbnail",
    "VideoSearchResult",
    "QueryRequest",
    "ModelConfig",
    "LoggingConfig",
    "YouTubeConfig",
]
