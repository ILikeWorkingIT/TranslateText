---
name: skill-agent-tech-writer
description: >-
  Router for the tech-writer agent. Opens /vision (skill-vision). Slice A has no
  /report-weekly yet; other drafts only from existing report facts.
disable-model-invocation: true
owner: tech-writer
---

# Скилл агента tech-writer

Открой и выполни точечный скилл. Этот файл — только маршрутизатор.

| Задача | Команда | Скилл |
| --- | --- | --- |
| Vision & Scope | `/vision` | `.cursor/skills/skill-vision.md` |

Команды `/report-weekly`, `/report-presentation`, `/release-notes` в срезе A не созданы.

Если ПМ просит текст для заказчика (не Vision):

1. Читай только существующие файлы в `reports/` (в том числе `daily/`, `commit-audit/`, `test-run.md`, `checklist.md`).
2. Пустые папки не заполняй выдуманными событиями. Напиши, каких артефактов не хватает.
3. Не меняй таблицы требований в `requirements/` и код в `src/`. Для `/vision` допускается запись `artifacts/vision-scope.md` и закрытых пар `VS` в `answers-project.md` по скиллу.
