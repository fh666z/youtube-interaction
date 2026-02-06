"""FastAPI application exposing the YouTube interaction system as a REST API."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.core.chain import create_chain, invoke_chain
from src.core.models import QueryRequest
from src.utils.logging import setup_logging, get_logger
from src.config.settings import get_settings


logger = get_logger(__name__)


class QueryResponse(BaseModel):
    """Response model for chain queries."""

    result: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    setup_logging(level=settings.log_level)

    app = FastAPI(
        title="YouTube Interaction API",
        description=(
            "HTTP API for the YouTube interaction system powered by LLMs and tools. "
            "Use this service to submit queries and receive processed responses."
        ),
        version="1.0.0",
    )

    @app.on_event("startup")
    def _startup() -> None:
        """Initialize shared resources on startup."""
        logger.info("Starting up YouTube Interaction API")
        # Create and cache the chain on the app state so it can be reused per process
        app.state.chain = create_chain()
        logger.info("Chain initialized and cached on app state")

    @app.post("/query", response_model=QueryResponse, summary="Process a query")
    def process_query(request: QueryRequest) -> QueryResponse:
        """
        Process a YouTube-related query using the universal chain.

        The request body should contain a `query` string. The response
        includes the final text result produced by the chain.
        """
        try:
            chain = getattr(app.state, "chain", None)
            if chain is None:
                logger.warning("Chain not initialized on app state; creating a new one")
                chain = create_chain()
                app.state.chain = chain

            logger.info("Processing query via HTTP API")
            result_text = invoke_chain(chain, request.query)
            return QueryResponse(result=result_text)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Error while processing query via API", exc_info=True)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/health", summary="Health check")
    def health_check() -> dict:
        """Simple health check endpoint."""
        return {"status": "ok"}

    return app


app = create_app()

