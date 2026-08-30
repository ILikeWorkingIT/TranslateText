"""S-09: предупреждение о несохранённом переводе (FT-032, UC-006)."""

from __future__ import annotations

from pathlib import Path

from conftest import DEFAULT_FAKE_MODELS
from ui.messages import (
    BASE_PROMPT,
    DIRECTION_RU_EN,
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    MSG_UNSAVED_TRANSLATION,
    TITLE_EMPTY_INSTRUCTION,
    TITLE_UNSAVED_TRANSLATION,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    pump_until,
    set_textbox_content,
    textbox_content,
)


PREFERRED_MODEL = "qwen2.5:3b"


def _fill_original(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _fill_translation(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле перевода"
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _click_translate(window) -> None:
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    button.invoke()
    window.update_idletasks()


def _click_open_file(window) -> None:
    button = find_button(window, LABEL_OPEN_FILE)
    assert button is not None, "есть кнопка Открыть файл"
    button.invoke()
    window.update_idletasks()


def _click_save(window) -> None:
    button = find_button(window, LABEL_SAVE_TRANSLATION)
    assert button is not None, "есть кнопка Сохранить перевод"
    button.invoke()
    window.update_idletasks()


def _save_to(monkeypatch, window, path: Path) -> None:
    monkeypatch.setattr(
        "ui.layout.filedialog.asksaveasfilename",
        lambda **kwargs: str(path),
    )
    _click_save(window)
    pump_until(window, lambda: bool(window._translation_saved) and path.is_file())


def _wait_translation(window, expected: str) -> None:
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле перевода"
    pump_until(window, lambda: textbox_content(box) == expected)


def test_should_show_unsaved_dialog_when_user_translates_with_unsaved_text(
    monkeypatch,
    open_window,
):
    """FT-032, US-006 AC1, dialog: несохранённый перевод — предупреждение перед «Перевести»."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_original(app, "Hello")
    _fill_translation(app, "Старый перевод")
    _click_translate(app)
    assert calls == [(TITLE_UNSAVED_TRANSLATION, MSG_UNSAVED_TRANSLATION)], (
        "показано предупреждение, что перевод не сохранён"
    )
    assert port.translate_calls == [], "до подтверждения Ollama не вызывается"


def test_should_not_start_translation_when_user_cancels_unsaved_dialog(
    monkeypatch,
    open_window,
):
    """FT-032, A0098, negative: отмена — перевод не начинается, поля на месте."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: False)
    _fill_original(app, "Hello")
    _fill_translation(app, "Старый перевод")
    _click_translate(app)
    original = find_textbox_for_label(app, LABEL_ORIGINAL)
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert original is not None and translation is not None
    assert textbox_content(original) == "Hello"
    assert textbox_content(translation) == "Старый перевод"
    assert port.translate_calls == []


def test_should_replace_translation_when_user_confirms_unsaved_and_translates(
    monkeypatch,
    open_window,
):
    """FT-032, FT-035, US-006 AC1: подтверждение — новый перевод заменяет поле."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    port.translation_result = "Новый"
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    _fill_original(app, "Hello")
    _fill_translation(app, "Старый перевод")
    _click_translate(app)
    _wait_translation(app, "Новый")
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None
    assert textbox_content(box) == "Новый"
    assert "Старый" not in textbox_content(box)
    assert port.translate_calls == [(PREFERRED_MODEL, BASE_PROMPT, "Hello")]


def test_should_show_unsaved_dialog_when_user_opens_file_with_unsaved_text(
    monkeypatch,
    open_window,
):
    """FT-032, US-006 AC2, dialog: предупреждение перед «Открыть файл»."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_translation(app, "Старый перевод")
    _click_open_file(app)
    assert calls == [(TITLE_UNSAVED_TRANSLATION, MSG_UNSAVED_TRANSLATION)]


def test_should_keep_fields_when_user_cancels_unsaved_dialog_before_open_file(
    monkeypatch,
    open_window,
):
    """FT-032, A0098, negative: отмена «Открыть файл» не меняет поля."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: False)
    _fill_original(app, "Был оригинал")
    _fill_translation(app, "Старый перевод")
    _click_open_file(app)
    original = find_textbox_for_label(app, LABEL_ORIGINAL)
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert original is not None and translation is not None
    assert textbox_content(original) == "Был оригинал"
    assert textbox_content(translation) == "Старый перевод"


def test_should_clear_translation_when_source_loaded_after_unsaved_confirm(
    monkeypatch,
    open_window,
):
    """A0099, US-006 AC2: успешная загрузка после подтверждения очищает перевод."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    monkeypatch.setattr("ui.layout.messagebox.askokcancel", lambda *_a, **_k: True)
    _fill_original(app, "Старый оригинал")
    _fill_translation(app, "Старый перевод")
    _click_open_file(app)
    app._apply_loaded_source("Текст из файла")
    original = find_textbox_for_label(app, LABEL_ORIGINAL)
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert original is not None and translation is not None
    assert textbox_content(original) == "Текст из файла"
    assert textbox_content(translation) == ""


def test_should_not_show_unsaved_dialog_when_translation_is_empty(
    monkeypatch,
    open_window,
):
    """FT-032, US-006 AC4: пустое поле перевода — без предупреждения."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return True

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_original(app, "Hello")
    _click_translate(app)
    _wait_translation(app, port.translation_result)
    assert calls == [], "при пустом переводе диалог FT-032 не показывается"


def test_should_not_show_unsaved_dialog_when_translation_was_saved(
    monkeypatch,
    open_window,
    tmp_path: Path,
):
    """FT-032, FT-004, US-006 AC3: после «Сохранить перевод» без правок — без предупреждения."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return True

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_original(app, "Hello")
    _fill_translation(app, "Сохранённый")
    _save_to(monkeypatch, app, tmp_path / "saved.txt")
    _click_translate(app)
    _wait_translation(app, port.translation_result)
    assert calls == [], "после сохранения без правок предупреждения нет"


def test_should_show_unsaved_dialog_when_user_edits_after_save(
    monkeypatch,
    open_window,
    tmp_path: Path,
):
    """FT-033, A0106: правка после сохранения снова делает перевод несохранённым."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_original(app, "Hello")
    _fill_translation(app, "Сохранённый")
    _save_to(monkeypatch, app, tmp_path / "saved.txt")
    _fill_translation(app, "Сохранённый и правленый")
    _click_translate(app)
    assert calls == [(TITLE_UNSAVED_TRANSLATION, MSG_UNSAVED_TRANSLATION)]


def test_should_not_show_unsaved_dialog_when_only_direction_changes(
    monkeypatch,
    window,
):
    """FT-053, A0124: смена направления не показывает FT-032."""
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_translation(window, "Несохранённый кусок.")
    window.direction.set(DIRECTION_RU_EN)
    window._on_direction(DIRECTION_RU_EN)
    window.update_idletasks()
    assert calls == []


def test_should_ask_empty_instruction_after_unsaved_confirm_when_both_apply(
    monkeypatch,
    open_window,
):
    """A0102: сначала FT-032, затем FT-029."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    titles: list[str] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        titles.append(title)
        return title == TITLE_UNSAVED_TRANSLATION

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    instruction = app.instruction
    set_textbox_content(instruction, "")
    instruction.event_generate("<KeyRelease>")
    _fill_original(app, "Hello")
    _fill_translation(app, "Старый")
    _click_translate(app)
    assert titles == [TITLE_UNSAVED_TRANSLATION, TITLE_EMPTY_INSTRUCTION]
    assert textbox_content(instruction) == "", (
        "отмена FT-029 после подтверждения FT-032 не подставляет промпт"
    )
    assert port.translate_calls == []


def test_should_show_unsaved_dialog_when_incomplete_translation_is_not_saved(
    monkeypatch,
    open_window,
):
    """A0097, US-006 AC4: неполный перевод после сбоя — несохранённый."""
    app, _port = open_window(DEFAULT_FAKE_MODELS)
    calls: list[tuple[str, str]] = []

    def fake_askokcancel(title: str, message: str, **kwargs: object) -> bool:
        calls.append((title, message))
        return False

    monkeypatch.setattr("ui.layout.messagebox.askokcancel", fake_askokcancel)
    _fill_original(app, "Hello")
    _fill_translation(app, "first")
    app._translation_saved = False
    _click_translate(app)
    assert calls == [(TITLE_UNSAVED_TRANSLATION, MSG_UNSAVED_TRANSLATION)]
