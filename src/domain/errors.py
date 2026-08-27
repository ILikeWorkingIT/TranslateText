from __future__ import annotations


class AppLayerError(Exception):
    """База ошибок прикладного слоя. Текст для Пользователя — в messages.py."""


class OllamaTimeoutError(AppLayerError):
    """Нет ответа Ollama дольше таймаута запроса."""


class OllamaUnavailableError(AppLayerError):
    """Нет соединения с локальным API или список моделей пуст."""


class OllamaModelError(AppLayerError):
    """Модель отказала на запрос фрагмента."""


class DocumentParseError(AppLayerError):
    """Файл своего формата, текст не извлечён."""


class SourceLimitExceededError(AppLayerError):
    """Оригинал длиннее 100 000 символов Unicode."""


class EmptyInstructionError(AppLayerError):
    """Пустая кастомная инструкция без согласия Пользователя."""


class QueueBusyError(AppLayerError):
    """Повторный старт перевода, пока очередь inProgress."""


class ExportWriteError(AppLayerError):
    """Сбой записи файла при «Сохранить перевод»."""
