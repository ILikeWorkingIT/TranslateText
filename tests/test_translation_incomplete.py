"""S-08: сбой фрагмента и таймаут 60 с (FT-028)."""

from __future__ import annotations

from domain.errors import OllamaModelError, OllamaTimeoutError
from ui.messages import (
    DIRECTION_RU_EN,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    LABEL_TRANSLATION_EN,
    STATUS_TRANSLATION_INCOMPLETE,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
    widget_text,
)

LONG_RU = (
    "Я начинающий вайб-кодер в Cursor. У меня есть проект по вайбкодингу. "
    "Разработаны скиллы, команды, структура проекта, требования к приложению, "
    "доменная модель и т.д. Начался процесс кодирования. "
)


def _two_paragraphs() -> str:
    part = "a" * 400
    return f"{part}\n\n{part}"


def test_should_show_incomplete_status_when_ollama_times_out(open_window):
    """FT-028, US-007 AC3: таймаут — статус не завершён, «Перевести» снова доступна."""
    app, port = open_window(("qwen2.5:3b",))
    port.translate_error = OllamaTimeoutError("timed out")
    app.direction.set(DIRECTION_RU_EN)
    app._on_direction(DIRECTION_RU_EN)
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, LONG_RU)
    find_button(app, LABEL_TRANSLATE).invoke()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_INCOMPLETE in widget_text(app.status),
        timeout_s=5.0,
    )
    assert is_disabled(find_button(app, LABEL_TRANSLATE)) is False, (
        "после обрыва Перевести снова доступна"
    )
    translation = find_textbox_for_label(app, LABEL_TRANSLATION_EN)
    assert translation is not None, "есть поле Английский перевод"
    assert textbox_content(translation) == "", (
        "первый фрагмент не успел — поле без обрывка"
    )
    assert textbox_content(box) == LONG_RU, "оригинал не очищен"


def test_should_show_incomplete_status_when_model_returns_error(open_window):
    """FT-028, A0044, US-007 AC2: ошибка модели — то же сообщение, не полный перевод."""
    app, port = open_window(("qwen2.5:3b",))
    port.translate_error = OllamaModelError("model failed")
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, "Hello")
    box.event_generate("<KeyRelease>")
    find_button(app, LABEL_TRANSLATE).invoke()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_INCOMPLETE in widget_text(app.status),
        timeout_s=5.0,
    )
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert translation is not None, "есть поле Русский перевод"
    assert textbox_content(translation) == "", (
        "сбой единственного фрагмента не заполняет поле обрывком"
    )
    assert is_disabled(find_button(app, LABEL_TRANSLATE)) is False


def test_should_keep_glued_translation_when_later_fragment_fails(open_window):
    """FT-028, NFT-007: сбой второго фрагмента — склейка первого в поле, очередь стоп."""
    app, port = open_window(("qwen2.5:3b",))
    port.translation_results = ("first",)
    port.translate_error = OllamaTimeoutError("timed out")
    port.error_from_call = 2
    original = _two_paragraphs()
    box = find_textbox_for_label(app, LABEL_ORIGINAL)
    assert box is not None, "есть поле Оригинальный текст"
    set_textbox_content(box, original)
    box.event_generate("<KeyRelease>")
    find_button(app, LABEL_TRANSLATE).invoke()
    pump_until(
        app,
        lambda: STATUS_TRANSLATION_INCOMPLETE in widget_text(app.status),
        timeout_s=5.0,
    )
    assert len(port.translate_calls) == 2, "второй фрагмент вызывался и сорвался"
    translation = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert translation is not None, "есть поле Русский перевод"
    glued = textbox_content(translation)
    assert glued.startswith("first"), "склейка успешного фрагмента на месте"
    assert "second" not in glued
    assert len(glued) >= len("first")
    assert textbox_content(box) == original, "оригинал не очищен"
    assert is_disabled(find_button(app, LABEL_TRANSLATE)) is False
