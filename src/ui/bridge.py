from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Protocol

from domain.errors import (
    AppLayerError,
    EmptyInstructionError,
    OllamaUnavailableError,
    SourceLimitExceededError,
    UnsavedTranslationError,
)
from domain.models import (
    ModelsRefreshedEvent,
    OllamaPort,
    QueueEvent,
    RefreshModelsCommand,
    StartTranslationCommand,
)
from use_cases.refresh_models import RefreshModels
from use_cases.start_translation import StartTranslation, require_ready_instruction
from use_cases.unsaved_translation import require_unsaved_confirmed


class UiHost(Protocol):
    def call_on_ui(self, func: Callable[[], None]) -> None: ...

    def winfo_exists(self) -> bool: ...


class ModelsBridge:
    def __init__(
        self,
        *,
        host: UiHost,
        ollama: OllamaPort,
        on_models: Callable[[ModelsRefreshedEvent], None],
        on_unavailable: Callable[[], None],
    ) -> None:
        self._host = host
        self._ollama = ollama
        self._use_case = RefreshModels(ollama)
        self._on_models = on_models
        self._on_unavailable = on_unavailable
        self._stop = threading.Event()
        self.models_refresh_request_id = 0

    def refresh(self, current_model: str) -> None:
        if self._stop.is_set():
            return
        self.models_refresh_request_id += 1
        command = RefreshModelsCommand(
            request_id=self.models_refresh_request_id,
            current_model=current_model,
        )
        worker = threading.Thread(
            target=self._worker,
            args=(command,),
            daemon=True,
        )
        worker.start()

    def close(self) -> None:
        self._stop.set()
        self._ollama.close()

    def _worker(self, command: RefreshModelsCommand) -> None:
        try:
            event = self._use_case.run(command)
        except OllamaUnavailableError:
            if self._stop.is_set():
                return
            self._host.call_on_ui(
                lambda rid=command.request_id: self._apply_unavailable(rid)
            )
            return
        if self._stop.is_set():
            return
        self._host.call_on_ui(lambda delivered=event: self._apply(delivered))

    def _apply(self, event: ModelsRefreshedEvent) -> None:
        if not self._can_apply(event.request_id):
            return
        self._on_models(event)

    def _apply_unavailable(self, request_id: int) -> None:
        if not self._can_apply(request_id):
            return
        self._on_unavailable()

    def _can_apply(self, request_id: int) -> bool:
        if self._stop.is_set():
            return False
        if not self._host.winfo_exists():
            return False
        return request_id == self.models_refresh_request_id


class TranslationBridge:
    def __init__(
        self,
        *,
        host: UiHost,
        ollama: OllamaPort,
        on_event: Callable[[QueueEvent], None],
        on_source_limit_exceeded: Callable[[], None] | None = None,
    ) -> None:
        self._host = host
        self._ollama = ollama
        self._use_case = StartTranslation(ollama)
        self._on_event = on_event
        self._on_source_limit_exceeded = on_source_limit_exceeded
        self._stop = threading.Event()
        self._cancel = threading.Event()
        self.translation_request_id = 0

    def start(
        self,
        *,
        original_text: str,
        instruction: str,
        model: str,
        direction: str,
        instruction_confirmed: bool | None = None,
        translation_text: str = "",
        translation_saved: bool = True,
        unsaved_confirmed: bool = False,
    ) -> None:
        if self._stop.is_set():
            return
        confirmed = (
            len(instruction) > 0
            if instruction_confirmed is None
            else instruction_confirmed
        )
        require_unsaved_confirmed(
            translation_text,
            translation_saved,
            confirmed=unsaved_confirmed,
        )
        require_ready_instruction(instruction)
        self._cancel.clear()
        self.translation_request_id += 1
        command = StartTranslationCommand(
            request_id=self.translation_request_id,
            original_text=original_text,
            instruction=instruction,
            instruction_confirmed=confirmed,
            model=model,
            direction=direction,
            translation_text=translation_text,
            translation_saved=translation_saved,
            unsaved_confirmed=unsaved_confirmed,
        )
        worker = threading.Thread(
            target=self._worker,
            args=(command,),
            daemon=True,
        )
        worker.start()

    def cancel(self) -> None:
        """FT-054: отмена Пользователя. Не закрывает HTTP-клиент (A0149, A0152)."""
        self._cancel.set()

    def close(self) -> None:
        self._stop.set()
        self._ollama.close()

    def _worker(self, command: StartTranslationCommand) -> None:
        def emit(event: QueueEvent) -> None:
            if self._stop.is_set():
                return
            self._host.call_on_ui(lambda delivered=event: self._apply(delivered))

        try:
            self._use_case.run(
                command,
                stop_event=self._stop,
                on_event=emit,
                cancel_event=self._cancel,
            )
        except EmptyInstructionError:
            return
        except UnsavedTranslationError:
            return
        except SourceLimitExceededError:
            if self._stop.is_set():
                return
            self._host.call_on_ui(self._apply_source_limit_exceeded)
        except AppLayerError:
            if self._stop.is_set():
                return
            self._host.call_on_ui(
                lambda rid=command.request_id: self._apply(
                    QueueEvent(
                        request_id=rid,
                        status="incomplete",
                        next_index=0,
                        processed_source_chars=0,
                        total_source_chars=len(command.original_text),
                        translation_so_far="",
                        incomplete_cause="ollama",
                    )
                ),
            )

    def _apply_source_limit_exceeded(self) -> None:
        if self._on_source_limit_exceeded is None:
            return
        if not self._host.winfo_exists():
            return
        self._on_source_limit_exceeded()

    def _apply(self, event: QueueEvent) -> None:
        if not self._can_apply(event.request_id):
            return
        self._on_event(event)

    def _can_apply(self, request_id: int) -> bool:
        if self._stop.is_set():
            return False
        if not self._host.winfo_exists():
            return False
        return request_id == self.translation_request_id
