"""S-02: список «Модель» из локального API при старте, клике и фокусе."""

import threading

from conftest import DEFAULT_FAKE_MODELS
from ui_helpers import (
    combo_values,
    pump_until,
    trigger_model_click,
    trigger_model_focus,
)


def test_should_select_qwen_when_window_opens_and_preferred_is_available(window):
    """FT-041, A0178, happy: при старте выбрана qwen2.5:7b, если она есть в ответе."""
    assert window.model.get() == "qwen2.5:7b", (
        "при старте в списке Модель выбрана qwen2.5:7b, если она есть в ответе API"
    )


def test_should_select_first_model_when_window_opens_without_qwen(open_window):
    """FT-041, A0178, edge: нет qwen2.5:7b — выбрана первая модель ответа."""
    names = ("mistral", "qwen2.5:3b")
    app, _port = open_window(names)
    assert app.model.get() == "mistral", (
        "при старте без qwen2.5:7b в списке Модель выбрана первая модель ответа API"
    )


def test_should_show_all_api_names_when_list_includes_non_qwen(open_window):
    """FT-005, NFT-013, happy: в списке все имена ответа API, без фильтра."""
    names = ("custom-finetune:latest", "llama3.2", "qwen2.5:3b")
    app, _port = open_window(names)
    assert combo_values(app.model) == names, (
        "список Модель показывает все имена ответа API без фильтра по имени"
    )


def test_should_update_model_list_when_user_clicks_model(open_window):
    """FT-045, NFT-013, happy: клик по «Модель» подтягивает новый список без пересборки окна."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    updated = ("llama3.2", "qwen2.5:3b", "phi3")
    port.names = updated
    trigger_model_click(app)
    pump_until(app, lambda: combo_values(app.model) == updated)
    assert combo_values(app.model) == updated, (
        "после клика по Модель в списке появляются имена нового ответа API"
    )


def test_should_update_model_list_when_model_receives_focus(open_window):
    """FT-045, A0055, happy: фокус на «Модель» опрашивает API и обновляет список."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    updated = ("llama3.2", "qwen2.5:3b", "gemma2")
    port.names = updated
    trigger_model_focus(app)
    pump_until(app, lambda: combo_values(app.model) == updated)
    assert combo_values(app.model) == updated, (
        "после фокуса на Модель в списке появляются имена нового ответа API"
    )


def test_should_keep_selected_model_when_it_remains_in_new_response(open_window):
    """FT-045, A0053, happy: повторный опрос не сбрасывает выбор, пока имя есть в ответе."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    app.model.set("llama3.2")
    app.update_idletasks()
    port.names = ("llama3.2", "qwen2.5:3b", "phi3")
    trigger_model_click(app)
    pump_until(app, lambda: "phi3" in combo_values(app.model))
    assert app.model.get() == "llama3.2", (
        "после повторного опроса выбранная модель сохраняется, если она есть в новом ответе"
    )


def test_should_keep_user_pick_when_refresh_started_with_old_model(open_window):
    """FT-045, A0053, edge: выбор во время опроса не затирается ответом со старым current."""
    app, port = open_window(("qwen2.5:3b", "qwen2.5:7b"))
    assert app.model.get() == "qwen2.5:7b"
    hold = threading.Event()
    port.list_hold = hold
    trigger_model_click(app)
    pump_until(app, lambda: port.list_calls >= 2)
    app.model.set("qwen2.5:3b")
    app.update_idletasks()
    hold.set()
    for _ in range(40):
        app.update()
    assert app.model.get() == "qwen2.5:3b", (
        "если Пользователь сменил модель, пока шёл опрос после клика, "
        "ответ опроса не возвращает прежнюю qwen2.5:7b"
    )


def test_should_select_default_when_current_model_missing_after_refresh(open_window):
    """FT-045, A0053, edge: исчезнувшая модель — снова правило FT-041."""
    app, port = open_window(("llama3.2", "mistral"))
    app.model.set("mistral")
    app.update_idletasks()
    port.names = ("qwen2.5:3b", "qwen2.5:7b", "phi3")
    trigger_model_click(app)
    pump_until(app, lambda: combo_values(app.model) == ("qwen2.5:3b", "qwen2.5:7b", "phi3"))
    assert app.model.get() == "qwen2.5:7b", (
        "если прежнего выбора нет в новом ответе, в списке снова правило умолчания FT-041"
    )


def test_should_not_poll_models_when_window_gains_focus(open_window):
    """A0079, negative: фокус окна без клика/фокуса на «Модель» API не опрашивает."""
    app, port = open_window(DEFAULT_FAKE_MODELS)
    app.original.focus_set()
    app.update_idletasks()
    calls_before = port.list_calls
    app.event_generate("<FocusIn>")
    for _ in range(20):
        app.update()
    assert port.list_calls == calls_before, (
        "возврат фокуса в окно без действия со списком Модель не опрашивает API"
    )
