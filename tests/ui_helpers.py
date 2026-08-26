from __future__ import annotations

import customtkinter as ctk


def iter_widgets(widget):
    yield widget
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield from iter_widgets(child)


def widget_text(widget) -> str:
    try:
        value = widget.cget("text")
    except Exception:
        return ""
    return str(value) if value is not None else ""


def find_by_text(root, text: str):
    for widget in iter_widgets(root):
        if widget_text(widget) == text:
            return widget
    return None


def find_button(root, text: str) -> ctk.CTkButton | None:
    for widget in iter_widgets(root):
        if isinstance(widget, ctk.CTkButton) and widget_text(widget) == text:
            return widget
    return None


def find_textbox_for_label(root, label_text: str) -> ctk.CTkTextbox | None:
    label = find_by_text(root, label_text)
    if label is None:
        return None
    parent = label.master
    for widget in iter_widgets(parent):
        if isinstance(widget, ctk.CTkTextbox):
            return widget
    return None


def find_progress_bar(root) -> ctk.CTkProgressBar | None:
    for widget in iter_widgets(root):
        if isinstance(widget, ctk.CTkProgressBar):
            return widget
    return None


def textbox_content(box: ctk.CTkTextbox) -> str:
    return box.get("0.0", "end-1c")


def set_textbox_content(box: ctk.CTkTextbox, value: str) -> None:
    box.delete("0.0", "end")
    if value:
        box.insert("0.0", value)


def is_disabled(widget) -> bool:
    try:
        state = str(widget.cget("state"))
    except Exception:
        return False
    return state == "disabled"


def collected_texts(root) -> list[str]:
    texts = []
    for widget in iter_widgets(root):
        value = widget_text(widget)
        if value:
            texts.append(value)
    return texts
