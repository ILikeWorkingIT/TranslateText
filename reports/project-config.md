# Конфигурация проекта

Заполняется по фактам репозитория. Не выдумывать стек. Источник правды для MAS — этот файл, не предварительное ТЗ, если они расходятся с `Axxxx`.

## Продукт

| Поле | Значение |
| --- | --- |
| Имя | TranslateText |
| Тип | Локальное desktop-приложение (окно, не сайт) |
| Назначение | Перевод больших текстов и документов EN↔RU через локальный Ollama |
| Сценарий MAS | S3 (описанный проект с кодом). Предпочтительный вход — `/pm` |
| Трекер | GitHub: `https://github.com/ILikeWorkingIT/TranslateText.git` |

## Стек

| Слой | Технология | Где зафиксировано |
| --- | --- | --- |
| Язык | Python 3 | `src/`, `tests/` |
| UI | customtkinter (окно приложения, не Gradio/Streamlit/браузер) | `src/ui/`, `src/app.py` |
| Прикладной слой | `src/domain/`, `src/services/`, `src/use_cases/` | `/app-layer` |
| Транспорт UI↔слой | `src/ui/bridge.py` | `/app-layer`, `/frontend` |
| HTTP-клиент | httpx (только к локальному Ollama) | `src/requirements.txt`, `src/services/ollama_gateway.py` |
| Свой HTTP-сервер | нет | README, ТЗ |
| FastAPI / Flask / облако | запрещены | `rule-python.mdc` |
| СУБД / NoSQL | нет | — |
| OpenAPI своего API | нет (`requirements/openapi.yaml` не создавать без своего сервера) | README |
| Тесты | pytest, поверхность desktop/customtkinter | `tests/` |
| Зависимости | `src/requirements.txt` (`customtkinter`, `httpx`, `python-docx`, `pypdf`) | — |
| Запуск UI | `artifacts/TranslateText.exe` (Проводник, без Python) или `src/run-ui.bat`; не терминал агента | README |

## Интеграции

| Система | Адрес / заметка | Источник |
| --- | --- | --- |
| Ollama | `http://127.0.0.1:11434`, `POST /api/chat`, контейнер `ollama_local` | `documentation/other-description.md`; `A0008`, `A0023`, `A0024`, `A0028` |
| Модель-пример | `qwen2.5:3b` | `other-description.md` |

Параметры пайплайна Stable Diffusion из `other-description.md` в стек TranslateText не входят.

## Владельцы артефактов (NFT и совместные)

| Артефакт | Владелец | Исполнительная команда |
| --- | --- | --- |
| Vision & Scope | tech-writer | `/vision` |
| ТЗ по ГОСТ 34.602-89 | tech-writer | `/gost-3460289` |
| ФТ | analyst | `/ft` |
| НФТ | architect | `/nft` (скилл `skill-nft` не переписывать) |
| US / UC / глоссарий / BPMN / Mermaid | analyst | `/us`, `/uc`, `/diagram-bpmn`, `/diagram-mermaid` |
| DDD / словарь данных / OpenAPI | architect | `/ddd`, `/data-dictionary`, `/openai` |
| QC ФТ/НФТ, US/UC, DDD, `/qc-stage` | anatomist | `/qc-ft-nft`, `/qc-us-uc`, `/qc-ddd`, `/qc-stage` |
| Макет окна | designer | `/ui-prototyping` |
| Рабочий UI | front-developer | `/frontend` |
| Прикладной слой | back-developer | `/app-layer` |
| Автотесты и прогон | tester | `/new-tests`, `/use-tests` |

## Ограничения MAS в этом репозитории

- Предпочтительный вход — ПМ. Прямые slash-команды допустимы.
- Существующие команды `/ft` … `/use-tests` не заменять оркестрационными обёртками.
- Переход глобального этапа — только после явного «утверждаю» / «принимаю этап» в чате ПМ. ПМ записывает `Stage: <id>: APPROVED` в `reports/pm-state.md` и не ставит эту строку сам.
- Delivery-команды (`/backlog-sync`, `/full-cycle`, `/commit-audit` и др.) в срезе A не развёрнуты.
