"""S-04: перевод одного короткого фрагмента — EN→RU, RU→EN, снимок, прогресс."""

from __future__ import annotations

import threading

from conftest import DEFAULT_FAKE_MODELS
from ui.messages import (
    BASE_PROMPT,
    BASE_PROMPT_RU_EN,
    DIRECTION_RU_EN,
    HINT_IN_PROGRESS,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    LABEL_TRANSLATION_EN,
)
from ui_helpers import (
    collected_texts,
    find_button,
    find_progress_bar,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
    trigger_model_click,
)

PREFERRED_MODEL = "qwen2.5:3b"
OTHER_MODEL = "llama3.2"


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


def _select_direction(window, value: str) -> None:
    window.direction.set(value)
    window._on_direction(value)
    window.update_idletasks()


def _wait_translation(window, expected: str, label: str) -> None:
    box = find_textbox_for_label(window, label)
    assert box is not None, "есть поле перевода"
    pump_until(window, lambda: textbox_content(box) == expected)


def _start_held_translation(app, port, original: str = "Hello") -> threading.Event:
    hold = threading.Event()
    port.translate_hold = hold
    _fill_original(app, original)
    _click_translate(app)
    pump_until(app, lambda: len(port.translate_calls) == 1)
    return hold


def test_should_put_russian_translation_in_field_when_user_translates_en_ru(
    open_window,
):
    """FT-009, FT-010, FT-016, US-001 AC1, happy: короткий EN→RU — один фрагмент в «Русский перевод»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "Привет"
    _fill_original(app, "Hello")
    _click_translate(app)
    _wait_translation(app, "Привет", LABEL_TRANSLATION)
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == "Привет", (
        "после Перевести в Русский перевод попадает результат одного фрагмента"
    )
    assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT, "Hello")], (
        "один запрос: выбранная модель, снимок инструкции EN→RU и исходник"
    )


def test_should_put_english_translation_in_field_when_user_translates_ru_en(
    open_window,
):
    """FT-002, FT-010, US-009 AC1, happy: короткий RU→EN — результат в «Английский перевод»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "Hello"
    _select_direction(app, DIRECTION_RU_EN)
    _fill_original(app, "Привет")
    _click_translate(app)
    _wait_translation(app, "Hello", LABEL_TRANSLATION_EN)
    box = find_textbox_for_label(app, LABEL_TRANSLATION_EN)
    assert box is not None, "есть поле Английский перевод"
    assert textbox_content(box) == "Hello", (
        "после Перевести в Английский перевод попадает результат"
    )
    assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT_RU_EN, "Привет")], (
        "запрос несёт снимок инструкции RU→EN и русский исходник"
    )


def test_should_use_selected_model_when_user_translates(open_window):
    """FT-006, happy: в запрос перевода уходит модель из списка «Модель»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    app.model.set(OTHER_MODEL)
    app.update_idletasks()
    _fill_original(app, "Hello")
    _click_translate(app)
    _wait_translation(app, port.translation_result, LABEL_TRANSLATION)
    assert port.translate_calls[0][0] == OTHER_MODEL, (
        "перевод идёт выбранной в списке моделью, не умолчанием"
    )


def test_should_show_progress_zero_then_hundred_when_single_fragment_translates(
    open_window,
):
    """FT-022, A0039, NFT-002, loading: один фрагмент — 0 % до ответа, 100 % после."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        bar = find_progress_bar(app)
        assert bar is not None, "есть индикатор прогресса"
        assert bar.get() == 0, (
            "до ответа Ollama индикатор 0 %, без ожидания модели"
        )
        button = find_button(app, LABEL_TRANSLATE)
        assert button is not None, "есть кнопка Перевести"
        assert is_disabled(button), (
            "первая смена UI — блокировка Перевести до ответа Ollama"
        )
    finally:
        hold.set()
    pump_until(app, lambda: find_progress_bar(app).get() == 1)
    assert find_progress_bar(app).get() == 1, (
        "после ответа одного фрагмента индикатор 100 %"
    )


def test_should_disable_translate_when_translation_is_in_progress(open_window):
    """FT-031, US-001 AC1, loading: пока идёт запрос, «Перевести» недоступна."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        button = find_button(app, LABEL_TRANSLATE)
        assert button is not None, "есть кнопка Перевести"
        assert is_disabled(button), "Перевести заблокирована, пока идёт перевод"
        original = find_textbox_for_label(app, LABEL_ORIGINAL)
        assert original is not None, "есть поле Оригинальный текст"
        assert textbox_content(original) == "Hello", (
            "оригинал на месте, пока идёт перевод"
        )
    finally:
        hold.set()


def test_should_show_in_progress_hint_when_pointer_hovers_during_translation(
    open_window,
):
    """FT-050, US-008, loading: наведение на заблокированную «Перевести» — «Идёт перевод»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port)
    try:
        button = find_button(app, LABEL_TRANSLATE)
        assert button is not None, "есть кнопка Перевести"
        button.event_generate("<Enter>")
        app.update_idletasks()
        assert any(HINT_IN_PROGRESS in text for text in collected_texts(app)), (
            "у заблокированной Перевести видна подсказка Идёт перевод"
        )
        assert HINT_IN_PROGRESS not in str(app.status.cget("text")), (
            "подсказка Идёт перевод не в строке статуса"
        )
    finally:
        hold.set()


def test_should_enable_translate_when_translation_finishes(open_window):
    """FT-031, happy: после ответа «Перевести» снова доступна."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    _fill_original(app, "Hello")
    _click_translate(app)
    _wait_translation(app, port.translation_result, LABEL_TRANSLATION)
    button = find_button(app, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), (
        "после окончания перевода Перевести доступна"
    )


def test_should_replace_previous_translation_when_user_translates_again(
    monkeypatch,
    open_window,
):
    """FT-035, US-001 AC3, happy: новый запуск заменяет поле перевода, не дописывает."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    port.translation_result = "Первый"
    _fill_original(app, "One")
    _click_translate(app)
    _wait_translation(app, "Первый", LABEL_TRANSLATION)
    port.translation_result = "Второй"
    _fill_original(app, "Two")
    _click_translate(app)
    _wait_translation(app, "Второй", LABEL_TRANSLATION)
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == "Второй", (
        "повторное Перевести подменяет прежний перевод"
    )
    assert "Первый" not in textbox_content(box), (
        "новый перевод не дописывается к старому"
    )


def test_should_keep_request_snapshot_when_fields_change_during_translation(
    open_window,
):
    """FT-011, NFT-014, A0052, edge: смена полей и клик «Модель» не меняют ушедший запрос."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    hold = _start_held_translation(app, port, original="Hello")
    try:
        _select_direction(app, DIRECTION_RU_EN)
        instruction = find_textbox_for_label(app, LABEL_CUSTOM_INSTRUCTION)
        assert instruction is not None, "есть поле Кастомная инструкция"
        set_textbox_content(instruction, "CHANGED")
        app.model.set(OTHER_MODEL)
        trigger_model_click(app)
        assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT, "Hello")], (
            "запрос держит снимок модели, инструкции и исходника со старта"
        )
        button = find_button(app, LABEL_TRANSLATE)
        assert button is not None, "есть кнопка Перевести"
        assert is_disabled(button), (
            "клик по Модель во время перевода не снимает блокировку FT-031"
        )
    finally:
        hold.set()
    pump_until(
        app,
        lambda: textbox_content(app.translation) == port.translation_result,
    )
    assert len(port.translate_calls) == 1, (
        "повторного запроса перевода из-за смены полей нет"
    )
