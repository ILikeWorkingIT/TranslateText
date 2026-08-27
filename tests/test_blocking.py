"""Must-блокировки кнопок и подсказка у «Перевести» — наблюдаемое состояние UI."""

from ui.messages import (
    HINT_NO_TEXT,
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

HINT_OLLAMA_DOWN = "Ollama не работает"
HINT_IN_PROGRESS = "Идёт перевод"
BLOCKING_HINTS = (HINT_NO_TEXT, HINT_OLLAMA_DOWN, HINT_IN_PROGRESS)


def test_should_disable_translate_when_original_is_empty(window):
    """FT-026, US-001 AC4, negative: «Перевести» заблокирована при пустом оригинале."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert is_disabled(button), "кнопка Перевести заблокирована, когда оригинал пуст"


def test_should_enable_translate_when_original_has_text(window):
    """FT-026, happy: «Перевести» доступна, когда оригинал непустой (до FT-048 / S-03)."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Hello")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), "кнопка Перевести доступна, когда оригинал непуст"


def test_should_enable_translate_when_original_is_only_spaces(window):
    """FT-026, edge: пустота — длина 0; одни пробелы не блокируют «Перевести»."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "   ")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), "кнопка Перевести доступна, когда оригинал — только пробелы"


def test_should_disable_save_when_translation_is_empty(window):
    """FT-027, US-003 AC3, negative: «Сохранить перевод» заблокирована при пустом переводе."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_SAVE_TRANSLATION)
    assert button is not None, "есть кнопка Сохранить перевод"
    assert is_disabled(button), "кнопка Сохранить перевод заблокирована, когда перевод пуст"


def test_should_enable_save_when_translation_has_text(window):
    """FT-027, A0100, happy: «Сохранить перевод» доступна, когда перевод непустой."""
    box = find_textbox_for_label(window, LABEL_TRANSLATION)
    assert box is not None, "есть поле Русский перевод"
    set_textbox_content(box, "Текст")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_SAVE_TRANSLATION)
    assert button is not None, "есть кнопка Сохранить перевод"
    assert not is_disabled(button), "кнопка Сохранить перевод доступна, когда перевод непуст"


def test_should_disable_translate_when_model_list_is_empty(window):
    """FT-048, US-001 AC4, negative: «Перевести» заблокирована при пустом списке моделей."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Hello")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
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
    """FT-050, US-008 AC1, disabled: подсказка «Нет текста для перевода» у заблокированной кнопки."""
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
    assert HINT_NO_TEXT not in str(window.status.cget("text")), (
        "подсказка Нет текста для перевода не в строке статуса"
    )


def test_should_not_show_no_text_hint_when_pointer_is_not_on_translate(window):
    """FT-050, A0092, empty: без наведения трёх подсказок блокировки на экране нет."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    visible = collected_texts(window)
    missing_ok = [hint for hint in BLOCKING_HINTS if not any(hint in text for text in visible)]
    assert missing_ok == list(BLOCKING_HINTS), (
        "без наведения на Перевести подсказки блокировки не показаны"
    )


def test_should_hide_blocking_hints_when_translate_is_enabled(window):
    """FT-050, US-008 AC4, happy: у доступной «Перевести» трёх подсказок нет."""
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Hello")
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert not is_disabled(button), "кнопка Перевести доступна, когда оригинал непуст"
    button.event_generate("<Enter>")
    window.update_idletasks()
    visible = collected_texts(window)
    shown = [hint for hint in BLOCKING_HINTS if any(hint in text for text in visible)]
    assert shown == [], "у доступной Перевести нет подсказок блокировки"
