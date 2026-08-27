from __future__ import annotations

import httpx
import pytest

from domain.errors import OllamaUnavailableError
from services.ollama_gateway import OLLAMA_BASE_URL, OllamaGateway


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(
        transport=handler,
        base_url=OLLAMA_BASE_URL,
        timeout=60.0,
        follow_redirects=False,
    )


def test_should_return_all_model_names_when_tags_response_has_several() -> None:
    """FT-005, happy: список имён без фильтра по семейству."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "http://127.0.0.1:11434/api/tags"
        return httpx.Response(
            200,
            json={
                "models": [
                    {"name": "llama3.2"},
                    {"name": "qwen2.5:3b"},
                    {"name": "custom-finetune:latest"},
                ]
            },
        )

    gateway = OllamaGateway(client=_client(httpx.MockTransport(handler)))
    try:
        names = gateway.list_models()
    finally:
        gateway.close()
    assert names == ("llama3.2", "qwen2.5:3b", "custom-finetune:latest")


def test_should_raise_unavailable_when_model_list_is_empty() -> None:
    """FT-024 / S-03 контракт шлюза: пустой список — OllamaUnavailableError."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"models": []})

    gateway = OllamaGateway(client=_client(httpx.MockTransport(handler)))
    try:
        with pytest.raises(OllamaUnavailableError):
            gateway.list_models()
    finally:
        gateway.close()


def test_should_raise_unavailable_when_tags_request_fails() -> None:
    """Нет соединения с локальным API — OllamaUnavailableError, без текста bat."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    gateway = OllamaGateway(client=_client(httpx.MockTransport(handler)))
    try:
        with pytest.raises(OllamaUnavailableError) as caught:
            gateway.list_models()
    finally:
        gateway.close()
    assert "start_ollama.bat" not in str(caught.value)


def test_should_close_httpx_client_when_gateway_closes() -> None:
    """close() закрывает Client."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"models": [{"name": "qwen2.5:3b"}]})

    gateway = OllamaGateway(client=_client(httpx.MockTransport(handler)))
    gateway.close()
    assert gateway._client.is_closed
