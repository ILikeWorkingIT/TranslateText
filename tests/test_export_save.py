"""S-10: ручное «Сохранить перевод» (UC-003, FT-004, FT-043, FT-044, FT-046)."""

from __future__ import annotations

from pathlib import Path

from docx import Document

from ui.messages import (
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATION,
    MSG_EXPORT_FAILED,
    SAVE_FILETYPES,
    TITLE_EXPORT_FAILED,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
)


def _fill_translation(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле перевода"
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _click_save(window) -> None:
    button = find_button(window, LABEL_SAVE_TRANSLATION)
    assert button is not None, "есть кнопка Сохранить перевод"
    button.invoke()
    window.update_idletasks()


def _docx_text(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def test_should_write_translation_field_to_txt_when_user_saves(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-004, US-003 AC1: диалог .txt — в файле содержимое поля перевода."""
    target = tmp_path / "перевод.txt"
    monkeypatch.setattr(
        "ui.layout.filedialog.asksaveasfilename",
        lambda **kwargs: str(target),
    )
    _fill_translation(window, "Текст из поля\nвторая строка")
    _click_save(window)
    pump_until(window, lambda: bool(window._translation_saved) and target.is_file())
    assert target.read_text(encoding="utf-8") == "Текст из поля\nвторая строка"
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    assert textbox_content(box) == "Текст из поля\nвторая строка"


def test_should_write_translation_field_to_docx_when_user_saves(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-004, FT-046: диалог .docx — абзацы поля в документе."""
    target = tmp_path / "translation.docx"
    monkeypatch.setattr(
        "ui.layout.filedialog.asksaveasfilename",
        lambda **kwargs: str(target),
    )
    _fill_translation(window, "Первый абзац\n\nВторой")
    _click_save(window)
    pump_until(window, lambda: bool(window._translation_saved) and target.is_file())
    assert _docx_text(target) == "Первый абзац\n\nВторой"


def test_should_offer_only_txt_and_docx_when_save_dialog_opens(monkeypatch, window):
    """FT-046: диалог предлагает только .txt и .docx."""
    captured: dict[str, object] = {}

    def fake_dialog(**kwargs: object) -> str:
        captured.update(kwargs)
        return ""

    monkeypatch.setattr("ui.layout.filedialog.asksaveasfilename", fake_dialog)
    _fill_translation(window, "есть текст")
    _click_save(window)
    filetypes = captured.get("filetypes")
    assert filetypes == list(SAVE_FILETYPES)
    joined = " ".join(f"{name} {pattern}" for name, pattern in SAVE_FILETYPES)
    assert ".txt" in joined and ".docx" in joined
    assert ".pdf" not in joined and ".md" not in joined
    assert captured.get("confirmoverwrite") is True


def test_should_not_change_existing_file_when_user_cancels_save_dialog(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-043, US-003 AC4: отмена диалога не меняет существующий файл и поле."""
    target = tmp_path / "уже.txt"
    target.write_text("на диске", encoding="utf-8")
    monkeypatch.setattr(
        "ui.layout.filedialog.asksaveasfilename",
        lambda **kwargs: "",
    )
    _fill_translation(window, "в поле")
    _click_save(window)
    window.update_idletasks()
    assert target.read_text(encoding="utf-8") == "на диске"
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    assert textbox_content(box) == "в поле"


def test_should_keep_translation_and_enable_save_when_write_fails(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-044, A0104: сбой записи — текст на месте, кнопка доступна, сообщение."""
    blocked = tmp_path / "папка.txt"
    blocked.mkdir()
    errors: list[tuple[str, str]] = []

    def fake_error(title: str, message: str, **kwargs: object) -> str:
        errors.append((title, message))
        return "ok"

    monkeypatch.setattr(
        "ui.layout.filedialog.asksaveasfilename",
        lambda **kwargs: str(blocked),
    )
    monkeypatch.setattr("ui.layout.messagebox.showerror", fake_error)
    _fill_translation(window, "оставить в поле")
    _click_save(window)
    pump_until(window, lambda: bool(errors))
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    assert textbox_content(box) == "оставить в поле"
    save = find_button(window, LABEL_SAVE_TRANSLATION)
    assert save is not None
    assert not is_disabled(save)
    assert errors == [(TITLE_EXPORT_FAILED, MSG_EXPORT_FAILED)]
    assert blocked.is_dir()
