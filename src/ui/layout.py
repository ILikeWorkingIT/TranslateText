from __future__ import annotations

import customtkinter as ctk

from ui.messages import (
    BASE_PROMPT,
    LABEL_CUSTOM_INSTRUCTION,
    LABEL_MODEL,
    LABEL_OPEN_FILE,
    LABEL_ORIGINAL,
    LABEL_PROGRESS,
    LABEL_SAVE_TRANSLATION,
    LABEL_TRANSLATE,
    LABEL_TRANSLATION,
    SAMPLE_MODEL,
    SAMPLE_MODELS,
    SAMPLE_ORIGINAL,
    SAMPLE_TRANSLATION,
)
from ui.theme import (
    BG,
    CARD,
    FIELD,
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

FONT_LABEL = ("Segoe UI", 13)
FONT_BODY = ("Segoe UI", 14)
FONT_BUTTON = ("Segoe UI", 13)
FONT_PRIMARY = ("Segoe UI", 15, "bold")
FONT_STATUS = ("Segoe UI", 12)


class TranslateTextWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TranslateText")
        self.geometry("1280x820")
        self.minsize(980, 640)
        self.configure(fg_color=BG)
        self._status_after = ""
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_panes()
        self._build_instruction()
        self._build_footer()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 8))
        header.grid_columnconfigure(0, weight=1)

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=0, sticky="e")
        self._ghost_button(actions, LABEL_OPEN_FILE).pack(side="left", padx=6)
        self._ghost_button(actions, LABEL_SAVE_TRANSLATION).pack(side="left", padx=6)

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
            values=list(SAMPLE_MODELS),
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
            command=self._on_model,
        )
        self.model.set(SAMPLE_MODEL)
        self.model.pack(side="left")

    def _build_panes(self) -> None:
        panes = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        panes.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        panes.grid_columnconfigure(0, weight=1)
        panes.grid_columnconfigure(1, weight=1)
        panes.grid_rowconfigure(0, weight=1)

        self._text_card(panes, LABEL_ORIGINAL, SAMPLE_ORIGINAL).grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )
        self._text_card(panes, LABEL_TRANSLATION, SAMPLE_TRANSLATION).grid(
            row=0, column=1, sticky="nsew", padx=(10, 0)
        )

    def _build_instruction(self) -> None:
        card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=LINE,
        )
        card.grid(row=2, column=0, sticky="ew", padx=28, pady=8)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text=LABEL_CUSTOM_INSTRUCTION,
            font=FONT_LABEL,
            text_color=LABEL,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        box = ctk.CTkTextbox(
            card,
            height=96,
            corner_radius=10,
            fg_color=FIELD,
            text_color=TEXT,
            border_width=0,
            font=FONT_BODY,
        )
        box.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        box.insert("0.0", BASE_PROMPT)

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        footer.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 8))
        footer.grid_columnconfigure(0, weight=1)

        progress_row = ctk.CTkFrame(footer, fg_color="transparent")
        progress_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        progress_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            progress_row,
            text=LABEL_PROGRESS,
            font=FONT_LABEL,
            text_color=MUTED,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        bar = ctk.CTkProgressBar(
            progress_row,
            height=8,
            corner_radius=8,
            fg_color=TRACK,
            progress_color=PROGRESS,
        )
        bar.grid(row=0, column=1, sticky="ew")
        bar.set(0)

        actions = ctk.CTkFrame(footer, fg_color="transparent")
        actions.grid(row=1, column=0)
        ctk.CTkButton(
            actions,
            text=LABEL_TRANSLATE,
            width=220,
            height=46,
            corner_radius=12,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=PRIMARY_TEXT,
            font=FONT_PRIMARY,
            command=lambda: self._toast(LABEL_TRANSLATE),
        ).pack()

        self.status = ctk.CTkLabel(
            footer,
            text="",
            font=FONT_STATUS,
            text_color=TOAST,
            anchor="center",
        )
        self.status.grid(row=2, column=0, pady=(12, 10))

    def _text_card(self, parent: ctk.CTkFrame, title: str, sample: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=LINE,
        )
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_LABEL,
            text_color=LABEL,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        box = ctk.CTkTextbox(
            card,
            corner_radius=10,
            fg_color=FIELD,
            text_color=TEXT,
            border_width=0,
            font=FONT_BODY,
        )
        box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 16))
        box.insert("0.0", sample)
        return card

    def _ghost_button(self, parent: ctk.CTkFrame, label: str) -> ctk.CTkButton:
        return ctk.CTkButton(
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
            command=lambda clicked=label: self._toast(clicked),
        )

    def _on_model(self, value: str) -> None:
        self._toast(f"{LABEL_MODEL}: {value}")

    def _toast(self, label: str) -> None:
        self.status.configure(
            text=f"Макет: «{label}». Функционал приложения не выполняется."
        )
        if self._status_after:
            self.after_cancel(self._status_after)
        self._status_after = self.after(3200, lambda: self.status.configure(text=""))

    def run(self) -> None:
        self.mainloop()


def run_app() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    TranslateTextWindow().run()
