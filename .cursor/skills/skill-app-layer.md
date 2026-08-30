---
name: skill-app-layer
description: >-
  Use when the user asks to implement the application/use-case layer behind
  the desktop window: Ollama HTTP client, Unicode text splitting, docx/pdf
  extract, export (UC-003 / FT-044), unsaved-translation warning (FT-032),
  translation queue, typed errors, worker-thread
  contract, or runs /app-layer. Pure Python modules — no FastAPI/Flask, no
  customtkinter in domain/services/use_cases. Do not use for UI chrome
  (/frontend), click-only mockups (/ui-prototyping), or running the suite
  (/use-tests).
disable-model-invocation: true
owner: back-developer
---

# Прикладной слой (слой за кнопками)

Скилл автономного application-инженера (ручной вызов **`/app-layer`**). Не подставляй факты другого проекта. Поведение — только из `Axxxx`, ФТ, UC, доменной модели и явного запроса.

Стек: **Python 3.11+**. HTTP к Ollama — **httpx** (синхронный `Client`). Документы — **python-docx**, **pypdf**. Эти три зависимости дописывай в `src/requirements.txt` только когда реализуешь шлюз или файлы. Пакет `ollama` не ставь. `customtkinter` в прикладной слой не импортируй.

---

## 1. Роль и архитектурная философия (слой за кнопками)

Роль: **Senior Application Engineer**. Выполняй SOP до конца. Не спрашивай, куда класть Ollama, если это уже сказано здесь.

### Тотальный запрет UI в прикладном слое

Пакеты `src/domain/`, `src/services/`, `src/use_cases/` — **прикладной слой**. В каждом их `.py` запрещено:

| Запрещено | Примеры |
| --- | --- |
| Импорт UI | `customtkinter`, `tkinter`, `tkinter.*`, `CTk*`, `messagebox`, `filedialog`, `ttk` |
| Обход | `importlib` UI, отложенный импорт в функции, `TYPE_CHECKING` ради виджетов |
| Виджеты и цикл | `after`, `mainloop`, `update()`, `CTk()`, цвета, `qa_id` |
| UX-вывод | `messagebox`, toast, `print` / `logging` как сообщение Пользователю |

Проверка до «готово»: в этих пакетах нет подстрок `customtkinter` и `tkinter`.

**Чистый контракт данных.** Вход и выход — `str`, `pathlib.Path`, `int`, `bool`, `tuple[...]`, frozen `@dataclass`. Колбэк — `Protocol` с одним методом, аргумент — dataclass события. Запрещены `dict[str, Any]`, «мешок» `dict`, виджет в сигнатуре, `None` вместо ошибки.

GIL **не** делает Tk потокобезопасным. Прикладной слой не трогает виджеты даже «на мгновение».

### Разделение ответственности

| Слой | Знает | Не знает |
| --- | --- | --- |
| `src/ui/` (хром) | виджеты, тема, `messages.py`, `qa_id` | httpx, нарезка, парсинг внутри `_build_*` |
| `src/ui/bridge.py` (клей) | `Thread(daemon=True)`, `widget.after(0, ...)`, два счётчика id, `winfo_exists`, `OllamaPort.close()` на закрытии окна | алгоритм нарезки, JSON Ollama |
| `src/domain/` | VO, команды, события, `AppLayerError` | Tk, httpx, ФС |
| `src/services/` | одна служба, I/O своей зоны | виджеты, `messages.py` |
| `src/use_cases/` | координация одной команды | виджеты, создание `httpx.Client` |

Соблюдай **DRY**, **KISS**, имена служб из `requirements/domain-model.md` (`SplitText`, `ExtractSource`, `StartTranslation`, `ExportTranslation`, `OllamaGateway`), канон `Axxxx` → ФТ/UC → домен. Не расширяй MVP.

Copy-in / events-out: в use case **не** передавай живой объект, которым UI одновременно пишет поля. Передай frozen-команду со строками и путями; состояние виджетов обновляй **только** в UI-потоке по событиям.

### Запрет лишней инфраструктуры

Запрещено: FastAPI, Flask, Django, Starlette, uvicorn, aiohttp-сервер, свой REST TranslateText, Gradio, Streamlit, облачный перевод, OpenAI-прокси. Все модули — обычные классы и функции. Ollama уже HTTP-сервер на машине; TranslateText — **клиент**, не сервер.

Адрес: `http://127.0.0.1:11434`. Перевод: `POST /api/chat`. Модели: `GET /api/tags`. Иной host или ключ — дефект (FT-012, FT-013, NFT-009). У httpx: `follow_redirects=False`.

### Куда класть код

| Что | Модуль |
| --- | --- |
| команды, VO, события, `OllamaPort` | `src/domain/models.py` |
| `AppLayerError` и наследники | `src/domain/errors.py` |
| `SplitText` | `src/services/split_text.py` |
| `OllamaGateway` (реализация порта) | `src/services/ollama_gateway.py` |
| `ExtractSource` | `src/services/extract_source.py` |
| ~~автосохранение~~ | **снято** (`A0096`, `A0112`, `A0115`); не создавать `autosave.py` |
| `ExportTranslation` | `src/services/export_translation.py` |
| `StartTranslation` | `src/use_cases/start_translation.py` |
| опрос моделей FT-045 | `src/use_cases/refresh_models.py` |
| загрузка файла | `src/use_cases/load_source.py` |
| один воркер + `after` | **только** `src/ui/bridge.py` |

Не плоди `src/repositories/`, `src/api/`, `src/adapters/`, DI-контейнер. Порт — `Protocol` в `domain`, одна реализация в `OllamaGateway`.

### Редирект (сразу)

- Макет «вид + клики» → `/ui-prototyping`.
- Новые виджеты, тема, `qa_id`, тексты подсказок → `/frontend`.
- Клей `bridge.py` в этом скилле **разрешён**; вёрстку и `messages.py` не переписывай, кроме импорта use case.
- Только UI-тесты → `/new-tests`. Только прогон → `/use-tests`.
- «Сервер / OpenAPI / localhost» → отказ.

После кода **не** запускай `/use-tests`. Unit без GUI — шаг 3 SOP.

### Типизация

- Публичные функции и методы, включая `-> None`. **`Any` запрещён.**
- Импорты — вверху модуля, не в теле.
- Длина — `len(str)` (Unicode, FT-030). Не байты. **Не токены модели.** `tiktoken`, tokenizer HuggingFace, «лимит токенов» — запрещены.

---

## 2. SOP для Use Cases

### 0. Режим (один)

| Режим | Когда | Что делать |
| --- | --- | --- |
| **фича** | нарезка, Ollama, файлы, очередь, предупреждение FT-032 | шаги 1 → 3; клей `bridge.py` — только если кнопке уже есть куда звать |
| **баг** | таймаут, `request_id`, битый файл, лимит имён | канон → минимальный дифф |

Нет канона / `@` / описания команды — спроси с рекомендацией.

Один ход = **один** use case или **одна** служба. Координатор **вызывает** уже существующие службы, не копирует их. Не реализуй FT-001…050 сразу.

### Шаг 1. Ядро

Читай узко: запрос → `Axxxx` / ФТ / UC → `requirements/domain-model.md` → словарь данных.

Зафиксируй: какая команда; какие VO; какие инварианты (`inProgress` без второй очереди; снимок модели/инструкции; `nextIndex`; `incomplete` ≠ полный перевод); чего служба не делает.

Вне MVP не кодируй: отмена очереди Пользователем, другие языки, облако, свой сервер, OCR, журнал для Пользователя.

### Шаг 2. Изолированный сервис

1. Типы и исключения — `src/domain/`.
2. Атомарная служба — `src/services/`. Зависимости (шлюз) — **в конструктор**, не глобальный `Client()`.
3. Координация — `src/use_cases/`. Use case **синхронный и блокирующий**: его зовут уже из воркера. Use case **не** создаёт `Thread` / `Process` / `asyncio`.
4. `StartTranslation` не создаёт `httpx.Client`: получает `OllamaPort`.
5. Путь ручного «Сохранить перевод» — из диалога Пользователя (FT-004), не фиксированная папка `output`.

```python
class OllamaPort(Protocol):
    def list_models(self) -> tuple[str, ...]: ...
    def translate_fragment(self, *, model: str, instruction: str, source: str) -> str: ...
    def close(self) -> None: ...

@dataclass(frozen=True)
class StartTranslationCommand:
    request_id: int  # только translation_request_id, не id опроса моделей
    original_text: str
    instruction: str
    instruction_confirmed: bool
    model: str

class StartTranslation:
    def __init__(self, ollama: OllamaPort) -> None: ...
    def run(
        self,
        command: StartTranslationCommand,
        *,
        stop_event: threading.Event,
        on_event: Callable[[QueueEvent], None],
    ) -> None: ...
```

`stop_event.is_set()` смотри **между** фрагментами и **до** следующего `translate_fragment`. Это **не** прерывает уже идущий синхронный `httpx.post`: он может держать воркер до таймаута 60 с. Поэтому:

- `OllamaGateway` владеет `httpx.Client`, реализует `close()` (`Client.close()` / выход из `with`).
- На `WM_DELETE_WINDOW` клей: `stop_event.set()`, затем `ollama.close()` (с UI-потока), чтобы сорвать сокет, если библиотека это позволяет.
- **Не** делай `thread.join()` без таймаута в обработчике закрытия — снова зависнет `mainloop`.
- Если `close()` не разбудил `post`, воркер **доживает** текущий запрос (≤ 60 с), затем видит `stop_event` и выходит **без** `on_event` / `after`. Это не отмена очереди Пользователем (A0044), а разбор закрытия окна. В комментариях кода не обещай «мгновенный abort».
- После любого исключения httpx: если `stop_event.is_set()`, **не** переводи очередь в `incomplete` и **не** зови колбэк — окно уже не принимает UI. Иначе сбой живого сеанса — обычный FT-028.

Диалог FT-029 — **только UI**. В команду: согласие уже дано или инструкция непустая. Иначе `EmptyInstructionError`, промпт в поле не подставляй.

### Шаг 3. Тест-мост (до клея)

Службы проектируй так, чтобы pytest покрыл их **без** окна, **без** живого Ollama, **без** импорта `src.ui`.

- Каталог `tests/`, имена `test_should_<поведение>_when_<условие>`. Не unittest. Не `mainloop`, не `CTk()`.
- Подмена: фейк `OllamaPort`, `httpx.MockTransport`, `tmp_path` для тестов `ExportTranslation`.
- Импорт `src.services.*` / `src.use_cases.*` не должен тянуть `customtkinter`.
- Минимум на затронутую зону: happy path; нарезка (≤5000 один фрагмент; абзац >5000; слово целое; никто >5000; `> 100_000` → `SourceLimitExceededError` из `SplitText`); таймаут 60 с → `incomplete`, склейка предыдущих жива; `.txt` cp1251 после неудачного utf-8; битый/пустой файл → `DocumentParseError`; `close()` шлюза.
- Контракт времени: у клиента `timeout=60` на запрос фрагмента (FT-028 / A0031). Живой GPU и NFT-001 (p95) не гоняй и не объявляй сданными.
- Клей `bridge.py` пиши **после** зелёных unit по службе. `/use-tests` в этом ходе не запускай.

---

## 3. Ключевые задачи

### Нарезка (`SplitText`)

Только `src/services/split_text.py`. Пользователь границы не задаёт (FT-021).

| Правило | Канон |
| --- | --- |
| Единица | символы Unicode `len(text)` (FT-030, A0015) |
| ≤ 5000 | один `Fragment` (FT-016) |
| > 5000 и ≤ 100 000 | очередь, не один запрос на весь текст (FT-015, FT-019) |
| > 100 000 | `SplitText` бросает `SourceLimitExceededError`, список фрагментов не возвращает (FT-023). Ollama не звать. `StartTranslation` **не** дублирует проверку длины: вызывает `SplitText` и даёт ошибке всплыть |
| Цель | 4000–5000; единственный/последний могут быть < 4000; **никто > 5000** (FT-017, A0032) |
| Границы | абзацы, не полуслово (FT-018) |
| Абзац > 5000 | предложения; предложение > 5000 — пробелы, слово не рвать (FT-025) |

Абзац: `\n\n`, иначе `\n`. Предложение: `.` / `!` / `?` + пробел или конец блока. Без NLP.

Пакуй абзацы, пока следующий не превысит 5000; окно 4000–5000, кроме хвоста. `order` с 0 (A0076). Возврат: `tuple[Fragment, ...]`. `Workspace` не мутируй. Единственный источник `SourceLimitExceededError` — `SplitText`.

### Ollama (`OllamaGateway`)

Один долгоживущий синхронный клиент на шлюз:

```python
self._client = httpx.Client(
    base_url="http://127.0.0.1:11434",
    timeout=60.0,
    follow_redirects=False,
)
```

Обязан `close()` (и лучше `__enter__` / `__exit__`, делегирующие к `Client`). Не оставляй сокеты открытыми до GC. Не создавай новый `Client` на каждый фрагмент без `close` предыдущего.

| Операция | Как |
| --- | --- |
| Модели | `GET /api/tags` → `tuple[str, ...]`, без фильтра (FT-005) |
| Фрагмент | `POST /api/chat`, `stream=False`; `system` = снимок инструкции, `user` = фрагмент, `model` = снимок |
| 60 с | весь запрос фрагмента. Тишина / `ReadTimeout` / `ConnectTimeout` → `OllamaTimeoutError` → очередь `incomplete` (FT-028, A0031) |
| Нет сети / пустой список | `OllamaUnavailableError`. Текст `start_ollama.bat` **не** клади в `args` исключения — это `messages.py` (FT-024) |
| Отказ модели | `OllamaModelError` → FT-028 |
| Стрим токенов | запрещён. Прогресс FT-022 — доля **символов исходных фрагментов** |
| Повтор запроса | не ретрай без канона |

Тело текста и инструкции — только на этот адрес (NFT-009). Возврат: `str` или исключение, не `None`.

### Документы (`ExtractSource`)

Диалог и фильтр FT-042 — UI. Служба получает `Path`.

| Формат | Как |
| --- | --- |
| `.txt`, `.md` | Сначала UTF-8 с BOM (`utf-8-sig`). Если `UnicodeDecodeError` — один фолбек `cp1251` (Windows-1251). Если снова ошибка — `DocumentParseError`. Не `latin-1` и не `errors="replace"` (скрытая порча текста) |
| `.docx` | python-docx, абзацы в сырой текст |
| `.pdf` | pypdf, `extract_text` по страницам |
| иное | не парсить |

Успех: непустой текст после `strip`. Пусто, одни пробелы/переводы строк, скан без текста, битый файл, ошибка библиотеки → `DocumentParseError`; перевод не стартовать (FT-039). Отмена диалога: службу не звать (FT-047). OCR / PyMuPDF — нет.

### Сохранение

ФС не в окне. Ручной экспорт — путь из диалога Пользователя (FT-004, FT-043).

**Автосохранение (FT-034…FT-040): снято** (`A0096`, `A0112`, `A0115`). Не реализовывать. Несохранённый перевод — UC-006 / FT-032…FT-033.

**Экспорт:** только `.txt` / `.docx` (FT-046). Диалог замены — UI (FT-043). Сбой → `ExportWriteError`, перевод не стирать (FT-044). Пустой перевод — не вызывать (FT-027).

---

## 4. Контракт Worker Thread

Тяжёлое (Ollama, парсинг, запись ФС, вся очередь фрагментов) **запрещено** в UI-потоке. Иначе `mainloop` встанет, окно «зависнет».

`asyncio` и Tk не смешивай. Воркеры: `threading.Thread(..., daemon=True)` **только в `src/ui/bridge.py`**.

### Кто стартует поток

| Кто | Делает | Не делает |
| --- | --- | --- |
| `bridge.py` | один daemon-поток на одну **задачу своего типа** (перевод или опрос моделей); в потоке — `use_case.run(...)`; колбэк: если `winfo_exists()` — `widget.after(0, ...)`; на закрытии — `stop_event.set()`, `ollama.close()`, `after_cancel` | нарезку, JSON Ollama; `join()` без таймаута |
| Use case / службы | синхронный I/O в том потоке, куда их вызвали; `stop_event` **между** фрагментами (не внутри `post`); `on_event` с dataclass | `Thread`, `after`, импорт Tk, `Client.close` из цикла нарезки |
| Хром окна | два счётчика (ниже); в `apply` сверка **своего** id | блокирующий httpx в `command=`; один глобальный id на всё |

Колбэк, который видит use case, с точки зрения слоя «просто функция». Потокобезопасность даёт **клей**: `on_event` из воркера не пишет в виджеты напрямую.

Не-daemon поток после закрытия окна запрещён (процесс зависнет). `update()` / вложенный `mainloop` «подождать Ollama» запрещены.

### Событие очереди

```python
@dataclass(frozen=True)
class QueueEvent:
    request_id: int
    status: Literal["inProgress", "completed", "incomplete"]
    next_index: int
    processed_source_chars: int
    total_source_chars: int
    translation_so_far: str
```

Процент считает UI. Один фрагмент: 0 % до ответа, 100 % после. Служба процент не хранит.

После фрагмента: склейка в `translation_so_far` (только уже успешные фрагменты), `nextIndex += 1`, `inProgress`.

Сбой **текущего** фрагмента: `status = incomplete`; `nextIndex` не увеличивать; в `translation_so_far` оставить склейку **уже успешных** фрагментов (не укорачивать её и не дописывать обрывок сбоя). Не помечать как полный перевод (FT-028).

Успех всей очереди: `completed`, новое значение **заменяет** правое поле (FT-035); текст несохранён до «Сохранить перевод» (FT-033).

### Два счётчика id (перевод ≠ опрос моделей)

**Запрещён один глобальный `request_id` на окно.** Иначе клик/фокус «Модель» (FT-045) во время `inProgress` увеличит id, и клей отбросит события перевода — очередь умрёт на полуслове. Список «Модель» во время перевода остаётся доступным (просмотр полей не отменяет очередь, FT-011 / A0052). Опрос **не** запрещай из‑за `inProgress`.

| Счётчик | Кто увеличивает | С чем сверяет клей |
| --- | --- | --- |
| `translation_request_id` | только старт «Перевести» (и новый запуск после конца/обрыва очереди) | только `QueueEvent.request_id` и поле перевода / прогресс |
| `models_refresh_request_id` | только опрос FT-045 (старт, клик, фокус «Модель») | только событие списка моделей |

1. В команду `StartTranslation` клади **только** `translation_request_id`. В `RefreshModels` — только `models_refresh_request_id`.
2. Клей перевода: `if event.request_id != translation_request_id: return` **до** записи в поля. Клей опроса **не** читает translation id.
3. Пока очередь `inProgress`, второй `StartTranslation` → `QueueBusyError` (FT-031). Второй **опрос моделей** при этом **легален** (свой поток, свой id). Не стартуй второй поток **перевода**.
4. Отмены очереди Пользователем нет (A0044). `stop_event` — закрытие окна, не кнопка «Отмена».

Закрытие окна и застрявший `post` — §2 (после сигнатуры `run`): `close()` клиента, без бесконечного `join`, иначе дожитие ≤ 60 с без колбэка в мёртвое окно.

---

## 5. Антипаттерны

**Нарушение буквы = нарушение духа.**

### Файлы-боги и лишний сервер

Нарезка, парсинг, httpx — не методы окна. Пайплайн в `layout.py` — стоп. FastAPI «чтобы UI сходил на localhost» — стоп.

### Гонки

Событие без своего id или клей с **одним** глобальным счётчиком на перевод и FT-045 — дефект. Не запускай второй **перевод**, не увеличив `translation_request_id`. Опрос моделей крутит только `models_refresh_request_id`.

### Исключения

Сервисы не молчат (`except: pass` / глотать в `str | None`). Не зовут alert. База: `AppLayerError`. Наследники:

| Класс | Когда |
| --- | --- |
| `OllamaTimeoutError` | нет ответа дольше 60 с |
| `OllamaUnavailableError` | нет соединения или пустой список моделей |
| `OllamaModelError` | отказ модели на фрагмент |
| `DocumentParseError` | формат свой, текст не извлечён (в т.ч. пустой/пробелы) |
| `SourceLimitExceededError` | `SplitText`, оригинал > 100 000 символов Unicode |
| `EmptyInstructionError` | пустая инструкция без согласия |
| `QueueBusyError` | повторный старт при `inProgress` |
| `ExportWriteError` | сбой ручного файла |

UI ловит `AppLayerError` и берёт фразу из `messages.py`. В исключении — тип и техническая деталь для теста, не простыня FT-024.

Не плоди второе имя `ParserError`: канон слоя — `DocumentParseError`.

### Стоп-краны

| Отговорка | Факт |
| --- | --- |
| «httpx в `layout.py` быстрее» | Служба + `bridge.py`. |
| «Свой FastAPI» | Сервера нет. |
| «Резать по токенам» | Только Unicode. |
| «Подожду в клике» | Зависший `mainloop`. |
| «Стрим в прогресс» | Доля исходных символов. |
| «OCR для пустого PDF» | `DocumentParseError`. |
| «Кнопка Отмена очереди» | Вне MVP. |
| «Поток внутри use case, так надёжнее» | Двойные потоки. Поток — только bridge. |
| «Один request_id на перевод и на список моделей» | Два счётчика. Иначе FT-045 убивает очередь. |
| «join воркера в WM_DELETE» | Зависший UI. `stop_event` + `close()`, daemon без вечного join. |

Зависимости сверх `httpx`, `python-docx`, `pypdf` — только по явной просьбе.

---

## 6. Формат коммуникации

Краткость. Не лей модуль. Не коммить и не пиши в память без просьбы.

**Что сделано** — режим; use case / служба (имя DDD + FT/UC).

**Модули** — `domain/` / `services/` / `use_cases/`; был ли `src/ui/bridge.py`.

**Типы** — команда, событие, порт, исключения. Без `Any`.

**Edge cases** — только сделанные: лимит 100k (`SplitText`); utf-8 затем cp1251; таймаут 60 с; `incomplete` без потери склейки; два id; `Client.close()`; `inProgress`.

**Как проверить** — список `test_should_…`; что подменено. Живой Ollama для unit не нужен. Предложи `/use-tests`; если менялся хром — `/frontend` и `/new-tests`. В этом запуске QA не выполняй.
