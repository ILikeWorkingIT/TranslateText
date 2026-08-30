from __future__ import annotations

from domain.errors import SourceLimitExceededError
from domain.models import (
    Fragment,
    MAX_FRAGMENT_CHARS,
    MAX_SOURCE_CHARS,
    TARGET_FRAGMENT_CHARS_MAX,
)


def _paragraph_sep(text: str) -> str:
    if "\n\n" in text:
        return "\n\n"
    if "\n" in text:
        return "\n"
    return ""


def _paragraphs(text: str) -> list[str]:
    sep = _paragraph_sep(text)
    if sep:
        return text.split(sep)
    return [text]


def _last_sentence_boundary(text: str) -> int:
    """Индекс конца последнего завершённого предложения (граница отрезка, exclusive)."""
    for index in range(len(text) - 1, -1, -1):
        if text[index] not in ".?!":
            continue
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if next_char == "" or next_char in " \n\t":
            return index + 1
    return -1


def _split_by_spaces(part: str, max_chars: int) -> list[str]:
    if len(part) <= max_chars:
        return [part]
    chunks: list[str] = []
    remaining = part
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        window = remaining[:max_chars]
        cut = window.rfind(" ")
        if cut <= 0:
            cut = max_chars
        chunk = remaining[:cut].rstrip()
        if not chunk:
            chunk = remaining[:max_chars]
            remaining = remaining[max_chars:]
        else:
            remaining = remaining[cut:].lstrip()
        chunks.append(chunk)
    return chunks


def _split_by_sentences(part: str, max_chars: int) -> list[str]:
    """Режет длинный текст по концам предложений (. ? !), иначе — по пробелам."""
    if len(part) <= max_chars:
        return [part]
    chunks: list[str] = []
    remaining = part
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        window = remaining[:max_chars]
        cut = _last_sentence_boundary(window)
        if cut <= 0:
            return _split_by_spaces(part, max_chars)
        chunk = remaining[:cut].rstrip()
        if not chunk:
            return _split_by_spaces(part, max_chars)
        remaining = remaining[cut:].lstrip()
        chunks.append(chunk)
    return chunks


def _split_oversized_part(part: str, max_chars: int) -> list[str]:
    """Сначала по строкам (\\n), затем по предложениям — не рвать фразу посередине."""
    if len(part) <= max_chars:
        return [part]
    if "\n" not in part:
        return _split_by_sentences(part, max_chars)
    lines = part.split("\n")
    units: list[str] = []
    current = ""
    for line in lines:
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            units.append(current)
        if len(line) <= max_chars:
            current = line
        else:
            units.extend(_split_by_sentences(line, max_chars))
            current = ""
    if current:
        units.append(current)
    return units


def _units(text: str) -> tuple[list[str], str]:
    sep = _paragraph_sep(text)
    parts = _paragraphs(text) if sep else [text]
    units: list[str] = []
    for part in parts:
        if not part:
            continue
        if len(part) <= TARGET_FRAGMENT_CHARS_MAX:
            units.append(part)
        else:
            units.extend(_split_oversized_part(part, TARGET_FRAGMENT_CHARS_MAX))
    return units, sep


class SplitText:
    """Нарезка по абзацам (FT-018), целевой объём 500–700 символов (A0141)."""

    def split(self, text: str) -> tuple[Fragment, ...]:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        length = len(text)
        if length > MAX_SOURCE_CHARS:
            raise SourceLimitExceededError(
                f"source length {length} exceeds {MAX_SOURCE_CHARS}"
            )
        if length == 0:
            return ()
        if length <= TARGET_FRAGMENT_CHARS_MAX:
            return (Fragment(order=0, source=text),)

        units, sep = _units(text)
        packed: list[str] = []
        current = ""

        for unit in units:
            candidate = f"{current}{sep}{unit}" if current else unit
            if len(candidate) <= TARGET_FRAGMENT_CHARS_MAX:
                current = candidate
                continue
            if current:
                packed.append(current)
            if len(unit) > MAX_FRAGMENT_CHARS:
                packed.append(unit)
                current = ""
            else:
                current = unit

        if current:
            packed.append(current)

        if not packed:
            return (Fragment(order=0, source=text),)

        return tuple(Fragment(order=index, source=chunk) for index, chunk in enumerate(packed))
