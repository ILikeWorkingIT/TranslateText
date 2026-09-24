"""S-05: пустая инструкция — диалог FT-029, согласие или отмена."""

from __future__ import annotations

from conftest import DEFAULT_FAKE_MODELS
from ui.messages import (
    BASE_PROMPT,
    BASE_PROMPT_RU_EN,
    DIRECTION_RU_EN,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    LABEL_TRANSLATION_EN,
    MSG_EMPTY_INSTRUCTION,
    TITLE_EMPTY_INSTRUCTION,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
)

PREFERRED_MODEL = "qwen2.5:7b"


def _fill_original(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _clear_instruction(window) -> None:
    box = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert box is not None, "есть поле Кастомная инструкция"
    set_textbox_content(box, "")
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


def test_should_enable_translate_when_instruction_is_empty_but_original_has_text(
    open_window,
):
    """FT-029, edge: пустая инструкция не блокирует «Перевести», если есть оригинал."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    _clear_instruction(app)
    _fill_original(app, "Hello")
    button = find_button(app, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), (
        "при пустой инструкции и непустом оригинале Перевести доступна"
    )


def test_should_show_empty_instruction_dialog_when_user_translates_without_instruction(
    monkeypatch,
    open_window,
):
    """FT-029, US-005 AC3, dialog: «Перевести» с пустой инструкцией открывает диалог."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _clear_instruction(app)
    _fill_original(app, "Hello")
    _click_translate(app)
    assert calls == [(TITLE_EMPTY_INSTRUCTION, MSG_EMPTY_INSTRUCTION)], (
        "показан диалог об отсутствии инструкции и базовом промпте"
    )
    assert port.translate_calls == [], "до согласия Ollama не вызывается"


def test_should_not_start_translation_when_user_cancels_empty_instruction_dialog(
    monkeypatch,
    open_window,
):
    """FT-029, US-005 AC4, negative: отмена — без перевода и без подстановки промпта."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: False)
    _clear_instruction(app)
    _fill_original(app, "Hello")
    instruction = find_textbox_for_label(app, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    _click_translate(app)
    assert textbox_content(instruction) == "", (
        "после отмены поле инструкции остаётся пустым"
    )
    assert port.translate_calls == [], "после отмены Ollama не вызывается"
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert translation is not None, "есть поле Русский перевод"
    assert textbox_content(translation) == "", "поле перевода не меняется"


def test_should_fill_base_prompt_and_translate_when_user_confirms_en_ru(
    monkeypatch,
    open_window,
):
    """FT-029, A0006, A0050, happy: согласие EN→RU — A0006 в поле и в запросе."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "Привет"
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    _clear_instruction(app)
    _fill_original(app, "Hello")
    instruction = find_textbox_for_label(app, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    _click_translate(app)
    assert textbox_content(instruction) == BASE_PROMPT, (
        "после согласия в поле базовый промпт EN→RU"
    )
    _wait_translation(app, "Привет", LABEL_TRANSLATION)
    assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT, "Hello")], (
        "перевод стартует со снимком A0006"
    )


def test_should_fill_ru_en_base_prompt_and_translate_when_user_confirms_ru_en(
    monkeypatch,
    open_window,
):
    """FT-029, A0122, happy: согласие RU→EN — A0122 в поле и в запросе."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "Hello"
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    _select_direction(app, DIRECTION_RU_EN)
    _clear_instruction(app)
    _fill_original(app, "Привет")
    instruction = find_textbox_for_label(app, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    _click_translate(app)
    assert textbox_content(instruction) == BASE_PROMPT_RU_EN, (
        "после согласия в поле базовый промпт RU→EN"
    )
    _wait_translation(app, "Hello", LABEL_TRANSLATION_EN)
    assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT_RU_EN, "Привет")], (
        "перевод стартует со снимком A0122"
    )
