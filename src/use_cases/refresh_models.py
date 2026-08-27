from __future__ import annotations

from domain.errors import OllamaUnavailableError
from domain.models import (
    PREFERRED_MODEL,
    ModelsRefreshedEvent,
    OllamaPort,
    RefreshModelsCommand,
)


class RefreshModels:
    def __init__(self, ollama: OllamaPort) -> None:
        self._ollama = ollama

    def run(self, command: RefreshModelsCommand) -> ModelsRefreshedEvent:
        models = self._ollama.list_models()
        if not models:
            raise OllamaUnavailableError("empty model list")
        selected = select_model(models, command.current_model)
        return ModelsRefreshedEvent(
            request_id=command.request_id,
            models=models,
            selected_model=selected,
        )


def select_model(models: tuple[str, ...], current_model: str) -> str:
    if current_model in models:
        return current_model
    if PREFERRED_MODEL in models:
        return PREFERRED_MODEL
    return models[0]
