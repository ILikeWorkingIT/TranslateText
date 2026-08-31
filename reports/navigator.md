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
| Vision & Scope | `artifacts/vision-scope.md` (команда `/vision`, роль tech-writer) |
| ТЗ по ГОСТ 34.602-89 | `artifacts/tz-gost-34-602.md` (команда `/gost-3460289`, роль tech-writer; шаблон имени `artifacts/tz-gost-<код>.md`) |
| Текущий этап, гейт, APPROVED | `reports/pm-state.md` |
| След требований → код / коммиты | `reports/traceability.md` |
| Снимок GitHub-бэклога | `reports/backlog-state.md` |
| Срезы продукта TranslateText | `reports/checklist.md` |
| Команды и скиллы | `.cursor/list-commands.md` |
| Закрытые ответы | `requirements/answers-project.md` |

## Сценарии

| ID | Когда | Первый шаг |
| --- | --- | --- |
| S1 | Новый репозиторий без требований | Перенос MAS — `documentation/mas-description.md` §10: `.cursor/`, `reports/templates/`, `navigator.md`, `AGENTS.md`; пустые каталоги; `/pm` → заполнить `project-config.md` (сценарий S1). Далее `/ft`, `/nft`, `/us`, `/vision`, `/gost-3460289` … |
| S2 | Код есть, требований нет | ПМ + временное чтение `src/`. Команды `/feature-from-code` в срезе A нет — не запускать. |
| S3 | Описанный проект (этот репозиторий) | `/pm` (статус или старт среза). ПМ читает `checklist.md` и `pm-state.md`. Срез: сначала `/app-layer` (если слой), затем `/frontend` (если UI), затем `/new-tests` и `/use-tests` отдельными ходами. После пакета — `/qc-stage`. Следующий глобальный этап — только после «утверждаю». |
| S4 | Отчёт заказчику | Команды `/report-weekly` в срезе A нет. Факты брать из уже существующих отчётов, не выдумывать. |
| S5 | Обычный чат | Пользователь вызывает slash-команду напрямую. Оркестрация ПМ на паузе. |

## Документация для заказчика (tech-writer)

Не срезы MVP (`reports/checklist.md`, S-01…S-13). Отдельные артефакты в `artifacts/`.

| Артефакт | Команда | Файл в этом репозитории | Когда |
| --- | --- | --- | --- |
| Vision & Scope | `/vision` | `artifacts/vision-scope.md` | Ранний или после части пакета требований; режимы «ранний» / «после пакета», правка, перенос ответов; не заменяет ФТ/НФТ. Согласование: «согласую Vision» / «принимаю Vision & Scope» — не путать с «утверждаю» этапа MAS |
| ТЗ по ГОСТ 34.602-89 | `/gost-3460289` | `artifacts/tz-gost-34-602.md` | После согласованных ФТ/НФТ/US/UC (рекомендуется); режимы: создание, реструктуризация, стилизация, аудит. Согласование: «согласую ТЗ» / «принимаю техническое задание» — не путать с «утверждаю» этапа MAS |

Скиллы: `.cursor/skills/skill-vision.md`, `.cursor/skills/skill-gost-3460289.md`. Закрытые Q&A — код `VS` (Vision) и `TZ` (ТЗ) в `requirements/answers-project.md`.

## Этот репозиторий сейчас

Сценарий S3. Продукт — TranslateText (Python, customtkinter, локальный Ollama). Свой HTTP-сервер не создавать. Артефакты документации: `artifacts/vision-scope.md`, `artifacts/tz-gost-34-602.md` (см. § «Документация для заказчика»).
