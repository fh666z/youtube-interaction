from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from youtube_tools import extract_video_id, fetch_transcript, search_youtube, get_full_metadata, get_thumbnails
from tool_call_processing import recursive_chain
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


    universal_chain = (
        RunnableLambda(lambda x: [HumanMessage(content=x["query"])])
        | RunnableLambda(lambda messages: messages + [llm_with_tools.invoke(messages)])
        | recursive_chain(llm_with_tools)
    )

    prompt = f"""
        Please analyze this YouTube video and provide a comprehensive summary.

        VIDEO TITLE: {video_metadata['title']}
        CHANNEL: {video_metadata['channel']}
        VIEWS: {video_metadata['views']}
        DURATION: {video_metadata['duration']} seconds
        LIKES: {video_metadata['likes']}

        TRANSCRIPT EXCERPT:
        {transcript[:3000]}... (transcript truncated for brevity)

        Based on this information, please provide:
        1. A concise summary of the video content (3-5 bullet points)
        2. The main topics or themes discussed
        3. The intended audience for this content
        4. A brief analysis of why this video might be performing well (or not)
        """
    query = {"query": "Show top 3 US trending videos with metadata and thumbnails"}
    try:
        result = universal_chain.invoke(query)
        pprint(result[-1].text)
    except Exception as e:
        print("Non-critical network error:", e)

