"""Извлечение текста исходного файла (UC-002, FT-003). Без виджетов."""

from __future__ import annotations

from pathlib import Path

from domain.errors import DocumentParseError
from domain.models import SourceFormat

_TEXT_FORMATS = frozenset({"txt", "md"})


def _decode_text_bytes(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return data.decode("cp1251")
        except UnicodeDecodeError as exc:
            raise DocumentParseError("cannot decode source") from exc


class ExtractSource:
    """Читает `.txt` / `.md`. `.docx` / `.pdf` — срез S-12."""

    def run(self, path: str, source_format: SourceFormat) -> str:
        if source_format not in _TEXT_FORMATS:
            raise DocumentParseError("unsupported format")
        try:
            data = Path(path).read_bytes()
        except OSError as exc:
            raise DocumentParseError(str(exc)) from exc
        text = _decode_text_bytes(data).replace("\r\n", "\n").replace("\r", "\n")
        if len(text.strip()) == 0:
            raise DocumentParseError("empty source")
        return text
