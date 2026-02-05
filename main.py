from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from youtube_tools import extract_video_id, fetch_transcript, search_youtube, get_full_metadata, get_thumbnails
import os
from pprint import pprint
import json

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Suppress pytube errors
import logging
pytube_logger = logging.getLogger('pytube')
pytube_logger.setLevel(logging.ERROR)


google_api_key = os.environ["GOOGLE_API_KEY"]

if __name__ == "__main__":
    
    print("Initializing the LLM")
    llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")

    print("Initializing the tools")
    tools = []
    tools.append(extract_video_id)
    tools.append(fetch_transcript)
    tools.append(search_youtube)
    tools.append(get_full_metadata)
    tools.append(get_thumbnails)

    tool_mapping = {
        "get_thumbnails": get_thumbnails,
        "extract_video_id": extract_video_id,
        "fetch_transcript": fetch_transcript,
        "search_youtube": search_youtube,
        "get_full_metadata": get_full_metadata
    }

    llm_with_tools = llm.bind_tools(tools)

    print("Querying the LLM ")
    query = "Summarize this video: https://www.youtube.com/watch?v=hfIUstzHs9A and summarize in english"
    messages = [HumanMessage(content=query)]

    # Continue conversation loop until no more tool calls
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        response = llm_with_tools.invoke(messages)
        messages.append(response)  # Preserve the full AIMessage with thought signatures

        print("----------------------------------------------------------")
        print(f"Response {iteration}:")
        pprint(response)
        pprint(response.content)
        
        if not response.tool_calls:
            # No more tool calls, we have the final answer
            print("----------------------------------------------------------")
            print("\nFinal Result:")
            print(response.content)
            break
        
        # Execute tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args")
            tool_result = tool_mapping[tool_name].run(tool_args)
            
            # Create ToolMessage - the response object already contains thought signatures
            # which are preserved when we append the AIMessage to messages
            tool_msg = ToolMessage(
                content=str(tool_result) if not isinstance(tool_result, str) else tool_result,
                tool_call_id=tool_call.get("id")
            )
            messages.append(tool_msg)
        
        iteration += 1
    
    if iteration >= max_iterations:
        print("Warning: Reached maximum iterations")

