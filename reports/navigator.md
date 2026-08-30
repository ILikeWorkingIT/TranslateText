# Навигатор MAS

С чего начать агенту. Детали ролей — `documentation/mas-description.md`. Стек — `reports/project-config.md`. Состояние этапа — `reports/pm-state.md`.

## Точка входа

Предпочтительный вход — `/pm` (`.cursor/commands/pm.md`, агент `.cursor/agents/agent-pm.md`).
Пустой `/pm` — статус и предложение следующего этапа, не автозапуск всех ролей.
Прямые slash-команды (`/ft`, `/frontend`, `/app-layer` …) допустимы и не удалены.

## Карта

| Что нужно | Куда |
| --- | --- |
| Стек и интеграции | `reports/project-config.md` |
| Текущий этап, гейт, APPROVED | `reports/pm-state.md` |
| След требований → код / коммиты | `reports/traceability.md` |
| Снимок GitHub-бэклога | `reports/backlog-state.md` |
| Срезы продукта TranslateText | `reports/checklist.md` |
| Команды и скиллы | `.cursor/list-commands.md` |
| Закрытые ответы | `requirements/answers-project.md` |

## Сценарии

| ID | Когда | Первый шаг |
| --- | --- | --- |
| S1 | Новый репозиторий без требований | Скопировать `.cursor/` и `reports/templates/`. Заполнить `project-config.md`. ПМ ведёт этапы документации существующими `/ft`, `/nft`, `/us` … |
| S2 | Код есть, требований нет | ПМ + временное чтение `src/`. Команды `/feature-from-code` в срезе A нет — не запускать. |
| S3 | Описанный проект (этот репозиторий) | `/pm` (статус или старт среза). ПМ читает `checklist.md` и `pm-state.md`. Срез: сначала `/app-layer` (если слой), затем `/frontend` (если UI), затем `/new-tests` и `/use-tests` отдельными ходами. После пакета — `/qc-stage`. Следующий глобальный этап — только после «утверждаю». |
| S4 | Отчёт заказчику | Команды `/report-weekly` в срезе A нет. Факты брать из уже существующих отчётов, не выдумывать. |
| S5 | Обычный чат | Пользователь вызывает slash-команду напрямую. Оркестрация ПМ на паузе. |

## Этот репозиторий сейчас

Сценарий S3. Продукт — TranslateText (Python, customtkinter, локальный Ollama). Свой HTTP-сервер не создавать.
