"""Unit tests for the FastAPI application."""

from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_health_check() -> None:
    """Health endpoint should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_endpoint_success(monkeypatch) -> None:
    """POST /query should return a result string when chain invocation succeeds."""

    # Patch create_chain/invoke_chain indirectly by patching app.state.chain
    class DummyChain:
        def invoke(self, _input):
            return ["dummy", type("Msg", (), {"content": "ok"})()]

    # Ensure chain is present
    app.state.chain = DummyChain()

    response = client.post("/query", json={"query": "test query"})
    assert response.status_code == 200
    body = response.json()
    assert "result" in body
    assert isinstance(body["result"], str)

