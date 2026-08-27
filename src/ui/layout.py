from __future__ import annotations

import tkinter
from typing import Literal

import customtkinter as ctk

from domain.models import ModelsRefreshedEvent
from services.ollama_gateway import OllamaGateway
from ui.bridge import ModelsBridge
from ui.messages import (
    DIRECTION_EN_RU,
    HINT_NO_TEXT,
    HINT_OLLAMA_DOWN,
    STATUS_OLLAMA_UNAVAILABLE,
    base_prompt_for_direction,
    translation_label_for_direction,
)
from ui.panels import FooterBar, HeaderBar, InstructionCard, TextPanes
from ui.theme import BG, CARD, FONT_STATUS, TEXT

TranslateState = Literal["idle"]
OllamaAvailability = Literal["unknown", "available", "unavailable"]


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
        self._applying_models = False
        self._ollama_availability: OllamaAvailability = "unknown"
        self._direction = DIRECTION_EN_RU
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self._models_bridge = ModelsBridge(
            host=self,
            ollama=OllamaGateway(),
            on_models=self._on_models_refreshed,
            on_unavailable=self._on_models_unavailable,
        )
        self._bind_model_refresh_triggers()
        self._request_models_refresh()

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

        self.footer = FooterBar(self, on_translate=self._on_translate)
        self.footer.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 8))
        self.progress = self.footer.progress
        self.translate = self.footer.translate
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
        self._watch_model_list()
        self._bind_translate_hover()
        self._refresh_action_states()

    def _watch_textbox(self, box: ctk.CTkTextbox) -> None:
        original_insert = box.insert
        original_delete = box.delete

        def insert(index: str, text: str, tags: str | None = None) -> None:
            original_insert(index, text, tags)
            self._refresh_action_states()

        def delete(index1: str, index2: str | None = None) -> None:
            original_delete(index1, index2)
            self._refresh_action_states()

        box.insert = insert
        box.delete = delete
        box.bind("<KeyRelease>", lambda _event: self._refresh_action_states())
        box.bind("<<Paste>>", lambda _event: self.after_idle(self._refresh_action_states))

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
        translate_blocked = original_empty or self._ollama_blocks_translate()
        self.translate.configure(state="disabled" if translate_blocked else "normal")
        self.save.configure(state="disabled" if translation_empty else "normal")
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

    def _on_open_file(self) -> None:
        return

    def _on_save_translation(self) -> None:
        return

    def _on_translate(self) -> None:
        if self._ollama_blocks_translate():
            return
        if len(self._text_of(self.original)) == 0:
            return

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
        bridge = getattr(self, "_models_bridge", None)
        if bridge is not None:
            bridge.close()
        super().destroy()

    def run(self) -> None:
        self.mainloop()


def run_app() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    TranslateTextWindow().run()
