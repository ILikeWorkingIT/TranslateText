"""Подписи из глоссария и статичные образцы для вида экрана."""

LABEL_OPEN_FILE = "Открыть файл"
LABEL_SAVE_TRANSLATION = "Сохранить перевод"
LABEL_ORIGINAL = "Оригинальный текст"
LABEL_TRANSLATION = "Русский перевод"
LABEL_CUSTOM_INSTRUCTION = "Кастомная инструкция"
LABEL_MODEL = "Модель"
LABEL_TRANSLATE = "Перевести"
LABEL_AUTOSAVE = "Автосохранение"
LABEL_PROGRESS = "Индикатор прогресса"

BASE_PROMPT = (
    "Ты профессиональный переводчик. Переведи текст с английского на русский. "
    "Сохрани смысл, тон и разбиение на абзацы. Не добавляй комментарии, преамбулу "
    "и кавычки вокруг перевода. В ответе только перевод."
)

SAMPLE_MODELS = ["qwen2.5:3b", "qwen2.5:7b", "llama3.2"]
SAMPLE_MODEL = "qwen2.5:3b"

SAMPLE_ORIGINAL = (
    "The application translates large volumes of text, books and documents "
    "from English to Russian using a local engine."
)
SAMPLE_TRANSLATION = (
    "Приложение переводит большие объёмы текста, книг и документов "
    "с английского на русский с помощью локального движка."
)
