# Отчёт гейта стадии

Анатомист заполняет по `/qc-stage`. ПМ читает вердикт. Не утверждает этап за пользователя.

## Манифест стадии

- stage-id: S-12
- команда из `.cursor/list-commands.md`: срез чеклиста; слои `/app-layer` + `/frontend`
- исполнитель: back-developer, front-developer, tester
- дата: 2026-08-30

## Артефакты

| Ожидаемый путь | Есть | Замечание |
| --- | --- | --- |
| `reports/checklist.md` (S-12) | да | `[x]`; ручная приёмка — чат 2026-08-30 («Все открывает, работает») |
| `src/services/extract_source.py` | да | `ExtractSource`: `.txt`/`.md`/`.docx`/`.pdf`; пустой/битый → `DocumentParseError` |
| `src/use_cases/load_source.py` | да | без изменений контракта |
| `src/requirements.txt` | да | добавлен `pypdf` |
| `src/ui/bridge.py` | да | `LoadSourceBridge` без смены контракта |
| `src/ui/layout.py`, `src/ui/messages.py` | да | `OPEN_FILETYPES` — четыре формата; `_source_format_of` для `.docx`/`.pdf` |
| `tests/test_extract_source.py`, `tests/test_open_source.py` | да | unit + GUI |
| `reports/test-run.md` | да | 200 passed |

## Чек-лист верификации

| # | Критерий | Результат | Заметка |
| --- | --- | --- | --- |
| 1 | Артефакт на правильном пути | pass | служба в `services/`; диалог в `layout.py` / `messages.py` |
| 2 | Нет правок вне Input Manifest роли | pass | нет FastAPI; OCR/PyMuPDF нет; UI не парсит файлы в `_build_*` |
| 3 | Существующий точечный скилл не затёрт | pass | `/app-layer` → `skill-app-layer.md`; `/frontend` → `skill-frontend-developer.md` |
| 4 | Критерии приёмки стадии проверяемы | pass | автотесты; ручная приёмка — launcher |

## Критерии «срез готов»

| Критерий | Результат | Заметка |
| --- | --- | --- |
| `.docx` и `.pdf` с текстом заполняют «Оригинальный текст» | pass | unit + GUI |
| Допустимый формат, текст не извлечён: сообщение, перевод не стартует | pass | пустой docx, PDF без слоя, битые файлы; поле не подменяется |
| Диалог не предлагает форматы вне FT-042 | pass | фильтр по умолчанию — все четыре; `.xlsx` не открывается |

## Замечания

| ID | Уровень | Суть | Где |
| --- | --- | --- | --- |
| S11-1 | — | Снято: `.docx`/`.pdf` и полный FT-042 закрыты в S-12. | — |

## Вердикт

Вердикт: `pass`
