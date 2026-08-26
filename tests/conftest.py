import sys
from pathlib import Path

import customtkinter as ctk
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = Path(__file__).resolve().parent
for path in (SRC, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ui.layout import TranslateTextWindow


@pytest.fixture
def window():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = TranslateTextWindow()
    app.withdraw()
    app.update_idletasks()
    yield app
    after_id = getattr(app, "_status_after", "")
    if after_id:
        try:
            app.after_cancel(after_id)
        except Exception:
            pass
    app.destroy()
