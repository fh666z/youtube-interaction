"""Tool registry for managing and discovering available tools."""

from typing import Dict, List, Any
from langchain.tools import BaseTool

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
    list_transcript_languages
)


# Registry mapping tool names to tool instances
TOOL_REGISTRY: Dict[str, BaseTool] = {
    "extract_video_id": extract_video_id,
    "fetch_transcript": fetch_transcript,
    "search_youtube": search_youtube,
    "get_full_metadata": get_full_metadata,
    "get_thumbnails": get_thumbnails,
    "get_channel_info": get_channel_info,
    "get_playlist_info": get_playlist_info,
    "get_playlist_videos": get_playlist_videos,
    "fetch_transcript_with_timestamps": fetch_transcript_with_timestamps,
    "list_transcript_languages": list_transcript_languages,
}


def get_all_tools() -> List[BaseTool]:
    """
    Get all registered tools.
    
    Returns:
        List of all registered tool instances.
    """
    return list(TOOL_REGISTRY.values())


def get_tool(name: str) -> BaseTool:
    """
    Get a specific tool by name.
    
    Args:
        name: Tool name
        
    Returns:
        Tool instance
        
    Raises:
        KeyError: If tool is not found in registry
    """
    if name not in TOOL_REGISTRY:
        available = ", ".join(TOOL_REGISTRY.keys())
        raise KeyError(f"Tool '{name}' not found. Available tools: {available}")
    return TOOL_REGISTRY[name]


def register_tool(name: str, tool: BaseTool) -> None:
    """
    Register a new tool in the registry.
    
    Args:
        name: Tool name
        tool: Tool instance to register
    """
    TOOL_REGISTRY[name] = tool
