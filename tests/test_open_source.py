"""S-11: «Открыть файл» `.txt` / `.md` (UC-002, FT-003, FT-047)."""

from __future__ import annotations

from pathlib import Path

from ui.messages import (
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_TRANSLATION,
    MSG_SOURCE_NOT_EXTRACTED,
    OPEN_FILETYPES,
    TITLE_SOURCE_NOT_EXTRACTED,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    pump_until,
    set_textbox_content,
    textbox_content,
)


def _fill_original(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _fill_translation(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _click_open(window) -> None:
    button = find_button(window, LABEL_OPEN_FILE)
    assert button is not None
    button.invoke()
    window.update_idletasks()


def _open_path(monkeypatch, window, path: Path) -> None:
    monkeypatch.setattr(
        "ui.layout.filedialog.askopenfilename",
        lambda **kwargs: str(path),
    )
    _click_open(window)


def test_should_put_txt_contents_in_original_when_user_opens_file(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-003: выбранный `.txt` появляется в «Оригинальный текст»."""
    target = tmp_path / "book.txt"
    target.write_text("Глава первая", encoding="utf-8")
    _open_path(monkeypatch, window, target)
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    pump_until(window, lambda: textbox_content(box) == "Глава первая")


def test_should_put_md_contents_in_original_when_user_opens_file(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """FT-003: выбранный `.md` появляется в «Оригинальный текст»."""
    target = tmp_path / "note.md"
    target.write_text("# Note\n\nbody", encoding="utf-8")
    _open_path(monkeypatch, window, target)
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    pump_until(window, lambda: textbox_content(box) == "# Note\n\nbody")


def test_should_offer_only_txt_and_md_when_open_dialog_opens(monkeypatch, window):
    """S-11: диалог предлагает только `.txt` и `.md` (полный FT-042 — S-12)."""
    captured: dict[str, object] = {}

    def fake_dialog(**kwargs: object) -> str:
        captured.update(kwargs)
        return ""

    monkeypatch.setattr("ui.layout.filedialog.askopenfilename", fake_dialog)
    _click_open(window)
    assert captured.get("filetypes") == list(OPEN_FILETYPES)
    joined = " ".join(f"{name} {pattern}" for name, pattern in OPEN_FILETYPES)
    assert ".txt" in joined and ".md" in joined
    assert ".docx" not in joined and ".pdf" not in joined


def test_should_keep_original_when_user_cancels_open_dialog(
    monkeypatch,
    window,
):
    """FT-047: отмена диалога не меняет левое поле."""
    monkeypatch.setattr(
        "ui.layout.filedialog.askopenfilename",
        lambda **kwargs: "",
    )
    _fill_original(window, "Был оригинал")
    _click_open(window)
    window.update_idletasks()
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    assert textbox_content(box) == "Был оригинал"


def test_should_keep_original_and_show_message_when_txt_is_empty(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """S-11: пустой `.txt` — сообщение, поле не подменять молча."""
    target = tmp_path / "empty.txt"
    target.write_text("", encoding="utf-8")
    errors: list[tuple[str, str]] = []

    def fake_error(title: str, message: str, **kwargs: object) -> str:
        errors.append((title, message))
        return "ok"

    monkeypatch.setattr("ui.layout.messagebox.showerror", fake_error)
    _fill_original(window, "Старый оригинал")
    _open_path(monkeypatch, window, target)
    pump_until(window, lambda: bool(errors))
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    assert textbox_content(box) == "Старый оригинал"
    assert errors == [(TITLE_SOURCE_NOT_EXTRACTED, MSG_SOURCE_NOT_EXTRACTED)]


def test_should_clear_translation_when_open_file_succeeds(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """A0099: успешная загрузка очищает поле перевода."""
    target = tmp_path / "src.txt"
    target.write_text("Новый исходник", encoding="utf-8")
    monkeypatch.setattr(
        "ui.layout.messagebox.askokcancel",
        lambda *_a, **_k: True,
    )
    _fill_original(window, "Старый оригинал")
    _fill_translation(window, "Старый перевод")
    _open_path(monkeypatch, window, target)
    original = find_textbox_for_label(window, LABEL_ORIGINAL)
    translation = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert original is not None and translation is not None
    pump_until(window, lambda: textbox_content(original) == "Новый исходник")
    assert textbox_content(translation) == ""


def test_should_keep_translation_when_open_file_fails(
    monkeypatch,
    window,
    tmp_path: Path,
):
    """UC-002: сбой извлечения не очищает поле перевода."""
    target = tmp_path / "empty.txt"
    target.write_text("   ", encoding="utf-8")
    errors: list[tuple[str, str]] = []

    def fake_error(title: str, message: str, **kwargs: object) -> str:
        errors.append((title, message))
        return "ok"

    monkeypatch.setattr("ui.layout.messagebox.showerror", fake_error)
    monkeypatch.setattr(
        "ui.layout.messagebox.askokcancel",
        lambda *_a, **_k: True,
    )
    _fill_original(window, "Оригинал")
    _fill_translation(window, "Перевод")
    _open_path(monkeypatch, window, target)
    pump_until(window, lambda: bool(errors))
    original = find_textbox_for_label(window, LABEL_ORIGINAL)
    translation = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert original is not None and translation is not None
    assert textbox_content(original) == "Оригинал"
    assert textbox_content(translation) == "Перевод"
