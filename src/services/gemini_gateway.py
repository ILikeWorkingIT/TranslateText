"""Облачный канал перевода Groq. Не заменяет Ollama."""

from __future__ import annotations

import logging
import os
import re
import ssl
import sys
from pathlib import Path

import httpx

from domain.errors import CloudKeyMissingError, CloudRateLimitError, CloudTranslationError
from domain.models import CLOUD_MODELS, DEFAULT_CLOUD_MODEL

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1/"
GROQ_CHAT_URL = f"{GROQ_BASE_URL}chat/completions"
CLOUD_TEMPERATURE = 0.2
CLOUD_REQUEST_GAP_SECONDS = 2.0
CLOUD_SYSTEM_PROMPT = (
    "You are an expert comic book translator. Translate English speech to Russian.\n"
    "Rules:\n"
    "- Use informal 'ты'/'иди' (never 'вы').\n"
    "- The text states 'The woman said to the woman'. "
    "Use STRICTLY female verb and pronoun endings "
    "(e.g., 'я получила', 'ты знала', 'я пришла').\n"
    "- Adapt gender-neutral slang contextually "
    "(e.g., 'That sucks, man' -> 'Это отстой, подруга' or 'Ну и отстой').\n"
    "- Output ONLY the final Russian translation. Keep line numbers. "
    "No quotes around the whole output, no explanations."
)
_KEY_MISSING = "Ключ Groq не задан. Укажите GROQ_API_KEY в файле .env."
_RATE_LIMIT = "Превышен лимит запросов Groq в минуту (RPM)."
_PROTECTED = re.compile(r"\b(?:Amanda|Sardu|Dawson|I)\b")


def prepare_cloud_text(text: str) -> str:
    """Края и нижний регистр только у текста запроса, не у поля оригинала."""
    stripped = text.strip()
    if stripped == "":
        return stripped
    return _lowercase_keeping_marks(stripped)


def translate_cloud(text: str, *, model: str | None = None, client: httpx.Client | None = None) -> str:
    """Перевод EN→RU через OpenAI-совместимый эндпоинт Groq."""
    prepared = prepare_cloud_text(text)
    chosen = _selected_model(model)
    api_key = _api_key()
    if api_key == "":
        logger.error(_KEY_MISSING)
        raise CloudKeyMissingError(_KEY_MISSING)
    payload = {
        "model": chosen,
        "temperature": CLOUD_TEMPERATURE,
        "messages": [
            {"role": "system", "content": CLOUD_SYSTEM_PROMPT},
            {"role": "user", "content": prepared},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    own_client = client is None
    http = client or httpx.Client(
        timeout=120.0,
        follow_redirects=False,
        verify=ssl.create_default_context(),
    )
    try:
        response = http.post(GROQ_CHAT_URL, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        logger.error("Groq: %s", exc)
        raise CloudTranslationError(str(exc)) from exc
    finally:
        if own_client:
            http.close()
    if response.status_code == 429:
        logger.error(_RATE_LIMIT)
        raise CloudRateLimitError(_RATE_LIMIT)
    if response.status_code >= 400:
        message = _http_error(response)
        logger.error(message)
        raise CloudTranslationError(message)
    content = _assistant_text(response)
    if content.strip() == "":
        logger.error("Groq вернул пустой перевод")
        raise CloudTranslationError("Groq вернул пустой перевод")
    return content


def _lowercase_keeping_marks(fragment: str) -> str:
    kept: list[str] = []

    def hold(match: re.Match[str]) -> str:
        kept.append(match.group(0))
        return f"\x00{len(kept) - 1}\x00"

    masked = _PROTECTED.sub(hold, fragment).lower()
    for index, word in enumerate(kept):
        masked = masked.replace(f"\x00{index}\x00", word)
    if fragment[:1].isalpha() and masked[:1].isalpha():
        masked = fragment[0] + masked[1:]
    return masked


def _selected_model(model: str | None) -> str:
    _load_dotenv()
    chosen = model if model is not None else DEFAULT_CLOUD_MODEL
    if chosen not in CLOUD_MODELS:
        return DEFAULT_CLOUD_MODEL
    return chosen


def _api_key() -> str:
    _load_dotenv()
    return os.environ.get("GROQ_API_KEY", "").strip()


def _dotenv_folders() -> tuple[Path, ...]:
    folders = [Path.cwd()]
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        folders.extend((exe_dir, exe_dir.parent, exe_dir.parent.parent))
    else:
        folders.append(Path(__file__).resolve().parents[2])
    return tuple(folders)


def _load_dotenv() -> None:
    for folder in _dotenv_folders():
        path = folder / ".env"
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.strip().partition("=")
            if separator != "=" or name == "" or name.startswith("#"):
                continue
            os.environ.setdefault(name, value.strip().strip('"').strip("'"))
        return


def _http_error(response: httpx.Response) -> str:
    try:
        body = response.json()
    except (ValueError, TypeError):
        body = {}
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            return str(error["message"])
        if isinstance(error, str):
            return error
    return f"Groq ответил {response.status_code}"


def _assistant_text(response: httpx.Response) -> str:
    try:
        body = response.json()
    except (ValueError, TypeError) as exc:
        raise CloudTranslationError(str(exc)) from exc
    if not isinstance(body, dict):
        raise CloudTranslationError("Groq вернул не объект")
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise CloudTranslationError("Groq не вернул choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise CloudTranslationError("Groq вернул пустой choices")
    message = first.get("message")
    if not isinstance(message, dict):
        raise CloudTranslationError("Groq не вернул message")
    content = message.get("content")
    if not isinstance(content, str):
        raise CloudTranslationError("Groq не вернул текст перевода")
    return content
