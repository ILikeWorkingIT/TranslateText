"""Извлечение текста исходного файла (UC-002, FT-003, FT-039). Без виджетов."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from pypdf import PdfReader

from domain.errors import DocumentParseError
from domain.models import SourceFormat

_TEXT_FORMATS = frozenset({"txt", "md"})
_ALLOWED_FORMATS = frozenset({"txt", "md", "docx", "pdf"})


def _decode_text_bytes(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return data.decode("cp1251")
        except UnicodeDecodeError as exc:
            raise DocumentParseError("cannot decode source") from exc


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _extract_text_file(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise DocumentParseError(str(exc)) from exc
    return _decode_text_bytes(data)


def _extract_docx(path: Path) -> str:
    try:
        document = Document(str(path))
    except Exception as exc:
        raise DocumentParseError(str(exc)) from exc
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            extracted = page.extract_text()
            pages.append(extracted if extracted else "")
    except DocumentParseError:
        raise
    except Exception as exc:
        raise DocumentParseError(str(exc)) from exc
    return "\n".join(pages)


class ExtractSource:
    """Читает `.txt`, `.md`, `.docx`, `.pdf`. Пустой/битый файл — DocumentParseError."""

    def run(self, path: str, source_format: SourceFormat) -> str:
        if source_format not in _ALLOWED_FORMATS:
            raise DocumentParseError("unsupported format")
        file_path = Path(path)
        if source_format in _TEXT_FORMATS:
            text = _extract_text_file(file_path)
        elif source_format == "docx":
            text = _extract_docx(file_path)
        else:
            text = _extract_pdf(file_path)
        text = _normalize_newlines(text)
        if len(text.strip()) == 0:
            raise DocumentParseError("empty source")
        return text
