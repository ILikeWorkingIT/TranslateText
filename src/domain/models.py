from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

ExportFormat = Literal["txt", "docx"]
SourceFormat = Literal["txt", "md", "docx", "pdf"]

PREFERRED_MODEL = "qwen2.5:3b"


MAX_SOURCE_CHARS = 100_000
MAX_FRAGMENT_CHARS = 700
TARGET_FRAGMENT_CHARS_MIN = 500
TARGET_FRAGMENT_CHARS_MAX = 700


@dataclass(frozen=True)
class Fragment:
    order: int
    source: str


class OllamaPort(Protocol):
    def list_models(self) -> tuple[str, ...]: ...

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
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


@dataclass(frozen=True)
class StartTranslationCommand:
    request_id: int
    original_text: str
    instruction: str
    instruction_confirmed: bool
    model: str
    direction: str
    translation_text: str = ""
    translation_saved: bool = True
    unsaved_confirmed: bool = False


@dataclass(frozen=True)
class ExportTranslationCommand:
    request_id: int
    translation_text: str
    path: str
    export_format: ExportFormat


@dataclass(frozen=True)
class LoadSourceCommand:
    request_id: int
    path: str
    source_format: SourceFormat


@dataclass(frozen=True)
class QueueEvent:
    request_id: int
    status: Literal["inProgress", "completed", "incomplete"]
    next_index: int
    processed_source_chars: int
    total_source_chars: int
    translation_so_far: str
    incomplete_cause: Literal["none", "cancelled", "ollama"] = "none"
