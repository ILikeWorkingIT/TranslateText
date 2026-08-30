# TranslateText

Локальное минималистичное десктоп-приложение на Python для перевода больших объёмов текста, книг и документов **между английским и русским** (направления EN→RU и RU→EN). Перевод бесплатный: движок — локальный Ollama, семейство моделей Qwen2.5.

Стек MVP: Python, окно на **customtkinter**, локальный HTTP API Ollama. Своего серверного бэкенда в ТЗ нет. Gradio и Streamlit названы в предварительном ТЗ; для окна приложения **не используются** (`A0173`).

## Как открыть интерфейс

Рабочее окно — **приложение** (тёмная студия на customtkinter), не сайт в браузере.

Откройте сами:

1. Готовое приложение без Python и Cursor: в проводнике запустите `artifacts\TranslateText.exe` (окно **TranslateText**). Пересборка: `src\build-exe.bat`.
2. Из исходников: в проводнике запустите `src\run-ui.bat` (поставит customtkinter при необходимости).

Браузер открывать не нужно. Для перевода нужен запущенный локальный Ollama. Как поставить приложение и Ollama **на другом компьютере без Docker** — `reports/instruction.md`.

Запасная команда в обычном терминале (не в чате агента):

    cd src
    python -m pip install -r requirements.txt
    python app.py

Нужен Python с tcl/tk. Из `run-ui.bat` / `app.py` и из exe доступны перевод, файлы и очередь (не «пустой макет»). Отдельный прогон только макета без прикладного слоя — через `/ui-prototyping`, если понадобится заново.

## Локальный Ollama

Запросы перевода идут на локальный адрес Ollama, не в облако. Сведения о машине — `documentation/other-description.md` (заметки из другого проекта; для TranslateText нужны только факты про Ollama, не пайплайн Stable Diffusion).

На этой машине (по `other-description.md`):

- API: `http://127.0.0.1:11434` (`POST /api/chat`)
- контейнер Docker: `ollama_local`, данные: `F:\Docker\ollama\ollama_data`
- пример модели: `qwen2.5:3b` (уже скачана)
- в той заметке Ollama запущена **на CPU**, GPU RTX 3060 отдана Forge

Стенд TranslateText закрыт ответами `A0161`, `A0024`, `A0028`: на время перевода GPU RTX 3060 отдавать Ollama, Forge параллельно не гонять. Норма времени — p95 ≤ 60 с на фрагмент 500–700 символов для `qwen2.5:3b`. Если Ollama недоступна — сообщение с путём `F:\Docker\Ollama\start_ollama.bat` (`A0008`).

## Документация API этого репозитория

Своего OpenAPI-контракта (`requirements/openapi.yaml`) нет: продукт ходит в API Ollama, своего HTTP-сервера в ТЗ нет. Если контракт появится по команде `/openai`, способ просмотра (Swagger UI / ReDoc) будет описан здесь и скриптами в `requirements`.

## Входные документы

- `documentation/Specification.md` — предварительное ТЗ (UI, разбиение на фрагменты, прогресс, Ollama, форматы файлов).
- `documentation/other-description.md` — среда Ollama на этой машине (адрес, Docker, модель, CPU/GPU).
- `documentation/project-structure-v1-1.md` — структура папок и правила именования (синхронизируется с `.cursor/rules/rule-structure.mdc`).

**Иерархия источников:** предварительное ТЗ — в `documentation/`; уточнения — в `requirements/answers-project.md` (`Axxxx`) и согласованных пакетах ФТ (`A0125`), НФТ (`A0127`), US (`A0132`), UC (`A0126`), доменной модели (`A0138`) и словаря данных (`A0139`); поздние уточнения — `A0142`–`A0176` и далее. При конфликте с предварительным ТЗ приоритет у `Axxxx` и согласованных требований. Поведение агента — в `AGENTS.md`; память проекта — в `reports/agent-memory.md` (команда «запомни» / `/pin-memory`). Порядок срезов MVP — `reports/checklist.md`.

## Что должно уметь приложение (по ТЗ и `Axxxx`)

- Выбрать **направление перевода** EN→RU или RU→EN (`FT-051`).
- Открыть файл `.txt`, `.md`, `.docx`, `.pdf` в левое окно «Оригинальный текст»; туда же можно вставить текст вручную.
- Правое **поле перевода** с подписью «Русский перевод» или «Английский перевод»; сохранить в `.txt` или `.docx`.
- Выбрать модель Ollama из списка, который опрашивает локальное API.
- Поле «Кастомная инструкция»; по умолчанию — базовый промпт текущего направления (с усилением «не задание», `A0143`).
- Кнопка «Перевести»; предупреждение о несохранённом переводе перед «Перевести» или «Открыть файл» (`FT-032`, US-006).
- Пока идёт перевод — команда **«Отменить перевод»** (`FT-054`, US-010).
- Длинный текст незаметно режется на фрагменты (целевой 500–700 символов, не длиннее 700), перевод по очереди, склейка справа; в запросе к Ollama — сырой фрагмент и хвост без маркеров `<<<`/`>>>` (`FT-055`).
- Индикатор прогресса при переводе большого документа.
- Если Ollama недоступна или список моделей пуст — «Перевести» заблокирована; по наведению подсказка, почему кнопка недоступна.

## Структура папок

| Папка / файл | Назначение | Статус | Коммит / репозиторий | Индексация ИИ |
| --- | --- | --- | --- | --- |
| `documentation` | ТЗ и материалы разработчика | есть | да | да |
| `requirements` | есть `glossary.md`, `answers-project.md`, `functional-requirements.md`, `non-functional-requirements.md`, `domain-model.md`, `data-dictionary.md`, `user-stories/`, `use-cases/`; `openapi.yaml` и скрипты просмотра API — целевые (своего HTTP нет) | частично | да | да |
| `diagrams` | текстовые диаграммы (PlantUML / Mermaid / BPMN); есть Mermaid | есть | да (текст) | да (текст; картинки и бинарники — нет) |
| `.cursor/skills` | промпты и инструкции для AI | есть | да | да |
| `.cursor/rules` | правила для AI | есть | да | да |
| `.cursor/commands` | команды Cursor (полный список — `.cursor/list-commands.md`: `/pm`, `/ft`, `/nft`, `/us`, `/uc`, `/qc-ft-nft`, `/qc-us-uc`, `/qc-ddd`, `/qc-stage`, `/diagram-bpmn`, `/diagram-mermaid`, `/ddd`, `/data-dictionary`, `/ui-prototyping`, `/frontend`, `/app-layer`, `/openai`, `/new-tests`, `/use-tests`, `/pin-memory`) | есть | да | да |
| `.cursor/agents` | девять Custom Agents MAS (`agent-pm` … `agent-tester`) | есть | да | да |
| `src` | исходный код MVP: окно customtkinter (`run-ui.bat`, `build-exe.bat`, `app.py`, `ui/`) и прикладной слой (`domain/`, `services/`, `use_cases/` по `/app-layer`) | есть | да | да |
| `reports` | есть `checklist.md`, `instruction.md`, `nft-001-measurement.md`, `agent-memory.md`, `incompatibility-ft-nft.md`, `incompatibility-us-uc.md`, `domain-model-review.md`, MAS-отчёты; `test-run.md` — по прогону `/use-tests` | частично | да | да |
| `artifacts` | вне `requirements`; готовый `TranslateText.exe` (сборка `src/build-exe.bat`, в git не кладётся) | есть (exe локально) | exe — нет | да (папка) |
| `tests` | автотесты pytest (desktop/customtkinter), карта `tests/coverage.md` | есть | да | да |
| `test-data` | зарезервирована; только по прямому заданию разработчика | целевая | да | да |
| `legacy` | исходники и аналитика другого проекта; только по прямому заданию | — | нет | нет |
| `old-skills` | скиллы из другого проекта; только по прямому заданию | — | нет | нет |

Корневые ориентиры: `AGENTS.md` (правила агента), `.cursor/list-commands.md` (список команд и скиллов).

`legacy/` и `old-skills/` исключены в `.gitignore` и `.cursorignore`. Не читать их самостоятельно, если разработчик явно не прикрепил файл через `@`.
