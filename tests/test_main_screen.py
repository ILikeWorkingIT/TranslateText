"""Стартовый экран: подписи глоссария, пустые поля покоя и кастомная инструкция."""

from ui.messages import (
    BASE_PROMPT,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_DIRECTION,
    LABEL_MODEL,
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
)

from conftest import DEFAULT_FAKE_MODELS
from ui_helpers import (
    combo_values,
    find_by_text,
    find_progress_bar,
    find_textbox_for_label,
    set_textbox_content,
    textbox_content,
)

GLOSSARY_LABELS = (
    LABEL_OPEN_FILE,
    LABEL_SAVE_TRANSLATION,
    LABEL_ORIGINAL,
    LABEL_TRANSLATION,
    LABEL_DIRECTION,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_MODEL,
    LABEL_TRANSLATE,
)


def test_should_show_all_glossary_labels_when_window_opens(window):
    """NFT-006, happy: на главном экране все 8 подписей глоссария (A0120, A0121)."""
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
    assert textbox_content(box) == BASE_PROMPT, (
        "в Кастомной инструкции показан базовый промпт переводчика"
    )


def test_should_show_model_list_when_window_opens(window):
    """FT-005, FT-045, happy: при старте список «Модель» совпадает с ответом API."""
    assert window.model is not None, "есть список Модель"
    assert combo_values(window.model) == DEFAULT_FAKE_MODELS, (
        "при старте список Модель показывает все имена ответа локального API"
    )


def test_should_show_progress_indicator_at_zero_when_window_opens(window):
    """FT-022, empty: индикатор прогресса на экране и показывает 0 % до перевода."""
    bar = find_progress_bar(window)
    assert bar is not None, "есть индикатор прогресса"
    assert bar.get() == 0, "индикатор прогресса показывает 0 % до перевода"


def test_should_show_empty_original_when_window_opens(window):
    """FT-001, empty: рабочее состояние покоя — «Оригинальный текст» длины 0."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    assert textbox_content(box) == "", "при старте Оригинальный текст пуст"


def test_should_show_empty_translation_when_window_opens(window):
    """FT-002, empty: рабочее состояние покоя — «Русский перевод» длины 0."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    assert textbox_content(box) == "", "при старте Русский перевод пуст"


def test_should_keep_replaced_instruction_when_user_edits_field(window):
    """FT-008, happy: Пользователь заменяет базовый промпт своим текстом."""
    box = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert box is not None, "есть поле Кастомная инструкция"
    set_textbox_content(box, "Пиши короче.")
    window.update_idletasks()
    assert textbox_content(box) == "Пиши короче.", (
        "в Кастомной инструкции остаётся текст, которым Пользователь заменил базовый промпт"
    )
