"""S-06: лимит 100 000 — отказ при «Перевести», без вызова Ollama."""

from __future__ import annotations

from conftest import DEFAULT_FAKE_MODELS
from domain.models import MAX_SOURCE_CHARS, TARGET_FRAGMENT_CHARS_MAX
from ui.messages import (
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    STATUS_SOURCE_LIMIT_EXCEEDED,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
)

OVER_LIMIT = "z" * (MAX_SOURCE_CHARS + 1)
AT_LIMIT = "w" * MAX_SOURCE_CHARS


def _fill_original(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _click_translate(window) -> None:
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    button.invoke()
    window.update_idletasks()


def test_should_keep_over_limit_text_in_field_before_translate(open_window) -> None:
    """FT-014, happy: поле держит > 100k до «Перевести»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, OVER_LIMIT)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    assert len(textbox_content(box)) == MAX_SOURCE_CHARS + 1
    assert port.translate_calls == [], "до Перевести Ollama не вызывается"


def test_should_not_call_ollama_when_user_translates_over_limit_text(
    open_window,
):
    """FT-023, US-001 AC4, negative: > 100k — без перевода и без Ollama."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, OVER_LIMIT)
    _click_translate(app)
    pump_until(app, lambda: STATUS_SOURCE_LIMIT_EXCEEDED in str(app.status.cget("text")))
    assert port.translate_calls == [], "при превышении лимита Ollama не вызывается"


def test_should_keep_original_when_user_translates_over_limit_text(open_window):
    """FT-023, A0036, negative: текст в поле не урезается."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, OVER_LIMIT)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    _click_translate(app)
    pump_until(app, lambda: STATUS_SOURCE_LIMIT_EXCEEDED in str(app.status.cget("text")))
    assert len(textbox_content(box)) == MAX_SOURCE_CHARS + 1, (
        "оригинал не обрезан после отказа"
    )
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert translation is not None, "есть поле перевода"
    assert textbox_content(translation) == "", "поле перевода не меняется"


def test_should_show_limit_message_when_user_translates_over_limit_text(
    open_window,
):
    """FT-023, A0007, error: видно сообщение о превышении объёма."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, OVER_LIMIT)
    _click_translate(app)
    pump_until(app, lambda: STATUS_SOURCE_LIMIT_EXCEEDED in str(app.status.cget("text")))
    assert STATUS_SOURCE_LIMIT_EXCEEDED in str(app.status.cget("text")), (
        "в статусе сообщение о превышении лимита"
    )


def test_should_enable_translate_when_original_exceeds_limit(open_window) -> None:
    """FT-014, edge: > 100k не блокирует кнопку до «Перевести»."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, OVER_LIMIT)
    button = find_button(app, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), (
        "Перевести доступна при тексте > 100k до нажатия"
    )


def test_should_translate_when_original_is_exactly_100000_chars(
    monkeypatch,
    open_window,
):
    """FT-023, A0141: ровно 100 000 — допустимо, нарезка на фрагменты ≤700."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "ok"
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    instruction = find_textbox_for_label(app, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    set_textbox_content(instruction, "")
    _fill_original(app, AT_LIMIT)
    _click_translate(app)
    pump_until(app, lambda: len(port.translate_calls) >= 1)
    assert len(port.translate_calls[0][2]) <= TARGET_FRAGMENT_CHARS_MAX
