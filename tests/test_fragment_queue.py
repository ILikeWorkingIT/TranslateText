"""S-07: очередь фрагментов через UI."""

from __future__ import annotations

from ui.messages import LABEL_ORIGINAL, LABEL_TRANSLATE, LABEL_TRANSLATION
from ui_helpers import (
    find_button,
    find_progress_bar,
    find_textbox_for_label,
    is_disabled,
    pump_until,
    set_textbox_content,
    textbox_content,
)


def _fill_original(window, text: str) -> None:
    box = find_textbox_for_label(window, LABEL_ORIGINAL)
    assert box is not None
    set_textbox_content(box, text)
    box.event_generate("<KeyRelease>")
    window.update_idletasks()


def _click_translate(window) -> None:
    button = find_button(window, LABEL_TRANSLATE)
    assert button is not None
    button.invoke()
    window.update_idletasks()


def test_should_glue_translation_when_long_text_splits_into_fragments(open_window):
    """FT-015, FT-020: два фрагмента — склейка в поле перевода."""
    app, port = open_window(("qwen2.5:3b",))
    part = "a" * 400
    original = f"{part}\n\n{part}"
    port.translation_results = ("first", "second")
    _fill_original(app, original)
    _click_translate(app)
    pump_until(app, lambda: len(port.translate_calls) == 2, timeout_s=5.0)
    pump_until(
        app,
        lambda: not is_disabled(find_button(app, LABEL_TRANSLATE)),
        timeout_s=5.0,
    )
    box = find_textbox_for_label(app, LABEL_TRANSLATION)
    assert box is not None
    assert textbox_content(box) == "firstsecond", (
        "после двух фрагментов в поле склейка перевода"
    )
    bar = find_progress_bar(app)
    assert bar is not None
    assert bar.get() == 1.0
