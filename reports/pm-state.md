# Состояние ПМ

Шаблон: `reports/templates/pm-state.template.md`.

## Текущий этап

- stage-id: S-07b
- stage-name: Сверхдлинный абзац (FT-025)
- status: idle
- approval: Stage: S-07: APPROVED; Stage: S-07b: APPROVED
- исполнитель: back-developer
- очередь: следующий срез **S-07c** (FT-054) — `/us` / `/uc`, затем `/app-layer` + `/frontend`

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

- Сделано: `/use-tests` 2026-08-30 — 111 passed; отчёт `reports/test-run.md`
- Сделано: утверждение S-07 и S-07b (чат)
- Сделано: `A0146`–`A0150` — отмена очереди в MVP (FT-054), детали согласованы
- Следующий срез: **S-07c** — отмена перевода; затем S-08
