"""Tool execution and processing logic."""

from typing import List, Dict, Any
import json
import logging

from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.language_models import BaseChatModel

from src.tools.registry import get_tool
from src.utils.exceptions import ToolExecutionError
from src.utils.logging import get_logger

logger = get_logger(__name__)


def execute_tool(tool_call: Dict[str, Any]) -> ToolMessage:
    """
    Execute a single tool call and return a ToolMessage.
    
    Args:
        tool_call: Dictionary containing tool call information with keys:
                   - name: Tool name
                   - args: Tool arguments
                   - id: Tool call ID
                   
    Returns:
        ToolMessage with execution result
        
    Raises:
        ToolExecutionError: If tool execution fails
    """
    try:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call["id"]
        
        logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")
        
        # Get tool from registry
        tool = get_tool(tool_name)
        
        # Execute tool
        result = tool.invoke(tool_args)
        
        # Serialize result
        if isinstance(result, (dict, list)):
            content = json.dumps(result, default=str)
        else:
            content = str(result)
        
        logger.debug(f"Tool {tool_name} executed successfully")
        
        return ToolMessage(
            content=content,
            tool_call_id=tool_call_id
        )
    except KeyError as e:
        error_msg = f"Tool call missing required field: {str(e)}"
        logger.error(error_msg)
        return ToolMessage(
            content=json.dumps({"error": error_msg}),
            tool_call_id=tool_call.get("id", "unknown")
        )
    except Exception as e:
        error_msg = f"Error executing tool {tool_call.get('name', 'unknown')}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return ToolMessage(
            content=json.dumps({"error": error_msg}),
            tool_call_id=tool_call.get("id", "unknown")
        )


def process_tool_calls(
    messages: List[Any],
    llm_with_tools: BaseChatModel
) -> List[Any]:
    """
    Process tool calls from the last message and get next LLM response.
    
    Args:
        messages: Current message history
        llm_with_tools: LLM instance with tools bound
        
    Returns:
        Updated message history with tool responses and next AI response
    """
    last_message = messages[-1]
    
    # Get tool calls from the last message
    tool_calls = getattr(last_message, 'tool_calls', [])
    
    if not tool_calls:
        logger.warning("process_tool_calls called but no tool calls found")
        return messages
    
    logger.info(f"Processing {len(tool_calls)} tool call(s)")
    
    # Execute all tool calls in parallel
    tool_messages = [execute_tool(tc) for tc in tool_calls]
    
    # Add tool responses to message history
    updated_messages = messages + tool_messages
    
    # Get next LLM response
    logger.debug("Invoking LLM with tool responses")
    next_ai_response = llm_with_tools.invoke(updated_messages)
    
    return updated_messages + [next_ai_response]


def should_continue(messages: List[Any]) -> bool:
    """
    Check if another iteration is needed (i.e., if there are tool calls).
    
    Args:
        messages: Current message history
        
    Returns:
        True if another iteration is needed, False otherwise
    """
    if not messages:
        return False
    
    last_message = messages[-1]
    tool_calls = getattr(last_message, 'tool_calls', None)
    return bool(tool_calls)


def _recursive_chain(
    messages: List[Any],
    llm_with_tools: BaseChatModel
) -> List[Any]:
    """
    Recursively process tool calls until completion.
    
    Args:
        messages: Current message history
        llm_with_tools: LLM instance with tools bound
        
    Returns:
        Final message history after all tool calls are processed
    """
    if should_continue(messages):
        logger.debug("Continuing recursive chain - more tool calls detected")
        new_messages = process_tool_calls(messages, llm_with_tools)
        return _recursive_chain(new_messages, llm_with_tools)
    
    logger.debug("Recursive chain complete - no more tool calls")
    return messages


def create_recursive_chain(llm_with_tools: BaseChatModel) -> RunnableLambda:
    """
    Create a recursive chain that processes tool calls until completion.
    
    Args:
        llm_with_tools: LLM instance with tools bound
        
    Returns:
        RunnableLambda that processes messages recursively
    """
    return RunnableLambda(lambda messages: _recursive_chain(messages, llm_with_tools))
