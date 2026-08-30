"""UC-006 / FT-032 / FT-033: гейт несохранённого перевода. Диалог — UI."""

from __future__ import annotations

from domain.errors import UnsavedTranslationError


def is_unsaved_translation(translation_text: str, translation_saved: bool) -> bool:
    """FT-033, A0097: непустое поле без успешного «Сохранить перевод» после изменения."""
    return len(translation_text) > 0 and not translation_saved


def require_unsaved_confirmed(
    translation_text: str,
    translation_saved: bool,
    *,
    confirmed: bool,
) -> None:
    """Команда «Перевести» / загрузки не принимается, пока UC-006 не подтверждён."""
    if not is_unsaved_translation(translation_text, translation_saved):
        return
    if not confirmed:
        raise UnsavedTranslationError("unsaved translation")


def saved_after_translation_text_change(translation_text: str) -> bool:
    """FT-033: пустое поле — сохранённое; любое непустое изменение — нет."""
    return len(translation_text) == 0


def saved_after_export_success() -> bool:
    """FT-004 (сохранённость): успешное «Сохранить перевод» до следующего изменения."""
    return True


def translation_after_source_loaded() -> tuple[str, bool]:
    """A0099: после успешной загрузки исходника очистить поле перевода."""
    return ("", True)
