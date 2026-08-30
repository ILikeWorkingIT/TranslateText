"""Регрессия: тексты пользователя RU→EN, один фрагмент."""

from __future__ import annotations

from ui.messages import (
    BASE_PROMPT_RU_EN,
    DIRECTION_RU_EN,
    LABEL_ORIGINAL,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION_EN,
)
from ui_helpers import (
    find_button,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
)

SHORT_RU = (
    "Я начинающий вайб-кодер в Cursor. У меня есть проект по вайбкодингу. "
    "Разработаны скиллы, команды, структура проекта, требования к приложению, "
    "доменная модель и т.д. "
)
LONG_RU = SHORT_RU + (
    "Начался процесс кодирования. Для понимания текущей ситуации в проекте "
    "прикладываю README, AGENTS, список команд вызова скиллов list-commands.md "
    "и чек лист для кодирования checklist.md, список текущих скиллов и ролей. "
    "Также после данного промта я приведу примерные текст промта для агента "
    "и текст с описанием мульти агентской схемы МАС, какой я ее вижу. "
)


def _select_ru_en(window) -> None:
    window.direction.set(DIRECTION_RU_EN)
    window._on_direction(DIRECTION_RU_EN)
    window.update_idletasks()


def _translate(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None
    button.invoke()
    window.update_idletasks()


def test_should_translate_user_short_ru_text_then_longer_ru_text(open_window):
    """Регрессия: короткий RU→EN, затем более длинный — оба в поле перевода."""
    app, port = open_window(("qwen2.5:3b",))
    port.translation_results = ("Short EN.", "Long EN translation.")
    _select_ru_en(app)
    _translate(app, SHORT_RU)
    pump_until(app, lambda: len(port.translate_calls) == 1, timeout_s=5.0)
    pump_until(
        app,
        lambda: not is_disabled(find_button(app, LABEL_TRANSLATE)),
        timeout_s=5.0,
    )
    out = find_textbox_for_label(app, LABEL_TRANSLATION_EN)
    assert out is not None
    assert textbox_content(out) == "Short EN."

    _translate(app, LONG_RU)
    pump_until(app, lambda: len(port.translate_calls) == 2, timeout_s=5.0)
    pump_until(
        app,
        lambda: not is_disabled(find_button(app, LABEL_TRANSLATE)),
        timeout_s=5.0,
    )
    assert textbox_content(out) == "Long EN translation.", (
        "второй перевод заменяет поле, не оставляет пустым"
    )
    assert port.translate_calls[1][1] == BASE_PROMPT_RU_EN
    assert port.translate_calls[1][2] == LONG_RU
