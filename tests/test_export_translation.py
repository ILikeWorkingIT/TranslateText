"""S-10: ExportTranslation без GUI (FT-004, FT-044, FT-046)."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest
from docx import Document

from domain.errors import ExportWriteError
from domain.models import ExportFormat, ExportTranslationCommand
from services.export_translation import ExportTranslation
from ui.bridge import ExportBridge
from use_cases.unsaved_translation import (
    is_unsaved_translation,
    saved_after_export_success,
)


class FakeHost:
    def __init__(self) -> None:
        self.ui_calls = 0

    def call_on_ui(self, func: Callable[[], None]) -> None:
        self.ui_calls += 1
        func()

    def winfo_exists(self) -> bool:
        return True


def _wait_until(predicate: Callable[[], bool]) -> None:
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("export bridge did not finish")


def _command(
    tmp_path: Path,
    *,
    text: str = "Готовый перевод",
    name: str = "out.txt",
    export_format: ExportFormat = "txt",
    request_id: int = 1,
) -> ExportTranslationCommand:
    return ExportTranslationCommand(
        request_id=request_id,
        translation_text=text,
        path=str(tmp_path / name),
        export_format=export_format,
    )


def _docx_text(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def test_should_write_field_contents_to_txt_when_export_runs(tmp_path: Path) -> None:
    """FT-004, US-003 AC1: в файл попадает содержимое поля перевода."""
    command = _command(tmp_path, text="Привет, мир\nвторая строка")
    ExportTranslation().run(command)
    written = Path(command.path)
    assert written.read_text(encoding="utf-8") == "Привет, мир\nвторая строка"


def test_should_write_field_contents_to_docx_when_export_runs(tmp_path: Path) -> None:
    """FT-004, FT-046: запись .docx совпадает с полем, включая абзацы."""
    command = _command(
        tmp_path,
        text="Первый\n\nВторой",
        name="out.docx",
        export_format="docx",
    )
    ExportTranslation().run(command)
    assert _docx_text(Path(command.path)) == "Первый\n\nВторой"


def test_should_overwrite_existing_file_when_export_is_invoked(tmp_path: Path) -> None:
    """FT-043: после согласия диалога ОС служба перезаписывает файл."""
    target = tmp_path / "exists.txt"
    target.write_text("старое", encoding="utf-8")
    command = _command(tmp_path, text="новое", name="exists.txt")
    ExportTranslation().run(command)
    assert target.read_text(encoding="utf-8") == "новое"


def test_should_raise_write_error_when_translation_is_empty(tmp_path: Path) -> None:
    """FT-027: пустой перевод в службу не пишем."""
    command = _command(tmp_path, text="")
    with pytest.raises(ExportWriteError):
        ExportTranslation().run(command)
    assert not (tmp_path / "out.txt").exists()


def test_should_raise_write_error_when_format_is_not_txt_or_docx(tmp_path: Path) -> None:
    """FT-046: иные форматы не записываются."""
    target = tmp_path / "out.pdf"
    command = ExportTranslationCommand(
        request_id=1,
        translation_text="текст",
        path=str(target),
        export_format="txt",
    )
    with pytest.raises(ExportWriteError):
        ExportTranslation().run(command)
    assert not target.exists()


def test_should_raise_write_error_when_path_cannot_be_written(tmp_path: Path) -> None:
    """FT-044: сбой записи → ExportWriteError, файл-каталог не становится текстом."""
    blocked = tmp_path / "dir.txt"
    blocked.mkdir()
    command = _command(tmp_path, name="dir.txt")
    with pytest.raises(ExportWriteError):
        ExportTranslation().run(command)


def test_should_keep_unsaved_when_export_raises(tmp_path: Path) -> None:
    """FT-044, FT-033: сбой не снимает несохранённость (флаг меняет только успех)."""
    blocked = tmp_path / "dir.txt"
    blocked.mkdir()
    with pytest.raises(ExportWriteError):
        ExportTranslation().run(_command(tmp_path, name="dir.txt"))
    assert is_unsaved_translation("текст", False) is True
    assert saved_after_export_success() is True


def test_should_notify_success_when_export_bridge_writes(tmp_path: Path) -> None:
    """Клей: успешная запись доходит до UI-колбэка."""
    host = FakeHost()
    successes: list[tuple[int, str]] = []
    errors: list[int] = []
    bridge = ExportBridge(
        host=host,
        on_success=lambda rid, text: successes.append((rid, text)),
        on_error=lambda rid: errors.append(rid),
    )
    target = tmp_path / "bridge.txt"
    bridge.start(
        translation_text="из моста",
        path=str(target),
        export_format="txt",
    )
    _wait_until(lambda: bool(successes) or bool(errors))
    assert successes == [(1, "из моста")]
    assert errors == []
    assert target.read_text(encoding="utf-8") == "из моста"


def test_should_notify_error_when_export_bridge_write_fails(tmp_path: Path) -> None:
    """Клей: сбой записи — on_error, без on_success."""
    host = FakeHost()
    successes: list[tuple[int, str]] = []
    errors: list[int] = []
    bridge = ExportBridge(
        host=host,
        on_success=lambda rid, text: successes.append((rid, text)),
        on_error=lambda rid: errors.append(rid),
    )
    blocked = tmp_path / "nope.txt"
    blocked.mkdir()
    bridge.start(
        translation_text="не запишется",
        path=str(blocked),
        export_format="txt",
    )
    _wait_until(lambda: bool(successes) or bool(errors))
    assert successes == []
    assert errors == [1]
