from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Literal

from domain.errors import AppLayerError, EmptyInstructionError, QueueBusyError
from domain.models import Fragment, OllamaPort, QueueEvent, StartTranslationCommand
from services.split_text import SplitText
from use_cases.unsaved_translation import require_unsaved_confirmed

IncompleteCause = Literal["none", "cancelled", "ollama"]


def require_ready_instruction(instruction: str) -> None:
    """FT-029: очередь не стартует с пустой инструкцией. Промпт не подставляем."""
    if len(instruction) == 0:
        raise EmptyInstructionError("empty instruction")


def restore_trailing_line_breaks(source: str, translated: str) -> str:
    """Хвостовые переводы строк исходного фрагмента — в склейке (A0142, FT-020)."""
    index = len(source)
    while index > 0 and source[index - 1] in "\r\n":
        index -= 1
    suffix = source[index:].replace("\r\n", "\n").replace("\r", "\n")
    if suffix == "":
        return translated
    return translated.rstrip("\r\n") + suffix


def _is_cancelled(cancel_event: Event | None) -> bool:
    return cancel_event is not None and cancel_event.is_set()


class StartTranslation:
    def __init__(self, ollama: OllamaPort, *, split_text: SplitText | None = None) -> None:
        self._ollama = ollama
        self._split_text = split_text or SplitText()
        self._busy = False

    def run(
        self,
        command: StartTranslationCommand,
        *,
        stop_event: Event,
        on_event: Callable[[QueueEvent], None],
        cancel_event: Event | None = None,
    ) -> None:
        if self._busy:
            raise QueueBusyError("queue inProgress")
        require_unsaved_confirmed(
            command.translation_text,
            command.translation_saved,
            confirmed=command.unsaved_confirmed,
        )
        require_ready_instruction(command.instruction)
        fragments = self._split_text.split(command.original_text)
        if not fragments:
            return
        self._busy = True
        try:
            self._run_fragment_queue(
                command,
                fragments,
                stop_event=stop_event,
                on_event=on_event,
                cancel_event=cancel_event,
            )
        finally:
            self._busy = False

    def _run_fragment_queue(
        self,
        command: StartTranslationCommand,
        fragments: tuple[Fragment, ...],
        *,
        stop_event: Event,
        on_event: Callable[[QueueEvent], None],
        cancel_event: Event | None,
    ) -> None:
        total = len(command.original_text)
        processed = 0
        translated_parts: list[str] = []

        on_event(
            self._event(
                command,
                status="inProgress",
                next_index=0,
                processed=0,
                translation="",
                total=total,
            )
        )

        for index, fragment in enumerate(fragments):
            if stop_event.is_set():
                return
            if _is_cancelled(cancel_event):
                on_event(
                    self._event(
                        command,
                        status="incomplete",
                        next_index=index,
                        processed=processed,
                        translation="".join(translated_parts),
                        total=total,
                        incomplete_cause="cancelled",
                    )
                )
                return
            try:
                translated = self._ollama.translate_fragment(
                    model=command.model,
                    instruction=command.instruction,
                    source=fragment.source,
                    direction=command.direction,
                )
            except AppLayerError:
                if stop_event.is_set():
                    return
                cause: IncompleteCause = (
                    "cancelled" if _is_cancelled(cancel_event) else "ollama"
                )
                on_event(
                    self._event(
                        command,
                        status="incomplete",
                        next_index=index,
                        processed=processed,
                        translation="".join(translated_parts),
                        total=total,
                        incomplete_cause=cause,
                    )
                )
                return

            translated = restore_trailing_line_breaks(fragment.source, translated)
            translated_parts.append(translated)
            processed += len(fragment.source)
            if stop_event.is_set():
                return
            if _is_cancelled(cancel_event):
                on_event(
                    self._event(
                        command,
                        status="incomplete",
                        next_index=index,
                        processed=processed,
                        translation="".join(translated_parts),
                        total=total,
                        incomplete_cause="cancelled",
                    )
                )
                return
            if index + 1 < len(fragments):
                on_event(
                    self._event(
                        command,
                        status="inProgress",
                        next_index=index + 1,
                        processed=processed,
                        translation="".join(translated_parts),
                        total=total,
                    )
                )

        on_event(
            self._event(
                command,
                status="completed",
                next_index=len(fragments),
                processed=total,
                translation="".join(translated_parts),
                total=total,
            )
        )

    def _event(
        self,
        command: StartTranslationCommand,
        *,
        status: Literal["inProgress", "completed", "incomplete"],
        next_index: int,
        processed: int,
        translation: str,
        total: int,
        incomplete_cause: IncompleteCause = "none",
    ) -> QueueEvent:
        return QueueEvent(
            request_id=command.request_id,
            status=status,
            next_index=next_index,
            processed_source_chars=processed,
            total_source_chars=total,
            translation_so_far=translation,
            incomplete_cause=incomplete_cause,
        )
