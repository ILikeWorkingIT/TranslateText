from __future__ import annotations

import queue
import tkinter
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Literal

import customtkinter as ctk

from domain.models import (
    ExportFormat,
    ModelsRefreshedEvent,
    QueueEvent,
    SourceFormat,
)
from services.ollama_gateway import OllamaGateway
from ui.bridge import ExportBridge, LoadSourceBridge, ModelsBridge, TranslationBridge
from ui.clipboard import read_plain_clipboard, write_plain_clipboard
from ui.messages import (
    DIRECTION_EN_RU,
    HINT_IN_PROGRESS,
    HINT_NO_TEXT,
    HINT_OLLAMA_DOWN,
    LABEL_OPEN_FILE,
    LABEL_SAVE_TRANSLATION,
    MSG_EMPTY_INSTRUCTION,
    MSG_EXPORT_FAILED,
    MSG_SOURCE_NOT_EXTRACTED,
    MSG_UNSAVED_TRANSLATION,
    OPEN_FILETYPES,
    SAVE_FILETYPES,
    STATUS_OLLAMA_UNAVAILABLE,
    STATUS_SOURCE_LIMIT_EXCEEDED,
    STATUS_TRANSLATION_CANCELLED,
    STATUS_TRANSLATION_INCOMPLETE,
    TITLE_EMPTY_INSTRUCTION,
    TITLE_EXPORT_FAILED,
    TITLE_SOURCE_NOT_EXTRACTED,
    TITLE_UNSAVED_TRANSLATION,
    base_prompt_for_direction,
    translation_label_for_direction,
)
from ui.panels import FooterBar, HeaderBar, InstructionCard, TextPanes
from ui.theme import BG, CARD, FONT_STATUS, TEXT

TranslateState = Literal["idle", "loading"]
OllamaAvailability = Literal["unknown", "available", "unavailable"]

_VK_C = 67
_VK_V = 86
_COPY_KEYSYMS = frozenset({"c", "cyrillic_es"})
_PASTE_KEYSYMS = frozenset({"v", "cyrillic_em"})


def _event_keycode(event: tkinter.Event) -> int:
    return int(getattr(event, "keycode", 0) or 0)


def _event_keysym(event: tkinter.Event) -> str:
    return str(getattr(event, "keysym", "") or "").lower()


def _is_copy_key(event: tkinter.Event) -> bool:
    return _event_keycode(event) == _VK_C or _event_keysym(event) in _COPY_KEYSYMS


def _is_paste_key(event: tkinter.Event) -> bool:
    return _event_keycode(event) == _VK_V or _event_keysym(event) in _PASTE_KEYSYMS


def _export_format_of(path: Path) -> ExportFormat | None:
    suffix = path.suffix.lower()
    if suffix in (".txt", ""):
        return "txt"
    if suffix == ".docx":
        return "docx"
    return None


def _source_format_of(path: Path) -> SourceFormat | None:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return "txt"
    if suffix == ".md":
        return "md"
    return None


class TranslateTextWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TranslateText")
        self.geometry("1280x820")
        self.minsize(980, 640)
        self.configure(fg_color=BG)
        self._status_after = ""
        self._hint_leave_after = ""
        self._ui_state: TranslateState = "idle"
        self._cancel_requested = False
        self._applying_models = False
        self._ollama_availability: OllamaAvailability = "unknown"
        self._direction = DIRECTION_EN_RU
        self._translation_saved = True
        self._paste_alive = True
        self._ui_callbacks: queue.SimpleQueue[Callable[[], None]] = queue.SimpleQueue()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self._models_bridge = ModelsBridge(
            host=self,
            ollama=OllamaGateway(),
            on_models=self._on_models_refreshed,
            on_unavailable=self._on_models_unavailable,
        )
        self._translation_bridge = TranslationBridge(
            host=self,
            ollama=OllamaGateway(),
            on_event=self._on_queue_event,
            on_source_limit_exceeded=self._on_source_limit_exceeded,
        )
        self._export_bridge = ExportBridge(
            host=self,
            on_success=self._on_export_success,
            on_error=self._on_export_error,
        )
        self._load_bridge = LoadSourceBridge(
            host=self,
            on_success=self._on_load_success,
            on_error=self._on_load_error,
        )
        self._bind_model_refresh_triggers()
        self._request_models_refresh()
        self.after(20, self._poll_ui_callbacks)

    def call_on_ui(self, callback: Callable[[], None]) -> None:
        """Колбэки из воркера — только через очередь главного потока Tk."""
        self._ui_callbacks.put(callback)

    def _poll_ui_callbacks(self) -> None:
        while True:
            try:
                callback = self._ui_callbacks.get_nowait()
            except queue.Empty:
                break
            try:
                callback()
            except tkinter.TclError:
                pass
        if self._paste_alive:
            self.after(20, self._poll_ui_callbacks)

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = HeaderBar(
            self,
            on_open_file=self._on_open_file,
            on_save_translation=self._on_save_translation,
            on_model=self._on_model,
            on_direction=self._on_direction,
            model_values=(),
            selected_model="",
            selected_direction=self._direction,
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 8))
        self.open_file = self.header.open_file
        self.save = self.header.save
        self.model = self.header.model
        self.direction = self.header.direction

        self.panes = TextPanes(self)
        self.panes.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        self.original = self.panes.original
        self.translation = self.panes.translation

        self.instruction_card = InstructionCard(
            self,
            initial_prompt=base_prompt_for_direction(self._direction),
        )
        self.instruction_card.grid(row=2, column=0, sticky="ew", padx=28, pady=8)
        self.instruction = self.instruction_card.instruction

        self.footer = FooterBar(
            self,
            on_translate=self._on_translate,
            on_cancel_translation=self._on_cancel_translation,
        )
        self.footer.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 8))
        self.progress = self.footer.progress
        self.translate = self.footer.translate
        self.cancel = self.footer.cancel
        self.status = self.footer.status

        self.translate_hint = ctk.CTkLabel(
            self,
            text="",
            font=FONT_STATUS,
            text_color=TEXT,
            fg_color=CARD,
            corner_radius=8,
        )
        self.translate_hint.qa_id = "hint-translate"

        self._watch_textbox(self.original)
        self._watch_textbox(self.translation)
        self._enable_field_paste(self.instruction)
        self._watch_model_list()
        self._bind_translate_hover()
        self._bind_window_paste()
        self._refresh_action_states()

    def _watch_textbox(self, box: ctk.CTkTextbox) -> None:
        original_insert = box.insert
        original_delete = box.delete

        def insert(index: str, text: str, tags: str | None = None) -> None:
            if tags is None:
                original_insert(index, text)
            else:
                original_insert(index, text, tags)
            self._sync_translation_saved_if_needed(box)
            self._refresh_action_states()

        def delete(index1: str, index2: str | None = None) -> None:
            original_delete(index1, index2)
            self._sync_translation_saved_if_needed(box)
            self._refresh_action_states()

        box.insert = insert
        box.delete = delete
        box.bind(
            "<KeyRelease>",
            lambda _event, watched=box: self._on_textbox_key_release(watched),
        )
        self._enable_field_paste(box)

    def _on_textbox_key_release(self, box: ctk.CTkTextbox) -> None:
        self._sync_translation_saved_if_needed(box)
        self._refresh_action_states()

    def _sync_translation_saved_if_needed(self, box: ctk.CTkTextbox) -> None:
        translation = getattr(self, "translation", None)
        if translation is None or box is not translation:
            return
        self._translation_saved = len(self._text_of(self.translation)) == 0

    def _enable_field_paste(self, box: ctk.CTkTextbox) -> None:
        def on_paste(_event: tkinter.Event) -> str:
            self._insert_clipboard(box)
            return "break"

        def on_copy(_event: tkinter.Event) -> str:
            self._copy_selection(box)
            return "break"

        def on_ctrl_key(event: tkinter.Event) -> str | None:
            # VK не зависит от раскладки: RU C → Cyrillic_es, V → Cyrillic_em.
            if _is_copy_key(event):
                self._copy_selection(box)
                return "break"
            if _is_paste_key(event):
                self._insert_clipboard(box)
                return "break"
            return None

        inner = getattr(box, "_textbox", box)
        for sequence in (
            "<<Paste>>",
            "<Control-v>",
            "<Control-V>",
            "<Control-Key-v>",
            "<Control-Key-V>",
            "<Control-Key-Cyrillic_em>",
            "<Control-Key-Cyrillic_EM>",
            "<Shift-Insert>",
        ):
            inner.bind(sequence, on_paste, add="+")
            box.bind(sequence, on_paste)
        for sequence in (
            "<<Copy>>",
            "<Control-c>",
            "<Control-C>",
            "<Control-Key-c>",
            "<Control-Key-C>",
            "<Control-Key-Cyrillic_es>",
            "<Control-Key-Cyrillic_ES>",
        ):
            inner.bind(sequence, on_copy, add="+")
            box.bind(sequence, on_copy)
        inner.bind("<Control-KeyPress>", on_ctrl_key, add="+")
        box.bind("<Control-KeyPress>", on_ctrl_key)
        try:
            inner.event_add(
                "<<Paste>>",
                "<Control-Key-Cyrillic_em>",
                "<Control-Key-Cyrillic_EM>",
            )
            inner.event_add(
                "<<Copy>>",
                "<Control-Key-Cyrillic_es>",
                "<Control-Key-Cyrillic_ES>",
            )
        except tkinter.TclError:
            pass
        canvas = getattr(box, "_canvas", None)
        if canvas is not None:
            canvas.bind("<Button-1>", lambda _event: box.focus_set(), add="+")
        tkinter.Misc.bind(box, "<Button-1>", lambda _event: box.focus_set(), add="+")

    def _bind_window_paste(self) -> None:
        for sequence in (
            "<Control-v>",
            "<Control-V>",
            "<Control-Key-v>",
            "<Control-Key-V>",
            "<Control-Key-Cyrillic_em>",
            "<Control-Key-Cyrillic_EM>",
            "<Shift-Insert>",
        ):
            tkinter.Misc.bind_all(self, sequence, self._on_window_paste, add="+")
        for sequence in (
            "<Control-c>",
            "<Control-C>",
            "<Control-Key-c>",
            "<Control-Key-C>",
            "<Control-Key-Cyrillic_es>",
            "<Control-Key-Cyrillic_ES>",
        ):
            tkinter.Misc.bind_all(self, sequence, self._on_window_copy, add="+")
        tkinter.Misc.bind_all(
            self, "<Control-KeyPress>", self._on_window_ctrl_key, add="+"
        )
        try:
            self.event_add(
                "<<Paste>>",
                "<Control-Key-Cyrillic_em>",
                "<Control-Key-Cyrillic_EM>",
            )
            self.event_add(
                "<<Copy>>",
                "<Control-Key-Cyrillic_es>",
                "<Control-Key-Cyrillic_ES>",
            )
        except tkinter.TclError:
            pass

    def _on_window_ctrl_key(self, event: tkinter.Event) -> str | None:
        if _is_copy_key(event):
            return self._on_window_copy(event)
        if _is_paste_key(event):
            return self._on_window_paste(event)
        return None

    def _on_window_copy(self, _event: tkinter.Event) -> str | None:
        if not getattr(self, "_paste_alive", False):
            return None
        if not self.winfo_exists():
            return None
        box = self._focused_app_textbox()
        if box is None:
            box = self._textbox_under_pointer()
        if box is None:
            return None
        if self._copy_selection(box):
            return "break"
        return None

    def _on_window_paste(self, event: tkinter.Event) -> str | None:
        if not getattr(self, "_paste_alive", False):
            return None
        if not self.winfo_exists():
            return None
        keycode = _event_keycode(event)
        keysym = _event_keysym(event)
        if keycode not in (0, _VK_V) and keysym not in (
            "v",
            "cyrillic_em",
            "insert",
            "",
        ):
            return None
        box = self._focused_app_textbox()
        if box is None:
            box = self._textbox_under_pointer()
        if box is None:
            return None
        box.focus_set()
        if self._insert_clipboard(box):
            return "break"
        return None

    def _focused_app_textbox(self) -> ctk.CTkTextbox | None:
        try:
            focused = self.focus_get()
        except tkinter.TclError:
            return None
        return self._as_app_textbox(focused)

    def _textbox_under_pointer(self) -> ctk.CTkTextbox | None:
        try:
            widget = self.winfo_containing(*self.winfo_pointerxy())
        except tkinter.TclError:
            return None
        return self._as_app_textbox(widget)

    def _as_app_textbox(self, widget: tkinter.Misc | None) -> ctk.CTkTextbox | None:
        known = (self.original, self.translation, self.instruction)
        current: tkinter.Misc | None = widget
        while current is not None:
            if current in known:
                return current
            parent = getattr(current, "master", None)
            if parent is current:
                break
            current = parent
        return None

    def _copy_selection(self, box: ctk.CTkTextbox) -> bool:
        inner = getattr(box, "_textbox", box)
        try:
            text = str(inner.get("sel.first", "sel.last"))
        except tkinter.TclError:
            return False
        if text == "":
            return False
        write_plain_clipboard(self, text)
        return True

    def _insert_clipboard(self, box: ctk.CTkTextbox) -> bool:
        text = read_plain_clipboard(self)
        if not text:
            return False
        inner = getattr(box, "_textbox", box)
        try:
            if str(inner.cget("state")) == "disabled":
                return False
        except tkinter.TclError:
            pass
        try:
            box.delete("sel.first", "sel.last")
        except tkinter.TclError:
            pass
        box.insert("insert", text)
        box.focus_set()
        self._refresh_action_states()
        return True

    def _watch_model_list(self) -> None:
        original_configure = self.model.configure

        def configure(**kwargs: str | int | float | bool | list[str] | tuple[str, ...]) -> None:
            original_configure(**kwargs)
            self._refresh_action_states()

        self.model.configure = configure

    def _bind_model_refresh_triggers(self) -> None:
        self.model.bind("<FocusIn>", self._on_model_focus)
        self.model.bind("<Button-1>", self._on_model_click)
        tkinter.Misc.bind(self.model, "<FocusIn>", self._on_model_focus, add="+")
        tkinter.Misc.bind(self.model, "<Button-1>", self._on_model_click, add="+")
        canvas = self.model._canvas
        canvas.tag_bind("right_parts", "<Button-1>", self._on_model_click, add="+")
        canvas.tag_bind("dropdown_arrow", "<Button-1>", self._on_model_click, add="+")

    def _on_model_focus(self, _event: object) -> str | None:
        self._request_models_refresh()
        return None

    def _on_model_click(self, _event: object) -> str | None:
        self._request_models_refresh()
        return None

    def _request_models_refresh(self) -> None:
        if self._applying_models:
            return
        self._models_bridge.refresh(str(self.model.get()))

    def _on_models_refreshed(self, event: ModelsRefreshedEvent) -> None:
        self._applying_models = True
        try:
            self._ollama_availability = "available"
            self.model.configure(values=list(event.models))
            self.model.set(event.selected_model)
        finally:
            self._applying_models = False
        self._refresh_action_states()

    def _on_models_unavailable(self) -> None:
        self._applying_models = True
        try:
            self._ollama_availability = "unavailable"
            self.model.configure(values=[])
            self.model.set("")
        finally:
            self._applying_models = False
        self._refresh_action_states()

    def _bind_translate_hover(self) -> None:
        self.translate.bind("<Enter>", self._on_translate_enter)
        self.translate.bind("<Leave>", self._on_translate_leave)
        original_generate = self.translate.event_generate

        def event_generate(sequence: str = "", **kwargs: str | int | float | bool) -> None:
            if sequence == "<Enter>":
                self._on_translate_enter(None)
            elif sequence == "<Leave>":
                self._on_translate_leave(None)
            try:
                original_generate(sequence, **kwargs)
            except tkinter.TclError:
                pass

        self.translate.event_generate = event_generate

    def _text_of(self, box: ctk.CTkTextbox) -> str:
        return box.get("0.0", "end-1c")

    def _set_instruction_text(self, value: str) -> None:
        self.instruction.delete("0.0", "end")
        if value:
            self.instruction.insert("0.0", value)

    def _set_translation_text(self, value: str) -> None:
        self.translation.delete("0.0", "end")
        if value:
            self.translation.insert("0.0", value)

    def _translation_in_progress(self) -> bool:
        return self._ui_state == "loading"

    def _models_empty(self) -> bool:
        values = self.model.cget("values")
        if values is None:
            return True
        return len(tuple(values)) == 0

    def _ollama_blocks_translate(self) -> bool:
        return (
            self._ollama_availability == "unavailable" or self._models_empty()
        )

    def _refresh_action_states(self) -> None:
        original_empty = len(self._text_of(self.original)) == 0
        translation_empty = len(self._text_of(self.translation)) == 0
        translate_blocked = (
            self._translation_in_progress()
            or original_empty
            or self._ollama_blocks_translate()
        )
        self.translate.configure(state="disabled" if translate_blocked else "normal")
        self.save.configure(state="disabled" if translation_empty else "normal")
        self._sync_cancel_visibility()
        if self._ollama_availability == "unavailable":
            self.status.configure(text=STATUS_OLLAMA_UNAVAILABLE)
        else:
            self.status.configure(text="")
        if not translate_blocked:
            self._hide_translate_hint()
            return
        try:
            hint_shown = bool(self.translate_hint.winfo_ismapped())
        except tkinter.TclError:
            hint_shown = False
        if hint_shown:
            self._show_translate_hint()

    def _on_translate_enter(self, _event: object) -> str | None:
        if self._hint_leave_after:
            self.after_cancel(self._hint_leave_after)
            self._hint_leave_after = ""
        self._show_translate_hint()
        return None

    def _on_translate_leave(self, _event: object) -> str | None:
        if self._hint_leave_after:
            self.after_cancel(self._hint_leave_after)
        self._hint_leave_after = self.after(50, self._hide_translate_hint)
        return None

    def _blocking_hint_text(self) -> str | None:
        if self._translation_in_progress():
            return HINT_IN_PROGRESS
        if self._ollama_blocks_translate():
            return HINT_OLLAMA_DOWN
        if len(self._text_of(self.original)) == 0:
            return HINT_NO_TEXT
        return None

    def _show_translate_hint(self) -> None:
        if str(self.translate.cget("state")) != "disabled":
            self._hide_translate_hint()
            return
        hint = self._blocking_hint_text()
        if hint is None:
            self._hide_translate_hint()
            return
        self.translate_hint.configure(text=hint)
        self.update_idletasks()
        try:
            x = self.translate.winfo_rootx() - self.winfo_rootx()
            y = self.translate.winfo_rooty() - self.winfo_rooty() - 40
        except tkinter.TclError:
            x, y = 24, 24
        self.translate_hint.place(x=max(x, 8), y=max(y, 8))

    def _hide_translate_hint(self) -> None:
        self._hint_leave_after = ""
        self.translate_hint.configure(text="")
        self.translate_hint.place_forget()

    def _sync_cancel_visibility(self) -> None:
        visible = self._translation_in_progress() and not self._cancel_requested
        try:
            self.footer.set_cancel_visible(visible)
        except tkinter.TclError:
            return

    def _on_cancel_translation(self) -> None:
        """FT-054: скрыть сразу; «Перевести» остаётся серой до конца запроса (A0151)."""
        if not self._translation_in_progress() or self._cancel_requested:
            return
        self._cancel_requested = True
        self._sync_cancel_visibility()
        self._translation_bridge.cancel()

    def _on_open_file(self) -> None:
        if not self._confirm_unsaved_if_needed():
            return
        self._continue_open_file()

    def _continue_open_file(self) -> None:
        """UC-002 после UC-006."""
        chosen = filedialog.askopenfilename(
            parent=self,
            title=LABEL_OPEN_FILE,
            filetypes=list(OPEN_FILETYPES),
        )
        if not chosen:
            return
        path = Path(chosen)
        source_format = _source_format_of(path)
        if source_format is None:
            messagebox.showerror(
                TITLE_SOURCE_NOT_EXTRACTED,
                MSG_SOURCE_NOT_EXTRACTED,
                parent=self,
            )
            return
        self._load_bridge.start(path=str(path), source_format=source_format)

    def _on_load_success(self, _request_id: int, text: str) -> None:
        self._apply_loaded_source(text)

    def _on_load_error(self, _request_id: int) -> None:
        messagebox.showerror(
            TITLE_SOURCE_NOT_EXTRACTED,
            MSG_SOURCE_NOT_EXTRACTED,
            parent=self,
        )

    def _apply_loaded_source(self, text: str) -> None:
        """A0099: успешная загрузка исходника очищает поле перевода."""
        self.original.delete("0.0", "end")
        if text:
            self.original.insert("0.0", text)
        self._set_translation_text("")
        self._translation_saved = True

    def _on_save_translation(self) -> None:
        text = self._text_of(self.translation)
        if len(text) == 0:
            return
        chosen = filedialog.asksaveasfilename(
            parent=self,
            title=LABEL_SAVE_TRANSLATION,
            defaultextension=".txt",
            filetypes=list(SAVE_FILETYPES),
            confirmoverwrite=True,
        )
        if not chosen:
            return
        path = Path(chosen)
        export_format = _export_format_of(path)
        if export_format is None:
            messagebox.showerror(
                TITLE_EXPORT_FAILED,
                MSG_EXPORT_FAILED,
                parent=self,
            )
            return
        self._export_bridge.start(
            translation_text=text,
            path=str(path),
            export_format=export_format,
        )

    def _on_export_success(self, _request_id: int, exported_text: str) -> None:
        if self._text_of(self.translation) == exported_text:
            self._translation_saved = True

    def _on_export_error(self, _request_id: int) -> None:
        messagebox.showerror(
            TITLE_EXPORT_FAILED,
            MSG_EXPORT_FAILED,
            parent=self,
        )
        self._refresh_action_states()

    def _on_translate(self) -> None:
        if self._translation_in_progress():
            return
        if self._ollama_blocks_translate():
            return
        original = self._text_of(self.original)
        if len(original) == 0:
            return
        if not self._confirm_unsaved_if_needed():
            return
        instruction = self._text_of(self.instruction)
        if len(instruction) == 0:
            if not self._confirm_empty_instruction():
                return
            instruction = base_prompt_for_direction(self._direction)
            self._set_instruction_text(instruction)
        model = str(self.model.get())
        if not model:
            return
        self._begin_translation(
            original_text=original,
            instruction=instruction,
            model=model,
        )

    def _confirm_unsaved_if_needed(self) -> bool:
        """FT-032: до FT-029 (A0102). Смена направления сюда не входит (FT-053)."""
        text = self._text_of(self.translation)
        if len(text) == 0 or self._translation_saved:
            return True
        return messagebox.askokcancel(
            TITLE_UNSAVED_TRANSLATION,
            MSG_UNSAVED_TRANSLATION,
            parent=self,
        )

    def _confirm_empty_instruction(self) -> bool:
        """FT-029: согласие или отмена; NFT-002 считается после согласия."""
        return messagebox.askokcancel(
            TITLE_EMPTY_INSTRUCTION,
            MSG_EMPTY_INSTRUCTION,
            parent=self,
        )

    def _begin_translation(
        self,
        *,
        original_text: str,
        instruction: str,
        model: str,
    ) -> None:
        self._ui_state = "loading"
        self._cancel_requested = False
        self.progress.set(0)
        self._refresh_action_states()
        self._translation_bridge.start(
            original_text=original_text,
            instruction=instruction,
            model=model,
            direction=self._direction,
            instruction_confirmed=True,
            translation_text=self._text_of(self.translation),
            translation_saved=self._translation_saved,
            unsaved_confirmed=True,
        )

    def _on_source_limit_exceeded(self) -> None:
        """FT-023: отказ без Ollama; оригинал не обрезается."""
        self._ui_state = "idle"
        self._cancel_requested = False
        self.progress.set(0)
        self._refresh_action_states()
        self.status.configure(text=STATUS_SOURCE_LIMIT_EXCEEDED)

    def _on_queue_event(self, event: QueueEvent) -> None:
        if event.status == "inProgress":
            self._set_progress_from_event(event)
            if event.translation_so_far:
                self._set_translation_text(event.translation_so_far)
            return
        if event.status == "completed":
            self._set_translation_text(event.translation_so_far)
            self.progress.set(1)
            self._ui_state = "idle"
            self._cancel_requested = False
            self._refresh_action_states()
            return
        if event.status == "incomplete":
            if event.translation_so_far:
                self._set_translation_text(event.translation_so_far)
            self._set_progress_from_event(event)
            self._ui_state = "idle"
            self._cancel_requested = False
            self._refresh_action_states()
            if event.incomplete_cause == "cancelled":
                self.status.configure(text=STATUS_TRANSLATION_CANCELLED)
            else:
                self.status.configure(text=STATUS_TRANSLATION_INCOMPLETE)
            return
        self._ui_state = "idle"
        self._cancel_requested = False
        self._refresh_action_states()

    def _set_progress_from_event(self, event: QueueEvent) -> None:
        if event.total_source_chars <= 0:
            self.progress.set(0)
            return
        self.progress.set(
            event.processed_source_chars / event.total_source_chars
        )

    def _on_model(self, _value: str) -> None:
        return

    def _on_direction(self, value: str) -> None:
        previous = self._direction
        if value == previous:
            return
        previous_prompt = base_prompt_for_direction(previous)
        next_prompt = base_prompt_for_direction(value)
        if self._text_of(self.instruction) == previous_prompt:
            self._set_instruction_text(next_prompt)
        self._direction = value
        self.panes.set_translation_title(translation_label_for_direction(value))

    def _on_close(self) -> None:
        for attr in ("_status_after", "_hint_leave_after"):
            after_id = getattr(self, attr)
            if after_id:
                try:
                    self.after_cancel(after_id)
                except tkinter.TclError:
                    pass
        self.destroy()

    def destroy(self) -> None:
        self._paste_alive = False
        translation = getattr(self, "_translation_bridge", None)
        if translation is not None:
            translation.close()
        models = getattr(self, "_models_bridge", None)
        if models is not None:
            models.close()
        export = getattr(self, "_export_bridge", None)
        if export is not None:
            export.close()
        load = getattr(self, "_load_bridge", None)
        if load is not None:
            load.close()
        super().destroy()

    def run(self) -> None:
        self.mainloop()


def run_app() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    TranslateTextWindow().run()
