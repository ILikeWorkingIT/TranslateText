from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ui.messages import (
    DIRECTION_EN_RU,
    DIRECTION_VALUES,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_DIRECTION,
    LABEL_MODEL,
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_PROGRESS,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
)
from ui.theme import (
    BG,
    CARD,
    FIELD,
    FONT_BODY,
    FONT_BUTTON,
    FONT_LABEL,
    FONT_PRIMARY,
    FONT_STATUS,
    GHOST,
    GHOST_HOVER,
    LABEL,
    LINE,
    MUTED,
    PRIMARY,
    PRIMARY_HOVER,
    PRIMARY_TEXT,
    PROGRESS,
    TEXT,
    TOAST,
    TRACK,
)


def _set_qa_id(widget: ctk.CTkBaseClass, qa_id: str) -> None:
    widget.qa_id = qa_id


def _focus_field_on_click(widget: ctk.CTkBaseClass, box: ctk.CTkTextbox) -> None:
    def _focus(_event: object, target: ctk.CTkTextbox = box) -> None:
        target.focus_set()

    widget.bind("<Button-1>", _focus)


def _ghost_button(
    parent: ctk.CTkFrame,
    *,
    label: str,
    command: Callable[[], None],
    qa_id: str,
) -> ctk.CTkButton:
    button = ctk.CTkButton(
        parent,
        text=label,
        width=150,
        height=36,
        corner_radius=10,
        fg_color=GHOST,
        hover_color=GHOST_HOVER,
        text_color=TEXT,
        border_width=1,
        border_color=LINE,
        font=FONT_BUTTON,
        command=command,
    )
    _set_qa_id(button, qa_id)
    return button


def _text_card(
    parent: ctk.CTkFrame,
    *,
    title: str,
    qa_id: str,
) -> tuple[ctk.CTkFrame, ctk.CTkLabel, ctk.CTkTextbox]:
    card = ctk.CTkFrame(
        parent,
        fg_color=CARD,
        corner_radius=16,
        border_width=1,
        border_color=LINE,
    )
    card.grid_rowconfigure(1, weight=1)
    card.grid_columnconfigure(0, weight=1)
    title_label = ctk.CTkLabel(
        card,
        text=title,
        font=FONT_LABEL,
        text_color=LABEL,
        anchor="w",
    )
    title_label.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
    box = ctk.CTkTextbox(
        card,
        corner_radius=10,
        fg_color=FIELD,
        text_color=TEXT,
        border_width=0,
        font=FONT_BODY,
    )
    box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 16))
    _set_qa_id(box, qa_id)
    _focus_field_on_click(title_label, box)
    _focus_field_on_click(card, box)
    return card, title_label, box


class HeaderBar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        *,
        on_open_file: Callable[[], None],
        on_save_translation: Callable[[], None],
        on_model: Callable[[str], None],
        on_direction: Callable[[str], None],
        model_values: tuple[str, ...],
        selected_model: str,
        selected_direction: str,
    ) -> None:
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=0, sticky="e")
        self.open_file = _ghost_button(
            actions,
            label=LABEL_OPEN_FILE,
            command=on_open_file,
            qa_id="btn-open-file",
        )
        self.open_file.pack(side="left", padx=6)
        self.save = _ghost_button(
            actions,
            label=LABEL_SAVE_TRANSLATION,
            command=on_save_translation,
            qa_id="btn-save-translation",
        )
        self.save.pack(side="left", padx=6)

        direction_wrap = ctk.CTkFrame(actions, fg_color="transparent")
        direction_wrap.pack(side="left", padx=(18, 6))
        ctk.CTkLabel(
            direction_wrap,
            text=LABEL_DIRECTION,
            font=FONT_LABEL,
            text_color=LABEL,
        ).pack(side="left", padx=(0, 8))
        self.direction = ctk.CTkComboBox(
            direction_wrap,
            values=list(DIRECTION_VALUES),
            width=110,
            height=36,
            corner_radius=10,
            border_width=1,
            border_color=LINE,
            fg_color=FIELD,
            button_color=GHOST,
            button_hover_color=GHOST_HOVER,
            dropdown_fg_color=CARD,
            dropdown_hover_color=GHOST_HOVER,
            dropdown_text_color=TEXT,
            text_color=TEXT,
            font=FONT_BUTTON,
            command=on_direction,
            state="readonly",
        )
        self.direction.set(selected_direction or DIRECTION_EN_RU)
        self.direction.pack(side="left")
        _set_qa_id(self.direction, "combo-direction")

        model_wrap = ctk.CTkFrame(actions, fg_color="transparent")
        model_wrap.pack(side="left", padx=(18, 6))
        ctk.CTkLabel(
            model_wrap,
            text=LABEL_MODEL,
            font=FONT_LABEL,
            text_color=LABEL,
        ).pack(side="left", padx=(0, 8))
        self.model = ctk.CTkComboBox(
            model_wrap,
            values=list(model_values),
            width=170,
            height=36,
            corner_radius=10,
            border_width=1,
            border_color=LINE,
            fg_color=FIELD,
            button_color=GHOST,
            button_hover_color=GHOST_HOVER,
            dropdown_fg_color=CARD,
            dropdown_hover_color=GHOST_HOVER,
            dropdown_text_color=TEXT,
            text_color=TEXT,
            font=FONT_BUTTON,
            command=on_model,
        )
        self.model.set(selected_model)
        self.model.pack(side="left")
        _set_qa_id(self.model, "combo-model")


class TextPanes(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        original_card, _original_title, self.original = _text_card(
            self, title=LABEL_ORIGINAL, qa_id="field-original"
        )
        original_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        translation_card, self.translation_title, self.translation = _text_card(
            self, title=LABEL_TRANSLATION, qa_id="field-translation"
        )
        translation_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def set_translation_title(self, title: str) -> None:
        self.translation_title.configure(text=title)


class InstructionCard(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, *, initial_prompt: str) -> None:
        super().__init__(
            master,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=LINE,
        )
        self.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(
            self,
            text=LABEL_CUSTOM_INSTRUCTION,
            font=FONT_LABEL,
            text_color=LABEL,
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        self.instruction = ctk.CTkTextbox(
            self,
            height=96,
            corner_radius=10,
            fg_color=FIELD,
            text_color=TEXT,
            border_width=0,
            font=FONT_BODY,
        )
        self.instruction.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        self.instruction.insert("0.0", initial_prompt)
        _set_qa_id(self.instruction, "field-instruction")
        _focus_field_on_click(title, self.instruction)
        _focus_field_on_click(self, self.instruction)


class FooterBar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        *,
        on_translate: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)

        progress_row = ctk.CTkFrame(self, fg_color="transparent")
        progress_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        progress_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            progress_row,
            text=LABEL_PROGRESS,
            font=FONT_LABEL,
            text_color=MUTED,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.progress = ctk.CTkProgressBar(
            progress_row,
            height=8,
            corner_radius=8,
            fg_color=TRACK,
            progress_color=PROGRESS,
        )
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress.set(0)
        _set_qa_id(self.progress, "progress-bar")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=1, column=0)
        self.translate_wrap = ctk.CTkFrame(actions, fg_color="transparent")
        self.translate_wrap.pack()
        self.translate = ctk.CTkButton(
            self.translate_wrap,
            text=LABEL_TRANSLATE,
            width=220,
            height=46,
            corner_radius=12,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=PRIMARY_TEXT,
            font=FONT_PRIMARY,
            command=on_translate,
        )
        self.translate.pack()
        _set_qa_id(self.translate, "btn-translate")

        self.status = ctk.CTkLabel(
            self,
            text="",
            font=FONT_STATUS,
            text_color=TOAST,
            anchor="center",
            justify="center",
            wraplength=900,
        )
        self.status.grid(row=2, column=0, pady=(12, 10))
        _set_qa_id(self.status, "label-status")
