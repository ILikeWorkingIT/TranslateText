"""FT-028 (минимум): статус при незавершённом переводе."""

from __future__ import annotations

from domain.errors import OllamaTimeoutError
from ui.messages import (
    DIRECTION_RU_EN,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION_EN,
    STATUS_TRANSLATION_INCOMPLETE,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    widget_text,
)

LONG_RU = (
    "Я начинающий вайб-кодер в Cursor. У меня есть проект по вайбкодингу. "
    "Разработаны скиллы, команды, структура проекта, требования к приложению, "
    "доменная модель и т.д. Начался процесс кодирования. "
)


def test_should_show_incomplete_status_when_ollama_times_out(open_window):
    """FT-028: таймаут/сбой — строка статуса, «Перевести» снова доступна."""
    app, port = open_window(("qwen2.5:3b",))
    port.translate_error = OllamaTimeoutError("timed out")
    app.direction.set(DIRECTION_RU_EN)
    app._on_direction(DIRECTION_RU_EN)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None
    set_textbox_content(box, LONG_RU)
    find_button(app, LABEL_TRANSLATE).invoke()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_INCOMPLETE in widget_text(app.status),
        timeout_s=5.0,
    )
    assert is_disabled(find_button(app, LABEL_TRANSLATE)) is False
    translation = find_textbox_for_label(app, LABEL_TRANSLATION_EN)
    assert translation is not None
    assert translation.get("0.0", "end-1c") == ""
