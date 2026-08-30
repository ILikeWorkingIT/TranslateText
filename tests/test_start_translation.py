"""S-05: старт очереди только после согласия или при непустой инструкции."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

import pytest

from domain.errors import EmptyInstructionError
from domain.models import QueueEvent, StartTranslationCommand
from ui.bridge import TranslationBridge
from use_cases.start_translation import StartTranslation, require_ready_instruction

PROMPT_EN_RU = (
    "Ты профессиональный переводчик. Переведи текст с английского на русский. "
    "Сохрани смысл, тон и разбиение на абзацы. Не добавляй комментарии, преамбулу "
    "и кавычки вокруг перевода. В ответе только перевод."
)
PROMPT_RU_EN = (
    "Ты профессиональный переводчик. Переведи текст с русского на английский. "
    "Сохрани смысл, тон и разбиение на абзацы. Не добавляй комментарии, преамбулу "
    "и кавычки вокруг перевода. В ответе только перевод."
)


class FakeOllama:
    def __init__(self, *, translation_prefix: str = "ok") -> None:
        self.translate_calls: list[tuple[str, str, str]] = []
        self._translation_prefix = translation_prefix

    def list_models(self) -> tuple[str, ...]:
        return ("qwen2.5:3b",)

    def translate_fragment(
        self, *, model: str, instruction: str, source: str
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        index = len(self.translate_calls) - 1
        return f"{self._translation_prefix}{index}"

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
    instruction: str,
    instruction_confirmed: bool,
    direction: str = "EN→RU",
) -> StartTranslationCommand:
    return StartTranslationCommand(
        request_id=1,
        original_text="Hello",
        instruction=instruction,
        instruction_confirmed=instruction_confirmed,
        model="qwen2.5:3b",
        direction=direction,
    )


def test_should_raise_empty_instruction_when_instruction_empty_and_not_confirmed() -> None:
    """FT-029, A0050: пустая инструкция без согласия — очередь не создаётся."""
    port = FakeOllama()
    events: list[object] = []
    with pytest.raises(EmptyInstructionError):
        StartTranslation(port).run(
            _command(instruction="", instruction_confirmed=False),
            stop_event=Event(),
            on_event=events.append,
        )
    assert port.translate_calls == [], "Ollama не вызывается без согласия"
    assert events == [], "событий очереди нет"


def test_should_not_substitute_prompt_when_instruction_empty_even_if_confirmed() -> None:
    """FT-029: прикладной слой не подставляет A0006/A0122 в поле и в запрос."""
    port = FakeOllama()
    with pytest.raises(EmptyInstructionError):
        StartTranslation(port).run(
            _command(instruction="", instruction_confirmed=True),
            stop_event=Event(),
            on_event=lambda _event: None,
        )
    assert port.translate_calls == [], "пустая инструкция не уходит в Ollama"


def test_should_start_with_snapshot_when_instruction_already_nonempty() -> None:
    """FT-011: непустая инструкция — снимок как в команде, без диалога."""
    port = FakeOllama()
    events: list[QueueEvent] = []
    command = _command(
        instruction="свой стиль",
        instruction_confirmed=False,
        direction="EN→RU",
    )
    StartTranslation(port).run(
        command,
        stop_event=Event(),
        on_event=events.append,
    )
    assert port.translate_calls == [("qwen2.5:3b", "свой стиль", "Hello")]
    assert command.direction == "EN→RU"
    assert events[-1].status == "completed"


def test_should_use_en_ru_prompt_in_snapshot_when_start_after_consent() -> None:
    """FT-029, A0006, A0050: после согласия снимок несёт базовый промпт EN→RU."""
    port = FakeOllama()
    command = _command(
        instruction=PROMPT_EN_RU,
        instruction_confirmed=True,
        direction="EN→RU",
    )
    StartTranslation(port).run(
        command,
        stop_event=Event(),
        on_event=lambda _event: None,
    )
    assert port.translate_calls == [("qwen2.5:3b", PROMPT_EN_RU, "Hello")]
    assert command.instruction == PROMPT_EN_RU
    assert command.direction == "EN→RU"


def test_should_use_ru_en_prompt_in_snapshot_when_start_after_consent() -> None:
    """FT-029, A0122: после согласия снимок несёт базовый промпт RU→EN."""
    port = FakeOllama()
    command = _command(
        instruction=PROMPT_RU_EN,
        instruction_confirmed=True,
        direction="RU→EN",
    )
    StartTranslation(port).run(
        command,
        stop_event=Event(),
        on_event=lambda _event: None,
    )
    assert port.translate_calls == [("qwen2.5:3b", PROMPT_RU_EN, "Hello")]
    assert command.direction == "RU→EN"


def test_should_raise_empty_instruction_when_bridge_starts_without_ready_prompt() -> None:
    """FT-029: клей не стартует воркер и не шлёт incomplete при пустой инструкции."""
    port = FakeOllama()
    host = FakeHost()
    events: list[object] = []
    bridge = TranslationBridge(host=host, ollama=port, on_event=events.append)
    with pytest.raises(EmptyInstructionError):
        bridge.start(
            original_text="Hello",
            instruction="",
            model="qwen2.5:3b",
            direction="EN→RU",
            instruction_confirmed=False,
        )
    assert bridge.translation_request_id == 0
    assert port.translate_calls == []
    assert host.ui_calls == 0
    assert events == []


def test_should_reject_empty_instruction_when_require_ready_is_called() -> None:
    """FT-029: общий гейт для UI и use case — пустая строка недопустима."""
    with pytest.raises(EmptyInstructionError):
        require_ready_instruction("")
    require_ready_instruction(PROMPT_EN_RU)


def test_should_translate_fragments_sequentially_when_text_exceeds_700() -> None:
    """FT-015, FT-019, FT-020: очередь — строго по порядку, склейка перевода."""
    port = FakeOllama(translation_prefix="part")
    part = "x" * 400
    original = f"{part}\n\n{part}"
    events: list[QueueEvent] = []
    command = StartTranslationCommand(
        request_id=7,
        original_text=original,
        instruction="свой стиль",
        instruction_confirmed=False,
        model="qwen2.5:3b",
        direction="EN→RU",
    )
    StartTranslation(port).run(
        command,
        stop_event=Event(),
        on_event=events.append,
    )
    assert len(port.translate_calls) == 2, "два абзаца — два запроса Ollama"
    assert port.translate_calls[0][2] == part
    assert port.translate_calls[1][2] == part
    assert events[-1].status == "completed"
    assert events[-1].translation_so_far == "part0part1"
    assert events[-1].processed_source_chars == len(original)


def test_should_emit_progress_after_each_fragment_when_queue_runs() -> None:
    """FT-022, NFT-005: processed_source_chars растёт после каждого фрагмента."""
    port = FakeOllama()
    part = "y" * 400
    original = f"{part}\n\n{part}"
    events: list[QueueEvent] = []
    command = StartTranslationCommand(
        request_id=8,
        original_text=original,
        instruction="style",
        instruction_confirmed=False,
        model="qwen2.5:3b",
        direction="EN→RU",
    )
    StartTranslation(port).run(
        command,
        stop_event=Event(),
        on_event=events.append,
    )
    progress_events = [
        event.processed_source_chars
        for event in events
        if event.status == "inProgress"
    ]
    assert progress_events[0] == 0
    assert progress_events[-1] == len(part)
    assert events[-1].processed_source_chars == len(original)
