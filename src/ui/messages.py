"""Подписи из глоссария и статичные образцы для вида экрана."""

LABEL_OPEN_FILE = "Открыть файл"
LABEL_SAVE_TRANSLATION = "Сохранить перевод"
LABEL_ORIGINAL = "Оригинальный текст"
LABEL_TRANSLATION = "Русский перевод"
LABEL_TRANSLATION_EN = "Английский перевод"
LABEL_DIRECTION = "Направление перевода"
LABEL_CUSTOM_INSTRUCTION = "Кастомная инструкция"
LABEL_MODEL = "Модель"
LABEL_TRANSLATE = "Перевести"
LABEL_PROGRESS = "Индикатор прогресса"

DIRECTION_EN_RU = "EN→RU"
DIRECTION_RU_EN = "RU→EN"
DIRECTION_VALUES = (DIRECTION_EN_RU, DIRECTION_RU_EN)

HINT_NO_TEXT = "Нет текста для перевода"
HINT_OLLAMA_DOWN = "Ollama не работает"
HINT_IN_PROGRESS = "Идёт перевод"
STATUS_OLLAMA_UNAVAILABLE = (
    "Локальный Ollama недоступен. Запустите файл start_ollama.bat "
    "в папке F:\\Docker\\Ollama"
)

BASE_PROMPT = (
    "Ты профессиональный переводчик. Переведи текст с английского на русский. "
    "Сохрани смысл, тон и разбиение на абзацы. Не добавляй комментарии, преамбулу "
    "и кавычки вокруг перевода. В ответе только перевод."
)

BASE_PROMPT_RU_EN = (
    "Ты профессиональный переводчик. Переведи текст с русского на английский. "
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


def base_prompt_for_direction(direction: str) -> str:
    if direction == DIRECTION_RU_EN:
        return BASE_PROMPT_RU_EN
    return BASE_PROMPT


def translation_label_for_direction(direction: str) -> str:
    if direction == DIRECTION_RU_EN:
        return LABEL_TRANSLATION_EN
    return LABEL_TRANSLATION
