from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from youtube_tools import extract_video_id, fetch_transcript, search_youtube, get_full_metadata, get_thumbnails, execute_tool
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
    llm = init_chat_model(model="gemini-3-pro-preview", model_provider="google_genai")

    print("Initializing the tools")
    tools = []
    tools.append(extract_video_id)
    tools.append(fetch_transcript)
    tools.append(search_youtube)
    tools.append(get_full_metadata)
    tools.append(get_thumbnails)
    llm_with_tools = llm.bind_tools(tools)


    summarization_chain = (
        # Start with initial query
        RunnablePassthrough.assign(
            messages=lambda x: [HumanMessage(content=x["query"])]
        )
        # First LLM call (extract video ID)
        | RunnablePassthrough.assign(
            ai_response=lambda x: llm_with_tools.invoke(x["messages"])
        )
        # Process first tool call
        | RunnablePassthrough.assign(
            tool_messages=lambda x: [
                execute_tool(tc) for tc in x["ai_response"].tool_calls
            ]
        )
        # Update message history
        | RunnablePassthrough.assign(
            messages=lambda x: x["messages"] + [x["ai_response"]] + x["tool_messages"]
        )
        # Second LLM call (fetch transcript)
        | RunnablePassthrough.assign(
            ai_response2=lambda x: llm_with_tools.invoke(x["messages"])
        )
        # Process second tool call
        | RunnablePassthrough.assign(
            tool_messages2=lambda x: [
                execute_tool(tc) for tc in x["ai_response2"].tool_calls
            ]
        )
        # Final message update
        | RunnablePassthrough.assign(
            messages=lambda x: x["messages"] + [x["ai_response2"]] + x["tool_messages2"]
        )
        # Generate final summary
        | RunnablePassthrough.assign(
            summary=lambda x: llm_with_tools.invoke(x["messages"]).content
        )
        # Return just the summary text
        | RunnableLambda(lambda x: x["summary"])
    )

    print("Querying the LLM with the summarization chain")
    result = summarization_chain.invoke({
        "query": "Summarize this YouTube video: https://www.youtube.com/watch?v=1bUy-1hGZpI"
    })

    pprint(result)
    #print("Video Summary:\n", result.content)
    
