"""Смена направления перевода: FT-051, FT-052, FT-053."""

from ui.messages import (
    BASE_PROMPT,
    BASE_PROMPT_RU_EN,
    DIRECTION_EN_RU,
    DIRECTION_RU_EN,
    DIRECTION_VALUES,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_TRANSLATION,
    LABEL_TRANSLATION_EN,
)
from ui_helpers import (
    combo_values,
    find_by_text,
    find_textbox_for_label,
    set_textbox_content,
    textbox_content,
    widget_text,
)


def _select_direction(window, value: str) -> None:
    window.direction.set(value)
    window._on_direction(value)
    window.update_idletasks()


def test_should_select_en_ru_when_window_opens(window):
    """FT-051, A0120, happy: при старте направление EN→RU."""
    assert window.direction is not None, "есть элемент Направление перевода"
    assert str(window.direction.get()) == DIRECTION_EN_RU, (
        "при старте выбрано направление EN→RU"
    )


def test_should_offer_only_en_ru_and_ru_en_when_window_opens(window):
    """FT-051, A0120, happy: в списке направления только EN→RU и RU→EN."""
    assert combo_values(window.direction) == DIRECTION_VALUES, (
        "в списке направления только EN→RU и RU→EN"
    )


def test_should_show_ru_en_base_prompt_when_direction_changes_and_instruction_is_base(
    window,
):
    """FT-052, A0123, happy: базовый промпт прежнего направления заменяется на новый."""
    instruction = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    assert textbox_content(instruction) == BASE_PROMPT, (
        "перед сменой в поле базовый промпт EN→RU"
    )
    _select_direction(window, DIRECTION_RU_EN)
    assert textbox_content(instruction) == BASE_PROMPT_RU_EN, (
        "после смены на RU→EN в поле базовый промпт RU→EN"
    )


def test_should_keep_custom_instruction_when_direction_changes(window):
    """FT-052, A0123, edge: своя инструкция при смене направления не затирается."""
    instruction = find_textbox_for_label(window, LABEL_CUSTOM_INSTRUCTION)
    assert instruction is not None, "есть поле Кастомная инструкция"
    set_textbox_content(instruction, "Пиши короче.")
    window.update_idletasks()
    _select_direction(window, DIRECTION_RU_EN)
    assert textbox_content(instruction) == "Пиши короче.", (
        "своя Кастомная инструкция после смены направления сохраняется"
    )


def test_should_show_english_translation_label_when_direction_is_ru_en(window):
    """FT-002, FT-053, A0121, happy: подпись поля перевода — «Английский перевод»."""
    _select_direction(window, DIRECTION_RU_EN)
    assert find_by_text(window, LABEL_TRANSLATION_EN) is not None, (
        "видна подпись Английский перевод"
    )
    assert find_by_text(window, LABEL_TRANSLATION) is None, (
        "подпись Русский перевод скрыта при RU→EN"
    )


def test_should_keep_translation_text_when_direction_changes(window):
    """FT-053, A0124, happy: текст поля перевода при смене направления не очищается."""
    translation = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert translation is not None, "есть поле перевода"
    set_textbox_content(translation, "Уже есть перевод.")
    window.update_idletasks()
    _select_direction(window, DIRECTION_RU_EN)
    box = find_textbox_for_label(window, LABEL_TRANSLATION_EN)
    assert box is not None, "поле перевода доступно по новой подписи"
    assert textbox_content(box) == "Уже есть перевод.", (
        "текст поля перевода после смены направления на месте"
    )


def test_should_not_show_ollama_status_when_only_direction_changes(window):
    """FT-053, A0124, negative: смена направления не показывает предупреждение FT-032."""
    translation = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert translation is not None, "есть поле перевода"
    set_textbox_content(translation, "Несохранённый кусок.")
    window.update_idletasks()
    _select_direction(window, DIRECTION_RU_EN)
    assert widget_text(window.status) == "", (
        "строка статуса пуста: смена направления не показывает предупреждение"
    )
