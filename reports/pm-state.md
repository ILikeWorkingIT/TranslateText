# Состояние ПМ

Шаблон: `reports/templates/pm-state.template.md`.

## Текущий этап

- stage-id: app-layer
- stage-name: Умолчание модели qwen2.5:7b (A0178, A0179)
- status: in-progress
- approval: Stage: S-07: APPROVED; Stage: S-07b: APPROVED; Stage: S-07c: APPROVED; Stage: S-08: APPROVED; Stage: S-09: APPROVED; Stage: S-10: APPROVED; Stage: S-11: APPROVED; Stage: S-12: APPROVED; Stage: S-13: APPROVED
- исполнитель: back-developer
- очередь: пустой /pm 2026-09-24 — статус, этап не стартовал. Гейт /qc-stage этого app-layer по-прежнему не запускался. Отдельно по запросу написана инструкция `reports/groq-instructions.md` (подключение Groq для другого чата). Глобальный этап не менялся.

`status`: `idle` | `in-progress` | `gate` | `blocked` | `awaiting-approval`.
`approval`: пусто или `Stage: <stage-id>: APPROVED` (ставит ПМ только после фразы пользователя «утверждаю» / «принимаю этап»).

## Гейт качества

- последний `/qc-stage`: 2026-08-30, `reports/review-report.md` (S-13)
- вердикт: pass
- critical / major открыты: нет
- minor / known issues: нет

## Блокеры

-

## Очередь действий

- Сделано: срезы S-00…S-13 отмечены готовыми; S-13 APPROVED (2026-08-30). Умолчание модели — `qwen2.5:7b` (A0178); `qwen2.5:3b` в списке не скрывается. Облачный канал закрыт ответами A0181–A0189 (FT-056–FT-060, Gemini); открытых вопросов по ФТ нет.
- Следующий шаг (предложение, без старта): `/qc-ft-nft` по пакету облачного канала. Среза в `checklist.md` на FT-056–FT-060 нет. Код не писать, пока нет отдельного среза и подтверждения. Гейт `/qc-stage` этапа `app-layer` (умолчание 7b) не запускался.
