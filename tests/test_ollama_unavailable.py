"""S-03: недоступный Ollama — статус FT-024, блокировка, восстановление."""

from conftest import DEFAULT_FAKE_MODELS
from ui.messages import (
    HINT_NO_TEXT,
    HINT_OLLAMA_DOWN,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    STATUS_OLLAMA_UNAVAILABLE,
)
from ui_helpers import (
    collected_texts,
    combo_values,
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
    trigger_model_click,
)


def wait_until_unavailable(app) -> None:
    pump_until(
        app,
        lambda: str(app.status.cget("text")) == STATUS_OLLAMA_UNAVAILABLE,
    )


def test_should_show_start_ollama_status_when_api_is_unavailable(open_window):
    """FT-024, NFT-011, US-007 AC1, negative: статус с bat-путём, пока API недоступен."""
    app, _port = open_window(())
    wait_until_unavailable(app)
    status = str(app.status.cget("text"))
    assert "start_ollama.bat" in status, "в строке статуса есть start_ollama.bat"
    assert "F:\\Docker\\Ollama" in status, "в строке статуса есть путь F:\\Docker\\Ollama"


def test_should_keep_original_text_when_ollama_becomes_unavailable(open_window):
    """FT-024, US-007 AC1, negative: поле «Оригинальный текст» не очищается."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Keep this original")
    box.event_generate("<KeyRelease>")
    app.update_idletasks()
    port.names = ()
    trigger_model_click(app)
    wait_until_unavailable(app)
    assert textbox_content(box) == "Keep this original", (
        "Оригинальный текст остаётся на месте, когда Ollama становится недоступна"
    )


def test_should_enable_translate_when_models_return_after_unavailable(open_window):
    """FT-024, FT-048, A0079, US-007 AC1, happy: клик по «Модель» снимает блокировку."""
    app, port = open_window(())
    wait_until_unavailable(app)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Hello")
    box.event_generate("<KeyRelease>")
    app.update_idletasks()
    port.names = DEFAULT_FAKE_MODELS
    trigger_model_click(app)
    pump_until(app, lambda: combo_values(app.model) == DEFAULT_FAKE_MODELS)
    button = find_button(app, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    assert str(app.status.cget("text")) == "", (
        "после непустого ответа API сообщение о недоступности Ollama снято"
    )
    assert not is_disabled(button), (
        "Перевести доступна после восстановления Ollama, когда оригинал непуст"
    )


def test_should_show_ollama_hint_when_original_empty_and_api_unavailable(open_window):
    """FT-050, A0082, US-008 AC5, edge: «Ollama не работает» важнее пустого оригинала."""
    app, _port = open_window(())
    wait_until_unavailable(app)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "")
    box.event_generate("<KeyRelease>")
    app.update_idletasks()
    button = find_button(app, LABEL_TRANSLATE)
    assert button is not None, "есть кнопка Перевести"
    button.event_generate("<Enter>")
    app.update_idletasks()
    visible = collected_texts(app)
    assert any(HINT_OLLAMA_DOWN in text for text in visible), (
        "у заблокированной Перевести видна подсказка Ollama не работает"
    )
    assert not any(HINT_NO_TEXT in text for text in visible), (
        "при недоступной Ollama не показывается Нет текста для перевода"
    )
