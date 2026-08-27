from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Protocol

from domain.errors import OllamaUnavailableError
from domain.models import ModelsRefreshedEvent, OllamaPort, RefreshModelsCommand
from use_cases.refresh_models import RefreshModels


class UiHost(Protocol):
    def after(self, ms: int, func: Callable[[], None]) -> str: ...

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
            self._host.after(
                0, lambda rid=command.request_id: self._apply_unavailable(rid)
            )
            return
        if self._stop.is_set():
            return
        self._host.after(0, lambda delivered=event: self._apply(delivered))

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
