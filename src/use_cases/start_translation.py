from __future__ import annotations

from collections.abc import Callable
from threading import Event

from domain.errors import AppLayerError, EmptyInstructionError, QueueBusyError
from domain.models import OllamaPort, QueueEvent, StartTranslationCommand


class StartTranslation:
    def __init__(self, ollama: OllamaPort) -> None:
        self._ollama = ollama
        self._busy = False

    def run(
        self,
        command: StartTranslationCommand,
        *,
        stop_event: Event,
        on_event: Callable[[QueueEvent], None],
    ) -> None:
        if self._busy:
            raise QueueBusyError("queue inProgress")
        if len(command.instruction) == 0:
            raise EmptyInstructionError("empty instruction")
        self._busy = True
        try:
            self._run_one_fragment(command, stop_event=stop_event, on_event=on_event)
        finally:
            self._busy = False

    def _run_one_fragment(
        self,
        command: StartTranslationCommand,
        *,
        stop_event: Event,
        on_event: Callable[[QueueEvent], None],
    ) -> None:
        source = command.original_text
        total = len(source)
        on_event(
            QueueEvent(
                request_id=command.request_id,
                status="inProgress",
                next_index=0,
                processed_source_chars=0,
                total_source_chars=total,
                translation_so_far="",
            )
        )
        if stop_event.is_set():
            return
        try:
            translated = self._ollama.translate_fragment(
                model=command.model,
                instruction=command.instruction,
                source=source,
            )
        except AppLayerError:
            if stop_event.is_set():
                return
            on_event(
                QueueEvent(
                    request_id=command.request_id,
                    status="incomplete",
                    next_index=0,
                    processed_source_chars=0,
                    total_source_chars=total,
                    translation_so_far="",
                )
            )
            return
        if stop_event.is_set():
            return
        on_event(
            QueueEvent(
                request_id=command.request_id,
                status="completed",
                next_index=1,
                processed_source_chars=total,
                total_source_chars=total,
                translation_so_far=translated,
            )
        )
