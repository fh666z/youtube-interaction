"""Chain construction and orchestration."""

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.language_models import BaseChatModel

from src.config.settings import get_settings
from src.tools.registry import get_all_tools
from src.processing.executor import create_recursive_chain
from src.utils.logging import get_logger

logger = get_logger(__name__)


def create_llm() -> BaseChatModel:
    """
    Create and configure the LLM instance.
    
    Returns:
        Configured LLM instance with tools bound
    """
    settings = get_settings()
    
    logger.info(f"Initializing LLM: {settings.model_name} ({settings.model_provider})")
    
    llm = init_chat_model(
        model=settings.model_name,
        model_provider=settings.model_provider
    )
    
    return llm


def create_chain() -> Runnable:
    """
    Create the universal chain for processing queries with tool calling.
    
    Returns:
        Runnable chain that processes queries and executes tools recursively
    """
    logger.info("Creating universal chain")
    
    # Initialize LLM
    llm = create_llm()
    
    # Get all tools
    tools = get_all_tools()
    logger.info(f"Binding {len(tools)} tools to LLM")
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Create recursive chain for tool execution
    recursive_chain = create_recursive_chain(llm_with_tools)
    
    # Build the universal chain
    universal_chain = (
        RunnableLambda(lambda x: [HumanMessage(content=x["query"])])
        | RunnableLambda(lambda messages: messages + [llm_with_tools.invoke(messages)])
        | recursive_chain
    )
    
    logger.info("Universal chain created successfully")
    return universal_chain


def invoke_chain(chain: Runnable, query: str) -> str:
    """
    Invoke the chain with a query and return the final response text.
    
    Args:
        chain: The chain to invoke
        query: User query string
        
    Returns:
        Final response text from the chain
        
    Raises:
        Exception: If chain execution fails
    """
    logger.info(f"Invoking chain with query: {query[:100]}...")
    
    query_dict = {"query": query}
    result = chain.invoke(query_dict)
    
    # Extract text from the last message
    if result and len(result) > 0:
        last_message = result[-1]
        response_text = getattr(last_message, 'content', str(last_message))
        logger.info("Chain execution completed successfully")
        return response_text
    
    logger.warning("Chain returned empty result")
    return "No response generated"
