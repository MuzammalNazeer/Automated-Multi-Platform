"""
Test suite for the Automated Multi-Platform Posting System.

Run with:
    pytest tests/ -v

All tests use httpx.AsyncClient with ASGITransport so the FastAPI app
is tested in-process without needing a running server.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# ── Fixtures / helpers ────────────────────────────────────────────────────────

VALID_MSG = (
    "Check out our latest business platform and grow your visibility. "
    "https://example.com"
)  # 86 characters – well within the 200-char limit


# ── Health check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check():
    """GET / should return HTTP 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


# ── Happy path ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_valid_message_returns_200():
    """A valid message should return HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": VALID_MSG})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_valid_message_has_results_list():
    """Response must contain a non-empty results list."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": VALID_MSG})
    body = resp.json()
    assert "results" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) > 0


@pytest.mark.asyncio
async def test_response_structure():
    """Every result entry must have all required fields with correct types."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": VALID_MSG})
    for item in resp.json()["results"]:
        assert "platform"      in item, "Missing 'platform' field"
        assert "status"        in item, "Missing 'status' field"
        assert "posted_url"    in item, "Missing 'posted_url' field"
        assert "public_access" in item, "Missing 'public_access' field"
        assert "date"          in item, "Missing 'date' field"
        assert "time"          in item, "Missing 'time' field"
        assert "error"         in item, "Missing 'error' field"
        assert item["status"] in ("success", "failed"), (
            f"status must be 'success' or 'failed', got: {item['status']}"
        )
        assert isinstance(item["public_access"], bool)


@pytest.mark.asyncio
async def test_success_key_is_bool():
    """Top-level 'success' field must be a boolean."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": VALID_MSG})
    assert isinstance(resp.json()["success"], bool)


# ── Validation: message length ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_message_exactly_200_chars_is_valid():
    """A message of exactly 200 characters with one URL must be accepted."""
    # Craft a message that is exactly 200 characters
    url = "https://example.com"
    padding = "A" * (200 - len(url) - 1)   # one space separator
    msg = padding + " " + url
    assert len(msg) == 200
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": msg})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_message_201_chars_rejected():
    """A message of 201 characters must be rejected with 422."""
    url = "https://example.com"
    padding = "A" * (201 - len(url) - 1)
    msg = padding + " " + url
    assert len(msg) == 201
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": msg})
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert "errors" in body


# ── Validation: URL rules ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_message_without_url_rejected():
    """Messages without a URL must be rejected with 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": "No link here at all!"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_message_with_two_urls_rejected():
    """Messages with more than one URL must be rejected with 422."""
    msg = "See https://example.com and also https://another.com"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": msg})
    assert resp.status_code == 422


# ── Validation: request body ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_missing_message_field_rejected():
    """Requests without a message field must return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_empty_message_rejected():
    """An empty string message must be rejected with 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_non_string_message_rejected():
    """A non-string message field must be rejected with 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/posting", json={"message": 12345})
    # FastAPI coerces integers to strings via Pydantic, so the validator still runs.
    # This should fail with 422 because "12345" has no URL.
    assert resp.status_code == 422

