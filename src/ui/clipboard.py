from __future__ import annotations

import ctypes
import html
import re
import sys
import tkinter
from ctypes import wintypes

_HTML_TYPES = ("HTML Format", "CF_HTML", "text/html")
_PLAIN_TYPES = (
    "UNICODETEXT",
    "CF_UNICODETEXT",
    "UTF8_STRING",
    "STRING",
    "text/plain",
)

_CF_UNICODETEXT = 13
_user32: ctypes.WinDLL | None = None
_kernel32: ctypes.WinDLL | None = None

if sys.platform == "win32":
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _user32.OpenClipboard.argtypes = [wintypes.HWND]
    _user32.OpenClipboard.restype = wintypes.BOOL
    _user32.CloseClipboard.argtypes = []
    _user32.CloseClipboard.restype = wintypes.BOOL
    _user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
    _user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
    _user32.GetClipboardData.argtypes = [wintypes.UINT]
    _user32.GetClipboardData.restype = wintypes.HANDLE
    _user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
    _user32.RegisterClipboardFormatW.restype = wintypes.UINT
    _kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    _kernel32.GlobalLock.restype = ctypes.c_void_p
    _kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    _kernel32.GlobalUnlock.restype = wintypes.BOOL


def read_plain_clipboard(widget: tkinter.Misc) -> str:
    """Текст из буфера: WinAPI Unicode/HTML, затем Tcl."""
    if sys.platform == "win32":
        win_text = _read_windows_clipboard()
        if win_text:
            return win_text
    try:
        value = widget.clipboard_get()
    except tkinter.TclError:
        value = ""
    if isinstance(value, str) and value:
        return value
    for clipboard_type in _PLAIN_TYPES:
        raw = _clipboard_type(widget, clipboard_type)
        if raw:
            return raw
    for clipboard_type in _HTML_TYPES:
        raw = _clipboard_type(widget, clipboard_type)
        if raw:
            plain = plain_text_from_html_clipboard(raw)
            if plain:
                return plain
    return ""


def write_plain_clipboard(widget: tkinter.Misc, text: str) -> None:
    """Текст в буфер через Tcl — читается Ctrl+V и другими приложениями."""
    widget.clipboard_clear()
    widget.clipboard_append(text)


def plain_text_from_html_clipboard(raw: str) -> str:
    fragment = _html_fragment(raw)
    fragment = re.sub(r"(?is)<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"(?is)</p\s*>", "\n", fragment)
    fragment = re.sub(r"(?is)<[^>]+>", "", fragment)
    return html.unescape(fragment).replace("\xa0", " ").strip()


def _clipboard_type(widget: tkinter.Misc, clipboard_type: str) -> str:
    try:
        value = widget.clipboard_get(type=clipboard_type)
    except tkinter.TclError:
        return ""
    if isinstance(value, str) and value:
        return value
    return ""


def _html_fragment(raw: str) -> str:
    start_mark = raw.find("<!--StartFragment-->")
    end_mark = raw.find("<!--EndFragment-->")
    if start_mark != -1 and end_mark != -1:
        return raw[start_mark + len("<!--StartFragment-->") : end_mark]
    start = _html_offset(raw, "StartFragment")
    end = _html_offset(raw, "EndFragment")
    if start is not None and end is not None and start < end <= len(raw):
        return raw[start:end]
    return raw


def _html_offset(raw: str, name: str) -> int | None:
    match = re.search(rf"{name}:(\d+)", raw)
    if match is None:
        return None
    return int(match.group(1))


def _read_windows_clipboard() -> str:
    """CF_UNICODETEXT / HTML Format через WinAPI — то, что читает Word."""
    if _user32 is None or _kernel32 is None:
        return ""
    if not _user32.OpenClipboard(None):
        return ""
    try:
        if _user32.IsClipboardFormatAvailable(_CF_UNICODETEXT):
            text = _lock_unicode(_CF_UNICODETEXT)
            if text:
                return text
        html_fmt = _user32.RegisterClipboardFormatW("HTML Format")
        if html_fmt and _user32.IsClipboardFormatAvailable(html_fmt):
            raw = _lock_bytes_as_text(html_fmt)
            if raw:
                plain = plain_text_from_html_clipboard(raw)
                if plain:
                    return plain
    finally:
        _user32.CloseClipboard()
    return ""


def _lock_unicode(fmt: int) -> str:
    if _user32 is None or _kernel32 is None:
        return ""
    handle = _user32.GetClipboardData(fmt)
    if not handle:
        return ""
    pointer = _kernel32.GlobalLock(handle)
    if not pointer:
        return ""
    try:
        return ctypes.wstring_at(pointer)
    finally:
        _kernel32.GlobalUnlock(handle)


def _lock_bytes_as_text(fmt: int) -> str:
    if _user32 is None or _kernel32 is None:
        return ""
    handle = _user32.GetClipboardData(fmt)
    if not handle:
        return ""
    pointer = _kernel32.GlobalLock(handle)
    if not pointer:
        return ""
    try:
        raw = ctypes.string_at(pointer)
    finally:
        _kernel32.GlobalUnlock(handle)
    for encoding in ("utf-8", "utf-16-le", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""
