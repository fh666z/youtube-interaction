# YouTube Interaction System

A flexible YouTube interaction system that uses Large Language Models (LLMs) with tool calling capabilities to search videos, extract transcripts, fetch metadata, and generate summaries.

## Features

- **LLM-Powered**: Uses Google's Gemini 3 Pro model with LangChain for intelligent query processing
- **Tool Calling**: Autonomous tool selection and execution for YouTube operations
- **Comprehensive Tools**:
  - Search YouTube videos
  - Extract video IDs from URLs
  - Fetch video transcripts
  - Get full video metadata (views, likes, comments, chapters)
  - Retrieve video thumbnails
- **Recursive Processing**: Automatically handles multi-step tool execution until completion
- **Type-Safe**: Built with Pydantic for data validation and type safety
- **Well-Organized**: Clean architecture with separation of concerns

## Architecture

```
src/
├── config/          # Configuration management
│   └── settings.py  # Centralized config with validation
├── core/            # Core business logic
│   ├── chain.py     # Chain construction and orchestration
│   ├── models.py    # Data models/Pydantic schemas
│   └── constants.py # Application constants
├── tools/           # Tool definitions
│   ├── youtube.py   # YouTube-specific tools
│   └── registry.py  # Tool registry/registration
├── processing/      # Tool execution logic
│   └── executor.py  # Tool call processing
├── utils/           # Utilities
│   ├── logging.py   # Logging configuration
│   └── exceptions.py # Custom exceptions
└── main.py          # Entry point
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube-interaction
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-3-pro-preview
MODEL_PROVIDER=google_genai
LOG_LEVEL=INFO
```

Or set the `GOOGLE_API_KEY` environment variable directly:
```bash
export GOOGLE_API_KEY=your_api_key_here  # On Windows: set GOOGLE_API_KEY=your_api_key_here
```

## Usage

### Basic CLI Usage

Run with default query:
```bash
python main.py
```

Run with custom query:
```bash
python main.py --query "Find videos about machine learning"
```

Set log level:
```bash
python main.py --log-level DEBUG
```

### HTTP Service Usage

You can also run the system as a long-running HTTP service with a REST API.

Start the API server with Uvicorn:

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Then send a query via HTTP:

```bash
curl -X POST "http://localhost:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"Show top 3 trending videos with metadata and thumbnails\"}"
```

You can check the health of the service:

```bash
curl http://localhost:8000/health
```

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Programmatic Usage

```python
from src.core.chain import create_chain, invoke_chain

# Create the chain
chain = create_chain()

# Invoke with a query
result = invoke_chain(chain, "Show me top 3 trending videos with metadata")
print(result)
```

## Service Management

The HTTP service is designed to be managed like a typical long-running process.

### Local development

- Start service:

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

- Stop service:

Use `Ctrl+C` in the terminal where Uvicorn is running.

### Example production options

You can choose one of several approaches depending on your environment:

- **Docker / containerized deployment**
  - Build an image that runs `uvicorn src.api.app:app`.
  - Manage lifecycle with `docker compose up/down/restart`.

- **Linux systemd service**
  - Create a systemd unit file that runs:

    ```ini
    ExecStart=/path/to/venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000
    ```

  - Then use:

    ```bash
    systemctl start youtube-interaction
    systemctl stop youtube-interaction
    systemctl restart youtube-interaction
    ```

- **Windows service**
  - Use a service wrapper such as NSSM to run the same Uvicorn command as a Windows service.
  - Start/stop via the Windows Services UI or `sc start/stop`.

## Configuration

Configuration is managed through environment variables or a `.env` file:

- `GOOGLE_API_KEY` (required): Your Google API key for Gemini
- `MODEL_NAME` (optional): LLM model name (default: `gemini-3-pro-preview`)
- `MODEL_PROVIDER` (optional): Model provider (default: `google_genai`)
- `LOG_LEVEL` (optional): Logging level - DEBUG, INFO, WARNING, ERROR (default: `INFO`)

## Testing

Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests (requires network):
```bash
pytest tests/integration/ -m integration
```

Run all tests:
```bash
pytest
```

## Project Structure

- **src/config/**: Configuration management with Pydantic settings
- **src/core/**: Core business logic including chain creation and data models
- **src/tools/**: YouTube tool definitions and registry
- **src/processing/**: Tool execution and recursive processing logic
- **src/utils/**: Utilities for logging and custom exceptions
- **tests/**: Test suite with unit and integration tests

## Best Practices Implemented

1. **Layered Architecture**: Clear separation of concerns
2. **Configuration Management**: Type-safe settings with validation
3. **Logging Infrastructure**: Centralized logging with proper levels
4. **Error Handling**: Custom exceptions with proper error propagation
5. **Type Safety**: Comprehensive type hints and Pydantic models
6. **Tool Registry**: Centralized tool management
7. **Testing**: Unit and integration test structure
8. **Documentation**: Comprehensive docstrings and README

## Dependencies

- `langchain`: LLM framework and tool integration
- `langchain-google-genai`: Google Gemini integration
- `pytube`: YouTube search functionality
- `youtube-transcript-api`: Transcript fetching
- `yt-dlp`: Video metadata and thumbnail extraction
- `pydantic-settings`: Type-safe configuration management
- `python-dotenv`: Environment variable management

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
