"""S-05: старт очереди только после согласия или при непустой инструкции."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

import pytest

from domain.errors import (
    AppLayerError,
    EmptyInstructionError,
    OllamaModelError,
    OllamaTimeoutError,
)
from domain.models import Fragment, QueueEvent, StartTranslationCommand
from services.split_text import SplitText
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
        self, *, model: str, instruction: str, source: str, direction: str = ""
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
    assert port.translate_calls[0][2] == f"{part}\n\n"
    assert port.translate_calls[1][2] == part
    assert events[-1].status == "completed"
    assert events[-1].translation_so_far == "part0\n\npart1"
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
    assert progress_events[-1] == len(part) + 2
    assert events[-1].processed_source_chars == len(original)


class _FixedSplit(SplitText):
    def split(self, _text: str) -> tuple[Fragment, ...]:
        return (
            Fragment(order=0, source="Hello.\n\n"),
            Fragment(order=1, source="Task: Go."),
        )


class _OmitBreaksOllama(FakeOllama):
    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        if source.startswith("Hello"):
            return "Hi."
        return "Task: Go."


def test_should_keep_blank_line_before_next_fragment_when_model_drops_it() -> None:
    """A0142, FT-020: исходник кончается на \\n\\n — в склейке пустая строка, не as.Task:."""
    port = _OmitBreaksOllama()
    events: list[QueueEvent] = []
    command = StartTranslationCommand(
        request_id=9,
        original_text="Hello.\n\nTask: Go.",
        instruction="style",
        instruction_confirmed=False,
        model="qwen2.5:3b",
        direction="EN→RU",
    )
    StartTranslation(port, split_text=_FixedSplit()).run(
        command,
        stop_event=Event(),
        on_event=events.append,
    )
    glued = events[-1].translation_so_far
    assert glued == "Hi.\n\nTask: Go."
    assert "Hi.Task:" not in glued


class _CancelDuringTranslate(FakeOllama):
    def __init__(self, cancel_event: Event, *, fail: bool = False) -> None:
        super().__init__()
        self._cancel_event = cancel_event
        self._fail = fail

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        self._cancel_event.set()
        if self._fail:
            raise OllamaModelError("fragment failed after cancel")
        return f"{self._translation_prefix}{len(self.translate_calls) - 1}"


def _queue_command(original: str, *, request_id: int = 10) -> StartTranslationCommand:
    return StartTranslationCommand(
        request_id=request_id,
        original_text=original,
        instruction="style",
        instruction_confirmed=False,
        model="qwen2.5:3b",
        direction="EN→RU",
    )


def test_should_not_start_next_fragment_when_user_cancels_queue() -> None:
    """FT-054, A0149: после отмены следующий фрагмент в Ollama не уходит."""
    cancel = Event()
    port = _CancelDuringTranslate(cancel)
    part = "x" * 400
    original = f"{part}\n\n{part}"
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    assert len(port.translate_calls) == 1
    assert events[-1].status == "incomplete"
    assert events[-1].incomplete_cause == "cancelled"
    assert events[-1].translation_so_far.startswith("ok0")


def test_should_append_in_flight_success_when_user_cancels() -> None:
    """A0152: успешный ответ текущего фрагмента после клика отмены — в склейке."""
    cancel = Event()
    port = _CancelDuringTranslate(cancel)
    part = "x" * 400
    original = f"{part}\n\n{part}"
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original, request_id=11),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    glued = events[-1].translation_so_far
    assert "ok0" in glued
    assert events[-1].processed_source_chars >= len(part)


def test_should_keep_incomplete_when_single_fragment_succeeds_after_cancel() -> None:
    """UC-010 §5.6: один фрагмент после отмены успешен — всё равно incomplete."""
    cancel = Event()
    port = _CancelDuringTranslate(cancel)
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command("Hello", request_id=12),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    assert events[-1].status == "incomplete"
    assert events[-1].incomplete_cause == "cancelled"
    assert events[-1].translation_so_far == "ok0"


def test_should_emit_cancelled_not_ollama_when_in_flight_fails_after_cancel() -> None:
    """A0153: после принятой отмены сбой текущего запроса — причина cancelled."""
    cancel = Event()
    port = _CancelDuringTranslate(cancel, fail=True)
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command("Hello", request_id=13),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    assert events[-1].status == "incomplete"
    assert events[-1].incomplete_cause == "cancelled"
    assert events[-1].translation_so_far == ""


def test_should_not_fill_field_with_fragment_when_cancel_before_any_success() -> None:
    """A0148: ни один фрагмент не успел — поле без обрывка."""
    cancel = Event()
    cancel.set()
    port = FakeOllama()
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command("Hello", request_id=14),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    assert port.translate_calls == []
    assert events[-1].status == "incomplete"
    assert events[-1].incomplete_cause == "cancelled"
    assert events[-1].translation_so_far == ""


def test_should_keep_previous_glue_when_cancel_then_later_fragment_fails() -> None:
    """NFT-007, A0155: склейка после отмены не короче, чем после последнего успеха."""
    cancel = Event()

    class _SucceedThenFail(FakeOllama):
        def translate_fragment(
            self, *, model: str, instruction: str, source: str, direction: str = ""
        ) -> str:
            self.translate_calls.append((model, instruction, source))
            if len(self.translate_calls) == 1:
                return "first"
            self._cancel_event.set()
            raise OllamaModelError("second failed")

        def __init__(self) -> None:
            super().__init__()
            self._cancel_event = cancel

    port = _SucceedThenFail()
    part = "x" * 400
    original = f"{part}\n\n{part}"
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original, request_id=15),
        stop_event=Event(),
        on_event=events.append,
        cancel_event=cancel,
    )
    after_first = [event for event in events if event.status == "inProgress" and event.next_index == 1]
    assert after_first
    last = events[-1]
    assert last.incomplete_cause == "cancelled"
    assert len(last.translation_so_far) >= len(after_first[-1].translation_so_far)


def test_should_not_emit_when_window_stop_is_set_during_queue() -> None:
    """Закрытие окна — не FT-054: колбэка incomplete нет."""
    stop = Event()

    class _StopOnCall(FakeOllama):
        def translate_fragment(
            self, *, model: str, instruction: str, source: str, direction: str = ""
        ) -> str:
            self.translate_calls.append((model, instruction, source))
            stop.set()
            return "late"

    port = _StopOnCall()
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command("Hello", request_id=16),
        stop_event=stop,
        on_event=events.append,
    )
    assert all(event.status != "incomplete" for event in events)


def test_should_request_cancel_when_bridge_cancel_is_called() -> None:
    """Клей: cancel() не close() клиента и не увеличивает translation_request_id."""
    port = FakeOllama()
    host = FakeHost()
    events: list[QueueEvent] = []
    bridge = TranslationBridge(host=host, ollama=port, on_event=events.append)
    bridge.cancel()
    assert port.translate_calls == []
    assert bridge.translation_request_id == 0


class _FailFromCall(FakeOllama):
    def __init__(self, *, fail_from: int, error: AppLayerError) -> None:
        super().__init__()
        self._fail_from = fail_from
        self._error = error

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        if len(self.translate_calls) >= self._fail_from:
            raise self._error
        return f"{self._translation_prefix}{len(self.translate_calls) - 1}"


def test_should_stop_queue_when_fragment_times_out() -> None:
    """FT-028, A0031: таймаут фрагмента — incomplete, следующий не стартует."""
    part = "x" * 400
    original = f"{part}\n\n{part}"
    port = _FailFromCall(fail_from=1, error=OllamaTimeoutError("timed out"))
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original, request_id=20),
        stop_event=Event(),
        on_event=events.append,
    )
    assert len(port.translate_calls) == 1
    last = events[-1]
    assert last.status == "incomplete"
    assert last.incomplete_cause == "ollama"
    assert last.translation_so_far == ""


def test_should_keep_glue_when_later_fragment_fails() -> None:
    """FT-028, A0013: сбой середины — склейка успешных, очередь стоп."""
    part = "x" * 400
    original = f"{part}\n\n{part}"
    port = _FailFromCall(fail_from=2, error=OllamaModelError("model refused"))
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original, request_id=21),
        stop_event=Event(),
        on_event=events.append,
    )
    assert len(port.translate_calls) == 2
    last = events[-1]
    assert last.status == "incomplete"
    assert last.incomplete_cause == "ollama"
    assert last.translation_so_far.startswith("ok0")
    assert "ok1" not in last.translation_so_far


def test_should_keep_glue_length_when_queue_fails() -> None:
    """NFT-007: после сбоя длина склейки не меньше, чем после последнего успеха."""
    part = "x" * 400
    original = f"{part}\n\n{part}"
    port = _FailFromCall(fail_from=2, error=OllamaTimeoutError("timed out"))
    events: list[QueueEvent] = []
    StartTranslation(port).run(
        _queue_command(original, request_id=22),
        stop_event=Event(),
        on_event=events.append,
    )
    after_first = [
        event
        for event in events
        if event.status == "inProgress" and event.next_index == 1
    ]
    assert after_first
    last = events[-1]
    assert last.status == "incomplete"
    assert len(last.translation_so_far) >= len(after_first[-1].translation_so_far)

