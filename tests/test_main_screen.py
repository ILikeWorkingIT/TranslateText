"""Стартовый экран: подписи глоссария и поля Must UI, которые уже есть в макете."""

from ui.messages import (
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_MODEL,
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
)

from ui_helpers import (
    find_by_text,
    find_progress_bar,
    find_textbox_for_label,
    textbox_content,
)

GLOSSARY_LABELS = (
    LABEL_OPEN_FILE,
    LABEL_SAVE_TRANSLATION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATION,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_MODEL,
    LABEL_TRANSLATE,
)

GLOSSARY_BASE_PROMPT = (
    "Ты профессиональный переводчик. Переведи текст с английского на русский. "
    "Сохрани смысл, тон и разбиение на абзацы. Не добавляй комментарии, преамбулу "
    "и кавычки вокруг перевода. В ответе только перевод."
)


def test_should_show_all_glossary_labels_when_window_opens(window):
    """NFT-006, happy: на главном экране все 7 подписей глоссария."""
    missing = [label for label in GLOSSARY_LABELS if find_by_text(window, label) is None]
    assert missing == [], "на главном экране есть все подписи глоссария"


def test_should_show_original_text_field_when_window_opens(window):
    """FT-001, happy: поле «Оригинальный текст» доступно."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"


def test_should_show_translation_field_when_window_opens(window):
    """FT-002, happy: поле «Русский перевод» доступно."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"


def test_should_show_custom_instruction_field_when_window_opens(window):
    """FT-007, happy: поле «Кастомная инструкция» доступно."""
    box = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert box is not None, "есть поле Кастомная инструкция"


def test_should_show_base_prompt_when_user_has_not_replaced_instruction(window):
    """FT-008, happy: в кастомной инструкции базовый промпт переводчика."""
    box = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert box is not None, "есть поле Кастомная инструкция"
    assert textbox_content(box) == GLOSSARY_BASE_PROMPT, (
        "в Кастомной инструкции показан базовый промпт переводчика"
    )


def test_should_show_model_list_when_window_opens(window):
    """FT-005, happy: на экране есть список «Модель»."""
    assert window.model is not None, "есть список Модель"
    values = window.model.cget("values")
    assert values is not None, "список Модель содержит значения"


def test_should_show_progress_indicator_at_zero_when_window_opens(window):
    """FT-022, empty: индикатор прогресса на экране и показывает 0 % до перевода."""
    bar = find_progress_bar(window)
    assert bar is not None, "есть индикатор прогресса"
    assert bar.get() == 0, "индикатор прогресса показывает 0 % до перевода"
