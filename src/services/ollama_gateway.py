from __future__ import annotations

from types import TracebackType

import httpx

from domain.errors import OllamaUnavailableError

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
        raise NotImplementedError

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
