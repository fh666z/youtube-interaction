"""Unit tests for tool registry."""

import pytest
from unittest.mock import Mock

from src.tools.registry import (
    get_all_tools,
    get_tool,
    register_tool,
    TOOL_REGISTRY
)
from langchain.tools import BaseTool


class TestToolRegistry:
    """Tests for tool registry."""
    
    def test_get_all_tools(self):
        """Test getting all registered tools."""
        tools = get_all_tools()
        assert len(tools) > 0
        assert all(isinstance(tool, BaseTool) for tool in tools)
    
    def test_get_tool_exists(self):
        """Test getting an existing tool."""
        tool = get_tool("extract_video_id")
        assert tool is not None
        assert isinstance(tool, BaseTool)
    
    def test_get_tool_not_found(self):
        """Test getting a non-existent tool raises KeyError."""
        with pytest.raises(KeyError):
            get_tool("non_existent_tool")
    
    def test_register_tool(self):
        """Test registering a new tool."""
        mock_tool = Mock(spec=BaseTool)
        mock_tool.name = "test_tool"
        
        original_count = len(TOOL_REGISTRY)
        register_tool("test_tool", mock_tool)
        
        assert len(TOOL_REGISTRY) == original_count + 1
        assert get_tool("test_tool") == mock_tool
        
        # Cleanup
        del TOOL_REGISTRY["test_tool"]
