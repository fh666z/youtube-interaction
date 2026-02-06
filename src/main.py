"""Main entry point for the YouTube interaction system."""

import argparse
import sys
from pprint import pprint

from src.core.chain import create_chain, invoke_chain
from src.utils.logging import setup_logging, get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="YouTube interaction system using LLM with tool calling"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="Show top 3 US trending videos with metadata and thumbnails",
        help="Query to process"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (overrides config)"
    )
    args = parser.parse_args()
    
    # Setup logging
    log_level = args.log_level or get_settings().log_level
    setup_logging(level=log_level)
    
    try:
        logger.info("Starting YouTube interaction system")
        
        # Create chain
        chain = create_chain()
        
        # Invoke chain with query
        result = invoke_chain(chain, args.query)
        
        # Print result
        print("\n" + "="*80)
        print("RESULT:")
        print("="*80)
        pprint(result)
        print("="*80 + "\n")
        
        logger.info("Application completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
