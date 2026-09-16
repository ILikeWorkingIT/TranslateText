# Инструкция: перенос MAS и методологии из TranslateText в другой проект

Документ для **агента целевого репозитория**. Пользователь кладёт копию проекта-образца в `legacy/` (или аналог) и передаёт этот файл через `@`.

Цель: перенести **мультиагентную систему (MAS), скиллы, правила, команды и шаблоны процесса** — без содержимого требований TranslateText (ФТ, US, UC, глоссарий, ответы `Axxxx`, код продукта, отчёты прогона).

Источник правды по составу папок образца: `legacy/.../documentation/project-structure-v1-1.md` и `legacy/.../.cursor/rules/rule-structure.mdc`. Описание ролей MAS: `legacy/.../documentation/mas-description.md`.

---

## 1. Контекст и запреты

TranslateText — desktop-приложение перевода через локальный Ollama (Python + customtkinter). Часть скиллов и правил **заточена под этот домен и стек**. Копировать «всё подряд без правок» нельзя.

| Делать | Не делать |
| --- | --- |
| Брать методологию (как писать ФТ/US/UC, QC, Vision, ГОСТ, оркестрацию PM) | Копировать заполненные `requirements/`, `artifacts/vision-scope.md`, `artifacts/tz-gost-*.md` как канон нового продукта |
| После копирования **санитизировать** файлы со стеком/доменом | Подставлять факты TranslateText (Ollama, нарезка 500–700, EN↔RU, `A0125`…) в новый проект |
| Создавать пустые/шаблонные `reports/project-config.md`, `pm-state.md` под **этот** репозиторий | Копировать `reports/agent-memory.md`, `checklist.md`, `pm-state.md`, замеры NFT, `test-run.md` образца |
| Читать `legacy/` только по явному `@` / поручению пользователя | Самостоятельно индексировать весь `legacy/` «на всякий случай» |

В целевом репо папка `legacy/` обычно в `.gitignore` / `.cursorignore`. Без `@` на этот файл или на нужный путь из `legacy/` — не лезь внутрь.

---

## 2. Что брать (обязательный каркас)

Корень ниже — относительно копии в `legacy/<имя-папки-TranslateText>/`. В целевом проекте пути те же, без префикса `legacy/...`.

### 2.1. Мультиагентная оболочка

| Откуда | Зачем |
| --- | --- |
| `.cursor/agents/agent-*.md` (девять ролей) | Custom Agents / subagents: pm, analyst, architect, tech-writer, anatomist, designer, front-developer, back-developer, tester |
| `.cursor/skills/skill-agent-*.md` | Маршрутизаторы ролей (что делает агент, куда писать, чего не трогать) |
| `.cursor/rules/role-*.mdc` | Input Manifest ролей (что читать/писать); после переноса поправить globs под структуру **целевого** `src/` |
| `.cursor/commands/pm.md`, `qc-stage.md`, `pin-memory.md` | Оркестрация этапов, гейт стадии, запись в память агента |
| `.cursor/list-commands.md` | Реестр команд; обновить под фактический набор после переноса |
| `AGENTS.md` | Общие инварианты (не выдумывать факты, `Axxxx`, формат ответа). **Вычистить** § про стек TranslateText и конкретные ID пакетов `A0125`… |
| `documentation/mas-description.md` | Описание MAS, перенос и создание с нуля — справочник для агента и человека |

### 2.2. Методология требований и артефактов (универсально)

Брать **скилл + команду** парами. Содержимое таблиц ФТ/US образца **не** брать.

| Команда | Скилл | Зачем |
| --- | --- | --- |
| `/vision` | `skill-vision` | Vision & Scope |
| `/gost-3460289` | `skill-gost-3460289` | ТЗ по ГОСТ 34.602-89 |
| `/ft` | `skill-ft` | Функциональные требования |
| `/nft` | `skill-nft` | Нефункциональные требования |
| `/us` | `skill-us` | User Stories |
| `/uc` | `skill-uc` | Use Cases (Cockburn) |
| `/qc-ft-nft` | `skill-quality-control-ft-nft` | QC ФТ/НФТ |
| `/qc-us-uc` | `skill-quality-control-us-uc` | QC US/UC |
| `/ddd` | `skill-ddd` | Доменная модель |
| `/qc-ddd` | `skill-quality-control-ddd` | QC доменной модели |
| `/data-dictionary` | `skill-data-dictionary` | Словарь данных |
| `/diagram-bpmn` | `skill-diagram-bpmn` | BPMN 2.0 |
| `/diagram-mermaid` | `skill-diagram-mermaid` | Mermaid (flowchart, DFD, class, sequence, C4) |
| `/openai` | `skill-openai` | OpenAPI + Swagger/ReDoc (только если у нового продукта свой HTTP API) |

Сопутствующие правила (брать):

- `rule-answers-project.mdc` — база закрытых ответов `Axxxx` в `requirements/answers-project.md`
- `rule-analyst-self-learning.mdc` — память агента только по явной команде
- `rule-propose-qc-ft-nft.mdc`, `rule-propose-qc-us-uc.mdc` — напоминания про QC после пакета

### 2.3. Шаблоны отчётов MAS

| Откуда | Зачем |
| --- | --- |
| `reports/templates/project-config.template.md` | Стек и профиль продукта целевого репо |
| `reports/templates/pm-state.template.md` | Состояние этапов |
| `reports/templates/review-gate-report.template.md` | Отчёт `/qc-stage` |
| Остальные шаблоны в `reports/templates/` | backlog/traceability/daily/commit-audit — по мере нужды |

Скопировать шаблоны → в целевом проекте создать рабочие файлы из шаблонов **пустыми/под факты нового продукта**, не копировать заполненные `project-config.md` / `pm-state.md` / `navigator.md` TranslateText.

### 2.4. Структура папок (как идея, не как клон дерева src)

Брать логику из `rule-structure.mdc` / `project-structure-v1-1.md`:

- `documentation/`, `requirements/`, `diagrams/`, `artifacts/`, `reports/`, `.cursor/{skills,rules,commands,agents}`, `tests/`
- соглашения имён: `us-NNN`, `uc-NNN`, `diagram-mermaid-NNN`, `bpmn-NNN`, отчёты QC

**Переписать** описание `src/`, launcher’ов, exe, Ollama, customtkinter под стек целевого продукта (или оставить placeholder «заполнить из project-config»).

---

## 3. Что брать с обязательной санитизацией

Эти файлы полезны как **паттерн разделения UI / прикладной слой / тесты**, но текст завязан на TranslateText. После копирования обобщить под `project-config` целевого репо.

| Файл | Проблема | Что сделать |
| --- | --- | --- |
| `skill-app-layer.md`, команда `/app-layer` | Ollama `:11434`, `SplitText` 500–700, qwen, EN↔RU, конкретные `Axxxx`/`FT`/`UC` | Оставить идею: domain/services/use_cases без UI-импортов, порт внешнего сервиса, клей потоков. Убрать домен перевода и константы образца |
| `skill-frontend-developer.md`, `/frontend` | Python + customtkinter как единственный стек | Заменить стек на факт из `project-config`; сохранить чеклист состояний (loading/error/empty), qa_id / test selectors по смыслу |
| `skill-ui-prototyping.md`, `/ui-prototyping` | Анти-примеры «перевод/нарезка»; упор на окно, не сайт | Оставить «макет без бизнес-логики»; убрать примеры домена TranslateText; если целевой продукт — веб, переписать анти-Gradio/«только окно» |
| `skill-new-tests-front.md`, `skill-use-tests-front.md`, `/new-tests`, `/use-tests` | Примеры нарезки/склейки из ФТ | Оставить pytest/web vs desktop, отчёт `reports/test-run.md`; вычистить доменные примеры |
| `rule-python.mdc` | Заголовок и стек TranslateText | Переименовать/переписать под язык целевого репо или удалить, если не Python |
| `rule-anti-overengineering.mdc`, `rule-anti-sycophancy.mdc` | Пометки «под TranslateText», customtkinter | Оставить дух правил; убрать привязку к продукту |
| `rule-structure.mdc` | Конкретные файлы `clipboard.py`, `TranslateText.spec`, NFT-001 | Обобщить список `src/` и отчётов |
| `role-front-developer.mdc`, `role-back-developer.mdc`, `role-designer.mdc` | Globs и запреты под CTk / Ollama / `bridge.py` | Подставить пути и границы слоёв целевого `src/` |
| `agent-front-developer.md`, `agent-back-developer.md`, `agent-designer.md` | Упоминания Ollama, customtkinter | Согласовать с санитизированными скиллами |
| `AGENTS.md` | Ориентиры пакетов `A0125`…, стек UI/Ollama | Оставить принципы; убрать ID ответов и стек образца |
| `.cursor/list-commands.md` | Описание `/app-layer` про Ollama/нарезку | После правок скиллов обновить формулировки |

Если целевой продукт **не** desktop Python + локальная модель — не копируй `skill-app-layer` / `skill-frontend-developer` дословно: возьми только разделение ролей front/back и напиши скиллы заново под стек.

---

## 4. Что не брать (содержимое продукта-образца)

| Не копировать в канон целевого проекта | Почему |
| --- | --- |
| `requirements/**` (ФТ, НФТ, US, UC, glossary, domain-model, data-dictionary, answers-project) | Это продукт TranslateText, не методология |
| `artifacts/vision-scope.md`, `artifacts/tz-gost-*.md` | Готовые документы чужого продукта |
| `src/**`, `tests/**`, `TranslateText.exe`, `*.spec` | Код и тесты образца |
| `reports/agent-memory.md`, `checklist.md`, `pm-state.md`, `project-config.md`, `navigator.md`, `traceability.md`, `backlog-state.md`, `test-run.md`, `nft-001-measurement.md`, `incompatibility-*.md`, `domain-model-review.md`, `review-report.md`, `instruction.md` | Состояние и выводы **этого** проекта |
| `diagrams/**` с моделями TranslateText | Чужой предмет моделирования |
| `README.md` образца как README целевого репо | Другой продукт; можно подсмотреть структуру разделов |

Исключение: пользователь **явно** просит перенести конкретный артефакт как образец формы (тогда копировать структуру/шаблон таблицы, не факты).

---

## 5. Рекомендуемый порядок работы агента целевого проекта

1. Прочитать этот файл целиком.
2. Уточнить у пользователя (с рекомендацией): стек UI (desktop/web), нужен ли свой HTTP API, нужен ли полный MAS из девяти ролей или только аналитика + PM.
3. Скопировать из `legacy/...` обязательный каркас §2 в корень целевого репо (не оставлять рабочие скиллы только внутри `legacy/`).
4. Выполнить санитизацию §3; обновить `list-commands.md` и `rule-structure.mdc` / `documentation/project-structure-*.md` под новое дерево.
5. Создать `reports/project-config.md` и `reports/pm-state.md` из шаблонов по фактам **этого** репозитория.
6. Создать пустые каркасы при необходимости: `requirements/answers-project.md` (заголовок + таблица без строк), `reports/agent-memory.md` (пустой журнал).
7. Не создавать ФТ/US/код TranslateText. Дальше — `/pm` или прямые команды (`/vision`, `/ft`, …) по задаче пользователя.
8. После переноса: кратко отчитаться — что скопировано, что санитизировано, что сознательно не бралось, какие вопросы остались.

---

## 6. Минимальный vs полный набор

**Минимум (только аналитика и документы):**  
§2.1 без front/back/designer/tester при желании упростить; §2.2 без `/openai` если API нет; §2.3 шаблоны PM; правила answers + self-learning; вычищенный `AGENTS.md`.

**Полный MAS как в образце:**  
всё из §2 + санитизированный §3 + роли front/back/designer/tester и команды UI/тестов, согласованные со стеком в `project-config`.

**Не включать без явной просьбы:**  
заполненные требования, код, тесты, память и чеклисты TranslateText (§4).

---

## 7. Критерий «готово» для переноса

- В целевом `.cursor/` есть команды и скиллы, пользователь может вызвать `/pm` или `/ft`.
- Нет в каноне путей/фактов: TranslateText, Ollama-порт, нарезка 500–700, qwen, конкретные `A0xxx` образца (кроме упоминаний в этом инструктаже внутри `legacy/`).
- `project-config.md` описывает **новый** продукт.
- `legacy/` не стал источником правды для разработки; источник правды — файлы целевого репо.

---

## 8. Справка: карта ролей → команды (как в образце)

| Роль | Типичные команды |
| --- | --- |
| pm | `/pm`, утверждение этапа |
| tech-writer | `/vision`, `/gost-3460289` |
| analyst | `/ft`, `/nft`, `/us`, `/uc`, `/data-dictionary` |
| anatomist | `/qc-ft-nft`, `/qc-us-uc`, `/qc-ddd`, `/qc-stage` |
| architect | `/ddd`, `/diagram-mermaid`, `/openai` (по необходимости) |
| designer | `/ui-prototyping` |
| front-developer | `/frontend` |
| back-developer | `/app-layer` |
| tester | `/new-tests`, `/use-tests` |

Точная таблица назначения — в `legacy/.../.cursor/agents/agent-pm.md` после копирования сверить с целевым `list-commands.md`.
