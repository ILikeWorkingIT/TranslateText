import sys
import threading
import tkinter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = Path(__file__).resolve().parent
for path in (SRC, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from domain.errors import AppLayerError, OllamaUnavailableError
from ui_helpers import (
    WorkerAfterMixin,
    combo_values,
    patch_combobox_event_generate,
    pump_until,
)

DEFAULT_FAKE_MODELS = ("llama3.2", "qwen2.5:3b")


class RecordingOllama:
    def __init__(self, names: tuple[str, ...]) -> None:
        self.names = names
        self.list_calls = 0
        self.translate_calls: list[tuple[str, str, str]] = []
        self.translation_result = "Привет"
        self.translation_results: tuple[str, ...] | None = None
        self.translate_error: AppLayerError | None = None
        self.translate_hold: threading.Event | None = None
        self.list_hold: threading.Event | None = None
        self.error_from_call: int | None = None

    def list_models(self) -> tuple[str, ...]:
        self.list_calls += 1
        hold = self.list_hold
        if hold is not None:
            hold.wait(timeout=10)
        if not self.names:
            raise OllamaUnavailableError("empty model list")
        return tuple(self.names)

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        self.translate_calls.append((model, instruction, source))
        hold = self.translate_hold
        if hold is not None:
            hold.wait(timeout=10)
        if self.translate_error is not None:
            if (
                self.error_from_call is None
                or len(self.translate_calls) >= self.error_from_call
            ):
                raise self.translate_error
        if self.translation_results is not None:
            index = len(self.translate_calls) - 1
            if index < len(self.translation_results):
                return self.translation_results[index]
        return self.translation_result

    def close(self) -> None:
        return


@pytest.fixture
def open_window(monkeypatch):
    from ui.layout import TranslateTextWindow

    class HarnessWindow(WorkerAfterMixin, TranslateTextWindow):
        def __init__(self) -> None:
            super().__init__()
            patch_combobox_event_generate(self)

    apps = []
    ports = []

    def _open(names: tuple[str, ...]):
        port = RecordingOllama(names)
        ports.append(port)
        monkeypatch.setattr("ui.layout.OllamaGateway", lambda: port)
        try:
            app = HarnessWindow()
        except tkinter.TclError:
            app = HarnessWindow()
        apps.append(app)
        app.withdraw()
        app.update_idletasks()
        if names:
            pump_until(app, lambda: combo_values(app.model) == names)
        return app, port

    yield _open
    for port in ports:
        if port.translate_hold is not None:
            port.translate_hold.set()
        if port.list_hold is not None:
            port.list_hold.set()
    for app in apps:
        for attr in ("_status_after", "_hint_leave_after"):
            after_id = getattr(app, attr, "")
            if after_id:
                try:
                    app.after_cancel(after_id)
                except Exception:
                    pass
        app.destroy()


@pytest.fixture
def window(open_window):
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    return app
