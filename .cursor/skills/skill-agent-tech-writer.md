---
name: skill-agent-tech-writer
description: >-
  Router for the tech-writer agent. Slice A has no /report-weekly yet.
  Drafts only from existing report facts.
disable-model-invocation: true
owner: tech-writer
---

# Скилл агента tech-writer

Команды `/report-weekly`, `/report-presentation`, `/release-notes` в срезе A не созданы.

Если ПМ просит текст для заказчика:

1. Читай только существующие файлы в `reports/` (в том числе `daily/`, `commit-audit/`, `test-run.md`, `checklist.md`).
2. Пустые папки не заполняй выдуманными событиями. Напиши, каких артефактов не хватает.
3. Не меняй `requirements/` и `src/`.
