from __future__ import annotations

from domain.errors import OllamaUnavailableError
from domain.models import (
    CLOUD_MODELS,
    DEFAULT_CLOUD_MODEL,
    PREFERRED_MODEL,
    ModelsRefreshedEvent,
    OllamaPort,
    RefreshModelsCommand,
)


class RefreshModels:
    def __init__(self, ollama: OllamaPort) -> None:
        self._ollama = ollama

    def run(self, command: RefreshModelsCommand) -> ModelsRefreshedEvent:
        local, ollama_available = self._local_models()
        models = local + CLOUD_MODELS
        if not models:
            raise OllamaUnavailableError("empty model list")
        selected = select_model(
            models,
            command.current_model,
            ollama_available=ollama_available,
        )
        return ModelsRefreshedEvent(
            request_id=command.request_id,
            models=models,
            selected_model=selected,
            ollama_available=ollama_available,
        )

    def _local_models(self) -> tuple[tuple[str, ...], bool]:
        try:
            models = self._ollama.list_models()
        except OllamaUnavailableError:
            return (), False
        if not models:
            return (), False
        return models, True


def select_model(
    models: tuple[str, ...],
    current_model: str,
    *,
    ollama_available: bool = True,
) -> str:
    if current_model in models:
        return current_model
    if ollama_available and PREFERRED_MODEL in models:
        return PREFERRED_MODEL
    if not ollama_available and DEFAULT_CLOUD_MODEL in models:
        return DEFAULT_CLOUD_MODEL
    if PREFERRED_MODEL in models:
        return PREFERRED_MODEL
    return models[0]
