from __future__ import annotations

from types import TracebackType

import httpx

from domain.errors import (
    OllamaModelError,
    OllamaTimeoutError,
    OllamaUnavailableError,
)

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_TIMEOUT_SECONDS = 60.0


class OllamaGateway:
    def __init__(self, client: httpx.Client | None = None) -> None:
        if client is None:
            self._client = httpx.Client(
                base_url=OLLAMA_BASE_URL,
                timeout=OLLAMA_TIMEOUT_SECONDS,
                follow_redirects=False,
            )
        else:
            self._client = client

    def list_models(self) -> tuple[str, ...]:
        try:
            response = self._client.get("/api/tags")
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise OllamaUnavailableError(str(exc)) from exc
        names = _model_names(payload)
        if not names:
            raise OllamaUnavailableError("empty model list")
        return names

    def translate_fragment(
        self, *, model: str, instruction: str, source: str
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": source},
            ],
            "stream": False,
        }
        try:
            response = self._client.post("/api/chat", json=payload)
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(str(exc)) from exc
        if response.status_code >= 400:
            raise OllamaModelError(_chat_error_message(response))
        try:
            body = response.json()
        except (ValueError, TypeError) as exc:
            raise OllamaModelError(str(exc)) from exc
        content = _assistant_content(body)
        if content is None or len(content.strip()) == 0:
            raise OllamaModelError("empty translation")
        return content

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OllamaGateway:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def _assistant_content(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    message = payload.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if not isinstance(content, str):
        return None
    return content


def _chat_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except (ValueError, TypeError):
        return f"HTTP {response.status_code}"
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, str) and error:
            return error
    return f"HTTP {response.status_code}"


def _model_names(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ()
    raw_models = payload.get("models")
    if not isinstance(raw_models, list):
        return ()
    names: list[str] = []
    for item in raw_models:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name:
            names.append(name)
    return tuple(names)
