from __future__ import annotations

from domain.errors import SourceLimitExceededError
from domain.models import (
    Fragment,
    MAX_FRAGMENT_CHARS,
    MAX_SOURCE_CHARS,
    TARGET_FRAGMENT_CHARS_MAX,
    TARGET_FRAGMENT_CHARS_MIN,
)

_SENTENCE_PUNCT = ".?!"
_CLOSING_QUOTES = "\"'»”’)"


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _is_decimal_dot(text: str, index: int) -> bool:
    return (
        text[index] == "."
        and index > 0
        and text[index - 1].isdigit()
        and index + 1 < len(text)
        and text[index + 1].isdigit()
    )


def _is_list_marker_dot(text: str, index: int) -> bool:
    """«1. Title» / «it.1. Title» — точка нумерации, не конец предложения."""
    if text[index] != ".":
        return False
    i = index - 1
    if i < 0 or not text[i].isdigit():
        return False
    while i >= 0 and text[i].isdigit():
        i -= 1
    if i >= 0 and not (text[i].isspace() or text[i] in _SENTENCE_PUNCT):
        return False
    nxt = index + 1
    if nxt >= len(text):
        return True
    return text[nxt].isspace() or text[nxt].isalpha()


def _after_closing_quotes(text: str, start: int) -> int:
    i = start
    while i < len(text) and text[i] in _CLOSING_QUOTES:
        i += 1
    return i


def _next_content(text: str, start: int) -> str:
    i = start
    while i < len(text) and text[i] in " \t":
        i += 1
    if i >= len(text):
        return ""
    return text[i]


def _is_sentence_boundary(text: str, index: int) -> bool:
    """Точка / ! / ? закрывает предложение; «.md file» и «1. What» — нет."""
    ch = text[index]
    if ch not in _SENTENCE_PUNCT:
        return False
    if index + 1 < len(text) and text[index + 1] in _SENTENCE_PUNCT:
        return False
    if ch == ".":
        if _is_decimal_dot(text, index):
            return False
        if _is_list_marker_dot(text, index):
            return False
    after = _after_closing_quotes(text, index + 1)
    if after >= len(text):
        return True
    nxt = text[after]
    if nxt in "\n":
        return True
    if nxt in " \t":
        following = _next_content(text, after)
        if following == "" or following == "\n":
            return True
        if ch in "?!":
            return True
        return following.isupper() or following.isdigit()
    if nxt.isalnum():
        if ch in "?!":
            return True
        return nxt.isupper() or nxt.isdigit()
    return False


def _attach_trailing_whitespace(text: str, end: int) -> int:
    """Конец абзаца / перевод строки остаётся у предложения, после которого стоит."""
    i = end
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def _sentence_units(text: str) -> list[str]:
    units: list[str] = []
    start = 0
    i = 0
    length = len(text)
    while i < length:
        if _is_sentence_boundary(text, i):
            end = _attach_trailing_whitespace(text, i + 1)
            units.append(text[start:end])
            start = end
            i = end
            continue
        i += 1
    if start < length:
        units.append(text[start:])
    return units


def _split_keeping_sep(text: str, sep: str) -> list[str]:
    parts = text.split(sep)
    units: list[str] = []
    last = len(parts) - 1
    for index, part in enumerate(parts):
        piece = part if index == last else f"{part}{sep}"
        if piece == "":
            continue
        if units and part == "":
            units[-1] += piece
        else:
            units.append(piece)
    return units


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
        cut = len(window) - 1
        while cut >= 0 and not window[cut].isspace():
            cut -= 1
        if cut >= 0:
            chunk = remaining[: cut + 1]
            remaining = remaining[cut + 1 :]
            chunks.append(chunk)
            continue
        token_end = 0
        while token_end < len(remaining) and not remaining[token_end].isspace():
            token_end += 1
        has_space_after = token_end < len(remaining)
        if has_space_after and token_end <= MAX_FRAGMENT_CHARS:
            space_end = token_end
            while space_end < len(remaining) and remaining[space_end].isspace():
                space_end += 1
            take = space_end if space_end <= MAX_FRAGMENT_CHARS else token_end
            chunk = remaining[:take]
            remaining = remaining[take:]
        elif has_space_after:
            chunk = remaining[:MAX_FRAGMENT_CHARS]
            remaining = remaining[MAX_FRAGMENT_CHARS:]
        else:
            chunk = remaining[:max_chars]
            remaining = remaining[max_chars:]
        chunks.append(chunk)
    return chunks


def _ends_with_sentence_punct(part: str) -> bool:
    stripped = part.rstrip()
    return bool(stripped) and stripped[-1] in _SENTENCE_PUNCT


def _split_oversize(part: str, max_chars: int) -> list[str]:
    if len(part) <= max_chars:
        return [part]
    if _ends_with_sentence_punct(part):
        return _split_by_spaces(part, max_chars)
    for sep in ("\n\n", "\n"):
        if sep not in part:
            continue
        pieces = _split_keeping_sep(part, sep)
        if len(pieces) <= 1:
            continue
        packed: list[str] = []
        for piece in pieces:
            packed.extend(_split_oversize(piece, max_chars))
        return packed
    return _split_by_spaces(part, max_chars)


def _fit_unit(unit: str, max_chars: int) -> list[str]:
    if len(unit) <= max_chars:
        return [unit]
    return _split_oversize(unit, max_chars)


def _pack(units: list[str], max_chars: int) -> list[str]:
    packed: list[str] = []
    current = ""
    for unit in units:
        for piece in _fit_unit(unit, max_chars):
            if not current:
                current = piece
                continue
            if (
                current.endswith("\n\n")
                and len(current) >= TARGET_FRAGMENT_CHARS_MIN
            ):
                packed.append(current)
                current = piece
                continue
            if len(current) + len(piece) <= max_chars:
                current += piece
                continue
            packed.append(current)
            current = piece
    if current:
        packed.append(current)
    return packed


class SplitText:
    """Нарезка по предложениям, целевой объём 500–700 символов (A0141, A0142)."""

    def split(self, text: str) -> tuple[Fragment, ...]:
        text = _normalize(text)
        length = len(text)
        if length > MAX_SOURCE_CHARS:
            raise SourceLimitExceededError(
                f"source length {length} exceeds {MAX_SOURCE_CHARS}"
            )
        if length == 0:
            return ()
        if length <= TARGET_FRAGMENT_CHARS_MAX:
            return (Fragment(order=0, source=text),)

        packed = _pack(_sentence_units(text), TARGET_FRAGMENT_CHARS_MAX)
        if not packed:
            return (Fragment(order=0, source=text),)
        return tuple(
            Fragment(order=index, source=chunk) for index, chunk in enumerate(packed)
        )
