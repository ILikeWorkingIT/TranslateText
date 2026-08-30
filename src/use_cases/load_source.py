"""Загрузка исходника в сеанс (UC-002, FT-003). Без виджетов."""

from __future__ import annotations

from domain.models import LoadSourceCommand
from services.extract_source import ExtractSource


class LoadSource:
    def __init__(self) -> None:
        self._extract = ExtractSource()

    def run(self, command: LoadSourceCommand) -> str:
        return self._extract.run(command.path, command.source_format)
