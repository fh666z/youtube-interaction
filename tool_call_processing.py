from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
import json
from youtube_tools import tool_mapping
__all__ = ["execute_tool", "process_tool_calls", "recursive_chain"]

def execute_tool(tool_call):
    """Execute single tool call and return ToolMessage"""
    try:
        result = tool_mapping[tool_call["name"]].invoke(tool_call["args"])
        content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
    except Exception as e:
        content = f"Error: {str(e)}"
    
    return ToolMessage(
        content=content,
        tool_call_id=tool_call["id"]
    )

def process_tool_calls(messages, llm_with_tools):
    """Recursive tool call processor"""
    last_message = messages[-1]
    
    # Execute all tool calls in parallel
    tool_messages = [
        execute_tool(tc) 
        for tc in getattr(last_message, 'tool_calls', [])
    ]
    
    # Add tool responses to message history
    updated_messages = messages + tool_messages
    
    # Get next LLM response
    next_ai_response = llm_with_tools.invoke(updated_messages)
    
    return updated_messages + [next_ai_response]

def should_continue(messages):
    """Check if you need another iteration"""
    last_message = messages[-1]
    return bool(getattr(last_message, 'tool_calls', None))

def _recursive_chain(messages, llm_with_tools):
    """Recursively process tool calls until completion"""
    if should_continue(messages):
        new_messages = process_tool_calls(messages, llm_with_tools)
        return _recursive_chain(new_messages, llm_with_tools)
    return messages

def recursive_chain(llm_with_tools):
    return RunnableLambda(lambda messages: _recursive_chain(messages, llm_with_tools))