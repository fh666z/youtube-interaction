"""Unit tests for tool processing."""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.processing.executor import (
    execute_tool,
    process_tool_calls,
    should_continue,
    _recursive_chain
)
from langchain_core.messages import AIMessage


class TestExecuteTool:
    """Tests for execute_tool function."""
    
    @patch('src.processing.executor.get_tool')
    def test_execute_tool_success(self, mock_get_tool):
        """Test successful tool execution."""
        mock_tool = Mock()
        mock_tool.invoke.return_value = {"result": "success"}
        mock_get_tool.return_value = mock_tool
        
        tool_call = {
            "name": "test_tool",
            "args": {"arg1": "value1"},
            "id": "call_123"
        }
        
        result = execute_tool(tool_call)
        assert result.tool_call_id == "call_123"
        assert "success" in result.content
    
    def test_execute_tool_missing_fields(self):
        """Test tool execution with missing fields."""
        tool_call = {"name": "test_tool"}  # Missing args and id
        
        result = execute_tool(tool_call)
        assert "error" in result.content.lower()


class TestShouldContinue:
    """Tests for should_continue function."""
    
    def test_should_continue_with_tool_calls(self):
        """Test should_continue returns True when tool calls exist."""
        message = Mock()
        message.tool_calls = [{"name": "test_tool"}]
        messages = [message]
        
        assert should_continue(messages) is True
    
    def test_should_continue_without_tool_calls(self):
        """Test should_continue returns False when no tool calls."""
        message = Mock()
        message.tool_calls = None
        messages = [message]
        
        assert should_continue(messages) is False
    
    def test_should_continue_empty_messages(self):
        """Test should_continue with empty messages."""
        assert should_continue([]) is False
