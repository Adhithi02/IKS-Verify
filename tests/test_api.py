import pytest
from httpx import ASGITransport, AsyncClient

from iks_verify.api.main import app


@pytest.fixture
async def api_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.anyio
async def test_health(api_client: AsyncClient):
    response = await api_client.get("/api/health")
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_ask(api_client: AsyncClient):
    response = await api_client.post(
        "/api/ask",
        json={"question": "What does the Gita say about action?", "system": "verify"},
    )
    assert response.status_code == 200
    assert "claims" in response.json()


@pytest.mark.anyio
async def test_verse_and_stream(api_client: AsyncClient):
    assert (await api_client.get("/api/verse/Gita/2/47")).status_code == 200
    async with api_client.stream(
        "POST",
        "/api/ask/stream",
        json={"question": "What is yoga?", "system": "verify"},
    ) as response:
        assert response.status_code == 200
        assert "event: pipeline" in (await response.aread()).decode()
