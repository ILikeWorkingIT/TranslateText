from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

PREFERRED_MODEL = "qwen2.5:3b"


class OllamaPort(Protocol):
    def list_models(self) -> tuple[str, ...]: ...

    def translate_fragment(
        self, *, model: str, instruction: str, source: str
    ) -> str: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class RefreshModelsCommand:
    request_id: int
    current_model: str


@dataclass(frozen=True)
class ModelsRefreshedEvent:
    request_id: int
    models: tuple[str, ...]
    selected_model: str
