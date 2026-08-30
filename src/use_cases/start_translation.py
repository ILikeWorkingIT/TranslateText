from __future__ import annotations

from collections.abc import Callable
from threading import Event

from domain.errors import AppLayerError, EmptyInstructionError, QueueBusyError
from domain.models import Fragment, OllamaPort, QueueEvent, StartTranslationCommand
from services.split_text import SplitText


def require_ready_instruction(instruction: str) -> None:
    """FT-029: очередь не стартует с пустой инструкцией. Промпт не подставляем."""
    if len(instruction) == 0:
        raise EmptyInstructionError("empty instruction")


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
    ) -> None:
        if self._busy:
            raise QueueBusyError("queue inProgress")
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
    ) -> None:
        total = len(command.original_text)
        processed = 0
        translated_parts: list[str] = []

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

        for index, fragment in enumerate(fragments):
            if stop_event.is_set():
                return
            try:
                translated = self._ollama.translate_fragment(
                    model=command.model,
                    instruction=command.instruction,
                    source=fragment.source,
                )
            except AppLayerError:
                if stop_event.is_set():
                    return
                on_event(
                    QueueEvent(
                        request_id=command.request_id,
                        status="incomplete",
                        next_index=index,
                        processed_source_chars=processed,
                        total_source_chars=total,
                        translation_so_far="".join(translated_parts),
                    )
                )
                return

            translated_parts.append(translated)
            processed += len(fragment.source)
            if stop_event.is_set():
                return
            if index + 1 < len(fragments):
                on_event(
                    QueueEvent(
                        request_id=command.request_id,
                        status="inProgress",
                        next_index=index + 1,
                        processed_source_chars=processed,
                        total_source_chars=total,
                        translation_so_far="".join(translated_parts),
                    )
                )

        on_event(
            QueueEvent(
                request_id=command.request_id,
                status="completed",
                next_index=len(fragments),
                processed_source_chars=total,
                total_source_chars=total,
                translation_so_far="".join(translated_parts),
            )
        )
