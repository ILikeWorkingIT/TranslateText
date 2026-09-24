import httpx
import pytest

from domain.errors import CloudKeyMissingError, CloudRateLimitError
from services.gemini_gateway import (
    CLOUD_REQUEST_GAP_SECONDS,
    CLOUD_TEMPERATURE,
    GROQ_CHAT_URL,
    prepare_cloud_text,
    translate_cloud,
)


def test_should_lowercase_whole_text_when_names_and_pronoun_stay() -> None:
    prepared = prepare_cloud_text('  HELLO Amanda, I SAID "DUDE"  ')
    assert prepared == 'Hello Amanda, I said "dude"'


def test_should_raise_when_groq_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr("services.gemini_gateway._load_dotenv", lambda: None)
    with pytest.raises(CloudKeyMissingError):
        translate_cloud("Hello")


def test_should_raise_rate_limit_when_groq_returns_429(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == GROQ_CHAT_URL
        return httpx.Response(429, json={"error": {"message": "rpm"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(CloudRateLimitError):
        translate_cloud("Hello", client=client)
    assert CLOUD_TEMPERATURE == 0.2
    assert 1.0 <= CLOUD_REQUEST_GAP_SECONDS <= 2.0
