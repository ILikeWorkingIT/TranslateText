"""SplitText: лимит источника и нарезка фрагментов (A0141, A0142)."""

from __future__ import annotations

import pytest

from domain.errors import SourceLimitExceededError
from domain.models import (
    MAX_FRAGMENT_CHARS,
    MAX_SOURCE_CHARS,
    TARGET_FRAGMENT_CHARS_MAX,
)
from services.split_text import SplitText

USER_EN = (
    "I am a beginner in wireframe coding at Cursor. I have a wireframe coding project. "
    "Skills, teams, project structure, app requirements, domain model, and other details "
    "have been developed. The coding process has begun. To understand the current situation "
    "in the project, I am attaching the README, AGENTS, list-commands.md file with the list "
    "of skill calls, the coding checklist, the list of current skills and roles, and any "
    "other relevant information. Additionally, I will provide a sample prompt for the agent "
    "and the text describing the multi-agent scheme (MAS), the vision I have for it."
    "1. What is the current context of the prompt? How does it relate to the intended use of the AI model?\n"
    "2. Are there any ambiguous or potentially misleading parts in the prompt that need clarification?\n"
    "3. What specific tasks or goals do you have in mind when using this AI model for the given prompt?"
    "Only after receiving my responses to your questions, develop a prompt for creating a "
    "multi-agent system in the files \"prompt-MAS.md\" and \"mas-description.md\", detailing "
    "the features of a multi-agent system. The prompt and files should be universal so that "
    "I can use them in other projects. I use a consistent structure of folders and files "
    "across all my projects, including the same skill and command names. However, they use "
    "different stacks; for example, some projects involve API development and the use of NoSQL data"
)


def _sources(text: str) -> list[str]:
    return [fragment.source for fragment in SplitText().split(text)]


def test_should_return_one_fragment_when_text_is_at_most_700_chars() -> None:
    """A0141: до 700 символов — один фрагмент."""
    text = "a" * 700
    fragments = SplitText().split(text)
    assert len(fragments) == 1
    assert fragments[0].source == text


def test_should_split_into_two_fragments_when_text_exceeds_700_with_paragraphs() -> None:
    """A0141, A0142, FT-018: >700 с абзацами — несколько фрагментов ≤700."""
    part = "a" * 400
    text = f"{part}\n\n{part}"
    fragments = SplitText().split(text)
    assert len(fragments) == 2
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert "".join(fragment.source for fragment in fragments) == text
    assert fragments[0].source.endswith("\n\n")
    assert fragments[1].source == part


def test_should_split_long_paragraph_into_700_char_chunks() -> None:
    """A0141: длинный абзац режется на куски ≤700."""
    words = ["word"] * 200
    text = " ".join(words)
    fragments = SplitText().split(text)
    assert len(fragments) >= 2
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert "".join(fragment.source for fragment in fragments) == text


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
    assert "".join(fragment.source for fragment in fragments) == text
    assert fragments[0].source.endswith("\n")
    assert fragments[1].source == part


def test_should_split_on_blank_line_when_text_uses_crlf() -> None:
    """FT-018: Windows \\r\\n\\r\\n между абзацами."""
    part = "a" * 400
    text = f"{part}\r\n\r\n{part}"
    fragments = SplitText().split(text)
    assert len(fragments) == 2
    assert fragments[0].source.endswith("\n\n")
    assert fragments[1].source == part


def test_should_split_100000_chars_into_many_fragments() -> None:
    """FT-023, A0141: 100k — допустимо, но много фрагментов ≤700."""
    text = "y" * MAX_SOURCE_CHARS
    fragments = SplitText().split(text)
    assert len(fragments) > 1
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert "".join(fragment.source for fragment in fragments) == text


def test_should_raise_source_limit_when_text_exceeds_100000_chars() -> None:
    """FT-023, A0036: > 100 000 — SourceLimitExceededError."""
    text = "x" * (MAX_SOURCE_CHARS + 1)
    with pytest.raises(SourceLimitExceededError):
        SplitText().split(text)


def test_should_split_long_paragraph_on_sentence_boundaries_not_spaces() -> None:
    """A0142: длинный текст с точками — резка по предложениям, не по пробелам."""
    sentence = "Это предложение номер один. "
    text = sentence * 40
    fragments = SplitText().split(text)
    assert len(fragments) >= 2
    for fragment in fragments[:-1]:
        assert fragment.source.rstrip().endswith(".")
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert "".join(fragment.source for fragment in fragments) == text


def test_should_keep_filename_extension_inside_sentence_when_splitting() -> None:
    """A0142: «list-commands.md file» — не граница предложения."""
    prefix = "Start. " + ("word " * 80)
    text = prefix + "See list-commands.md file with the list of calls. Next sentence here."
    sources = _sources(text)
    joined = "".join(sources)
    assert joined == text
    assert any("list-commands.md file" in source for source in sources)
    assert not any(source.lstrip().startswith("file with the list") for source in sources)


def test_should_split_after_period_when_numbered_list_follows_without_space() -> None:
    """A0142: «it.1. What» — граница после it., нумерация 1. не рвёт пункт."""
    lead = ("word " * 130).strip() + ". "
    text = (
        f"{lead}The vision I have for it."
        "1. What is the current context of the prompt? "
        "2. Are there any ambiguous parts?"
    )
    sources = _sources(text)
    assert "".join(sources) == text
    assert any(source.rstrip().endswith("it.") for source in sources)
    assert any(source.lstrip().startswith("1. What is the current context") for source in sources)
    assert not any(source.strip() == "1." for source in sources)


def test_should_split_after_question_when_next_sentence_has_no_space() -> None:
    """A0142: «prompt?Only after» — граница после вопроса."""
    lead = ("word " * 124).strip() + ". "
    text = (
        f"{lead}What specific tasks do you have for the given prompt?"
        "Only after receiving my responses, develop the files."
    )
    sources = _sources(text)
    assert "".join(sources) == text
    assert any(source.rstrip().endswith("prompt?") for source in sources)
    assert any(source.lstrip().startswith("Only after") for source in sources)


def test_should_attach_paragraph_break_to_previous_sentence() -> None:
    """A0142: конец абзаца остаётся у последнего предложения перед ним."""
    first = "Первое предложение. " * 20
    second = "Второе предложение после абзаца."
    text = f"{first.rstrip()}\n\n{second}"
    fragments = SplitText().split(text)
    assert "".join(fragment.source for fragment in fragments) == text
    assert any("\n\n" in fragment.source for fragment in fragments)
    for fragment in fragments:
        assert not fragment.source.startswith("\n")
    if len(fragments) >= 2:
        assert fragments[0].source.endswith("\n\n")


def test_should_keep_numbered_item_as_one_sentence() -> None:
    """A0142: пункт «1. What is…?» целиком, не обрыв после «1.»."""
    item = "1. What is the current context of the prompt?"
    text = ("Intro sentence. " * 30) + item
    sources = _sources(text)
    assert "".join(sources) == text
    matching = [source for source in sources if "What is the current context" in source]
    assert matching
    for source in matching:
        assert "1. What is the current context of the prompt?" in source


def test_should_start_new_fragment_after_filled_paragraph_break() -> None:
    """A0141, A0142: абзац ≥500 и \\n\\n — следующий абзац с Task не дописывать в тот же фрагмент."""
    intro = ("Это вводное предложение про проект в Cursor. " * 15).strip()
    assert len(intro) >= 500
    task = (
        "Task:\nИзучи контекст текущего промта. "
        "Сформулируй и задай мне несколько вопросов."
    )
    text = f"{intro}\n\n{task}"
    fragments = SplitText().split(text)
    assert "".join(fragment.source for fragment in fragments) == text
    assert len(fragments) >= 2
    assert fragments[0].source.endswith("\n\n")
    assert "Task:" not in fragments[0].source
    assert fragments[1].source.lstrip().startswith("Task:")
    assert "Изучи контекст текущего промта" in fragments[1].source
    """A0142: блок Task режется по предложениям; Task: уходит с первым из них."""
    intro = "Я начинающий вайб-кодер в Cursor. " * 8
    task_line = (
        "Изучи контекст текущего промта. Сформулируй и задай мне несколько вопросов."
    )
    task_block = f"Task:\n{task_line}\nТолько после ответов разработай prompt-MAS.md."
    text = f"{intro.strip()}\n\n{task_block}\n\nFormat:\nВыведи две ссылки."
    fragments = SplitText().split(text)
    sources = [fragment.source for fragment in fragments]
    assert "".join(sources) == text
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    for source in sources:
        if "Изучи контекст текущего промта." in source:
            assert "Изучи контекст текущего промта." in source
            assert not source.rstrip().endswith("Изучи контекст текущего пром")


def test_should_split_user_en_text_on_real_sentences() -> None:
    """A0142: образец EN — не рвать «.md file», «1.» и «?Only»."""
    fragments = SplitText().split(USER_EN)
    sources = [fragment.source for fragment in fragments]
    assert "".join(sources) == USER_EN
    assert len(fragments) >= 2
    assert all(len(fragment.source) <= TARGET_FRAGMENT_CHARS_MAX for fragment in fragments)
    assert not any(source.lstrip().startswith("file with the list") for source in sources)
    assert not any(source.strip() in {"1.", "2.", "3."} for source in sources)
    numbered = [
        source
        for source in sources
        if "What is the current context of the prompt?" in source
        or "Are there any ambiguous" in source
        or "What specific tasks or goals" in source
    ]
    assert numbered, "пункты списка попали во фрагменты"
    for source in numbered:
        stripped = source.lstrip()
        if stripped.startswith(("1.", "2.", "3.")):
            assert "?" in source
    only_after = [source for source in sources if "Only after receiving" in source]
    assert only_after
    for source in only_after:
        assert not source.lstrip().startswith("fter receiving")


def test_should_never_exceed_hard_cap_5000_chars_per_fragment() -> None:
    """A0009: ни один фрагмент не длиннее 5000."""
    part = "z" * 6000
    fragments = SplitText().split(part)
    assert all(len(fragment.source) <= MAX_FRAGMENT_CHARS for fragment in fragments)
    assert "".join(fragment.source for fragment in fragments) == part


def _assert_words_not_split(sources: list[str]) -> None:
    for left, right in zip(sources, sources[1:]):
        if left and right and left[-1].isalnum() and right[0].isalnum():
            raise AssertionError(
                f"слово разорвано: ...{left[-24:]!r} | {right[:24]!r}"
            )


def test_should_split_paragraph_over_5000_on_sentences_without_breaking_words() -> None:
    """FT-025, S-07b: один абзац >5000 — несколько фрагментов, слово не рвать."""
    sentence = "This is a complete sentence about translation quality. "
    text = sentence * 100
    assert "\n\n" not in text
    assert len(text) > MAX_FRAGMENT_CHARS
    fragments = SplitText().split(text)
    sources = [fragment.source for fragment in fragments]
    assert len(fragments) >= 2
    assert all(len(fragment.source) <= MAX_FRAGMENT_CHARS for fragment in fragments)
    assert "".join(sources) == text
    _assert_words_not_split(sources)


def test_should_keep_word_intact_when_sentence_exceeds_5000() -> None:
    """FT-025: предложение >5000, слово длиннее 700 и короче 5000 — целиком."""
    long_word = "W" * 800
    text = ("word " * 900) + long_word + " end."
    assert len(text) > MAX_FRAGMENT_CHARS
    fragments = SplitText().split(text)
    sources = [fragment.source for fragment in fragments]
    assert any(long_word in source for source in sources)
    assert all(len(fragment.source) <= MAX_FRAGMENT_CHARS for fragment in fragments)
    assert "".join(sources) == text
    _assert_words_not_split(sources)
