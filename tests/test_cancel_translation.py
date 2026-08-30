"""S-07c: команда «Отменить перевод» в окне (FT-054)."""

from __future__ import annotations

import threading

from conftest import DEFAULT_FAKE_MODELS
from domain.errors import OllamaTimeoutError
from ui.messages import (
    DIRECTION_RU_EN,
    HINT_IN_PROGRESS,
    LABEL_CANCEL_TRANSLATION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    STATUS_TRANSLATION_CANCELLED,
    STATUS_TRANSLATION_INCOMPLETE,
)
from ui_helpers import (
    collected_texts,
    find_button,
    find_textbox_for_label,
    is_disabled,
    is_shown,
    pump_until,
    set_textbox_content,
    textbox_content,
    widget_text,
)


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


def _cancel_button(window):
    button = find_button(window, LABEL_CANCEL_TRANSLATION)
    assert button is not None, "виджет Отменить перевод есть в дереве"
    return button


def _click_cancel(window) -> None:
    button = _cancel_button(window)
    assert is_shown(button), "Отменить перевод видна, пока идёт перевод"
    button.invoke()
    window.update_idletasks()


def _start_held_translation(
    app, port, original: str = "Hello"
) -> threading.Event:
    hold = threading.Event()
    port.translate_hold = hold
    _fill_original(app, original)
    _click_translate(app)
    pump_until(app, lambda: len(port.translate_calls) == 1)
    return hold


def _two_paragraphs() -> str:
    part = "a" * 400
    return f"{part}\n\n{part}"


def test_should_hide_cancel_when_translation_is_idle(window):
    """FT-054, A0147, US-010 AC1, empty: в покое «Отменить перевод» не видна."""
    button = _cancel_button(window)
    assert is_shown(button) is False, (
        "команда Отменить перевод скрыта, пока перевод не идёт"
    )


def test_should_show_cancel_when_translation_is_in_progress(open_window):
    """FT-054, A0147, US-010 AC1, loading: во время перевода команда видна."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        button = _cancel_button(app)
        assert is_shown(button), (
            "пока действует FT-031, видна команда Отменить перевод"
        )
        translate = find_button(app, LABEL_TRANSLATE)
        assert translate is not None, "есть кнопка Перевести"
        assert is_disabled(translate), "Перевести заблокирована, пока идёт перевод"
        translate.event_generate("<Enter>")
        app.update_idletasks()
        assert any(HINT_IN_PROGRESS in text for text in collected_texts(app)), (
            "наведение на Перевести показывает Идёт перевод"
        )
    finally:
        hold.set()


def test_should_hide_cancel_immediately_when_user_cancels(open_window):
    """FT-054, A0151, loading: после клика команда скрывается сразу."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        _click_cancel(app)
        assert is_shown(_cancel_button(app)) is False, (
            "после Отменить перевод команда скрыта, не ждёт конца HTTP"
        )
        _cancel_button(app).invoke()
        app.update_idletasks()
        assert len(port.translate_calls) == 1, (
            "повторный клик отмены, пока дожитие идёт, — нет операции"
        )
    finally:
        hold.set()


def test_should_keep_translate_disabled_when_cancel_waits_for_request(
    open_window,
):
    """FT-031, A0151, loading: клик отмены сам «Перевести» не разблокирует."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        _click_cancel(app)
        translate = find_button(app, LABEL_TRANSLATE)
        assert translate is not None, "есть кнопка Перевести"
        assert is_disabled(translate), (
            "Перевести остаётся серой, пока текущий запрос не завершился"
        )
    finally:
        hold.set()


def test_should_show_cancelled_status_when_user_cancels(open_window):
    """FT-054, A0150, error: статус — отмена Пользователя, не сбой Ollama."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    _click_cancel(app)
    hold.set()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_CANCELLED in widget_text(app.status),
    )
    assert STATUS_TRANSLATION_INCOMPLETE not in widget_text(app.status), (
        "после отмены не показывать причину FT-028"
    )
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == port.translation_result, (
        "успех текущего запроса после отмены дописывается в поле"
    )


def test_should_not_start_next_fragment_when_user_cancels_from_window(
    open_window,
):
    """FT-054, A0149, negative: из окна следующий фрагмент в Ollama не уходит."""
    app, port = open_window(("qwen2.5:3b",))
    port.translation_results = ("first", "second")
    hold = _start_held_translation(app, port, original=_two_paragraphs())
    _click_cancel(app)
    hold.set()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_CANCELLED in widget_text(app.status),
        timeout_s=5.0,
    )
    assert len(port.translate_calls) == 1, (
        "после отмены второй фрагмент в Ollama не стартует"
    )
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == "first\n\n", (
        "в поле склейка первого фрагмента с разрывом абзаца, без второго"
    )


def test_should_enable_translate_when_cancelled_request_finishes(open_window):
    """FT-031, A0151, happy: после конца запроса «Перевести» снова доступна."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    _click_cancel(app)
    hold.set()
    pump_until(
        app,
        lambda: not is_disabled(find_button(app, LABEL_TRANSLATE)),
    )
    translate = find_button(app, LABEL_TRANSLATE)
    assert translate is not None, "есть кнопка Перевести"
    assert is_disabled(translate) is False, (
        "после завершения отменённого запроса Перевести доступна"
    )
    assert is_shown(_cancel_button(app)) is False, (
        "после конца очереди Отменить перевод снова скрыта"
    )


def test_should_keep_cancelled_status_when_in_flight_fails_after_cancel(
    open_window,
):
    """A0153, A0148, error: сбой после отмены — сообщение FT-054, поле без обрывка."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    _click_cancel(app)
    port.translate_error = OllamaTimeoutError("timed out")
    hold.set()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_CANCELLED in widget_text(app.status),
    )
    assert STATUS_TRANSLATION_INCOMPLETE not in widget_text(app.status), (
        "принятая отмена важнее последующего сбоя Ollama"
    )
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == "", (
        "если фрагмент не успел, поле не заполняется обрывком"
    )


def test_should_show_cancelled_status_when_user_cancels_ru_en(open_window):
    """US-010 AC3, error: отмена при RU→EN — то же сообщение статуса."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    app.direction.set(DIRECTION_RU_EN)
    app._on_direction(DIRECTION_RU_EN)
    hold = _start_held_translation(app, port, original="Привет")
    _click_cancel(app)
    hold.set()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_CANCELLED in widget_text(app.status),
    )
    assert STATUS_TRANSLATION_INCOMPLETE not in widget_text(app.status), (
        "при RU→EN причина тоже отмена Пользователя, не сбой Ollama"
    )
