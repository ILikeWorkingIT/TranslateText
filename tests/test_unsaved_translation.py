"""S-09: гейт несохранённого перевода (FT-032, FT-033) без GUI."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

import pytest

from domain.errors import UnsavedTranslationError
from domain.models import QueueEvent, StartTranslationCommand
from ui.bridge import TranslationBridge
from use_cases.start_translation import StartTranslation
from use_cases.unsaved_translation import (
    is_unsaved_translation,
    require_unsaved_confirmed,
    saved_after_export_success,
    saved_after_translation_text_change,
    translation_after_source_loaded,
)


class FakeOllama:
    def __init__(self) -> None:
        self.translate_calls: list[tuple[str, str, str]] = []

    def list_models(self) -> tuple[str, ...]:
        return ("qwen2.5:3b",)

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        return "ok"

    def close(self) -> None:
        return


class FakeHost:
    def __init__(self) -> None:
        self.ui_calls = 0

    def call_on_ui(self, func: Callable[[], None]) -> None:
        self.ui_calls += 1
        func()

    def winfo_exists(self) -> bool:
        return True


def _command(
    *,
    translation_text: str = "",
    translation_saved: bool = True,
    unsaved_confirmed: bool = False,
) -> StartTranslationCommand:
    return StartTranslationCommand(
        request_id=1,
        original_text="Hello",
        instruction="style",
        instruction_confirmed=True,
        model="qwen2.5:3b",
        direction="EN→RU",
        translation_text=translation_text,
        translation_saved=translation_saved,
        unsaved_confirmed=unsaved_confirmed,
    )


def test_should_not_treat_empty_field_as_unsaved_when_saved_flag_is_false() -> None:
    """FT-032, AC4: пустое поле — предупреждение не требуется."""
    assert is_unsaved_translation("", False) is False
    assert is_unsaved_translation("", True) is False
    require_unsaved_confirmed("", False, confirmed=False)


def test_should_not_treat_nonempty_as_unsaved_when_export_succeeded() -> None:
    """FT-033, FT-004: после успешного сохранения до правки — не несохранённый."""
    assert is_unsaved_translation("Готово", True) is False
    require_unsaved_confirmed("Готово", True, confirmed=False)


def test_should_treat_nonempty_as_unsaved_when_not_exported() -> None:
    """FT-033, A0097: непустое поле без «Сохранить перевод» — несохранённый."""
    assert is_unsaved_translation("Кусок", False) is True
    with pytest.raises(UnsavedTranslationError):
        require_unsaved_confirmed("Кусок", False, confirmed=False)


def test_should_raise_unsaved_when_queue_starts_without_confirmation() -> None:
    """FT-032: очередь не стартует, Ollama не вызывается."""
    port = FakeOllama()
    events: list[object] = []
    with pytest.raises(UnsavedTranslationError):
        StartTranslation(port).run(
            _command(translation_text="Старый", translation_saved=False),
            stop_event=Event(),
            on_event=events.append,
        )
    assert port.translate_calls == []
    assert events == []


def test_should_start_queue_when_unsaved_is_confirmed() -> None:
    """FT-032, A0098: после подтверждения перевод идёт."""
    port = FakeOllama()
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _command(
            translation_text="Старый",
            translation_saved=False,
            unsaved_confirmed=True,
        ),
        stop_event=Event(),
        on_event=events.append,
    )
    assert port.translate_calls == [("qwen2.5:3b", "style", "Hello")]
    assert events[-1].status == "completed"
    assert events[-1].translation_so_far == "ok"


def test_should_start_queue_when_incomplete_translation_is_confirmed() -> None:
    """A0097: неполный текст после сбоя — несохранённый; с подтверждением очередь идёт."""
    port = FakeOllama()
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _command(
            translation_text="first",
            translation_saved=False,
            unsaved_confirmed=True,
        ),
        stop_event=Event(),
        on_event=events.append,
    )
    assert port.translate_calls != []


def test_should_raise_unsaved_when_bridge_starts_without_confirmation() -> None:
    """FT-032: клей не стартует воркер без подтверждения UC-006."""
    port = FakeOllama()
    host = FakeHost()
    events: list[object] = []
    bridge = TranslationBridge(host=host, ollama=port, on_event=events.append)
    with pytest.raises(UnsavedTranslationError):
        bridge.start(
            original_text="Hello",
            instruction="style",
            model="qwen2.5:3b",
            direction="EN→RU",
            translation_text="Старый",
            translation_saved=False,
            unsaved_confirmed=False,
        )
    assert bridge.translation_request_id == 0
    assert port.translate_calls == []
    assert host.ui_calls == 0


def test_should_mark_saved_when_translation_field_becomes_empty() -> None:
    """FT-033: пустой перевод считается сохранённым."""
    assert saved_after_translation_text_change("") is True
    assert saved_after_translation_text_change("текст") is False


def test_should_mark_saved_when_export_succeeds() -> None:
    """FT-004 (сохранённость): успешная запись снимает несохранённость."""
    assert saved_after_export_success() is True


def test_should_clear_translation_when_source_loaded_successfully() -> None:
    """A0099: после успешной загрузки исходника поле перевода пустое и сохранённое."""
    text, saved = translation_after_source_loaded()
    assert text == ""
    assert saved is True
    assert is_unsaved_translation(text, saved) is False
