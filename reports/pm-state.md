# Состояние ПМ

Шаблон: `reports/templates/pm-state.template.md`.

## Текущий этап

- stage-id:
- stage-name:
- status: idle
- approval:
- исполнитель:
- очередь:

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

-
