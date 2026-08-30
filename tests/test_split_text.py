"""SplitText: лимит источника и нарезка фрагментов (A0141: 500–700 символов)."""

from __future__ import annotations

import pytest

from domain.errors import SourceLimitExceededError
from domain.models import (
    MAX_FRAGMENT_CHARS,
    MAX_SOURCE_CHARS,
    TARGET_FRAGMENT_CHARS_MAX,
)
from services.split_text import SplitText


def test_should_return_one_fragment_when_text_is_at_most_700_chars() -> None:
    """A0141: до 700 символов — один фрагмент."""
    text = "a" * 700
    fragments = SplitText().split(text)
    assert len(fragments) == 1
    assert fragments[0].source == text


def test_should_split_into_two_fragments_when_text_exceeds_700_with_paragraphs() -> None:
    """A0141, FT-018: >700 с абзацами — несколько фрагментов ≤700."""
    part = "a" * 400
    text = f"{part}\n\n{part}"
    fragments = SplitText().split(text)
    assert len(fragments) == 2
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert fragments[0].source == part
    assert fragments[1].source == part


def test_should_split_long_paragraph_into_700_char_chunks() -> None:
    """A0141: длинный абзац режется на куски ≤700."""
    words = ["word"] * 200
    text = " ".join(words)
    fragments = SplitText().split(text)
    assert len(fragments) >= 2
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)


def test_should_preserve_short_paragraphs_in_one_fragment_when_total_under_700() -> None:
    """FT-018, edge: короткие абзацы — один фрагмент."""
    text = "First.\n\nSecond.\n\nThird."
    fragments = SplitText().split(text)
    assert len(fragments) == 1
    assert fragments[0].source == text


def test_should_split_on_single_newline_when_no_blank_line() -> None:
    """FT-018: при отсутствии \\n\\n режем по одиночному \\n."""
    part = "a" * 400
    text = f"{part}\n{part}"
    fragments = SplitText().split(text)
    assert len(fragments) == 2
    assert fragments[0].source == part


def test_should_split_on_blank_line_when_text_uses_crlf() -> None:
    """FT-018: Windows \\r\\n\\r\\n между абзацами."""
    part = "a" * 400
    text = f"{part}\r\n\r\n{part}"
    fragments = SplitText().split(text)
    assert len(fragments) == 2
    assert fragments[0].source == part


def test_should_split_100000_chars_into_many_fragments() -> None:
    """FT-023, A0141: 100k — допустимо, но много фрагментов ≤700."""
    text = "y" * MAX_SOURCE_CHARS
    fragments = SplitText().split(text)
    assert len(fragments) > 1
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert sum(len(fragment.source) for fragment in fragments) == MAX_SOURCE_CHARS


def test_should_raise_source_limit_when_text_exceeds_100000_chars() -> None:
    """FT-023, A0036: > 100 000 — SourceLimitExceededError."""
    text = "x" * (MAX_SOURCE_CHARS + 1)
    with pytest.raises(SourceLimitExceededError):
        SplitText().split(text)


def test_should_split_long_paragraph_on_sentence_boundaries_not_spaces() -> None:
    """A0141: длинный текст с точками — резка по предложениям, не по пробелам."""
    sentence = "Это предложение номер один. "
    text = sentence * 40
    fragments = SplitText().split(text)
    assert len(fragments) >= 2
    for fragment in fragments[:-1]:
        assert fragment.source.rstrip().endswith(".")
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)


def test_should_split_task_block_on_lines_not_mid_sentence() -> None:
    """A0141: блок Task с одинарными \\n — резка по строкам, не по предложению внутри фразы."""
    intro = "Я начинающий вайб-кодер в Cursor. " * 8
    task_line = (
        "Изучи контекст текущего промта. Сформулируй и задай мне несколько вопросов."
    )
    task_block = f"Task:\n{task_line}\nТолько после ответов разработай prompt-MAS.md."
    text = f"{intro.strip()}\n\n{task_block}\n\nFormat:\nВыведи две ссылки."
    fragments = SplitText().split(text)
    sources = [fragment.source for fragment in fragments]
    task_fragments = [source for source in sources if "Task:" in source or task_line in source]
    assert task_fragments, "блок Task попал во фрагменты"
    for chunk in task_fragments:
        if task_line in chunk:
            assert chunk.count(task_line) == 1, "строка Task не разорвана посередине"
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)


def test_should_never_exceed_hard_cap_5000_chars_per_fragment() -> None:
    """A0009: ни один фрагмент не длиннее 5000."""
    part = "z" * 6000
    fragments = SplitText().split(part)
    assert all(len(fragment.source) <= MAX_FRAGMENT_CHARS for fragment in fragments)
