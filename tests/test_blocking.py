"""Must-блокировки кнопок и подсказка у «Перевести» — наблюдаемое состояние UI."""

from ui.messages import (
    LABEL_ORIGINAL,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
)

from ui_helpers import (
    collected_texts,
    find_button,
    find_textbox_for_label,
    is_disabled,
    set_textbox_content,
)

HINT_NO_TEXT = "Нет текста для перевода"


def test_should_disable_translate_when_original_is_empty(window):
    """FT-026, US-001, negative: «Перевести» заблокирована при пустом оригинале."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert is_disabled(button), "кнопка Перевести заблокирована, когда оригинал пуст"


def test_should_disable_save_when_translation_is_empty(window):
    """FT-027, US-003, negative: «Сохранить перевод» заблокирована при пустом переводе."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_SAVE_TRANSLATION)
    assert button is not None, "есть кнопка Сохранить перевод"
    assert is_disabled(button), "кнопка Сохранить перевод заблокирована, когда перевод пуст"


def test_should_keep_autosave_enabled_when_translation_is_empty(window):
    """FT-027, US-003, edge: пустой перевод не блокирует «Автосохранение»."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    set_textbox_content(box, "")
    window.update_idletasks()
    assert not is_disabled(window.autosave), (
        "галочка Автосохранение не блокируется из-за пустого перевода"
    )


def test_should_disable_translate_when_model_list_is_empty(window):
    """FT-048, US-001, negative: «Перевести» заблокирована при пустом списке моделей."""
    window.model.configure(values=[])
    window.model.set("")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert is_disabled(button), "кнопка Перевести заблокирована, когда список моделей пуст"


def test_should_keep_model_list_enabled_when_model_list_is_empty(window):
    """FT-049, US-007, happy: список «Модель» доступен, даже если моделей нет."""
    window.model.configure(values=[])
    window.model.set("")
    window.update_idletasks()
    assert not is_disabled(window.model), (
        "список Модель доступен для клика и фокуса при пустом списке"
    )


def test_should_show_no_text_hint_when_pointer_hovers_blocked_translate(window):
    """FT-050, US-008, disabled: подсказка «Нет текста для перевода» у заблокированной кнопки."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    button.event_generate("<Enter>")
    window.update_idletasks()
    assert any(HINT_NO_TEXT in text for text in collected_texts(window)), (
        "у заблокированной Перевести видна подсказка Нет текста для перевода"
    )
