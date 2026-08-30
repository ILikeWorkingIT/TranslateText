# Состояние ПМ

Шаблон: `reports/templates/pm-state.template.md`.

## Текущий этап

- stage-id: S-07
- stage-name: Очередь фрагментов по абзацам (FT-015…FT-020, FT-022)
- status: awaiting-approval
- approval:
- исполнитель: back-developer
- очередь: ручная приёмка S-07 → /use-tests (полный прогон)

`status`: `idle` | `in-progress` | `gate` | `blocked` | `awaiting-approval`.
`approval`: пусто или `Stage: <stage-id>: APPROVED` (ставит ПМ только после фразы пользователя «утверждаю» / «принимаю этап»).

## Гейт качества

- последний `/qc-stage`:
- вердикт:
- critical / major открыты: нет
- minor / known issues:

## Блокеры

-

## Очередь действий

- Сделано: `/app-layer` — `EmptyInstructionError` до воркера; промпт не подставляется; снимок — инструкция из команды
- Сделано: `/frontend` — диалог FT-029 при пустой инструкции; после согласия — базовый промпт текущего направления и старт перевода
- Сделано: `/new-tests` — 5 UI-тестов S-05 в `tests/test_empty_instruction.py`
- Сделано: `/use-tests` — 70 passed, 1 error (env Tcl); отчёт `reports/test-run.md`
- Сделано: ручная приёмка S-06 (2026-08-30) — сообщение о лимите работает
- Сделано: `/app-layer` S-07 — `SplitText` по абзацам; очередь фрагментов в `StartTranslation`
- Сделано: `/frontend` S-07 — прогресс и частичная склейка в поле перевода
- Сделано: unit-тесты S-07 в `test_split_text.py`, `test_start_translation.py`
- Сделано: B-001 — Ctrl+C на русской раскладке (VK_C / Cyrillic_es), как Ctrl+V (VK_V / Cyrillic_em)
- Следующий срез после приёмки: **S-07b** — сверхдлинный абзац (FT-025)
