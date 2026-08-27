from __future__ import annotations

import threading
import time
import tkinter
from collections.abc import Callable

import customtkinter as ctk


def iter_widgets(widget):
    yield widget
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield from iter_widgets(child)


def widget_text(widget) -> str:
    try:
        value = widget.cget("text")
    except Exception:
        return ""
    return str(value) if value is not None else ""


def find_by_text(root, text: str):
    for widget in iter_widgets(root):
        if widget_text(widget) == text:
            return widget
    return None


def find_button(root, text: str) -> ctk.CTkButton | None:
    for widget in iter_widgets(root):
        if isinstance(widget, ctk.CTkButton) and widget_text(widget) == text:
            return widget
    return None


def find_textbox_for_label(root, label_text: str) -> ctk.CTkTextbox | None:
    label = find_by_text(root, label_text)
    if label is None:
        return None
    parent = label.master
    for widget in iter_widgets(parent):
        if isinstance(widget, ctk.CTkTextbox):
            return widget
    return None


def find_progress_bar(root) -> ctk.CTkProgressBar | None:
    for widget in iter_widgets(root):
        if isinstance(widget, ctk.CTkProgressBar):
            return widget
    return None


def textbox_content(box: ctk.CTkTextbox) -> str:
    return box.get("0.0", "end-1c")


def set_textbox_content(box: ctk.CTkTextbox, value: str) -> None:
    box.delete("0.0", "end")
    if value:
        box.insert("0.0", value)


def is_disabled(widget) -> bool:
    try:
        state = str(widget.cget("state"))
    except Exception:
        return False
    return state == "disabled"


def collected_texts(root) -> list[str]:
    texts = []
    for widget in iter_widgets(root):
        value = widget_text(widget)
        if value:
            texts.append(value)
    return texts


def combo_values(combo: ctk.CTkComboBox) -> tuple[str, ...]:
    raw = combo.cget("values")
    if raw is None:
        return ()
    return tuple(str(item) for item in raw)


class WorkerAfterMixin:
    """В тестах без mainloop: after() из воркера не зовёт Tcl, колбэк выполняется в потоке Tk."""

    def __init__(self) -> None:
        self._after_from_worker: list[tuple[Callable[..., object], tuple[object, ...]]] = []
        self._after_lock = threading.Lock()
        super().__init__()

    def after(
        self,
        ms: int,
        func: Callable[..., object] | None = None,
        *args: object,
    ) -> str:
        if func is not None and threading.current_thread() is not threading.main_thread():
            with self._after_lock:
                self._after_from_worker.append((func, args))
            return "worker-after"
        if func is None:
            return super().after(ms)
        return super().after(ms, func, *args)

    def drain_worker_after(self) -> None:
        with self._after_lock:
            jobs = list(self._after_from_worker)
            self._after_from_worker.clear()
        for func, args in jobs:
            func(*args)


def patch_combobox_event_generate(window: ctk.CTk) -> None:
    """withdraw() не доставляет Button-1/FocusIn в CTkComboBox; как у «Перевести», event_generate зовёт обработчики окна."""
    combo = window.model
    original = combo.event_generate

    def event_generate(sequence: str = "", **kwargs: str | int | float | bool) -> None:
        if sequence == "<Button-1>":
            window._on_model_click(None)
        elif sequence == "<FocusIn>":
            window._on_model_focus(None)
        try:
            original(sequence, **kwargs)
        except tkinter.TclError:
            pass

    combo.event_generate = event_generate


def pump_until(window: ctk.CTk, predicate: Callable[[], bool], *, timeout_s: float = 2.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        drain = getattr(window, "drain_worker_after", None)
        if drain is not None:
            drain()
        window.update()
        if predicate():
            return
    raise AssertionError("окно не достигло ожидаемого состояния")


def trigger_model_click(window: ctk.CTk) -> None:
    window.model.event_generate("<Button-1>")
    window.update()


def trigger_model_focus(window: ctk.CTk) -> None:
    window.model.event_generate("<FocusIn>")
    window.update()
