"""B-001: Ctrl+C с русской раскладки копирует выделение, не вставляет."""

from __future__ import annotations

import tkinter

from ui.layout import _is_copy_key, _is_paste_key
from ui.messages import LABEL_TRANSLATION
from ui_helpers import find_textbox_for_label, set_textbox_content, textbox_content

_SAMPLE = "Copy me from translation"


class _KeyEvent:
    def __init__(self, keycode: int, keysym: str) -> None:
        self.keycode = keycode
        self.keysym = keysym


def _select_all(box) -> None:
    inner = getattr(box, "_textbox", box)
    inner.tag_add("sel", "1.0", "end-1c")
    inner.focus_force()
    box.focus_force()


def _clipboard_text(window) -> str:
    try:
        return str(window.clipboard_get())
    except tkinter.TclError:
        return ""


def test_should_treat_cyrillic_es_as_copy_not_paste() -> None:
    """B-001: на RU у клавиши C keysym Cyrillic_es, VK_C=67 — это copy, не paste."""
    ru_c = _KeyEvent(67, "Cyrillic_es")
    ru_v = _KeyEvent(86, "Cyrillic_em")
    assert _is_copy_key(ru_c)
    assert not _is_paste_key(ru_c)
    assert _is_paste_key(ru_v)
    assert not _is_copy_key(ru_v)


def test_should_copy_translation_when_ctrl_c_uses_cyrillic_es(
    window, monkeypatch
) -> None:
    """B-001: RU Ctrl+C копирует выделение поля перевода в буфер."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    set_textbox_content(box, _SAMPLE)
    _select_all(box)
    monkeypatch.setattr(window, "_focused_app_textbox", lambda: box)
    window.clipboard_clear()
    window.clipboard_append("STALE")
    window.update_idletasks()
    result = window._on_window_ctrl_key(_KeyEvent(67, "Cyrillic_es"))
    window.update_idletasks()
    assert result == "break"
    assert _clipboard_text(window) == _SAMPLE, (
        "Ctrl+C на русской раскладке копирует выделение поля перевода"
    )
    assert textbox_content(box) == _SAMPLE, "копирование не должно менять поле"


def test_should_copy_translation_when_ctrl_c_uses_latin_c(
    window, monkeypatch
) -> None:
    """B-001: EN Ctrl+C по-прежнему копирует."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    set_textbox_content(box, _SAMPLE)
    _select_all(box)
    monkeypatch.setattr(window, "_focused_app_textbox", lambda: box)
    window.clipboard_clear()
    window.update_idletasks()
    result = window._on_window_ctrl_key(_KeyEvent(67, "c"))
    window.update_idletasks()
    assert result == "break"
    assert _clipboard_text(window) == _SAMPLE
